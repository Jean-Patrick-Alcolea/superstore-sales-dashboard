# Imports

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# load data

df = pd.read_csv(Path("data") / "Superstore_clean.csv")
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Page configuration

st.set_page_config(page_title="Superstore Dashboard", layout="wide")
st.title("Superstore Sales and Profit Dashboard")
st.markdown("Visualizing key insights from the superstore dataset")

# Filters

st.sidebar.header("Filters")
regions = st.sidebar.multiselect(
    "Select Region(s)", options=df["Region"].unique(), default=df["Region"].unique()
)
segments = st.sidebar.multiselect(
    "Select Segment(s)", options=df["Segment"].unique(), default=df["Segment"].unique()
)
categories = st.sidebar.multiselect(
    "Select Category(ies)",
    options=df["Category"].unique(),
    default=df["Category"].unique(),
)

min_date = df["Order Date"].min()
max_date = df["Order Date"].max()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

filtered_df = df[
    (df["Region"].isin(regions))
    & (df["Segment"].isin(segments))
    & (df["Category"].isin(categories))
    & (df["Order Date"] >= pd.to_datetime(date_range[0]))
    & (df["Order Date"] <= pd.to_datetime(date_range[1]))
]

# KPIs

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
aov = filtered_df.groupby("Order ID")["Sales"].sum().mean()
margin = total_profit / total_sales

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Average Order Value", f"${aov:,.2f}")
col4.metric("Profit Margin", f"{margin:.2%}")

# Monthly Sales

monthly = (
    filtered_df.groupby([filtered_df["Order Date"].dt.to_period("M")])["Sales"]
    .sum()
    .reset_index()
)

monthly["Order Date"] = monthly["Order Date"].astype(str)

fig1 = px.line(monthly, x="Order Date", y="Sales", title="Monthly Sales Trend")
st.plotly_chart(fig1, use_container_width=True)

# Sales and Profit by Category

cat = filtered_df.groupby("Category")[["Sales", "Profit"]].sum().reset_index()
fig2 = px.bar(
    cat, x="Category", y="Sales", color="Profit", title="Sales and Profit by Category"
)
st.plotly_chart(fig2, use_container_width=True)

# Sales by Region and Segment

region_seg = filtered_df.groupby(["Region", "Segment"])[["Sales"]].sum().reset_index()
fig3 = px.bar(
    region_seg,
    x="Region",
    y="Sales",
    color="Segment",
    barmode="group",
    title="Sales by Region and Segment",
)
st.plotly_chart(fig3, use_container_width=True)

# Top products by Profit

top_products = (
    filtered_df.groupby("Product Name")["Profit"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top_products,
    x="Profit",
    y="Product Name",
    orientation="h",
    title="Top 10 products by Profit",
)
st.plotly_chart(fig4, use_container_width=True)
