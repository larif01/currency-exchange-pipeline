import pandas as pd
import pytest
from src.analytics import calculate_kpis


def test_kpis():
    frame = pd.DataFrame({"quote_date": ["2026-01-02", "2026-01-01"],
                          "sell_rate": [5.5, 5.0]})
    result = calculate_kpis(frame)
    assert result["latest"] == 5.5
    assert result["average"] == pytest.approx(5.25)
    assert result["variation_pct"] == pytest.approx(10.0)
    assert result["observations"] == 2


def test_empty():
    result = calculate_kpis(pd.DataFrame(columns=["quote_date", "sell_rate"]))
    assert result["observations"] == 0
    assert result["variation_pct"] == 0
