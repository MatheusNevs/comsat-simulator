import streamlit as st
from models.ground_station import GroundStation

CIDADES_BASE = {
    "Brasília": {"lat": -15.79, "lon": -47.88},
    "São Paulo": {"lat": -23.55, "lon": -46.63},
    "Manaus": {"lat": -3.11, "lon": -60.02}
}

def render_station_panel():
    st.sidebar.header("🏠 Estações Terrenas")
    
    if 'stations' not in st.session_state:
        st.session_state['stations'] = []

    modo = st.sidebar.radio("Adicionar Estação:", ["Cidades Base", "Customizada"])
    
    if modo == "Cidades Base":
        escolha = st.sidebar.selectbox("Selecione a cidade:", list(CIDADES_BASE.keys()))
        ganho_rx = st.sidebar.number_input("Ganho RX da antena (dBi)", value=40.0)
        
        if st.sidebar.button("Adicionar Estação"):
            lat = CIDADES_BASE[escolha]["lat"]
            lon = CIDADES_BASE[escolha]["lon"]
            station = GroundStation(escolha, lat, lon, ganho_rx)
            st.session_state['stations'].append(station)
            st.sidebar.success(f"{escolha} adicionada!")
            
    # Exibe as estações já adicionadas
    if st.session_state['stations']:
        st.sidebar.markdown("### Estações no Cenário")
        for st_obj in st.session_state['stations']:
            st.sidebar.text(f"🔸 {st_obj.name}")
