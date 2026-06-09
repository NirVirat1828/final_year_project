from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app


def write_openapi_schema(output_path: Path) -> Dict[str, Any]:
    schema = app.openapi()
    output_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    return schema


def _format_schema_reference(schema: Dict[str, Any] | None) -> str:
    if not schema:
        return "No schema available"

    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]

    schema_type = schema.get("type")
    if schema_type == "array":
        return f"array[{_format_schema_reference(schema.get('items'))}]"
    if schema_type == "object":
        properties = schema.get("properties", {})
        if properties:
            return "object"
        return "object"

    return schema.get("title") or schema_type or "value"


def _required_fields(schema: Dict[str, Any] | None) -> List[str]:
    if not schema:
        return []
    return list(schema.get("required", []))


def _render_request_body(request_body: Dict[str, Any] | None) -> List[str]:
    if not request_body:
        return ["No request body."]

    content = request_body.get("content", {})
    json_schema = content.get("application/json", {}).get("schema", {})
    lines = [f"- Content type: application/json", f"- Schema: {_format_schema_reference(json_schema)}"]

    required_fields = _required_fields(json_schema)
    if required_fields:
        lines.append(f"- Required fields: {', '.join(required_fields)}")

    properties = json_schema.get("properties", {})
    if properties:
        lines.append("- Fields:")
        for field_name, field_schema in properties.items():
            description = field_schema.get("description", "")
            field_type = field_schema.get("type", "object")
            required_marker = "required" if field_name in required_fields else "optional"
            suffix = f" - {description}" if description else ""
            lines.append(f"  - `{field_name}` ({field_type}, {required_marker}){suffix}")

    return lines


def _render_response(response_spec: Dict[str, Any]) -> List[str]:
    content = response_spec.get("content", {})
    json_schema = content.get("application/json", {}).get("schema", {})
    lines = [f"- Schema: {_format_schema_reference(json_schema)}"]

    properties = json_schema.get("properties", {})
    if properties:
        lines.append("- Response fields:")
        for field_name, field_schema in properties.items():
            field_type = field_schema.get("type", "object")
            suffix = f" - {field_schema.get('description', '')}" if field_schema.get("description") else ""
            lines.append(f"  - `{field_name}` ({field_type}){suffix}")

    return lines


def generate_api_contract(schema: Dict[str, Any], output_path: Path) -> None:
    lines: List[str] = ["# API Contract", ""]

    paths = schema.get("paths", {})
    for path_name in sorted(paths):
        lines.append(f"## `{path_name}`")
        lines.append("")

        path_item = paths[path_name]
        for method in sorted(path_item):
            operation = path_item[method]
            summary = operation.get("summary") or operation.get("operationId") or "No summary"
            lines.append(f"### {method.upper()} {path_name}")
            lines.append(f"- Summary: {summary}")

            if operation.get("parameters"):
                lines.append("- Parameters:")
                for parameter in operation["parameters"]:
                    required_marker = "required" if parameter.get("required") else "optional"
                    schema_info = parameter.get("schema", {})
                    lines.append(
                        f"  - `{parameter.get('name')}` ({parameter.get('in')}, {required_marker}, {schema_info.get('type', 'object')})"
                    )

            lines.append("- Request body:")
            lines.extend(_render_request_body(operation.get("requestBody")))

            responses = operation.get("responses", {})
            lines.append("- Responses:")
            for status_code in sorted(responses):
                lines.append(f"  - `{status_code}`")
                lines.extend(f"    {line}" for line in _render_response(responses[status_code]))

            lines.append("")

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    openapi_path = ROOT_DIR / "openapi.json"
    contract_path = ROOT_DIR / "api_contract.md"
    schema = write_openapi_schema(openapi_path)
    generate_api_contract(schema, contract_path)
    print(f"Wrote {openapi_path}")
    print(f"Wrote {contract_path}")


if __name__ == "__main__":
    main()
