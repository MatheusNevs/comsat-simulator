"""
ComSat Simulator - Aplicação Principal (Streamlit)

Este arquivo é o ponto de entrada principal do simulador ComSat. Ele configura a página Streamlit,
aplica o CSS customizado para permitir uma visualização em tela cheia (100% viewport) do mapa 3D
e orquestra a renderização dos painéis laterais de configuração e do globo interativo.
"""

import streamlit as st
from ui.sidebar.satellite_panel import render_satellite_panel
from ui.sidebar.station_panel import render_station_panel
from ui.tabs.tab_globe import render_tab_globe

# Configuração da página no Streamlit (Título da aba, ícone e layout em largura total)
st.set_page_config(
    page_title="ComSat Simulator",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada: remove o cabeçalho, rodapé e margens nativas do Streamlit,
# garantindo que o iframe do globo 3D ocupe 100% da altura e largura da tela (100vh/100vw).
st.markdown("""
<style>
/* Esconde o header nativo do Streamlit (botão Deploy, menu hambúrguer e footer) */
header[data-testid="stHeader"]   { display: none !important; }
[data-testid="stToolbar"]        { display: none !important; }
[data-testid="stDecoration"]     { display: none !important; }
[data-testid="stStatusWidget"]   { display: none !important; }
.stDeployButton                  { display: none !important; }
#MainMenu                        { display: none !important; }
footer                           { display: none !important; }

/* Remove todos os paddings e margens da área de conteúdo principal */
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

/* Força os componentes customizados (iframe) a preencherem toda a altura da tela (100vh) */
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
    """
    Função principal de execução da aplicação.
    - Inicializa e renderiza o painel de satélites na barra lateral.
    - Renderiza o painel de estações terrenas na barra lateral.
    - Obtém o estado atual do cenário a partir do st.session_state.
    - Renderiza o componente de mapa 3D (globo) com os satélites e estações configurados.
    """
    # Barra lateral esquerda: formulários para adicionar e editar satélites e estações terrenas
    render_satellite_panel()
    st.sidebar.markdown("---")
    render_station_panel()

    # Recupera a lista de satélites e estações cadastradas na sessão do usuário
    satellites = st.session_state.get('satellites', [])
    stations   = st.session_state.get('stations',   [])

    # Renderiza o globo 3D interativo na área principal
    render_tab_globe(satellites, stations)


if __name__ == "__main__":
    main()
