import pytest
from src.transform import normalize_quotes


def make_row(ts, buy=5.0, sell=5.1, kind="Fechamento"):
    return {"dataHoraCotacao": ts, "cotacaoCompra": buy,
            "cotacaoVenda": sell, "tipoBoletim": kind}


def test_one_quote_per_day_and_currency():
    rows = [
        make_row("2026-11-02 13:00:00.000", 5.01, 5.03),
        make_row("2026-11-02 13:15:00.000", 5.02, 5.04),
        make_row("2026-11-03 13:00:00.000", 5.05, 5.07),
    ]
    result = normalize_quotes("usd", rows)
    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert result[0]["quote_date"] == "2026-11-02"
    assert result[0]["sell_rate"] == 5.04


def test_ignores_non_closing_bulletin():
    assert normalize_quotes("EUR", [make_row("2026-11-02 10:00:00.000", kind="Abertura")]) == []


@pytest.mark.parametrize("row", [
    {"dataHoraCotacao": "not a date", "cotacaoCompra": 5, "cotacaoVenda": 5.1},
    make_row("2026-11-02 13:00:00.000", -1, 5),
    make_row("2026-11-02 13:00:00.000", 5.5, 5.1),
])
def test_rejects_invalid_quotes(row):
    with pytest.raises(ValueError, match="Invalid PTAX record"):
        normalize_quotes("USD", [row])
