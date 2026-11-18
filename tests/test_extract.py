from datetime import date
import pytest
from src.extract import fetch_ptax, MAX_PAGE_SIZE


class FakeResponse:
    def __init__(self, rows):
        self.rows = rows

    def raise_for_status(self):
        return None

    def json(self):
        return {"value": self.rows}


class FakeSession:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return FakeResponse(next(self.pages))


def test_fetch_passes_correct_odata_params():
    session = FakeSession([[{"cotacaoVenda": 5.0}]])
    result = fetch_ptax("usd", date(2026, 1, 2), date(2026, 1, 9), session)
    assert len(result) == 1
    assert session.calls[0]["params"]["@codigoMoeda"] == "'USD'"
    assert session.calls[0]["params"]["@dataInicialCotacao"] == "'01-02-2026'"
    assert session.calls[0]["timeout"] == (5, 30)


def test_fetch_pagination():
    session = FakeSession([[{"id": i} for i in range(MAX_PAGE_SIZE)], [{"id": MAX_PAGE_SIZE}]])
    result = fetch_ptax("EUR", date(2026, 1, 1), date(2026, 1, 31), session)
    assert len(result) == MAX_PAGE_SIZE + 1
    assert session.calls[1]["params"]["$skip"] == str(MAX_PAGE_SIZE)


def test_rejects_invalid_range_or_currency():
    with pytest.raises(ValueError, match="Start date"):
        fetch_ptax("USD", date(2026, 2, 1), date(2026, 1, 1))
    with pytest.raises(ValueError, match="not supported"):
        fetch_ptax("XYZ", date(2026, 1, 1), date(2026, 2, 1))
