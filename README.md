# Currency Exchange Data Pipeline 💱

![Python](https://img.shields.io/badge/Python-3.12-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-0a7)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-ff4b4b)
![Tests](https://img.shields.io/badge/Tests-pytest-3775a9)

A portfolio-ready **end-to-end ETL and analytics project** that extracts official daily closing exchange-rate quotations (PTAX) from the **Central Bank of Brazil (BCB)**, cleans and validates the response, stores it in SQLite, and displays it in an interactive Streamlit dashboard.

This project demonstrates **REST API ingestion, JSON processing, data quality, time-series analysis, SQL, unit testing, and idempotent persistence**.

## Architecture

```text
BCB PTAX OData API ── HTTP + retry ──> Python extract
                                         |
                                Validate / normalize
                                         |
                                     SQLite
                                         |
                           Streamlit + SQL analytics
```

## Stack

- Python 3.12 · requests · pandas
- SQLite with a composite primary key (`currency`, `quote_date`)
- Streamlit (interactive analytics dashboard)
- pytest + GitHub Actions (CI)

## Quick start

```bash
git clone https://github.com/larif01/currency-exchange-pipeline.git
cd currency-exchange-pipeline
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt

# Fetch the last 30 days of official BCB PTAX closing quotations
python -m src.main

# Launch the interactive dashboard
streamlit run dashboard.py

# Run offline unit tests (no real API calls)
python -m pytest -q
```

Streamlit normally opens at `http://localhost:8501`. An internet connection is required **only to collect live API data**.

### Custom date range and currencies

```bash
python -m src.main --start 2026-10-01 --end 2026-11-17 --currencies USD EUR
```

Use ISO `YYYY-MM-DD` dates. Collection is bounded to USD and EUR and uses BCB's `CotacaoMoedaPeriodoFechamento` OData endpoint.

## Dashboard

The interactive Streamlit UI provides:

- Latest **selling quotation** for the chosen currency (BRL per USD/EUR)
- Mean, minimum, maximum, and percentage change over the selected period
- Time-series chart for buy and sell rates
- Date and currency filters, table view, and CSV download

**Demo mode:** if you haven't run the ETL, the dashboard uses `data/demo_rates.csv`. These rates are **synthetic and explicitly labeled**, *not official exchange rates*. Once you execute the ETL, the UI reads `outputs/exchange_rates.db`.

## Database

`exchange_rates(currency, quote_date, buy_rate, sell_rate)`

The composite primary key prevents duplicate observations. Repeated ETL runs update existing dates rather than duplicating records. The `outputs/` folder is ignored by Git.

The `sql/analysis.sql` file includes latest rate, monthly averages, min/max and observed day-on-day variations. Query via:

```bash
sqlite3 outputs/exchange_rates.db < sql/analysis.sql
```

## Repository structure

```text
currency-exchange-pipeline/
├── .github/workflows/ci.yml
├── data/demo_rates.csv
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── analytics.py
│   └── main.py
├── sql/analysis.sql
├── tests/
├── dashboard.py
├── requirements.txt
└── README.md
```

## Engineering design

**Extraction:** HTTPS request to BCB's official PTAX OData API. Automatic retries on transient failures, explicit timeouts, and paginated responses.

**Transformation:** validates timestamp and positive numeric rates; filters to closing bulletin records; selects one quote per currency and observation date.

**Load:** atomic SQLite upsert, constrained by a composite primary key. SQL analysis and the dashboard consume the same persisted dataset.

**Quality:** offline tests verify query parameters, pagination, invalid data handling, aggregation, and idempotence. GitHub Actions runs tests on PRs and pushes.

## Data source and important notes

- [Banco Central do Brasil — PTAX Open Data](https://dadosabertos.bcb.gov.br/dataset/taxas-de-cambio-todos-os-boletins-diarios)
- [BCB PTAX OData API documentation](https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/documentacao)

PTAX is a **reference exchange rate**, not a bank's retail conversion rate or a real-time trading price. There are no quotes on every calendar date (weekends and holidays typically have no daily closing bulletin). The API may be temporarily unavailable.

## Next steps

- Deploy a public Streamlit app with a scheduled API ingestion
- Add Airflow or GitHub Actions scheduled refresh
- Add PostgreSQL and dbt models for larger data engineering pipelines

---
Portfolio project · Educational purposes
