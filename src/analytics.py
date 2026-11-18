"""Pure KPI functions shared with the dashboard."""
from __future__ import annotations
import pandas as pd


def calculate_kpis(frame: pd.DataFrame) -> dict[str, float | int]:
    """Return summary statistics for a single currency, ordered by quote date."""
    if frame.empty:
        return {"latest": 0.0, "average": 0.0, "minimum": 0.0,
                "maximum": 0.0, "variation_pct": 0.0, "observations": 0}
    df = frame.sort_values("quote_date")
    rates = pd.to_numeric(df["sell_rate"])
    first, last = float(rates.iloc[0]), float(rates.iloc[-1])
    return {
        "latest": last,
        "average": float(rates.mean()),
        "minimum": float(rates.min()),
        "maximum": float(rates.max()),
        "variation_pct": (last / first - 1) * 100 if first else 0.0,
        "observations": int(len(df)),
    }
