import streamlit as st
import pandas as pd
import plotly.express as px
import os
import gdown

# Load data from Google Drive
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1ZVp4JQKiBl0rs_YyKH828ESdJe8_n8qC"
    output = "HealthyJuice_Cleaned.csv"

    if not os.path.exists(output):
        gdown.download(url, output, quiet=False)

    if os.path.exists(output):
        return pd.read_csv(output, parse_dates=["POS_DT"])
    else:
        st.error("CSV file could not be downloaded. Please check the link or file permissions.")
        return pd.DataFrame()

# ✅ LOAD the data
df = load_data()

# ✅ HALT the app if data didn't load properly
if df.empty:
    st.stop()



# Sidebar filters for all dimensions
st.sidebar.header("Filter Options")
state_filter = st.sidebar.multiselect("Select State", df["STATE"].dropna().unique())
city_filter = st.sidebar.multiselect("Select City", df["CITY"].dropna().unique())
zip_filter = st.sidebar.multiselect("Select ZIP Code", df["ZIP"].dropna().unique())
category_filter = st.sidebar.multiselect("Select Category", df["IRI_TSA_CATEGORY"].dropna().unique())
brand_filter = st.sidebar.multiselect("Select Brand", df["IRI_TSA_BRAND"].dropna().unique())
type_filter = st.sidebar.multiselect("Select Product Type", df["IRI_TSA_TYPE"].dropna().unique())
date_range = st.sidebar.date_input("Select Date Range", [df['POS_DT'].min(), df['POS_DT'].max()])

# Apply filters
if state_filter:
    df = df[df["STATE"].isin(state_filter)]
if city_filter:
    df = df[df["CITY"].isin(city_filter)]
if zip_filter:
    df = df[df["ZIP"].isin(zip_filter)]
if category_filter:
    df = df[df["IRI_TSA_CATEGORY"].isin(category_filter)]
if brand_filter:
    df = df[df["IRI_TSA_BRAND"].isin(brand_filter)]
if type_filter:
    df = df[df["IRI_TSA_TYPE"].isin(type_filter)]
df = df[(df['POS_DT'] >= pd.to_datetime(date_range[0])) & (df['POS_DT'] <= pd.to_datetime(date_range[1]))]

# Dashboard Title
st.title("HealthyJuice @ WellMart - Retail Dashboard")

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales ($)", f"${df['STORE_SALES_AMOUNT'].sum():,.2f}")
col2.metric("Units Sold", f"{df['STORE_SALES_UNITS'].sum():,.0f}")
col3.metric("OOS Incidents", f"{(df['STORE_OOS_IND'] == 1).sum()}")
col4.metric("Stores", df["STOR_ID"].nunique())

# Sales Over Time
sales_trend = df.groupby(df['POS_DT'].dt.to_period("M")).agg({'STORE_SALES_AMOUNT': 'sum'}).reset_index()
sales_trend['POS_DT'] = sales_trend['POS_DT'].astype(str)
st.plotly_chart(px.line(sales_trend, x='POS_DT', y='STORE_SALES_AMOUNT', title='Monthly Sales Trend'), use_container_width=True)

# Sales by State
sales_state = df.groupby("STATE")["STORE_SALES_AMOUNT"].sum().reset_index()
st.plotly_chart(px.bar(sales_state, x="STATE", y="STORE_SALES_AMOUNT", title="Sales by State"), use_container_width=True)

# Sales by City
sales_city = df.groupby("CITY")["STORE_SALES_AMOUNT"].sum().reset_index()
st.plotly_chart(px.bar(sales_city, x="CITY", y="STORE_SALES_AMOUNT", title="Sales by City"), use_container_width=True)

# Sales by ZIP
sales_zip = df.groupby("ZIP")["STORE_SALES_AMOUNT"].sum().reset_index()
st.plotly_chart(px.bar(sales_zip, x="ZIP", y="STORE_SALES_AMOUNT", title="Sales by ZIP Code"), use_container_width=True)

# Product Category Breakdown
category_chart = df.groupby("IRI_TSA_CATEGORY")["STORE_SALES_AMOUNT"].sum().reset_index()
st.plotly_chart(px.pie(category_chart, names="IRI_TSA_CATEGORY", values="STORE_SALES_AMOUNT", title="Sales by Product Category"), use_container_width=True)

# Brand Sales
brand_chart = df.groupby("IRI_TSA_BRAND")["STORE_SALES_AMOUNT"].sum().reset_index()
st.plotly_chart(px.bar(brand_chart, x="IRI_TSA_BRAND", y="STORE_SALES_AMOUNT", title="Sales by Brand"), use_container_width=True)

# Product Type Performance
type_chart = df.groupby("IRI_TSA_TYPE")["STORE_SALES_AMOUNT"].sum().reset_index()
st.plotly_chart(px.bar(type_chart, x="STORE_SALES_AMOUNT", y="IRI_TSA_TYPE", orientation='h', title="Top Product Types"), use_container_width=True)

# Inventory Overview
inventory_chart = df.groupby("STATE")[["STORE_ON_HAND_UNITS", "STORE_RECEIPT_UNITS"]].sum().reset_index()
st.plotly_chart(px.bar(inventory_chart, x="STATE", y=["STORE_ON_HAND_UNITS", "STORE_RECEIPT_UNITS"], barmode="group", title="Inventory by State"), use_container_width=True)

# OOS by State
oos_chart = df[df["STORE_OOS_IND"] == 1].groupby("STATE").size().reset_index(name="OOS_Incidents")
st.plotly_chart(px.bar(oos_chart, x="STATE", y="OOS_Incidents", title="OOS Incidents by State"), use_container_width=True)

# Store-Level Insights
st.header("Store Performance Insights")

# Top 10 Stores by Total Sales
top_stores = df.groupby("STOR_ID").agg({
    "STORE_SALES_AMOUNT": "sum",
    "STORE_SALES_UNITS": "sum",
    "STORE_OOS_IND": "sum"
}).sort_values(by="STORE_SALES_AMOUNT", ascending=False).reset_index().head(10)

fig_top_stores = px.bar(top_stores, x="STOR_ID", y="STORE_SALES_AMOUNT", title="Top 10 Stores by Total Sales")
st.plotly_chart(fig_top_stores, use_container_width=True)

# Bottom 10 Stores by Total Sales
bottom_stores = df.groupby("STOR_ID").agg({
    "STORE_SALES_AMOUNT": "sum",
    "STORE_SALES_UNITS": "sum",
    "STORE_OOS_IND": "sum"
}).sort_values(by="STORE_SALES_AMOUNT", ascending=True).reset_index().head(10)

fig_bottom_stores = px.bar(bottom_stores, x="STOR_ID", y="STORE_SALES_AMOUNT", title="Bottom 10 Stores by Total Sales")
st.plotly_chart(fig_bottom_stores, use_container_width=True)

# OOS Rate by Store
oos_rate = df.groupby("STOR_ID").agg({
    "STORE_OOS_IND": "mean",
    "STORE_SALES_AMOUNT": "sum"
}).reset_index().sort_values(by="STORE_OOS_IND", ascending=False).head(10)
oos_rate["OOS_Rate (%)"] = oos_rate["STORE_OOS_IND"] * 100

fig_oos_rate = px.bar(oos_rate, x="STOR_ID", y="OOS_Rate (%)", title="Top 10 Stores by OOS Rate")
st.plotly_chart(fig_oos_rate, use_container_width=True)
