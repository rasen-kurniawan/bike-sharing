import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

sns.set_theme(style="whitegrid")

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "merged_bike.csv")
def load_data():
    df = pd.read_csv("csv_path")
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

def create_daily_trend_df(df):
    # Hanya pakai source=day untuk trend harian
    day_data = df[df["source"] == "day"].copy()
    trend = day_data.resample(rule="D", on="dteday").agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    return trend

def create_corr_df(df):
    return df[["temp", "atemp", "hum", "windspeed", "cnt"]]

def create_season_df(df):
    season_df = df.groupby("season")["cnt"].mean().reset_index()
    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    season_df["season_label"] = season_df["season"].map(season_map)
    return season_df

def create_usertype_df(df):
    return df.groupby("workingday")[["casual", "registered"]].mean().reset_index()

def suhu_category(temp):
    if temp < 0.3:
        return "Cold"
    elif temp < 0.6:
        return "Pleasant"
    else:
        return "Hot"

def hour_category(hr):
    if hr == -1:
        return "N/A (Day Data)"
    elif 0 <= hr <= 6:
        return "Dini Hari"
    elif 7 <= hr <= 15:
        return "Pagi-Siang"
    elif 16 <= hr <= 19:
        return "Sore"
    else:
        return "Malam"

def create_tempbin_df(df):
    temp_df = df.copy()
    temp_df["temp_bin"] = temp_df["temp"].apply(suhu_category)
    return temp_df.groupby("temp_bin")["cnt"].mean().reindex(["Cold", "Pleasant", "Hot"]).reset_index()

def create_timebin_df(df):
    hour_data = df[df["source"] == "hour"].copy()
    hour_data["time_bin"] = hour_data["hr"].apply(hour_category)
    order = ["Dini Hari", "Pagi-Siang", "Sore", "Malam"]
    return hour_data.groupby("time_bin")["cnt"].mean().reindex(order).reset_index()




# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
all_df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.title("🚲 Bike Sharing Filter")

    # Filter Source
    source_options = ["All", "day", "hour"]
    selected_source = st.selectbox("Sumber Data", source_options)

    # Filter Season
    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    all_seasons = sorted(all_df["season"].unique())
    selected_seasons = st.multiselect(
        "Musim",
        options=all_seasons,
        default=all_seasons,
        format_func=lambda x: season_map[x]
    )

    # Filter Weathersit
    weather_map = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain"}
    all_weather = sorted(all_df["weathersit"].unique())
    selected_weather = st.multiselect(
        "Kondisi Cuaca",
        options=all_weather,
        default=all_weather,
        format_func=lambda x: weather_map.get(x, str(x))
    )

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
filtered_df = all_df.copy()

if selected_source != "All":
    filtered_df = filtered_df[filtered_df["source"] == selected_source]

filtered_df = filtered_df[
    (filtered_df["season"].isin(selected_seasons)) &
    (filtered_df["weathersit"].isin(selected_weather))
]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Analisis penyewaan sepeda berdasarkan data **Capital Bikeshare** (2011–2012).")
st.divider()

# ─────────────────────────────────────────────
# SECTION 1 — METRIC OVERVIEW
# ─────────────────────────────────────────────
st.subheader("📊 Overview")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Penyewaan", f"{filtered_df['cnt'].sum():,}")
with col2:
    st.metric("Rata-rata Harian", f"{filtered_df[filtered_df['source']=='day']['cnt'].mean():,.0f}")
with col3:
    st.metric("Total Casual", f"{filtered_df['casual'].sum():,}")
with col4:
    st.metric("Total Registered", f"{filtered_df['registered'].sum():,}")

st.divider()

# ─────────────────────────────────────────────
# SECTION 2 — DAILY RENTALS TREND
# ─────────────────────────────────────────────
st.subheader("📈 Daily Rentals Trend")

trend_df = create_daily_trend_df(filtered_df)

