import streamlit as st
from data.satellites import CATALOGO_SATELITES
from models.satellite import Satellite

def render_satellite_panel():
    st.sidebar.header("🛰️ Configuração do Satélite")
    
    # Inicia a lista de satélites na sessão se não existir
    if 'satellites' not in st.session_state:
        st.session_state['satellites'] = []

    modo = st.sidebar.radio("Adicionar Satélite:", ["Do Catálogo", "Customizado"])
    
    if modo == "Do Catálogo":
        nomes = [sat["name"] for sat in CATALOGO_SATELITES]
        escolha = st.sidebar.selectbox("Selecione:", nomes)
        if st.sidebar.button("Adicionar"):
            dados = next(item for item in CATALOGO_SATELITES if item["name"] == escolha)
            sat = Satellite(**dados)
            st.session_state['satellites'].append(sat)
            st.sidebar.success(f"{sat.name} adicionado!")
    else:
        with st.sidebar.form("novo_satelite_form"):
            nome = st.text_input("Nome")
            lon = st.number_input("Longitude (ex: -70 para 70°W)", value=0.0)
            ptx = st.number_input("Potência TX (W)", value=100.0)
            gtx = st.number_input("Ganho Antena (dBi)", value=30.0)
            freq = st.number_input("Frequência (GHz)", value=12.0)
            
            submit = st.form_submit_button("Adicionar Customizado")
            if submit and nome:
                sat = Satellite(nome, "GEO", lon, ptx, gtx, freq)
                st.session_state['satellites'].append(sat)
                st.sidebar.success("Adicionado!")

    # Exibe os satélites já adicionados
    if st.session_state['satellites']:
        st.sidebar.markdown("### Satélites no Cenário")
        for s in st.session_state['satellites']:
            st.sidebar.text(f"🔹 {s.name} ({s.longitude_deg}°)")
