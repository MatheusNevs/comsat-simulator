import streamlit as st
from models.ground_station import GroundStation

CIDADES_BASE = {
    "Brasília":        {"lat": -15.79, "lon": -47.88},
    "São Paulo":       {"lat": -23.55, "lon": -46.63},
    "Rio de Janeiro":  {"lat": -22.91, "lon": -43.17},
    "Manaus":          {"lat":  -3.11, "lon": -60.02},
    "Fortaleza":       {"lat":  -3.72, "lon": -38.54},
    "Porto Alegre":    {"lat": -30.03, "lon": -51.23},
    "Belém":           {"lat":  -1.46, "lon": -48.50},
}


def render_station_panel():
    st.sidebar.header("📡 Estações Terrenas")

    if 'stations' not in st.session_state:
        st.session_state['stations'] = []

    modo = st.sidebar.radio("Adicionar:", ["Cidade Base", "Customizada"], horizontal=True)

    if modo == "Cidade Base":
        escolha  = st.sidebar.selectbox("Selecione:", list(CIDADES_BASE.keys()), label_visibility="collapsed")
        ganho_rx = st.sidebar.number_input("Ganho RX (dBi)", value=40.0)
        if st.sidebar.button("➕ Adicionar ao Cenário", key="btn_add_stn_cidade", use_container_width=True):
            nomes_atuais = [s.name for s in st.session_state['stations']]
            if escolha not in nomes_atuais:
                c = CIDADES_BASE[escolha]
                st.session_state['stations'].append(
                    GroundStation(escolha, c["lat"], c["lon"], ganho_rx)
                )
                st.rerun()
            else:
                st.sidebar.warning(f"{escolha} já está no cenário.")
    else:
        with st.sidebar.form("nova_estacao_form"):
            nome     = st.text_input("Nome da Estação")
            lat      = st.number_input("Latitude (graus)", value=-15.79)
            lon      = st.number_input("Longitude (graus)", value=-47.88)
            ganho_rx = st.number_input("Ganho RX (dBi)", value=40.0)
            if st.form_submit_button("➕ Adicionar Customizada", use_container_width=True) and nome:  # form_submit_button não precisa de key
                st.session_state['stations'].append(
                    GroundStation(nome, lat, lon, ganho_rx)
                )
                st.rerun()

    # Lista de estações no cenário com botão de remoção
    stations = st.session_state['stations']
    if stations:
        st.sidebar.markdown("**No cenário:**")
        for i, s in enumerate(stations):
            col_name, col_btn = st.sidebar.columns([3, 1])
            col_name.markdown(f"🔸 **{s.name}**  \n`{s.latitude_deg:.2f}°, {s.longitude_deg:.2f}°`")
            if col_btn.button("✕", key=f"rm_stn_{i}", help=f"Remover {s.name}"):
                st.session_state['stations'].pop(i)
                st.rerun()
