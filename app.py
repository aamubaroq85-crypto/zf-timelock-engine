import time
import random
import streamlit as st
import pandas as pd
import requests

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="ZF-Core V16.3-OMNI | Risk & Execution Engine",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ ZF-Core Omni-Engine + Risk Protocol (Tech No. 2, 3, 16, 33, 51, & 52)")
st.markdown("Integrasi Sinkronisasi Temporal, Filter Jitter, Depth Mapper, ZF-Score, hingga Dynamic Stop-Loss & Capital Allocator.")

# Panel Kontrol Samping (Sidebar)
st.sidebar.header("Parameter Ekosistem & Risiko")
selected_pair = st.sidebar.selectbox("Pilih Aset Pasar", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
refresh_rate = st.sidebar.slider("Interval Refresh (detik)", 1, 5, 2)
total_capital = st.sidebar.number_input("Total Modal Simulasi ($)", min_value=100.0, max_value=100000.0, value=1000.0, step=100.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Pengaturan Risiko")
jitter_threshold = st.sidebar.number_input(
    "Ambang Batas Jitter Filter",
    min_value=0.0001,
    max_value=0.0050,
    value=0.0010,
    step=0.0001,
    format="%.4f",
    key="jitter_input"
)
stop_loss_pct = st.sidebar.slider("Ambang Batas Dynamic Stop-Loss (%)", 0.5, 5.0, 1.5, step=0.5)

# Inisialisasi State Session
if "data_log" not in st.session_state:
    st.session_state.data_log = []
if "last_price" not in st.session_state:
    st.session_state.last_price = 0.0

class ZFRiskIntegratedEngine:
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
        """Teknologi No. 16: ZF-Depth Mapper"""
        bid_depth = round(random.uniform(10.5, 50.2), 2)
        ask_depth = round(random.uniform(10.5, 50.2), 2)
        imbalance_ratio = round(bid_depth / (bid_depth + ask_depth), 2)
        return {
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "imbalance_ratio": imbalance_ratio
        }

    def evaluate_risk_protocols(self, current_price: float, zf_score: float, capital: float, sl_pct: float) -> dict:
        """Teknologi No. 51 & 52: Dynamic Stop-Loss & ZF-Score Capital Allocator"""
        # Alokasi modal proporsional: Semakin stabil ZF-Score (mendekati 0), semakin besar porsi modal yang diizinkan
        risk_multiplier = max(0.1, 1.0 - zf_score)
        allocated_capital = round(capital * risk_multiplier, 2)
        
        # Hitung titik Dynamic Stop-Loss berdasarkan persentase drift
        stop_loss_price = round(current_price * (1.0 - (sl_pct / 100.0)), 4)
        
        # Status proteksi kritis jika ZF-Score terlalu tinggi
        status_risiko = "NORMAL / AMAN" if zf_score < 0.85 else "PERINGATAN KRITIS (High Drift)"
        
        return {
            "allocated_capital": allocated_capital,
            "stop_loss_price": stop_loss_price,
            "risk_status": status_risiko
        }

engine = ZFRiskIntegratedEngine()

# Layout Utama Dasbor (Metrik Baris Atas)
col_top1, col_top2, col_top3, col_top4 = st.columns(4)

with col_top1:
    metric_time = st.empty()
with col_top2:
    metric_zf = st.empty()
with col_top3:
    metric_alloc = st.empty()
with col_top4:
    metric_sl = st.empty()

st.markdown("---")
col_view1, col_view2 = st.columns([2, 1])

with col_view1:
    st.subheader(f"Arus Data & Risiko Terstruktur: {selected_pair}")
    table_placeholder = st.empty()

with col_view2:
    st.subheader("Matriks Proteksi & Kedalaman")
    depth_placeholder = st.empty()

# Fungsi Pengambilan Data & Eksekusi Pipeline Risiko
def fetch_and_process_risk(symbol, capital, sl_pct):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            raw_data = response.json()
            raw_price = float(raw_data.get("price", 0.0))
            
            # 1. Time-Lock Timestamp (No. 2)
            timestamp_us = engine.get_precise_timestamp()
            
            # 2. Jitter Filter (No. 3)
            clean_price, is_noise = engine.filter_noise_jitter(
                raw_price, st.session_state.last_price, jitter_threshold
            )
            
            deviation = abs(raw_price - st.session_state.last_price) if st.session_state.last_price > 0 else 0.0
            st.session_state.last_price = clean_price
            
            # 3. ZF-Score Stabilitas (No. 33)
            zf_score = engine.calculate_zf_score(deviation)
            
            # 4. Depth Mapper (No. 16)
            depth_data = engine.map_depth_and_structure(clean_price)
            
            # 5. Risk Protocols: Capital Allocator & Dynamic Stop-Loss (No. 51 & 52)
            risk_data = engine.evaluate_risk_protocols(clean_price, zf_score, capital, sl_pct)
            
            packet = {
                "timestamp_us": timestamp_us,
                "clean_price": clean_price,
                "zf_score": zf_score,
                "alokasi_modal": risk_data["allocated_capital"],
                "stop_loss": risk_data["stop_loss_price"],
                "status_risiko": risk_data["risk_status"]
            }
            return packet
    except Exception as e:
        st.warning(f"Menunggu sinkronisasi jaringan: {e}")
    return None

# Tombol Kontrol Utama (Toggle)
run_engine = st.toggle("Aktifkan Ekosistem ZF-Core (Risk-Managed Mode)", value=False)

if run_engine:
    st.info("Engine aktif dan memproses protokol manajemen risiko secara real-time...")
    
    packet = fetch_and_process_risk(selected_pair, total_capital, stop_loss_pct)
    if packet:
        st.session_state.data_log.insert(0, packet)
        if len(st.session_state.data_log) > 15:
            st.session_state.data_log.pop()
        
        # Perbarui Metrik Utama di Atas
        metric_time.metric("Time-Lock (us)", packet["timestamp_us"])
        metric_zf.metric("ZF-Score", packet["zf_score"])
        metric_alloc.metric("Alokasi Modal ($)", packet["alokasi_modal"])
        metric_sl.metric("Dynamic Stop-Loss", packet["stop_loss"])
        
        # Perbarui Tabel & Panel Risiko
        df = pd.DataFrame(st.session_state.data_log)
        table_placeholder.dataframe(df, use_container_width=True)
        
        depth_placeholder.json({
            "Status Sistemik": packet["status_risiko"],
            "Harga Acuan": packet["clean_price"],
            "Batas Stop-Loss": packet["stop_loss"]
        })
    
    time.sleep(refresh_rate)
    st.rerun()
else:
    st.info("Nyalakan tombol sakelar di atas untuk mengaktifkan seluruh modul teknologi ZF-Core beserta protokol manajemen risiko.")
