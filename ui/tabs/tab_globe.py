import streamlit.components.v1 as components
from ui.components.globe_renderer import render_globe_html, GLOBE_HEIGHT_PX


def render_tab_globe(satellites, stations):
    html = render_globe_html(satellites, stations)
    components.html(html, height=GLOBE_HEIGHT_PX, scrolling=False)
