from typing import Optional, Dict


def estimate_remaining_days(
    predicted_days_since_harvest: float,
    max_shelf_life_days: float = 14.0,
) -> float:
    """
    Estimate remaining shelf-life (in days) from predicted current age.

    Remaining = max_shelf_life_days - predicted_days_since_harvest, clipped to [0, max_shelf_life_days].

    Parameters
    ----------
    predicted_days_since_harvest : float
        Output of the Storage Day regression model.
    max_shelf_life_days : float
        Configurable maximum shelf-life for the storage conditions.

    Returns
    -------
    float
        Estimated remaining shelf-life in days.
    """
    remaining = max_shelf_life_days - float(predicted_days_since_harvest)
    if remaining < 0:
        remaining = 0.0
    if remaining > max_shelf_life_days:
        remaining = max_shelf_life_days
    return remaining


def estimate_remaining_from_folic_linear(
    predicted_folic_um: float,
    baseline_um: float = 5.0,
    threshold_um: float = 1.0,
    max_shelf_life_days: float = 14.0,
) -> float:
    """
    Linear mapping heuristic: maps folic fraction to remaining days.

    See `estimate_remaining_from_folic_decay` for a kinetics-based approach.
    """
    if baseline_um <= threshold_um:
        return max_shelf_life_days
    frac = (float(predicted_folic_um) - threshold_um) / (baseline_um - threshold_um)
    if frac < 0:
        frac = 0.0
    if frac > 1:
        frac = 1.0
    return frac * max_shelf_life_days


def estimate_remaining_from_folic_decay(
    predicted_folic_um: float,
    predicted_days_since_harvest: float,
    baseline_um: float = 5.0,
    threshold_um: float = 1.0,
) -> float:
    """
    Exponential decay model to estimate remaining days without fixed max life.

    Assumes folic acid follows first-order decay: F(t) = F0 * exp(-k t)
      - F0 ≈ baseline_um (fresh level)
      - Given current age t = predicted_days_since_harvest and F(t) = predicted_folic_um,
        estimate decay rate k = -ln(F(t)/F0) / t
      - Time to reach end-of-life threshold F_thresh: t_thresh = ln(F0/F_thresh)/k
      - Remaining days = max(t_thresh - t, 0)

    Edge handling:
      - If t ≈ 0 or F(t) ≥ F0, k is ill-defined; fall back to large remaining (use linear heuristic).
      - If predicted_folic_um ≤ threshold_um, remaining = 0.

    Returns remaining days estimate based on kinetics, adapting to faster/slower decay per batch.
    """
    t = float(predicted_days_since_harvest)
    F_t = float(predicted_folic_um)
    F0 = float(baseline_um)
    F_thresh = float(threshold_um)

    if F_t <= F_thresh:
        return 0.0
    if t <= 0.0 or F_t >= F0 or F0 <= 0.0 or F_thresh <= 0.0:
        # Fall back to linear heuristic with a generous cap of 30 days
        return estimate_remaining_from_folic_linear(F_t, F0, F_thresh, max_shelf_life_days=30.0)

    # Estimate decay constant k
    ratio = F_t / F0
    try:
        import math
        k = -math.log(ratio) / t
        if k <= 0.0:
            # Non-decaying or invalid; fallback
            return estimate_remaining_from_folic_linear(F_t, F0, F_thresh, max_shelf_life_days=30.0)
        t_thresh = math.log(F0 / F_thresh) / k
        remaining = t_thresh - t
        if remaining < 0.0:
            remaining = 0.0
        # Reasonable cap to avoid runaway if parameters are extreme
        if remaining > 90.0:
            remaining = 90.0
        return remaining
    except Exception:
        return estimate_remaining_from_folic_linear(F_t, F0, F_thresh, max_shelf_life_days=30.0)


def summarize_remaining_life(
    predicted_days_since_harvest: Optional[float] = None,
    predicted_folic_um: Optional[float] = None,
    config: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Produce a compact summary using available predictions.

    If both signals are present, returns both estimates for transparency.

    Config keys (optional):
      - max_shelf_life_days (default 14)
      - baseline_um (default 5)
      - threshold_um (default 1)

    Returns
    -------
    dict
        {
          "remaining_days_from_age": float | None,
          "remaining_days_from_folic": float | None,
          "recommended_remaining_days": float,
        }
    """
    cfg = {
        "max_shelf_life_days": 14.0,
        "baseline_um": 5.0,
        "threshold_um": 1.0,
    }
    if config:
        cfg.update(config)

    rem_age = None
    rem_folic = None

    if predicted_days_since_harvest is not None:
        rem_age = estimate_remaining_days(
            predicted_days_since_harvest, cfg["max_shelf_life_days"]
        )
    if predicted_folic_um is not None:
        if predicted_days_since_harvest is not None:
            rem_folic = estimate_remaining_from_folic_decay(
                predicted_folic_um,
                predicted_days_since_harvest,
                cfg["baseline_um"],
                cfg["threshold_um"],
            )
        else:
            rem_folic = estimate_remaining_from_folic_linear(
                predicted_folic_um,
                cfg["baseline_um"],
                cfg["threshold_um"],
                cfg["max_shelf_life_days"],
            )

    # Recommendation strategy: if both available, take the minimum for safety
    candidates = [v for v in (rem_age, rem_folic) if v is not None]
    if candidates:
        recommended = min(candidates)
    else:
        recommended = cfg["max_shelf_life_days"]

    return {
        "remaining_days_from_age": rem_age if rem_age is not None else float("nan"),
        "remaining_days_from_folic": rem_folic if rem_folic is not None else float("nan"),
        "recommended_remaining_days": recommended,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Estimate remaining shelf-life from model predictions."
    )
    parser.add_argument("--predicted_days", type=float, default=None,
                        help="Predicted days since harvest (from day model)")
    parser.add_argument("--predicted_folic", type=float, default=None,
                        help="Predicted folic acid in µM (from folic model)")
    parser.add_argument("--max_days", type=float, default=14.0,
                        help="Maximum shelf-life under given conditions")
    parser.add_argument("--baseline_um", type=float, default=5.0,
                        help="Fresh baseline folic acid level (µM)")
    parser.add_argument("--threshold_um", type=float, default=1.0,
                        help="End-of-life folic acid threshold (µM)")
    args = parser.parse_args()

    summary = summarize_remaining_life(
        predicted_days_since_harvest=args.predicted_days,
        predicted_folic_um=args.predicted_folic,
        config={
            "max_shelf_life_days": args.max_days,
            "baseline_um": args.baseline_um,
            "threshold_um": args.threshold_um,
        },
    )
    print(summary)
