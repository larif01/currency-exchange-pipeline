import sqlite3
from src.load import load_quotes


def test_idempotent_upsert(tmp_path):
    db = tmp_path / "ptax.db"
    row = {"currency": "USD", "quote_date": "2026-11-02",
           "buy_rate": 5.1, "sell_rate": 5.2}
    assert load_quotes([row], db) == 1
    assert load_quotes([row], db) == 1
    updated = {**row, "sell_rate": 5.3}
    load_quotes([updated], db)
    with sqlite3.connect(db) as conn:
        count, rate = conn.execute("SELECT COUNT(*), MAX(sell_rate) FROM exchange_rates").fetchone()
    assert count == 1
    assert rate == 5.3


def test_empty_load_initializes_database(tmp_path):
    db = tmp_path / "ptax.db"
    assert load_quotes([], db) == 0
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM exchange_rates").fetchone()[0] == 0
