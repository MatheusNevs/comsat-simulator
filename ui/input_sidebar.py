import streamlit as st

def render_sidebar():
    """
    Renderiza os menus de entrada de dados na barra lateral e retorna um dicionário com os parâmetros.
    """
    st.sidebar.header("Parâmetros do Enlace")
    
    params = {}

    # --- Aba 1: Transmissor ---
    with st.sidebar.expander("📡 Transmissor (TX)", expanded=True):
        params['frequencia_ghz'] = st.number_input("Frequência (GHz)", min_value=1.0, value=12.0, step=0.5)
        params['potencia_tx_w'] = st.number_input("Potência Transmitida (W)", min_value=0.1, value=100.0, step=10.0)
        params['ganho_tx_dbi'] = st.number_input("Ganho da Antena TX (dBi)", value=30.0, step=1.0)
        params['perdas_linha_tx_db'] = st.number_input("Perdas na Linha TX (dB)", value=1.0, step=0.1)

    # --- Aba 2: Canal Espacial ---
    with st.sidebar.expander("🌌 Canal Espacial", expanded=False):
        params['distancia_km'] = st.number_input("Distância (km)", min_value=100.0, value=38000.0, step=1000.0)
        params['perda_atmosferica_db'] = st.number_input("Atenuação Atmosférica (dB)", value=0.5, step=0.1)

    # --- Aba 3: Receptor ---
    with st.sidebar.expander("📡 Receptor (RX)", expanded=False):
        params['ganho_rx_dbi'] = st.number_input("Ganho da Antena RX (dBi)", value=40.0, step=1.0)
        params['perdas_linha_rx_db'] = st.number_input("Perdas na Linha RX (dB)", value=0.5, step=0.1)
        
        st.markdown("*Mais funcionalidades de ruído serão adicionadas aqui futuramente.*")

    return params