if trend_df.empty:
    st.warning("Tidak ada data harian untuk filter ini.")
else:
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(trend_df["dteday"], trend_df["cnt"], color="#2E86C1", linewidth=2, marker="o", markersize=3, label="Total")
    ax.fill_between(trend_df["dteday"], trend_df["cnt"], alpha=0.15, color="#2E86C1")
    ax.set_xlabel("Tanggal", fontsize=12)
    ax.set_ylabel("Jumlah Penyewaan", fontsize=12)
    ax.legend()
    ax.tick_params(axis="x", labelsize=10)
    st.pyplot(fig)

st.divider()

# ─────────────────────────────────────────────
# SECTION 3 — KORELASI CUACA
# ─────────────────────────────────────────────
st.subheader("🌤️ Korelasi Faktor Cuaca vs Total Penyewaan")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Day Data**")
    day_corr = create_corr_df(filtered_df[filtered_df["source"] == "day"])
    if len(day_corr) > 1:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(day_corr.corr(), annot=True, cmap="RdYlGn", fmt=".2f", ax=ax)
        ax.set_title("Korelasi - Day", fontsize=13)
        st.pyplot(fig)
    else:
        st.info("Data day tidak tersedia.")

with col2:
    st.markdown("**Hour Data**")
    hour_corr = create_corr_df(filtered_df[filtered_df["source"] == "hour"])
    if len(hour_corr) > 1:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(hour_corr.corr(), annot=True, cmap="RdYlGn", fmt=".2f", ax=ax)
        ax.set_title("Korelasi - Hour", fontsize=13)
        st.pyplot(fig)
    else:
        st.info("Data hour tidak tersedia.")

st.divider()

# ─────────────────────────────────────────────
# SECTION 4 — DISTRIBUSI PER MUSIM
# ─────────────────────────────────────────────
st.subheader("🍂 Distribusi Penyewaan per Musim")

palette = ["#AED6F1", "#F9E79F", "#A9DFBF", "#F5CBA7"]
season_order = [1, 2, 3, 4]
season_labels = ["Spring", "Summer", "Fall", "Winter"]

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Day Data** (total penyewaan per hari)")
    day_season = filtered_df[filtered_df["source"] == "day"]
    if not day_season.empty:
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.boxplot(data=day_season, x="season", y="cnt",
                    order=season_order, palette=palette, ax=ax)
        ax.set_xticklabels(season_labels)
        ax.set_xlabel("Musim", fontsize=11)
        ax.set_ylabel("Jumlah Penyewaan", fontsize=11)
        ax.set_title("Distribusi per Musim - Day", fontsize=13, fontweight="bold")
        st.pyplot(fig)
    else:
        st.info("Data day tidak tersedia.")

with col2:
    st.markdown("**Hour Data** (total penyewaan per jam)")
    hour_season = filtered_df[filtered_df["source"] == "hour"]
    if not hour_season.empty:
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.boxplot(data=hour_season, x="season", y="cnt",
                    order=season_order, palette=palette, ax=ax)
        ax.set_xticklabels(season_labels)
        ax.set_xlabel("Musim", fontsize=11)
        ax.set_ylabel("Jumlah Penyewaan", fontsize=11)
        ax.set_title("Distribusi per Musim - Hour", fontsize=13, fontweight="bold")
        st.pyplot(fig)
    else:
        st.info("Data hour tidak tersedia.")

st.divider()

# ─────────────────────────────────────────────
# SECTION 5 — CASUAL VS REGISTERED
# ─────────────────────────────────────────────
st.subheader("👥 Casual vs Registered: Hari Kerja vs Libur")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Day Data**")
    day_user = create_usertype_df(filtered_df[filtered_df["source"] == "day"])
    if not day_user.empty:
        fig, ax = plt.subplots(figsize=(6, 5))
        day_user.set_index("workingday").plot(
            kind="bar", stacked=True, color=["#E67E22", "#2E86C1"], ax=ax
        )
        ax.set_xticklabels(["Libur/Weekend", "Hari Kerja"], rotation=0)
        ax.set_ylabel("Rata-rata Penyewaan")
        ax.set_title("Tipe Pengguna - Day", fontsize=13)
        ax.legend(title="Tipe")
        st.pyplot(fig)
    else:
        st.info("Data day tidak tersedia.")

