"""
Painel Lateral de Gerenciamento de Estações Terrenas (ui/sidebar/station_panel.py)

Interface Streamlit para cadastro de estações terrenas a partir de cidades pré-definidas no Brasil
ou customizadas via entrada direta de latitude/longitude e parâmetros de antena/ruído.
"""

import streamlit as st
from models.ground_station import GroundStation

# Catálogo de cidades pré-configuradas no Brasil com coordenadas geográficas aproximadas
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
    """
    Renderiza os formulários da barra lateral para adição e remoção de estações terrenas no cenário.
    """
    st.sidebar.header("📡 Estações Terrenas")

    # Inicialização da lista de estações na sessão Streamlit
    if 'stations' not in st.session_state:
        st.session_state['stations'] = []

    modo = st.sidebar.radio("Adicionar:", ["Cidade Base", "Customizada"], horizontal=True)

    if modo == "Cidade Base":
        escolha  = st.sidebar.selectbox("Selecione:", list(CIDADES_BASE.keys()), label_visibility="collapsed")
        
        # Formulário expansível de parâmetros de antena e ruído da estação
        with st.sidebar.expander("Configurações da Estação"):
            gain_mode = st.radio("Ganho de Antena por:", ["Valor Direto", "Diâmetro e Eficiência"], key="cb_gain_mode")
            ganho_rx = st.number_input("Ganho RX (dBi)", value=40.0, step=0.5, key="cb_gain")
            diameter = st.number_input("Diâmetro (m)", value=1.8, step=0.1, key="cb_diameter")
            efficiency = st.number_input("Eficiência (%)", value=60.0, step=5.0, key="cb_eff")
            
            st.markdown("**Transmissor (Uplink)**")
            ptx = st.number_input("Potência TX (W)", value=120.0, step=5.0, key="cb_ptx")
            gtx = st.number_input("Ganho TX (dBi)", value=42.0, step=0.5, key="cb_gtx")
            tx_loss = st.number_input("Perda Guia de Onda TX (dB)", value=0.5, step=0.1, key="cb_tx_loss")
            
            st.markdown("**Ruído do Terminal**")
            t_ant = st.number_input("Temp. Antena (K)", value=50.0, step=5.0, key="cb_tant")
            t_lna = st.number_input("Temp. LNA (K)", value=80.0, step=5.0, key="cb_tlna")
            g_lna = st.number_input("Ganho LNA (dB)", value=50.0, step=1.0, key="cb_glna")
            t_down = st.number_input("Temp. Downconverter (K)", value=290.0, step=10.0, key="cb_tdown")
            nf_rec = st.number_input("Receiver Noise Figure (dB)", value=8.0, step=0.5, key="cb_nf")

        if st.sidebar.button("➕ Adicionar ao Cenário", key="btn_add_stn_cidade", use_container_width=True):
            nomes_atuais = [s.name for s in st.session_state['stations']]
            if escolha not in nomes_atuais:
                c = CIDADES_BASE[escolha]
                st.session_state['stations'].append(
                    GroundStation(
                        name=escolha,
                        latitude_deg=c["lat"],
                        longitude_deg=c["lon"],
                        rx_gain_dbi=ganho_rx,
                        gain_mode=gain_mode,
                        antenna_diameter_m=diameter,
                        antenna_efficiency_pct=efficiency,
                        temp_antenna_k=t_ant,
                        temp_lna_k=t_lna,
                        gain_lna_db=g_lna,
                        temp_down_k=t_down,
                        nf_rec_db=nf_rec,
                        tx_power_w=ptx,
                        tx_gain_dbi=gtx,
                        tx_line_loss_db=tx_loss
                    )
                )
                st.rerun()
            else:
                st.sidebar.warning(f"{escolha} já está no cenário.")
    else:
        with st.sidebar.form("nova_estacao_form"):
            nome     = st.text_input("Nome da Estação", placeholder="Ex: Estação Brasília")
            lat      = st.number_input("Latitude (graus)", value=-15.79, step=0.01)
            lon      = st.number_input("Longitude (graus)", value=-47.88, step=0.01)
            
            st.markdown("**Configurações de Antena**")
            gain_mode = st.radio("Ganho de Antena por:", ["Valor Direto", "Diâmetro e Eficiência"])
            ganho_rx = st.number_input("Ganho RX (dBi)", value=40.0, step=0.5)
            diameter = st.number_input("Diâmetro (m)", value=1.8, step=0.1)
            efficiency = st.number_input("Eficiência (%)", value=60.0, step=5.0)
            
            st.markdown("**Transmissor (Uplink)**")
            ptx = st.number_input("Potência TX (W)", value=120.0, step=5.0)
            gtx = st.number_input("Ganho TX (dBi)", value=42.0, step=0.5)
            tx_loss = st.number_input("Perda Guia de Onda TX (dB)", value=0.5, step=0.1)
            
            st.markdown("**Ruído do Terminal**")
            t_ant = st.number_input("Temp. Antena (K)", value=50.0, step=5.0)
            t_lna = st.number_input("Temp. LNA (K)", value=80.0, step=5.0)
            g_lna = st.number_input("Ganho LNA (dB)", value=50.0, step=1.0)
            t_down = st.number_input("Temp. Downconverter (K)", value=290.0, step=10.0)
            nf_rec = st.number_input("Receiver Noise Figure (dB)", value=8.0, step=0.5)

            if st.form_submit_button("➕ Adicionar Customizada", use_container_width=True) and nome:
                st.session_state['stations'].append(
                    GroundStation(
                        name=nome,
                        latitude_deg=lat,
                        longitude_deg=lon,
                        rx_gain_dbi=ganho_rx,
                        gain_mode=gain_mode,
                        antenna_diameter_m=diameter,
                        antenna_efficiency_pct=efficiency,
                        temp_antenna_k=t_ant,
                        temp_lna_k=t_lna,
                        gain_lna_db=g_lna,
                        temp_down_k=t_down,
                        nf_rec_db=nf_rec,
                        tx_power_w=ptx,
                        tx_gain_dbi=gtx,
                        tx_line_loss_db=tx_loss
                    )
                )
                st.rerun()

    # Lista de estações terrenas no cenário com suporte à exclusão
    stations = st.session_state['stations']
    if stations:
        st.sidebar.markdown("**No cenário:**")
        for i, s in enumerate(stations):
            col_name, col_btn = st.sidebar.columns([3, 1])
            col_name.markdown(f"🔸 **{s.name}**  \n`{s.latitude_deg:.2f}°, {s.longitude_deg:.2f}°`")
            if col_btn.button("✕", key=f"rm_stn_{i}", help=f"Remover {s.name}"):
                st.session_state['stations'].pop(i)
                st.rerun()
