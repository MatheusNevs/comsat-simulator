import streamlit as st
from ui.components.globe_renderer import create_globe_figure

def render_tab_globe():
    st.subheader("🌍 Visualização do Cenário")
    
    satellites = st.session_state.get('satellites', [])
    stations = st.session_state.get('stations', [])
    
    if not satellites and not stations:
        st.info("Nenhum satélite ou estação configurado. Use o painel lateral para adicionar elementos ao cenário.")
        return

    # Renderiza o globo no Plotly
    fig = create_globe_figure(satellites, stations)
    
    # Exibe o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)
