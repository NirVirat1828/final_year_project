"""
PDF Generation Utility Module.

Provides low-level infrastructure to render professional PDF documents
using ReportLab.  All rendering logic is isolated here — no database
models, no FastAPI imports, no business logic.

The single public function ``generate_prediction_pdf`` accepts a plain
dictionary describing a prediction record and returns the finished PDF
entirely in memory as ``bytes``.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# ──────────────────────────────────────────────────────────────────────
# Colour palette
# ──────────────────────────────────────────────────────────────────────

_NAVY = colors.HexColor("#1B2A4A")
_DARK_BLUE = colors.HexColor("#29417A")
_LIGHT_BLUE = colors.HexColor("#DCE6F1")
_ACCENT_GREEN = colors.HexColor("#27AE60")
_ACCENT_ORANGE = colors.HexColor("#E67E22")
_LIGHT_GREY = colors.HexColor("#F5F5F5")
_WHITE = colors.white
_BLACK = colors.black


# ──────────────────────────────────────────────────────────────────────
# Custom paragraph styles
# ──────────────────────────────────────────────────────────────────────

_BASE_STYLES = getSampleStyleSheet()

_TITLE_STYLE = ParagraphStyle(
    "ReportTitle",
    parent=_BASE_STYLES["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=_NAVY,
    spaceAfter=4,
    alignment=1,  # centre
)

_SUBTITLE_STYLE = ParagraphStyle(
    "ReportSubtitle",
    parent=_BASE_STYLES["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=colors.grey,
    spaceAfter=16,
    alignment=1,
)

_SECTION_STYLE = ParagraphStyle(
    "SectionHeader",
    parent=_BASE_STYLES["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=16,
    textColor=_DARK_BLUE,
    spaceBefore=14,
    spaceAfter=6,
)

_BODY_STYLE = ParagraphStyle(
    "BodyText",
    parent=_BASE_STYLES["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=13,
    textColor=_BLACK,
)

_FOOTER_STYLE = ParagraphStyle(
    "FooterText",
    parent=_BASE_STYLES["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=8,
    leading=10,
    textColor=colors.grey,
    alignment=1,
)


# ──────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────

def _fmt(value: Any, precision: int = 4) -> str:
    """Format a numeric value to *precision* decimal places."""
    try:
        return f"{float(value):.{precision}f}"
    except (ValueError, TypeError):
        return str(value) if value is not None else "N/A"


def _kv_table(rows: List[List[str]]) -> Table:
    """
    Build a two-column key → value table with alternating row shading.

    Args:
        rows: A list of ``[key, value]`` pairs (no header row).

    Returns:
        A styled ReportLab ``Table`` object.
    """
    table = Table(rows, colWidths=[2.4 * inch, 4.0 * inch])

    style_commands: list = [
        # Global
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
    ]
    # Alternating row shading
    for i in range(len(rows)):
        if i % 2 == 0:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), _LIGHT_GREY))

    table.setStyle(TableStyle(style_commands))
    return table


def _data_table(headers: List[str], rows: List[List[str]],
                col_widths: Optional[List[float]] = None) -> Table:
    """
    Build a table with a header row and body rows.

    Args:
        headers: Column header strings.
        rows: Body data as a list of rows (each row is a list of strings).
        col_widths: Optional explicit column widths.

    Returns:
        A styled ReportLab ``Table`` object.
    """
    data = [headers] + rows
    table = Table(data, colWidths=col_widths)

    style_commands = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), _DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), _WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        # Body rows
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
    ]
    # Alternating body row shading
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_commands.append(("BACKGROUND", (0, i), (-1, i), _LIGHT_GREY))

    table.setStyle(TableStyle(style_commands))
    return table


def _horizontal_rule() -> Table:
    """Return a thin horizontal line spanning the page width."""
    line = Table([[""]], colWidths=[6.5 * inch])
    line.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1, _LIGHT_BLUE),
    ]))
    return line


def _add_page_number(canvas: Any, doc: SimpleDocTemplate) -> None:
    """Draws the page number on the bottom right corner."""
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    page_num = f"Page {doc.page}"
    canvas.drawRightString(letter[0] - 0.75 * inch, 0.4 * inch, page_num)
    canvas.restoreState()


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────

def generate_prediction_pdf(record: Dict[str, Any]) -> bytes:
    """
    Generate a professional PDF report from a structured prediction record.

    The *record* dictionary must contain the following top-level keys:

    - ``prediction_id`` (int)
    - ``batch_id`` (str)
    - ``model_version`` (str)
    - ``freshness_grade`` (str)
    - ``prediction_days`` (float)
    - ``confidence`` (float)
    - ``storage_temperature`` (float)
    - ``latency_ms`` (float)
    - ``created_at`` (datetime | str | None)
    - ``sensor_readings`` (List[float])
    - ``nutritional_status`` (str)
    - ``estimated_age_days`` (float)
    - ``endpoint`` (str)

    Args:
        record: A flat dictionary containing all prediction fields.

    Returns:
        The PDF document as raw ``bytes``, generated entirely in memory.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    elements: list = []

    def _format_dt(dt_val: Any) -> str:
        if isinstance(dt_val, datetime):
            return dt_val.strftime("%d %B %Y\n%H:%M:%S UTC")
        elif isinstance(dt_val, str):
            try:
                # Handle standard ISO strings safely
                clean_str = dt_val.replace('Z', '+00:00')
                dt = datetime.fromisoformat(clean_str)
                return dt.strftime("%d %B %Y\n%H:%M:%S UTC")
            except ValueError:
                return dt_val
        return "N/A"

    generated_ts = _format_dt(datetime.now(timezone.utc))
    prediction_ts = _format_dt(record.get("created_at"))


    # ── Header ───────────────────────────────────────────────────────
    elements.append(Paragraph(
        "Electronic Tongue Orange Freshness Report", _TITLE_STYLE
    ))
    subtitle_parts = [
        f"Prediction ID: {record.get('prediction_id', 'N/A')}",
        f"Batch ID: {record.get('batch_id', 'N/A')}",
        f"Generated: {generated_ts}",
        f"Model Version: {record.get('model_version', 'N/A')}",
    ]
    elements.append(Paragraph(" &nbsp;|&nbsp; ".join(subtitle_parts), _SUBTITLE_STYLE))
    elements.append(_horizontal_rule())
    elements.append(Spacer(1, 10))

    # ── 1. Batch Information ─────────────────────────────────────────
    elements.append(Paragraph("Batch Information", _SECTION_STYLE))
    elements.append(_kv_table([
        ["Batch ID", str(record.get("batch_id", "N/A"))],
        ["Storage Temperature", f"{_fmt(record.get('storage_temperature'), 1)} °C"],
        ["Endpoint", str(record.get("endpoint", "/api/v1/analyze-batch"))],
        ["Prediction Timestamp", prediction_ts],
    ]))
    elements.append(Spacer(1, 8))

    # Sensor readings table
    readings: list = record.get("sensor_readings", [])
    if readings:
        elements.append(Paragraph("Sensor Readings", _SECTION_STYLE))

        # Build rows of up to 6 columns
        cols = 6
        header = [f"S{i + 1}" for i in range(min(cols, len(readings)))]
        body_rows: List[List[str]] = []
        for start in range(0, len(readings), cols):
            chunk = readings[start:start + cols]
            row = [_fmt(v, 4) for v in chunk]
            # Pad the last row if needed
            while len(row) < len(header):
                row.append("")
            body_rows.append(row)

        col_w = [1.08 * inch] * len(header)
        elements.append(_data_table(header, body_rows, col_widths=col_w))
        elements.append(Spacer(1, 8))

    elements.append(_horizontal_rule())
    elements.append(Spacer(1, 6))

    # ── 2. Prediction Summary (highlighted) ──────────────────────────
    elements.append(Paragraph("Prediction Summary", _SECTION_STYLE))

    raw_grade = str(record.get("freshness_grade", "N/A")).upper()
    grade_map = {
        "A": ("Fresh", _ACCENT_GREEN),
        "B": ("Good", colors.HexColor("#2980B9")), # Blue
        "C": ("Old", _ACCENT_ORANGE),
        "REJECT": ("Spoiled", colors.HexColor("#C0392B")), # Red
        "F": ("Spoiled", colors.HexColor("#C0392B")),
    }
    status_text, status_colour = grade_map.get(raw_grade, (raw_grade, _BLACK))

    confidence_val = record.get("confidence")
    if confidence_val is not None:
        confidence_str = f"{_fmt(confidence_val, 2)}%"
    else:
        confidence_str = "N/A"

    summary_rows = [
        ["Estimated Age (days)", _fmt(record.get("estimated_age_days"), 2)],
        ["Freshness Status", status_text],
        ["Confidence", confidence_str],
        ["Nutritional Status", str(record.get("nutritional_status", "N/A"))],
    ]
    summary_table = _kv_table(summary_rows)

    # Colour-highlight the status value cell
    summary_table.setStyle(TableStyle([
        ("TEXTCOLOR", (1, 1), (1, 1), status_colour),
        ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 6))
    elements.append(_horizontal_rule())
    elements.append(Spacer(1, 6))

    # ── 2b. Top Influential Features (Optional SHAP) ─────────────────
    shap_features = record.get("shap_features")
    if shap_features and isinstance(shap_features, list):
        elements.append(Paragraph("Top Influential Features", _SECTION_STYLE))
        
        # Build a table for features
        headers = ["Rank", "Feature Name", "Impact", "Importance"]
        shap_rows = []
        for feat in shap_features:
            rank = str(feat.get("rank", ""))
            name = str(feat.get("feature_name", ""))
            impact = str(feat.get("impact", ""))
            importance = _fmt(feat.get("absolute_importance"), 4)
            shap_rows.append([rank, name, impact, importance])
            
        elements.append(_data_table(headers, shap_rows, col_widths=[0.6*inch, 2.5*inch, 1.2*inch, 1.2*inch]))
        elements.append(Spacer(1, 6))
        elements.append(_horizontal_rule())
        elements.append(Spacer(1, 6))

    # ── 3. Metadata ──────────────────────────────────────────────────
    elements.append(Paragraph("Metadata", _SECTION_STYLE))
    elements.append(_kv_table([
        ["Prediction ID", str(record.get("prediction_id", "N/A"))],
        ["Model Version", str(record.get("model_version", "N/A"))],
        ["Inference Latency", f"{_fmt(record.get('latency_ms'), 2)} ms"],
        ["Generated Time", generated_ts],
    ]))
    elements.append(Spacer(1, 14))

    # ── Footer ───────────────────────────────────────────────────────
    elements.append(_horizontal_rule())
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "Automatically generated by the Electronic Tongue Prediction API.",
        _FOOTER_STYLE,
    ))
    elements.append(Paragraph(
        "This report is intended for analytical purposes only.",
        _FOOTER_STYLE,
    ))

    # ── Build ────────────────────────────────────────────────────────
    doc.build(
        elements,
        onFirstPage=_add_page_number,
        onLaterPages=_add_page_number,
    )
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
