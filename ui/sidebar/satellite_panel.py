import streamlit as st
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
            nome = st.text_input("Nome")
            lon  = st.number_input("Longitude (ex: -70 para 70°W)", value=0.0)
            ptx  = st.number_input("Potência TX (W)", value=100.0)
            gtx  = st.number_input("Ganho Antena (dBi)", value=30.0)
            freq = st.number_input("Frequência (GHz)", value=12.0)
            if st.form_submit_button("➕ Adicionar Customizado", use_container_width=True) and nome:  # form_submit_button não precisa de key
                st.session_state['satellites'].append(
                    Satellite(nome, "GEO", lon, ptx, gtx, freq)
                )
                st.rerun()

    # Lista de satélites no cenário com botão de remoção
    sats = st.session_state['satellites']
    if sats:
        st.sidebar.markdown("**No cenário:**")
        for i, s in enumerate(sats):
            col_name, col_btn = st.sidebar.columns([3, 1])
            col_name.markdown(f"🔹 **{s.name}**  \n`{s.longitude_deg}°`")
            if col_btn.button("✕", key=f"rm_sat_{i}", help=f"Remover {s.name}"):
                st.session_state['satellites'].pop(i)
                st.rerun()
