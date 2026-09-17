import time
import streamlit as st
import pandas as pd
import requests

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="ZF-Core V16.3-OMNI | Time-Lock Engine",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Microsecond Time-Lock Engine (ZF-Tech No. 2)")
st.markdown("Sistem sinkronisasi temporal presisi tinggi berbasis standar **Time-Lock 2326**.")

# Panel Kontrol Samping
st.sidebar.header("Pengaturan Sesi")
selected_pair = st.sidebar.selectbox("Pilih Aset Pasar", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
refresh_rate = st.sidebar.slider("Kecepatan Segar Data (detik)", 1, 5, 2)

# Inisialisasi State Session untuk menyimpan riwayat data
if "data_log" not in st.session_state:
    st.session_state.data_log = []

class MicrosecondTimeLockEngine:
    def __init__(self, time_lock_version: str = "Time-Lock 2326"):
        self.time_lock_version = time_lock_version

    def get_precise_timestamp(self) -> int:
        """Menghasilkan stempel waktu presisi tinggi dalam mikrosekon."""
        return (time.time_ns() // 1000)

    def lock_and_sync_packet(self, raw_data: dict) -> dict:
        arrival_micro_ts = self.get_precise_timestamp()
        return {
            "temporal_lock": self.time_lock_version,
            "synchronized_timestamp_us": int(arrival_micro_ts),
            "symbol": raw_data.get("symbol", selected_pair),
            "price": float(raw_data.get("price", 0.0)),
            "status": "LOCKED_SYNCHRONIZED"
        }

engine = MicrosecondTimeLockEngine()

# Layout Utama Dasbor
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Arus Data Real-Time: {selected_pair}")
    table_placeholder = st.empty()

with col2:
    st.subheader("Status Tensor Waktu")
    metric_placeholder = st.empty()

# Mengambil data menggunakan REST API Publik Binance (Alternatif stabil di Cloud)
def fetch_latest_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"Menunggu sinkronisasi jaringan: {e}")
    return None

# Tombol Kontrol Utama di HP
run_engine = st.toggle("Aktifkan Microsecond Time-Lock Stream", value=False)

if run_engine:
    st.info("Engine aktif dan menyinkronkan stempel waktu temporal...")
    
    # Loop aman untuk Streamlit Cloud
    while run_engine:
        raw_data = fetch_latest_price(selected_pair)
        if raw_data:
            synced = engine.lock_and_sync_packet(raw_data)
            
            # Masukkan ke riwayat log
            st.session_state.data_log.insert(0, synced)
            if len(st.session_state.data_log) > 15:
                st.session_state.data_log.pop()
            
            # Perbarui Tampilan Tabel & Metrik
            df = pd.DataFrame(st.session_state.data_log)
            table_placeholder.dataframe(df, use_container_width=True)
            
            metric_placeholder.metric(
                label="Timestamp Terkunci (us)", 
                value=synced["synchronized_timestamp_us"],
                delta=f"Harga: {synced['price']}"
            )
        
        time.sleep(refresh_rate)
        st.rerun()
else:
    st.warning("Silakan aktifkan tombol sakelar di atas untuk memulai aliran data terenkripsi.")
