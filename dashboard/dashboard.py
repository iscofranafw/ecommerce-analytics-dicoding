import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    layout="wide"
)

sns.set(style="whitegrid")

@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "main_data.csv"
    df = pd.read_csv(csv_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

main_df = load_data()

# Sidebar Filter Interaktif
with st.sidebar:
    st.title("E-Commerce Analytics")
    st.markdown("Filter interaktif untuk mengeksplorasi performa penjualan dan segmentasi pelanggan.")

    min_date = main_df["order_purchase_timestamp"].min().date()
    max_date = main_df["order_purchase_timestamp"].max().date()

    date_range = st.date_input(
        label="Rentang Waktu Transaksi",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    all_states = sorted(main_df["customer_state"].dropna().unique().tolist())
    selected_states = st.multiselect(
        label="Pilih Negara Bagian (State)",
        options=all_states,
        default=[]
    )

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_df = main_df[
    (main_df["order_purchase_timestamp"].dt.date >= start_date) &
    (main_df["order_purchase_timestamp"].dt.date <= end_date)
]

if selected_states:
    filtered_df = filtered_df[filtered_df["customer_state"].isin(selected_states)]

# Header Dashboard & KPI Utama
st.title("E-Commerce Public Dataset: Executive Dashboard")
st.markdown(f"**Periode Analisis:** `{start_date}` s/d `{end_date}`")

col1, col2, col3, col4 = st.columns(4)
with col1:
    total_orders = filtered_df["order_id"].nunique()
    st.metric("Total Pesanan (Delivered)", f"{total_orders:,}")
with col2:
    total_revenue = filtered_df["price"].sum()
    st.metric("Total Revenue Produk", f"BRL {total_revenue:,.2f}")
with col3:
    unique_customers = filtered_df["customer_unique_id"].nunique()
    st.metric("Total Pelanggan Unik", f"{unique_customers:,}")
with col4:
    avg_delivery = filtered_df["delivery_time_days"].mean() if len(filtered_df) > 0 else 0
    st.metric("Rata-rata Durasi Kirim", f"{avg_delivery:.1f} Hari")

st.markdown("---")

# Visualisasi 1: Top & Bottom Kategori Produk
st.subheader("1. Performa Kategori Produk: Revenue Tertinggi vs Terendah")

category_df = filtered_df.groupby("product_category_name_english", as_index=False).agg(
    total_revenue=("price", "sum"),
    total_orders=("order_id", "nunique")
).sort_values(by="total_revenue", ascending=False)

fig_cat, ax_cat = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
colors_top = ["#1f77b4"] + ["#b0c4de"] * 4
colors_bottom = ["#d95f02"] + ["#e0e0e0"] * 4

if not category_df.empty:
    sns.barplot(
        x="total_revenue",
        y="product_category_name_english",
        data=category_df.head(5),
        palette=colors_top,
        ax=ax_cat[0]
    )
    ax_cat[0].set_title("5 Kategori dengan Revenue Tertinggi", fontsize=13, fontweight="bold")
    ax_cat[0].set_xlabel("Total Revenue (BRL)")
    ax_cat[0].set_ylabel(None)

    sns.barplot(
        x="total_revenue",
        y="product_category_name_english",
        data=category_df.sort_values(by="total_revenue", ascending=True).head(5),
        palette=colors_bottom,
        ax=ax_cat[1]
    )
    ax_cat[1].set_title("5 Kategori dengan Revenue Terendah", fontsize=13, fontweight="bold")
    ax_cat[1].set_xlabel("Total Revenue (BRL)")
    ax_cat[1].set_ylabel(None)
    ax_cat[1].invert_xaxis()
    ax_cat[1].yaxis.set_label_position("right")
    ax_cat[1].yaxis.tick_right()

st.pyplot(fig_cat)

st.markdown("---")

# Visualisasi 2: Distribusi Geografis & Tren Bulanan
st.subheader("2. Distribusi Geografis Pelanggan & Tren Transaksi Bulanan")
col_geo, col_trend = st.columns(2)

with col_geo:
    state_df = filtered_df.groupby("customer_state", as_index=False).agg(
        total_orders=("order_id", "nunique")
    ).sort_values(by="total_orders", ascending=False).head(10)

    fig_state, ax_state = plt.subplots(figsize=(8, 5))
    if not state_df.empty:
        sns.barplot(
            x="total_orders",
            y="customer_state",
            data=state_df,
            palette=["#1f77b4"] + ["#b0c4de"] * (len(state_df) - 1),
            ax=ax_state
        )
    ax_state.set_title("Top 10 Negara Bagian Berdasarkan Volume Pesanan", fontweight="bold")
    ax_state.set_xlabel("Jumlah Pesanan")
    ax_state.set_ylabel("State")
    st.pyplot(fig_state)

with col_trend:
    trend_df = filtered_df.copy()
    trend_df["year_month"] = trend_df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    monthly_df = trend_df.groupby("year_month", as_index=False).agg(
        total_orders=("order_id", "nunique")
    )
    fig_trend, ax_trend = plt.subplots(figsize=(8, 5))
    if not monthly_df.empty:
        ax_trend.plot(monthly_df["year_month"], monthly_df["total_orders"], marker="o", linewidth=2.5, color="#1f77b4")
        ax_trend.tick_params(axis="x", rotation=45)
    ax_trend.set_title("Tren Volume Pesanan Bulanan", fontweight="bold")
    ax_trend.set_xlabel("Bulan")
    ax_trend.set_ylabel("Jumlah Pesanan")
    st.pyplot(fig_trend)

st.markdown("---")

# Visualisasi 3: Analisis Lanjutan RFM & Manual Grouping
st.subheader("3. Analisis Lanjutan: RFM Analysis & Segmentasi Pelanggan")

if not filtered_df.empty:
    ref_date = filtered_df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = filtered_df.groupby("customer_unique_id", as_index=False).agg(
        max_date=("order_purchase_timestamp", "max"),
        frequency=("order_id", "nunique"),
        monetary=("total_order_value", "sum")
    )
    rfm["recency"] = (ref_date - rfm["max_date"]).dt.days

    rfm_col1, rfm_col2, rfm_col3 = st.columns(3)
    rfm_col1.metric("Rata-rata Recency (Hari)", f"{rfm['recency'].mean():.1f}")
    rfm_col2.metric("Rata-rata Frequency (Kali)", f"{rfm['frequency'].mean():.2f}")
    rfm_col3.metric("Rata-rata Monetary (BRL)", f"BRL {rfm['monetary'].mean():,.2f}")

    # Manual Grouping
    rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), q=4, labels=[4, 3, 2, 1]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm["f_score"] = np.where(rfm["frequency"] > 1, 4, 1)

    def segment_customer(row):
        if row["f_score"] == 4 and row["r_score"] >= 3:
            return "Champions / Repeat Loyal"
        elif row["r_score"] >= 3 and row["m_score"] >= 3:
            return "High-Value Recent"
        elif row["r_score"] >= 3 and row["m_score"] < 3:
            return "Promising / New Customers"
        elif row["r_score"] == 2:
            return "At Risk / Need Attention"
        else:
            return "Hibernating / Lost"

    rfm["customer_segment"] = rfm.apply(segment_customer, axis=1)
    seg_counts = rfm.groupby("customer_segment", as_index=False)["customer_unique_id"].count().sort_values(
        by="customer_unique_id", ascending=False
    )

    fig_rfm, ax_rfm = plt.subplots(figsize=(10, 4.5))
    sns.barplot(
        x="customer_unique_id",
        y="customer_segment",
        data=seg_counts,
        palette=["#1f77b4"] + ["#b0c4de"] * (len(seg_counts) - 1),
        ax=ax_rfm
    )
    ax_rfm.set_title("Distribusi Segmen Pelanggan (RFM Manual Grouping)", fontweight="bold")
    ax_rfm.set_xlabel("Jumlah Pelanggan Unik")
    ax_rfm.set_ylabel("Segmen Pelanggan")
    st.pyplot(fig_rfm)