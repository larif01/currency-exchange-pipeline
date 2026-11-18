"""SQLite persistence with a composite business key and UPSERT."""
from __future__ import annotations
from pathlib import Path
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS exchange_rates (
  currency TEXT NOT NULL CHECK(currency IN ('USD', 'EUR')),
  quote_date TEXT NOT NULL,
  buy_rate REAL NOT NULL CHECK(buy_rate > 0),
  sell_rate REAL NOT NULL CHECK(sell_rate > 0),
  PRIMARY KEY (currency, quote_date)
);
CREATE INDEX IF NOT EXISTS idx_exchange_rates_date
ON exchange_rates (quote_date);
"""


def load_quotes(rows: list[dict], database: str | Path) -> int:
    """Persist rows atomically. Re-running a date range never multiplies rows."""
    db = Path(database)
    db.parent.mkdir(parents=True, exist_ok=True)
    records = [(r["currency"], r["quote_date"], r["buy_rate"], r["sell_rate"]) for r in rows]
    with sqlite3.connect(db) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            """
            INSERT INTO exchange_rates (currency, quote_date, buy_rate, sell_rate)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (currency, quote_date) DO UPDATE SET
                buy_rate=excluded.buy_rate, sell_rate=excluded.sell_rate
            """, records
        )
        conn.commit()
    return len(records)
