"""
Módulo de Exibição de Resultados (ui/results_panel.py)

Renderiza o painel de métricas e tabelas de resultados na interface do Streamlit.
"""

import streamlit as st

def render_results(parametros: dict, resultados: dict):
    """
    Renderiza os resultados consolidados do Link Budget em abas explicativas na tela principal.

    Parâmetros:
        parametros (dict): Parâmetros de entrada utilizados na simulação.
        resultados (dict): Dicionário com os resultados calculados (EIRP, FSPL, Prx, etc.).
    """
    st.subheader("📊 Resumo dos Resultados do Enlace")
    
    tab1, tab2, tab3 = st.tabs(["Link Budget Básico", "Análise de Ruído", "Gráficos"])

    with tab1:
        st.markdown("### Valores Informados")
        st.write(f"**Frequência:** {parametros.get('frequencia_ghz', 12.0)} GHz")
        st.write(f"**Distância:** {parametros.get('distancia_km', 38000.0)} km")
        
        st.markdown("### Resultados Calculados")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("EIRP", f"{resultados.get('eirp', 0.0)} dBW")
        col2.metric("Perda Espaço Livre (FSPL)", f"{resultados.get('fspl', 0.0)} dB")
        col3.metric("Potência Recebida (Prx)", f"{resultados.get('potencia_recebida_dbm', 0.0)} dBm")
        
        st.info("💡 **Dica:** É possível interagir diretamente com o globo 3D e o painel de análise lateral para cálculos completos de ruído e BER.")

    with tab2:
        st.write("Cálculos completos de G/T, Tsys, C/N0 e Eb/N0 estão integrados ao painel lateral do globo 3D.")

    with tab3:
        st.write("Gráficos de dispersão de atenuação e curva teórica de BER disponíveis para exportação em PDF.")
