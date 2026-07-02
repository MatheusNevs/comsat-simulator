import streamlit as st

def render_results(parametros, resultados):
    """
    Renderiza os resultados do Link Budget na tela principal.
    """
    st.subheader("📊 Resumo dos Resultados")
    
    # Exemplo de como usar abas para separar os resultados no futuro
    tab1, tab2, tab3 = st.tabs(["Link Budget Básico", "Análise de Ruído", "Gráficos"])

    with tab1:
        st.markdown("### Valores Informados")
        st.write(f"**Frequência:** {parametros['frequencia_ghz']} GHz")
        st.write(f"**Distância:** {parametros['distancia_km']} km")
        
        st.markdown("### Resultados do Link Budget")
        # Usando colunas para métricas bonitas
        col1, col2, col3 = st.columns(3)
        
        col1.metric("EIRP", f"{resultados['eirp']} dBW")
        col2.metric("Perda no Espaço Livre (FSPL)", f"{resultados['fspl']} dB")
        col3.metric("Potência Recebida", f"{resultados['potencia_recebida']} dBm")
        
        st.info("💡 **Dica:** Estes valores atualmente são simulações. A seguir, implementaremos as equações matemáticas (Core).")

    with tab2:
        st.write("Em construção: Aqui exibiremos G/T, Teff, C/N0, Eb/N0, etc.")

    with tab3:
        st.write("Em construção: Aqui exibiremos o gráfico Waterfall do enlace.")
