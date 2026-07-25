"""
Painel Lateral de Gerenciamento de Satélites (ui/sidebar/satellite_panel.py)

Interface Streamlit para seleção de satélites pré-definidos do catálogo ou cadastro customizado
com parâmetros de transmissão, recepção (uplink/downlink) e importação de diagramas de radiação.
"""

import streamlit as st
import pandas as pd
from data.satellites import CATALOGO_SATELITES
from models.satellite import Satellite


def render_satellite_panel():
    """
    Renderiza o formulário da barra lateral para adicionar, configurar e remover satélites do cenário.
    """
    st.sidebar.header("🛰️ Satélites")

    # Garante a inicialização da lista de satélites na sessão
    if 'satellites' not in st.session_state:
        st.session_state['satellites'] = []

    modo = st.sidebar.radio("Adicionar:", ["Do Catálogo", "Customizado"], horizontal=True)

    if modo == "Do Catálogo":
        nomes = [sat["name"] for sat in CATALOGO_SATELITES]
        escolha = st.sidebar.selectbox("Selecione:", nomes, label_visibility="collapsed")
        if st.sidebar.button("➕ Adicionar ao Cenário", key="btn_add_sat_catalogo", use_container_width=True):
            dados = next(item for item in CATALOGO_SATELITES if item["name"] == escolha)
            # Evita a duplicação de satélites com o mesmo nome no cenário
            nomes_atuais = [s.name for s in st.session_state['satellites']]
            if dados["name"] not in nomes_atuais:
                st.session_state['satellites'].append(Satellite(**dados))
                st.rerun()
            else:
                st.sidebar.warning(f"{dados['name']} já está no cenário.")
    else:
        with st.sidebar.form("novo_satelite_form"):
            nome = st.text_input("Nome", placeholder="Ex: Star One C2")
            lon  = st.number_input("Longitude (ex: -70 para 70°W)", value=0.0, step=0.5)
            ptx  = st.number_input("Potência TX (W)", value=100.0, step=5.0)
            gtx  = st.number_input("Ganho de Pico TX (dBi)", value=30.0, step=0.5)
            freq = st.number_input("Frequência TX / Downlink (GHz)", value=12.0, step=0.5)
            tx_loss = st.number_input("Perda de Guia de Onda TX (dB)", value=1.0, min_value=0.0, step=0.1)
            
            st.markdown("**Configurações do Receptor (Uplink)**")
            rx_freq = st.number_input("Frequência RX / Uplink (GHz)", value=14.0, step=0.5)
            rx_gain = st.number_input("Ganho Antena RX (dBi)", value=30.0, step=0.5)
            rx_loss = st.number_input("Perda Guia de Onda RX (dB)", value=1.0, min_value=0.0, step=0.1)
            
            with st.expander("Parâmetros do Receptor do Satélite"):
                sat_t_ant = st.number_input("Sat. Temp. Antena (K)", value=290.0, step=10.0)
                sat_t_lna = st.number_input("Sat. Temp. LNA (K)", value=150.0, step=10.0)
                sat_g_lna = st.number_input("Sat. Ganho LNA (dB)", value=50.0, step=5.0)
                sat_t_down = st.number_input("Sat. Temp. Downconverter (K)", value=290.0, step=10.0)
                sat_nf_rec = st.number_input("Sat. Noise Figure Receptor (dB)", value=8.0, step=0.5)
            
            st.markdown("**Diagrama de Radiação**")
            pattern_type = st.selectbox("Tipo de Padrão", ["Isotrópica", "Modelo Parabólico", "Carregar CSV"])
            pattern_hpbw = st.number_input("Largura de feixe θ_3dB (graus)", value=2.0, min_value=0.1, step=0.1)
            
            arquivo_csv = st.file_uploader("Upload do CSV (Ângulo, Ganho_Relativo)", type=["csv"], help="CSV com duas colunas: angulo (graus) e ganho_relativo (dB)")

            if st.form_submit_button("➕ Adicionar Customizado", use_container_width=True) and nome:
                pattern_data = None
                if pattern_type == "Carregar CSV" and arquivo_csv is not None:
                    try:
                        df = pd.read_csv(arquivo_csv)
                        # Limpeza e padronização dos nomes de colunas
                        df.columns = [c.strip().lower() for c in df.columns]
                        # Identifica automaticamente as colunas de ângulo e ganho
                        angle_col = next((c for c in df.columns if "ang" in c or "deg" in c), df.columns[0])
                        gain_col = next((c for c in df.columns if "gan" in c or "gain" in c or "rel" in c), df.columns[1])
                        # Ordenação por ângulo e remoção de valores nulos
                        df_clean = df[[angle_col, gain_col]].dropna().sort_values(by=angle_col)
                        pattern_data = df_clean.values.tolist()
                    except Exception as e:
                        st.error(f"Erro ao processar arquivo: {e}")
                        st.stop()
                
                st.session_state['satellites'].append(
                    Satellite(
                        name=nome,
                        orbit_type="GEO",
                        longitude_deg=lon,
                        tx_power_w=ptx,
                        tx_gain_dbi=gtx,
                        frequency_ghz=freq,
                        tx_line_loss_db=tx_loss,
                        rx_frequency_ghz=rx_freq,
                        rx_gain_dbi=rx_gain,
                        rx_line_loss_db=rx_loss,
                        sat_temp_antenna_k=sat_t_ant,
                        sat_temp_lna_k=sat_t_lna,
                        sat_gain_lna_db=sat_g_lna,
                        sat_temp_down_k=sat_t_down,
                        sat_nf_rec_db=sat_nf_rec,
                        pattern_type=pattern_type,
                        pattern_hpbw=pattern_hpbw,
                        pattern_data=pattern_data
                    )
                )
                st.rerun()

    # Exibição da lista de satélites ativos no cenário com opção de remoção
    sats = st.session_state['satellites']
    if sats:
        st.sidebar.markdown("**No cenário:**")
        for i, s in enumerate(sats):
            col_name, col_btn = st.sidebar.columns([3, 1])
            col_name.markdown(f"🔹 **{s.name}**  \n`{s.longitude_deg}° | {s.pattern_type}`")
            if col_btn.button("✕", key=f"rm_sat_{i}", help=f"Remover {s.name}"):
                st.session_state['satellites'].pop(i)
                st.rerun()
