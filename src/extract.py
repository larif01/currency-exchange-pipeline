"""Read official daily closing PTAX rates via BCB's OData API."""
from __future__ import annotations
from datetime import date
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoMoedaPeriodoFechamento("
    "codigoMoeda=@codigoMoeda,"
    "dataInicialCotacao=@dataInicialCotacao,"
    "dataFinalCotacao=@dataFinalCotacao)"
)
SUPPORTED_CURRENCIES = ("USD", "EUR")
MAX_PAGE_SIZE = 1000


def build_session() -> requests.Session:
    """Create a session with bounded timeout and transient-error retry."""
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.7, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"Accept": "application/json", "User-Agent": "currency-exchange-pipeline/1.0"})
    return session


def fetch_ptax(currency: str, start: date, end: date, session: requests.Session | None = None) -> list[dict]:
    """Fetch daily closing records with pagination, preserving raw API fields."""
    currency = currency.upper()
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Currency not supported: {currency}")
    if start > end:
        raise ValueError("Start date must not exceed end date")
    client = session or build_session()
    output: list[dict] = []
    offset = 0
    while True:
        params = {
            "@codigoMoeda": f"'{currency}'",
            "@dataInicialCotacao": f"'{start:%m-%d-%Y}'",
            "@dataFinalCotacao": f"'{end:%m-%d-%Y}'",
            "$format": "json",
            "$top": str(MAX_PAGE_SIZE),
            "$skip": str(offset),
        }
        response = client.get(BASE_URL, params=params, timeout=(5, 30))
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("value"), list):
            raise ValueError("Unexpected response format from BCB PTAX API")
        batch = payload["value"]
        output.extend(batch)
        if len(batch) < MAX_PAGE_SIZE:
            break
        offset += len(batch)
    return output
