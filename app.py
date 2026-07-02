import streamlit as st
from ui.sidebar.satellite_panel import render_satellite_panel
from ui.sidebar.station_panel import render_station_panel
from ui.tabs.tab_globe import render_tab_globe

# Configuração da página inicial
st.set_page_config(
    page_title="ComSat Simulator",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Monta a barra lateral (oculta por padrão, expansível pelo usuário)
    render_satellite_panel()
    st.sidebar.markdown("---")
    render_station_panel()

    satellites = st.session_state.get('satellites', [])
    stations = st.session_state.get('stations', [])

    # Globo 3D em destaque, ocupando a página inteira
    render_tab_globe(satellites, stations)

    st.markdown("---")

    tab_link, tab_noise, tab_perf, tab_pdf = st.tabs([
        "📊 Link Budget", "📡 Ruído", "📶 Desempenho", "📄 PDF"
    ])

    with tab_link:
        st.write("Aba de Link Budget (Sprint 3 - Em breve)")

    with tab_noise:
        st.write("Aba de Análise de Ruído (Sprint 4 - Em breve)")

    with tab_perf:
        st.write("Aba de Desempenho e BER (Sprint 5 - Em breve)")

    with tab_pdf:
        st.write("Aba de Relatórios (Em breve)")

if __name__ == "__main__":
    main()
