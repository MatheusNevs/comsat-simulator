"""
Aba do Globo 3D Interativo (ui/tabs/tab_globe.py)

Encapsula a chamada ao gerador HTML do globo 3D e renderiza o componente no Streamlit.
"""

import streamlit.components.v1 as components
from ui.components.globe_renderer import render_globe_html


def render_tab_globe(satellites, stations):
    """
    Gera o código HTML/JS do globo 3D interativo contendo os satélites e estações terrenas
    e o insere na interface através de um componente customizado do Streamlit.

    Parâmetros:
        satellites (list[Satellite]): Lista de objetos satélite cadastrados.
        stations (list[GroundStation]): Lista de objetos estação terrena cadastrados.
    """
    html = render_globe_html(satellites, stations, height=900)
    # A altura de 1200px garante o preenchimento total do iframe no viewport do navegador
    components.html(html, height=1200, scrolling=False)
