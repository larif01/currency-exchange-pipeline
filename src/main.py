"""CLI to retrieve daily official PTAX closing quotations."""
from __future__ import annotations
import argparse
from datetime import date, timedelta
from pathlib import Path
import logging
from src.extract import fetch_ptax, SUPPORTED_CURRENCIES
from src.transform import normalize_quotes
from src.load import load_quotes

LOGGER = logging.getLogger(__name__)


def run(start: date, end: date, currencies: list[str], database: Path) -> dict[str, int]:
    if start > end:
        raise ValueError("Start date must not exceed end date")
    summary = {}
    for currency in currencies:
        LOGGER.info("Fetching %s from %s through %s", currency, start, end)
        raw = fetch_ptax(currency, start, end)
        normalized = normalize_quotes(currency, raw)
        loaded = load_quotes(normalized, database)
        summary[currency] = loaded
        LOGGER.info("%s: %s closing quotes stored", currency, loaded)
    return summary


def main() -> None:
    today = date.today()
    parser = argparse.ArgumentParser(description="Collect BCB official PTAX closing quotations")
    parser.add_argument("--start", type=date.fromisoformat, default=today - timedelta(days=30))
    parser.add_argument("--end", type=date.fromisoformat, default=today)
    parser.add_argument("--currencies", nargs="+", choices=SUPPORTED_CURRENCIES, default=list(SUPPORTED_CURRENCIES))
    parser.add_argument("--database", type=Path, default=Path("outputs/exchange_rates.db"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        print(run(args.start, args.end, args.currencies, args.database))
    except Exception:
        LOGGER.exception("Unable to complete PTAX ETL; retry later or check internet access")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
