"""Streamlit dashboard reading directly from the dbt-built DuckDB marts.

Opens the warehouse read-only so it never conflicts with a concurrent
`dbt run` holding the write lock.

Run:
    streamlit run dashboard/app.py
"""
from __future__ import annotations

import duckdb
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import WAREHOUSE_PATH

st.set_page_config(page_title="Retail Analytics", layout="wide")
st.title("Retail Analytics")

# A single accent hue for magnitude charts (one series, ranked by value -
# color here would be purely decorative, so every bar gets the same color
# and the ranking does the work). A small fixed-order palette for the one
# true categorical chart (order status).
ACCENT = "#0173B2"
STATUS_COLORS = {"completed": "#029E73", "cancelled": "#DE8F05", "returned": "#CC3311"}


@st.cache_data(ttl=30)
def load_data() -> pd.DataFrame:
    con = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    try:
        df = con.execute(
            """
            select
                f.order_date,
                f.status,
                f.quantity,
                f.line_total,
                p.product_name,
                p.category,
                c.country
            from main.fact_orders f
            join main.dim_products p on f.product_id = p.product_id
            join main.dim_customers c on f.customer_id = c.customer_id
            """
        ).fetchdf()
    finally:
        con.close()
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


try:
    df = load_data()
except Exception:
    st.error("No warehouse found yet. Run `python run_pipeline.py` first.")
    st.stop()

completed = df[df["status"] == "completed"]

kpi_cols = st.columns(3)
kpi_cols[0].metric("Total revenue (completed orders)", f"${completed['line_total'].sum():,.0f}")
kpi_cols[1].metric("Completed orders", f"{completed['order_date'].count():,}")
kpi_cols[2].metric(
    "Avg order line value",
    f"${completed['line_total'].mean():,.2f}" if len(completed) else "$0.00",
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue over time")
    daily_revenue = completed.groupby(completed["order_date"].dt.to_period("M"))["line_total"].sum()
    daily_revenue.index = daily_revenue.index.to_timestamp()
    fig = go.Figure(go.Scatter(x=daily_revenue.index, y=daily_revenue.values, mode="lines", line=dict(color=ACCENT, width=2)))
    fig.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)", height=350, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Orders by status")
    status_counts = df["status"].value_counts()
    fig = go.Figure(
        go.Bar(
            x=status_counts.index,
            y=status_counts.values,
            marker_color=[STATUS_COLORS.get(s, "#888888") for s in status_counts.index],
        )
    )
    fig.update_layout(xaxis_title="Status", yaxis_title="Order lines", height=350, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 10 products by revenue")
    top_products = completed.groupby("product_name")["line_total"].sum().sort_values(ascending=False).head(10)
    fig = go.Figure(go.Bar(x=top_products.values, y=top_products.index, orientation="h", marker_color=ACCENT))
    fig.update_layout(xaxis_title="Revenue ($)", yaxis_title="", height=400, margin=dict(t=20), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Revenue by category")
    category_revenue = completed.groupby("category")["line_total"].sum().sort_values(ascending=False)
    fig = go.Figure(go.Bar(x=category_revenue.values, y=category_revenue.index, orientation="h", marker_color=ACCENT))
    fig.update_layout(xaxis_title="Revenue ($)", yaxis_title="", height=400, margin=dict(t=20), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)
