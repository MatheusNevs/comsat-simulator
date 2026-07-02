import streamlit as st
from ui.sidebar.satellite_panel import render_satellite_panel
from ui.sidebar.station_panel import render_station_panel
from ui.tabs.tab_globe import render_tab_globe

st.set_page_config(
    page_title="ComSat Simulator",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Remove TODA a UI nativa do Streamlit e garante que o iframe ocupe 100% do viewport
st.markdown("""
<style>
/* Esconde o header com botão Deploy, menu, e footer */
header[data-testid="stHeader"]   { display: none !important; }
[data-testid="stToolbar"]        { display: none !important; }
[data-testid="stDecoration"]     { display: none !important; }
[data-testid="stStatusWidget"]   { display: none !important; }
.stDeployButton                  { display: none !important; }
#MainMenu                        { display: none !important; }
footer                           { display: none !important; }

/* Remove todos os paddings e margens da área principal */
html, body, .stApp               { overflow: hidden !important; }
.main .block-container           {
    padding:    0 !important;
    max-width:  100% !important;
    margin:     0 !important;
}
section[data-testid="stMain"]    {
    padding:    0 !important;
    overflow:   hidden !important;
}
[data-testid="stMainBlockContainer"] {
    padding:    0 !important;
    max-width:  100% !important;
}

/* Faz o wrapper do componente e o iframe preencherem 100vh */
div[data-testid="stCustomComponentV1"],
div[data-testid="stCustomComponentV1"] > div {
    height:     100vh !important;
    max-height: 100vh !important;
    overflow:   hidden !important;
}
div[data-testid="stCustomComponentV1"] iframe {
    height:     100vh !important;
    width:      100%  !important;
    border:     none  !important;
    display:    block !important;
}
</style>
""", unsafe_allow_html=True)


def main():
    # Barra lateral esquerda — configuração do cenário
    render_satellite_panel()
    st.sidebar.markdown("---")
    render_station_panel()

    satellites = st.session_state.get('satellites', [])
    stations   = st.session_state.get('stations',   [])

    # Seção para Geração de Relatório PDF Customizado
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Relatório Técnico PDF")
    if satellites and stations:
        sat_names = [s.name for s in satellites]
        stn_names = [s.name for s in stations]
        
        sel_sat_name = st.sidebar.selectbox("Satélite para Relatório", sat_names, key="pdf_sat_sel")
        sel_stn_name = st.sidebar.selectbox("Estação para Relatório", stn_names, key="pdf_stn_sel")
        
        sel_sat = next(s for s in satellites if s.name == sel_sat_name)
        sel_stn = next(s for s in stations if s.name == sel_stn_name)
        
        bw_mhz = st.sidebar.number_input("Banda do Canal (MHz)", min_value=0.1, value=36.0, step=1.0, key="pdf_bw")
        rb_mbps = st.sidebar.number_input("Taxa de Bits (Mbps)", min_value=0.1, value=50.0, step=1.0, key="pdf_rb")
        mod_type = st.sidebar.selectbox("Modulação", ["BPSK", "QPSK", "8PSK", "16QAM"], index=1, key="pdf_mod")
        
        from core.pdf_generator import gerar_pdf_report_bytes
        try:
            pdf_data = gerar_pdf_report_bytes(sel_sat, sel_stn, bw_mhz, rb_mbps, mod_type)
            st.sidebar.download_button(
                label="💾 Download Relatório PDF",
                data=pdf_data,
                file_name=f"ComSat_Relatorio_{sel_sat.name}_{sel_stn.name}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.sidebar.error(f"Erro ao gerar PDF: {str(e)}")
    else:
        st.sidebar.info("Configure satélites e estações para habilitar o relatório.")

    # Área principal: somente o globo
    render_tab_globe(satellites, stations)


if __name__ == "__main__":
    main()
