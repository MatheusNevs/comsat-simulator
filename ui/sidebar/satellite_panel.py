import streamlit as st
import pandas as pd
from data.satellites import CATALOGO_SATELITES
from models.satellite import Satellite


def render_satellite_panel():
    st.sidebar.header("🛰️ Satélites")

    if 'satellites' not in st.session_state:
        st.session_state['satellites'] = []

    modo = st.sidebar.radio("Adicionar:", ["Do Catálogo", "Customizado"], horizontal=True)

    if modo == "Do Catálogo":
        nomes = [sat["name"] for sat in CATALOGO_SATELITES]
        escolha = st.sidebar.selectbox("Selecione:", nomes, label_visibility="collapsed")
        if st.sidebar.button("➕ Adicionar ao Cenário", key="btn_add_sat_catalogo", use_container_width=True):
            dados = next(item for item in CATALOGO_SATELITES if item["name"] == escolha)
            # Evita duplicatas pelo nome
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
            freq = st.number_input("Frequência (GHz)", value=12.0, step=0.5)
            tx_loss = st.number_input("Perda de Guia de Onda TX (dB)", value=1.0, min_value=0.0, step=0.1)
            
            st.markdown("**Diagrama de Radiação**")
            pattern_type = st.selectbox("Tipo de Padrão", ["Isotrópica", "Modelo Parabólico", "Carregar CSV"])
            pattern_hpbw = st.number_input("Largura de feixe θ_3dB (graus)", value=2.0, min_value=0.1, step=0.1)
            
            arquivo_csv = st.file_uploader("Upload do CSV (Ângulo, Ganho_Relativo)", type=["csv"], help="CSV com duas colunas: angulo (graus) e ganho_relativo (dB)")
 
            if st.form_submit_button("➕ Adicionar Customizado", use_container_width=True) and nome:
                pattern_data = None
                if pattern_type == "Carregar CSV" and arquivo_csv is not None:
                    try:
                        df = pd.read_csv(arquivo_csv)
                        # Limpa nomes de colunas
                        df.columns = [c.strip().lower() for c in df.columns]
                        # Detecta colunas de ângulo e ganho
                        angle_col = next((c for c in df.columns if "ang" in c or "deg" in c), df.columns[0])
                        gain_col = next((c for c in df.columns if "gan" in c or "gain" in c or "rel" in c), df.columns[1])
                        # Ordena e remove nulos
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
                        pattern_type=pattern_type,
                        pattern_hpbw=pattern_hpbw,
                        pattern_data=pattern_data,
                        tx_line_loss_db=tx_loss
                    )
                )
                st.rerun()

    # Lista de satélites no cenário com botão de remoção
    sats = st.session_state['satellites']
    if sats:
        st.sidebar.markdown("**No cenário:**")
        for i, s in enumerate(sats):
            col_name, col_btn = st.sidebar.columns([3, 1])
            col_name.markdown(f"🔹 **{s.name}**  \n`{s.longitude_deg}° | {s.pattern_type}`")
            if col_btn.button("✕", key=f"rm_sat_{i}", help=f"Remover {s.name}"):
                st.session_state['satellites'].pop(i)
                st.rerun()