with col2:
    st.markdown("**Hour Data**")
    hour_user = create_usertype_df(filtered_df[filtered_df["source"] == "hour"])
    if not hour_user.empty:
        fig, ax = plt.subplots(figsize=(6, 5))
        hour_user.set_index("workingday").plot(
            kind="bar", stacked=True, color=["#E67E22", "#2E86C1"], ax=ax
        )
        ax.set_xticklabels(["Libur/Weekend", "Hari Kerja"], rotation=0)
        ax.set_ylabel("Rata-rata Penyewaan")
        ax.set_title("Tipe Pengguna - Hour", fontsize=13)
        ax.legend(title="Tipe")
        st.pyplot(fig)
    else:
        st.info("Data hour tidak tersedia.")

st.divider()

# ─────────────────────────────────────────────
# SECTION 6A — SEGMENTASI TEMPERATUR
# ─────────────────────────────────────────────
st.subheader("🌡️ Pertanyaan 1: Profil Penyewaan Berdasarkan Segmentasi Temperatur")
st.markdown("_Bagaimana profil dan karakteristik penyewaan sepeda bila dilakukan segmentasi dataset berdasarkan temperatur udara?_")

category_order = ["Cold", "Pleasant", "Hot"]

# Siapkan data day saja untuk pertanyaan 1
day_temp_df = filtered_df[filtered_df["source"] == "day"].copy()
day_temp_df["temp_bin"] = day_temp_df["temp"].apply(suhu_category)
day_temp_df["temp_bin"] = pd.Categorical(day_temp_df["temp_bin"], categories=category_order, ordered=True)

if day_temp_df.empty:
    st.warning("Tidak ada data day untuk filter ini.")
else:
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 12))

    # Grafik 1: Casual vs Registered per kategori suhu
    df_melted = day_temp_df.melt(
        id_vars="temp_bin",
        value_vars=["casual", "registered"],
        var_name="user_type",
        value_name="avg_rentals"
    )
    sns.barplot(
        data=df_melted,
        x="temp_bin", y="avg_rentals",
        hue="user_type",
        palette="viridis",
        errorbar=None,
        ax=axes[0]
    )
    axes[0].set_title("Rata-rata Penyewaan: Casual vs Registered per Kategori Suhu", fontsize=15, fontweight="bold")
    axes[0].set_xlabel("Kategori Suhu", fontsize=12)
    axes[0].set_ylabel("Rata-rata Jumlah Penyewaan", fontsize=12)
    axes[0].legend(title="Tipe Pengguna", fontsize=11)
    for p in axes[0].patches:
        axes[0].annotate(f'{p.get_height():.0f}',
                         (p.get_x() + p.get_width() / 2., p.get_height()),
                         ha='center', va='bottom', fontsize=10)

    # Grafik 2: Boxplot distribusi total penyewaan
    sns.boxplot(
        data=day_temp_df,
        x="temp_bin", y="cnt",
        palette="Spectral",
        ax=axes[1]
    )
    axes[1].set_title("Distribusi Total Penyewaan (cnt) per Kategori Suhu", fontsize=15, fontweight="bold")
    axes[1].set_xlabel("Kategori Suhu", fontsize=12)
    axes[1].set_ylabel("Total Penyewaan", fontsize=12)

    plt.tight_layout()
    st.pyplot(fig)

st.divider()

