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



    # Área principal: somente o globo
    render_tab_globe(satellites, stations)


if __name__ == "__main__":
    main()
