import time
import random
import streamlit as st
import pandas as pd
import requests
import datetime

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="ZF-Core V16.4-OMNI | Advanced Tensor & History Engine",
    page_icon="📈",
    layout="wide"
)

st.title("📈 ZF-Core Omni-Engine + Tensor Visualizer & History Log")
st.markdown("Integrasi Modul Stabilitas Temporal, Jitter Filter, Tensor Line Chart, Peringatan Dini, serta Unduh Log Riwayat CSV.")

# Panel Kontrol Samping (Sidebar)
st.sidebar.header("Parameter Ekosistem & Analitik")
selected_pair = st.sidebar.selectbox("Pilih Aset Pasar", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
refresh_rate = st.sidebar.slider("Interval Refresh (detik)", 1, 5, 2)
total_capital = st.sidebar.number_input("Total Modal Simulasi ($)", min_value=100.0, max_value=100000.0, value=1000.0, step=100.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Pengaturan Risiko & Ambang Batas")
jitter_threshold = st.sidebar.number_input(
    "Ambang Batas Jitter Filter",
    min_value=0.0001,
    max_value=0.0050,
    value=0.0010,
    step=0.0001,
    format="%.4f"
)
stop_loss_pct = st.sidebar.slider("Ambang Batas Dynamic Stop-Loss (%)", 0.5, 5.0, 1.5, step=0.5)

# Inisialisasi State Session
if "data_log" not in st.session_state:
    st.session_state.data_log = []
if "last_price" not in st.session_state:
    st.session_state.last_price = 0.0

class ZFTensorAdvancedEngine:
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

    def evaluate_risk_protocols(self, current_price: float, zf_score: float, capital: float, sl_pct: float) -> dict:
        """Teknologi No. 51 & 52: Dynamic Stop-Loss & ZF-Score Capital Allocator"""
        risk_multiplier = max(0.1, 1.0 - zf_score)
        allocated_capital = round(capital * risk_multiplier, 2)
        stop_loss_price = round(current_price * (1.0 - (sl_pct / 100.0)), 4)
        
        # Peringatan Dini / Alert System (Kategori V)
        if zf_score >= 0.85:
            status_risiko = "⚠️ PERINGATAN KRITIS: Volatilitas Tinggi Terdeteksi!"
        elif zf_score >= 0.50:
            status_risiko = "⚡ WASPADA: Fluktuasi Menengah"
        else:
            status_risiko = "✅ NORMAL / STABIL"
            
        return {
            "allocated_capital": allocated_capital,
            "stop_loss_price": stop_loss_price,
            "risk_status": status_risiko
        }

engine = ZFTensorAdvancedEngine()

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

# Area Visualisasi Tensor (Grafik Tren / Line Chart)
st.subheader("📊 Visualisasi Tensor: Tren Harga Bersih & Indeks Stabilitas ZF-Score")
chart_placeholder = st.empty()

col_view1, col_view2 = st.columns([2, 1])

with col_view1:
    st.subheader(f"Arus Data Sesi Berjalan: {selected_pair}")
    table_placeholder = st.empty()

with col_view2:
    st.subheader("Sistem Peringatan Dini & Log")
    alert_placeholder = st.empty()
    download_placeholder = st.empty()

# Fungsi Pengambilan Data & Pipeline Tensor
def fetch_and_process_tensor(symbol, capital, sl_pct):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            raw_data = response.json()
            raw_price = float(raw_data.get("price", 0.0))
            
            timestamp_us = engine.get_precise_timestamp()
            human_time = datetime.datetime.now().strftime("%H:%M:%S")
            
            clean_price, is_noise = engine.filter_noise_jitter(
                raw_price, st.session_state.last_price, jitter_threshold
            )
            
            deviation = abs(raw_price - st.session_state.last_price) if st.session_state.last_price > 0 else 0.0
            st.session_state.last_price = clean_price
            
            zf_score = engine.calculate_zf_score(deviation)
            risk_data = engine.evaluate_risk_protocols(clean_price, zf_score, capital, sl_pct)
            
            packet = {
                "Waktu": human_time,
                "Timestamp_us": timestamp_us,
                "Harga_Bersih": clean_price,
                "ZF_Score": zf_score,
                "Alokasi_Modal": risk_data["allocated_capital"],
                "Stop_Loss": risk_data["stop_loss_price"],
                "Status": risk_data["risk_status"]
            }
            return packet
    except Exception as e:
        st.warning(f"Menunggu sinkronisasi jaringan: {e}")
    return None

# Tombol Kontrol Utama (Toggle)
run_engine = st.toggle("Aktifkan Tensor & Analitik Sesi (Omni-Mode)", value=False)

if run_engine:
    st.info("Engine Tensor aktif dan merekam arus data riwayat secara real-time...")
    
    packet = fetch_and_process_tensor(selected_pair, total_capital, stop_loss_pct)
    if packet:
        st.session_state.data_log.insert(0, packet)
        if len(st.session_state.data_log) > 50: # Batasi memori sesi hingga 50 data terakhir
            st.session_state.data_log.pop()
        
        # Perbarui Metrik Utama di Atas
        metric_time.metric("Time-Lock (us)", packet["Timestamp_us"])
        metric_zf.metric("ZF-Score", packet["ZF_Score"])
        metric_alloc.metric("Alokasi Modal ($)", packet["Alokasi_Modal"])
        metric_sl.metric("Dynamic Stop-Loss", packet["Stop_Loss"])
        
        # Konversi Log ke DataFrame untuk Visualisasi & Tabel
        df = pd.DataFrame(st.session_state.data_log)
        
        # Tampilkan Grafik Tren Harga Bersih (Tensor Visualization)
        if not df.empty:
            chart_placeholder.line_chart(df.set_index("Waktu")[["Harga_Bersih"]])
        
        # Perbarui Tabel Log Arus Data
        table_placeholder.dataframe(df, use_container_width=True)
        
        # Peringatan Dini
        if "KRITIS" in packet["Status"]:
            alert_placeholder.error(packet["Status"])
        elif "WASPADA" in packet["Status"]:
            alert_placeholder.warning(packet["Status"])
        else:
            alert_placeholder.success(packet["Status"])
            
        # Tombol Unduh Log Riwayat CSV
        csv_data = df.to_csv(index=False).encode('utf-8')
        download_placeholder.download_button(
            label="📥 Unduh Riwayat Sesi (CSV)",
            data=csv_data,
            file_name=f"ZF_Core_Log_{selected_pair}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    time.sleep(refresh_rate)
    st.rerun()
else:
    st.info("Nyalakan tombol sakelar di atas untuk memulai pemantauan grafik tensor dan perekaman log riwayat.")