# ─────────────────────────────────────────────
# SECTION 6B — SEGMENTASI WAKTU
# ─────────────────────────────────────────────
st.subheader("⏰ Pertanyaan 2: Rentang Waktu Ideal & Distribusi Pengguna")
st.markdown("_Kapan rentang waktu yang paling ideal bagi penyewa sepeda, serta bagaimana distribusi penggunanya pada jam sibuk vs jam istirahat?_")

time_order = ["Dini Hari", "Pagi-Siang", "Sore", "Malam"]

# Siapkan data hour saja untuk pertanyaan 2
hour_time_df = filtered_df[filtered_df["source"] == "hour"].copy()
hour_time_df["time_bin"] = hour_time_df["hr"].apply(hour_category)
hour_time_df = hour_time_df[hour_time_df["time_bin"] != "N/A (Day Data)"]
hour_time_df["time_bin"] = pd.Categorical(hour_time_df["time_bin"], categories=time_order, ordered=True)

if hour_time_df.empty:
    st.warning("Tidak ada data hour untuk filter ini.")
else:
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(14, 12))

    # Grafik 1: Casual vs Registered per waktu
    df_hour_melted = hour_time_df.melt(
        id_vars="time_bin",
        value_vars=["casual", "registered"],
        var_name="user_type",
        value_name="avg_rentals"
    )
    sns.barplot(
        data=df_hour_melted,
        x="time_bin", y="avg_rentals",
        hue="user_type",
        palette="magma",
        errorbar=None,
        ax=axes[0]
    )
    axes[0].set_title("Rata-rata Penyewaan per Kategori Waktu (Casual vs Registered)", fontsize=14, fontweight="bold")
    axes[0].set_xlabel("Kategori Waktu", fontsize=12)
    axes[0].set_ylabel("Rata-rata Jumlah Penyewaan", fontsize=12)
    axes[0].legend(title="Tipe Pengguna", fontsize=11)
    for p in axes[0].patches:
        axes[0].annotate(f'{p.get_height():.0f}',
                         (p.get_x() + p.get_width() / 2., p.get_height()),
                         ha='center', va='bottom', fontsize=10)

    # Grafik 2: Total cnt + tren suhu & kelembapan (dual axis)
    avg_time = hour_time_df.groupby("time_bin", observed=True)[["cnt", "temp", "hum"]].mean().reset_index()

    color_cnt = "#2E86C1"
    ax_left = axes[1]
    ax_right = ax_left.twinx()

    ax_left.plot(avg_time["time_bin"], avg_time["cnt"],
                 marker="o", color=color_cnt, linewidth=3, label="Total Rental (cnt)")
    ax_left.fill_between(range(len(avg_time)), avg_time["cnt"], alpha=0.1, color=color_cnt)
    ax_left.set_ylabel("Rata-rata Total Penyewaan (cnt)", fontsize=12, color=color_cnt)
    ax_left.tick_params(axis="y", labelcolor=color_cnt)

    ax_right.plot(avg_time["time_bin"], avg_time["temp"],
                  marker="s", color="#E74C3C", linewidth=2, linestyle="--", label="Suhu (Avg Temp)")
    ax_right.plot(avg_time["time_bin"], avg_time["hum"],
                  marker="d", color="#2980B9", linewidth=2, linestyle="--", label="Kelembapan (Avg Hum)")
    ax_right.set_ylabel("Skala Temp / Hum (Normalized)", fontsize=12)

    axes[1].set_title("Hubungan Tren Waktu dengan Faktor Lingkungan (Temp & Hum)", fontsize=14, fontweight="bold")
    axes[1].set_xlabel("Kategori Waktu", fontsize=12)

    # Gabung legend kedua axis
    lines_left, labels_left = ax_left.get_legend_handles_labels()
    lines_right, labels_right = ax_right.get_legend_handles_labels()
    ax_left.legend(lines_left + lines_right, labels_left + labels_right, loc="upper right", fontsize=10)

    plt.tight_layout()
    st.pyplot(fig)

st.divider()
st.caption("Copyright © Bike Sharing Dashboard 2024")
