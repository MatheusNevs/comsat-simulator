import streamlit.components.v1 as components
from ui.components.globe_renderer import render_globe_html


def render_tab_globe(satellites, stations):
    html = render_globe_html(satellites, stations, height=900)
    # height=1200 garante que o iframe é maior que qualquer viewport comum.
    # O JS interno redimensiona para o tamanho real do parent via window.frameElement.
    components.html(html, height=1200, scrolling=False)
