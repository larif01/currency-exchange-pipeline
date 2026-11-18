"""Validate and normalize official PTAX quotations."""
from __future__ import annotations
from datetime import datetime
from math import isfinite


def normalize_quotes(currency: str, raw_rows: list[dict]) -> list[dict]:
    """Return one closing quotation per currency and business date.

    Raise on malformed provider records rather than silently invent rates.
    A day can contain multiple bulletin records; retain the last timestamp.
    """
    latest: dict[tuple[str, str], tuple[str, dict]] = {}
    for row in raw_rows:
        try:
            raw_timestamp = str(row["dataHoraCotacao"])
            timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
            day = timestamp.date().isoformat()
            buy = float(row["cotacaoCompra"])
            sell = float(row["cotacaoVenda"])
            if not all(map(isfinite, (buy, sell))) or buy <= 0 or sell <= 0:
                raise ValueError("Rates must be positive finite numbers")
            if buy > sell:
                raise ValueError("Buy rate cannot exceed sell rate")
            kind = row.get("tipoBoletim")
            if kind is not None and kind != "Fechamento":
                continue
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"Invalid PTAX record: {row!r}") from exc
        key = (currency.upper(), day)
        normalized = {"currency": currency.upper(), "quote_date": day,
                      "buy_rate": buy, "sell_rate": sell}
        if key not in latest or raw_timestamp > latest[key][0]:
            latest[key] = (raw_timestamp, normalized)
    return [item[1] for _, item in sorted(latest.items())]
