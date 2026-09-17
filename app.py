import asyncio
import json
import time
import streamlit as st
import pandas as pd
import websockets

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
selected_pair = st.sidebar.selectbox("Pilih Aset Pasar", ["btcusdt", "ethusdt", "solusdt"])
max_rows = st.sidebar.slider("Batas Riwayat Tampilan", 10, 100, 20)

# Inisialisasi State Session untuk menyimpan data stream secara real-time
if "data_log" not in st.session_state:
    st.session_state.data_log = []

class MicrosecondTimeLockEngine:
    def __init__(self, time_lock_version: str = "Time-Lock 2326"):
        self.time_lock_version = time_lock_version

    def get_precise_timestamp(self) -> int:
        """Menghasilkan stempel waktu presisi tinggi dalam mikrosekon."""
        return (time.time_ns() // 1000)

    async def lock_and_sync_packet(self, raw_data: dict) -> dict:
        arrival_micro_ts = self.get_precise_timestamp()
        return {
            "temporal_lock": self.time_lock_version,
            "synchronized_timestamp_us": int(arrival_micro_ts),
            "price": float(raw_data.get("p", 0.0)),
            "quantity": float(raw_data.get("q", 0.0)),
            "status": "LOCKED_SYNCHRONIZED"
        }

# Layout Utama Dasbor
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Arus Data Live: {selected_pair.upper()}")
    table_placeholder = st.empty()

with col2:
    st.subheader("Status Tensor Waktu")
    metric_placeholder = st.empty()

# Fungsi Utama Penghubung WebSocket (Asinkron)
async def fetch_live_stream(symbol):
    uri = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
    engine = MicrosecondTimeLockEngine()
    
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                raw_packet = json.loads(message)
                synced = await engine.lock_and_sync_packet(raw_packet)
                
                # Masukkan data ke riwayat state
                st.session_state.data_log.insert(0, synced)
                if len(st.session_state.data_log) > max_rows:
                    st.session_state.data_log.pop()
                
                # Perbarui tampilan UI Streamlit secara dinamis
                df = pd.DataFrame(st.session_state.data_log)
                table_placeholder.dataframe(df, use_container_width=True)
                
                metric_placeholder.metric(
                    label="Waktu Sinkron Terakhir (us)", 
                    value=synced["synchronized_timestamp_us"],
                    delta=f"Harga: {synced['price']}"
                )
                
                # Berikan jeda mikrotik agar tidak membebani browser HP
                await asyncio.sleep(0.1)
    except Exception as e:
        st.error(f"Koneksi terputus atau galeri jaringan: {e}")

# Tombol Eksekusi di HP
if st.button("Jalankan Engine Stream"):
    with st.spinner("Menghubungkan ke jaringan WebSocket bursa..."):
        try:
            asyncio.run(fetch_live_stream(selected_pair))
        except RuntimeError:
            # Mengatasi loop asyncio yang sudah berjalan di lingkungan cloud
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(fetch_live_stream(selected_pair))
