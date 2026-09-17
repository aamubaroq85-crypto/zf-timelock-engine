import time
import random
import streamlit as st
import pandas as pd
import requests

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="ZF-Core V16.3-OMNI | Integrated Engine",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ ZF-Core Omni-Engine (Tech No. 2, 3, 16, & 33)")
st.markdown("Integrasi Sinkronisasi Temporal, Filter Jitter, Depth Mapper, dan Kalkulasi ZF-Score.")

# Panel Kontrol Samping (Sidebar)
st.sidebar.header("Parameter Ekosistem")
selected_pair = st.sidebar.selectbox("Pilih Aset Pasar", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
refresh_rate = st.sidebar.slider("Interval Refresh (detik)", 1, 5, 2)

st.sidebar.markdown("---")
st.sidebar.subheader("Pengaturan Jitter")

# Menggunakan number_input agar mudah dikontrol lewat HP tanpa macet
jitter_threshold = st.sidebar.number_input(
    "Ambang Batas Jitter Filter",
    min_value=0.0001,
    max_value=0.0050,
    value=0.0010,
    step=0.0001,
    format="%.4f",
    key="jitter_input"
)

# Inisialisasi State Session
if "data_log" not in st.session_state:
    st.session_state.data_log = []
if "last_price" not in st.session_state:
    st.session_state.last_price = 0.0

class ZFIntegratedEngine:
    def __init__(self, time_lock_version: str = "Time-Lock 2326"):
        self.time_lock_version = time_lock_version

    def get_precise_timestamp(self) -> int:
        """Teknologi No. 2: Microsecond Time-Lock Engine"""
        return (time.time_ns() // 1000)

    def filter_noise_jitter(self, current_price: float, previous_price: float, threshold: float) -> tuple:
        """Teknologi No. 3: Noise Filter Jitter"""
        if previous_price == 0.0:
            return current_price, False
        
        diff = abs(current_price - previous_price)
        is_noise = diff < threshold
        filtered_price = previous_price if is_noise else current_price
        return filtered_price, is_noise

    def calculate_zf_score(self, price_deviation: float) -> float:
        """Teknologi No. 33: ZF-Score Engine (Skala 0 - 1)"""
        score = 1.0 / (1.0 + (1.0 / (max(price_deviation, 0.00001))))
        return round(min(max(score, 0.0), 1.0), 4)

    def map_depth_and_structure(self, price: float) -> dict:
        """Teknologi No. 16: ZF-Depth Mapper (Simulasi Kedalaman Order Book)"""
        bid_depth = round(random.uniform(10.5, 50.2), 2)
        ask_depth = round(random.uniform(10.5, 50.2), 2)
        imbalance_ratio = round(bid_depth / (bid_depth + ask_depth), 2)
        return {
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "imbalance_ratio": imbalance_ratio
        }

engine = ZFIntegratedEngine()

# Layout Utama Dasbor (3 Kolom Metrik di Atas)
col_top1, col_top2, col_top3 = st.columns(3)

with col_top1:
    metric_time = st.empty()
with col_top2:
    metric_zf = st.empty()
with col_top3:
    metric_noise = st.empty()

st.markdown("---")
col_view1, col_view2 = st.columns([2, 1])

with col_view1:
    st.subheader(f"Arus Data Terfilter: {selected_pair}")
    table_placeholder = st.empty()

with col_view2:
    st.subheader("Matriks Kedalaman (Depth)")
    depth_placeholder = st.empty()

# Fungsi Pengambilan Data & Eksekusi Pipeline
def fetch_and_process(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            raw_data = response.json()
            raw_price = float(raw_data.get("price", 0.0))
            
            # 1. Teknologi No. 2: Time-Lock Timestamp
            timestamp_us = engine.get_precise_timestamp()
            
            # 2. Teknologi No. 3: Filter Jitter Noise
            clean_price, is_noise = engine.filter_noise_jitter(
                raw_price, st.session_state.last_price, jitter_threshold
            )
            
            # Hitung deviasi untuk ZF-Score
            deviation = abs(raw_price - st.session_state.last_price) if st.session_state.last_price > 0 else 0.0
            st.session_state.last_price = clean_price
            
            # 3. Teknologi No. 33: ZF-Score Stabilitas
            zf_score = engine.calculate_zf_score(deviation)
            
            # 4. Teknologi No. 16: Depth Mapper
            depth_data = engine.map_depth_and_structure(clean_price)
            
            packet = {
                "timestamp_us": timestamp_us,
                "raw_price": raw_price,
                "clean_price": clean_price,
                "filtered_noise": "YES" if is_noise else "NO",
                "zf_score": zf_score,
                "bid_vol": depth_data["bid_depth"],
                "ask_vol": depth_data["ask_depth"],
                "ratio": depth_data["imbalance_ratio"]
            }
            return packet
    except Exception as e:
        st.warning(f"Menunggu sinkronisasi jaringan: {e}")
    return None

# Tombol Kontrol Utama (Toggle)
run_engine = st.toggle("Aktifkan Ekosistem ZF-Core (Omni Mode)", value=False)

if run_engine:
    st.info("Engine aktif dan menyinkronkan stempel waktu temporal...")
    
    # Ambil data 1 siklus per eksekusi (Stabil, tanpa infinite while loop)
    packet = fetch_and_process(selected_pair)
    if packet:
        # Masukkan ke log riwayat
        st.session_state.data_log.insert(0, packet)
        if len(st.session_state.data_log) > 15:
            st.session_state.data_log.pop()
        
        # Perbarui Metrik Utama di Atas
        metric_time.metric("Time-Lock (us)", packet["timestamp_us"])
        metric_zf.metric("ZF-Score Stabilitas", packet["zf_score"], delta="Aman (<0.99)" if packet["zf_score"] < 0.99 else "Kritis!")
        metric_noise.metric("Status Noise Jitter", packet["filtered_noise"])
        
        # Perbarui Tabel Riwayat & Depth Mapper
        df = pd.DataFrame(st.session_state.data_log)
        table_placeholder.dataframe(df, use_container_width=True)
        
        depth_placeholder.json({
            "Bid Volume": packet["bid_vol"],
            "Ask Volume": packet["ask_vol"],
            "Bid/Ask Imbalance Ratio": packet["ratio"]
        })
    
    # Jeda sesuai interval, lalu refresh halaman secara aman
    time.sleep(refresh_rate)
    st.rerun()
else:
    st.info("Nyalakan tombol sakelar di atas untuk mengaktifkan pemrosesan serentak 4 modul teknologi ZF-Core.")
