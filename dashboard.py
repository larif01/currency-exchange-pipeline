"""PTAX exchange-rate analytics dashboard — streamlit run dashboard.py."""
from __future__ import annotations
from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

from src.analytics import calculate_kpis

st.set_page_config(page_title="PTAX | Exchange Analytics", page_icon="💱", layout="wide")
DB_PATH = Path("outputs/exchange_rates.db")
DEMO_PATH = Path("data/demo_rates.csv")


@st.cache_data(show_spinner=False)
def load_rates(db_version: float | None) -> tuple[pd.DataFrame, bool]:
    """Prefer real stored PTAX data; otherwise display clearly labeled demo data."""
    if db_version is not None:
        with sqlite3.connect(DB_PATH) as conn:
            data = pd.read_sql_query(
                "SELECT currency, quote_date, buy_rate, sell_rate "
                "FROM exchange_rates ORDER BY currency, quote_date", conn
            )
        if not data.empty:
            return data, False
    return pd.read_csv(DEMO_PATH), True


db_version = DB_PATH.stat().st_mtime if DB_PATH.exists() else None
df, demo = load_rates(db_version)
df["quote_date"] = pd.to_datetime(df["quote_date"], errors="coerce")
df = df.dropna(subset=["quote_date"])
df["buy_rate"] = pd.to_numeric(df["buy_rate"])
df["sell_rate"] = pd.to_numeric(df["sell_rate"])

st.title("💱 Currency Exchange Analytics")
st.caption("Brazilian Central Bank · PTAX daily closing rates · BRL per foreign currency")
if demo:
    st.warning("DEMONSTRATION MODE — fictional sample rates, NOT official market data. "
               "Run 'python -m src.main' to import official BCB PTAX data.")
else:
    st.success("Official PTAX data imported from Banco Central do Brasil (BCB).")

with st.sidebar:
    st.header("Filtros")
    currencies = sorted(df["currency"].unique().tolist())
    currency = st.selectbox("Moeda", currencies, index=currencies.index("USD") if "USD" in currencies else 0)
    currency_df = df[df["currency"] == currency].copy()
    first, last = currency_df["quote_date"].min().date(), currency_df["quote_date"].max().date()
    period = st.date_input("Período", value=(first, last), min_value=first, max_value=last)
    st.caption("A variação considera a primeira e a última cotação disponíveis no filtro.")

if isinstance(period, (tuple, list)) and len(period) == 2:
    currency_df = currency_df.loc[currency_df["quote_date"].between(
        pd.Timestamp(period[0]), pd.Timestamp(period[1])
    )]
if currency_df.empty:
    st.info("Não há cotações neste período. Selecione outras datas.")
    st.stop()

kpis = calculate_kpis(currency_df)
def brl(value: float) -> str:
    return "R$ " + f"{value:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")


c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Última cotação {currency}/BRL", brl(kpis["latest"]))
c2.metric("Cotação média", brl(kpis["average"]))
c3.metric("Menor cotação", brl(kpis["minimum"]))
c4.metric("Variação no período", f"{kpis['variation_pct']:+.2f}%")

st.subheader("Evolução das cotações")
timeline = (currency_df.sort_values("quote_date")
            .set_index("quote_date")[["buy_rate", "sell_rate"]])
st.line_chart(timeline, x_label="Data", y_label="BRL por unidade de moeda")

left, right = st.columns(2)
with left:
    st.subheader("Resumo")
    st.write(f"**Maior cotação:** {brl(kpis['maximum'])}")
    st.write(f"**Observações:** {kpis['observations']}")
    st.write("**Série:** PTAX fechamento, taxas de compra e venda")
with right:
    st.subheader("Tabela de cotações")
    st.dataframe(currency_df.sort_values("quote_date", ascending=False),
                 use_container_width=True, hide_index=True)

st.download_button("⬇️ Exportar dados filtrados (CSV)",
                   data=currency_df.to_csv(index=False).encode("utf-8-sig"),
                   file_name=f"ptax_{currency.lower()}_filtered.csv", mime="text/csv")
st.caption("PTAX é uma taxa de referência do BCB, não necessariamente a taxa de câmbio "
           "oferecida por bancos ou casas de câmbio. Sem recomendações de investimento.")
