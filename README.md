# 🛰️ ComSat Simulator

O **ComSat Simulator** é uma ferramenta computacional tridimensional interativa projetada para o dimensionamento de sistemas de comunicação via satélite. Desenvolvido para dar suporte à análise de enlaces de satélites geoestacionários (GEO), este projeto integra um modelo matemático detalhado de propagação, ruído, modulação e interferência orbital com uma interface gráfica rica e interativa em WebGL (Globe.gl) incorporada a um painel de controle Streamlit.

---

## 🚀 Funcionalidades Principais

*   **Modelo de Transponder Completo (Uplink + Downlink):** Avaliação simultânea de ambos os enlaces com cascata de componentes de transmissão e recepção.
*   **Atenuações Dinâmicas por Chuva e Atmosfera:** Implementação das diretrizes da **ITU-R P.618** para atenuação por trajeto inclinado e **ITU-R P.838** para interpolação de coeficientes de polarização circular em função da frequência, com probabilidade de indisponibilidade ($P$) e taxa de precipitação ($R_{0.01}$) customizáveis.
*   **Análise de Ruído em Cascata (Fórmula de Friis):** Cálculo da temperatura de ruído equivalente do receptor ($T_{eff}$) e do sistema ($T_{sys}$) tanto para a estação terrena (Downlink) quanto para o satélite (Uplink), avaliando antena, LNA, downconverter e mixer.
*   **Interferência de Satélites Adjacentes (ASI / uASI):** Cálculo geométrico e tridimensional da interferência no downlink (dASI) gerada por outros satélites próximos e no uplink (uASI) gerada por estações adjacentes, baseado em sua separação angular topocêntrica e largura de feixe de antena ($\theta_{3\text{dB}}$).
*   **Desempenho e Curvas de BER:** Suporte aos esquemas de modulação **BPSK, QPSK, 8PSK e 16QAM**, com plotagem dinâmica da curva teórica de Bit Error Rate (BER) versus o ponto de operação real $E_b/(N_0 + I_0)$ obtido no link.
*   **Impressão de Relatório Técnico (PDF):** Geração client-side instantânea de um relatório técnico de engenharia de **2 páginas** formatado e detalhado contendo tabelas de perdas, cascata de ruído e gráficos de BER vetorizados.

---

## 📋 Pré-requisitos

Para rodar o projeto localmente, você precisa ter instalado em sua máquina:
*   **Python 3.9** ou superior.
*   Um navegador web moderno (Chrome, Firefox, Edge, Safari) com aceleração de hardware WebGL habilitada.

---

## 🛠️ Como Executar o Projeto

Siga as instruções abaixo de acordo com o seu sistema operacional.

### 🐧 No Linux / macOS

1.  **Abra o terminal** na pasta raiz do projeto.
2.  **Crie o ambiente virtual (venv):**
    ```bash
    python3 -m venv .venv
    ```
3.  **Ative o ambiente virtual:**
    ```bash
    source .venv/bin/activate
    ```
4.  **Instale as dependências necessárias:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
5.  **Inicie a aplicação:**
    ```bash
    streamlit run app.py
    ```

---

### 🪟 No Windows

1.  **Abra o Prompt de Comando (cmd) ou PowerShell** na pasta raiz do projeto.
2.  **Crie o ambiente virtual (venv):**
    ```cmd
    python -m venv .venv
    ```
3.  **Ative o ambiente virtual:**
    *   *No Prompt de Comando (CMD):*
        ```cmd
        .venv\Scripts\activate.bat
        ```
    *   *No PowerShell:*
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
        *(Nota: Se houver restrições de script no PowerShell, execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` antes de ativar).*
4.  **Instale as dependências necessárias:**
    ```cmd
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
5.  **Inicie a aplicação:**
    ```cmd
    streamlit run app.py
    ```

---

## 📁 Estrutura de Diretórios

O projeto está organizado da seguinte forma:

```text
comsat/
│
├── app.py                     # Script principal e ponto de entrada da aplicação Streamlit
├── requirements.txt           # Dependências do Python (Streamlit, Pandas, etc.)
│
├── data/                      # Base de dados (catálogos de satélites pré-definidos)
│   └── satellites.py
│
├── models/                    # Classes de dados de Satélites e Estações Terrenas
│   ├── satellite.py
│   └── ground_station.py
│
├── core/                      # Motores de cálculo em Python (link budget, ruído, modulações)
│   ├── link_budget.py
│   ├── noise.py
│   └── modulation.py
│
└── ui/                        # Componentes de Interface Gráfica
    ├── sidebar/               # Painéis da barra lateral (configuração de satélites/estações)
    │   ├── satellite_panel.py
    │   └── station_panel.py
    │
    ├── tabs/                  # Estrutura principal de visualização da área principal
    │   └── tab_globe.py
    │
    └── components/            # Visualização tridimensional do globo WebGL e análise (JavaScript)
        └── globe_renderer.py  # Renderização do Globe.gl e Motor Matemático em tempo real no cliente
```

---

## 🧑‍💻 Utilizando o Simulador

1.  **Configurar Satélites/Estações**: Use a barra lateral esquerda para adicionar satélites do catálogo ou criar entidades customizadas (incluindo frequências de uplink/downlink, perdas de linha, LNAs e diagramas de radiação).
2.  **Visualizar Enlaces**: Clique em uma estação e arraste o mouse no globo para ver os links se formarem. A cor do caminho indica a saúde do link:
    *   🟢 **Verde**: Margem combinada $\ge 3\text{ dB}$ (adequado).
    *   🟡 **Amarelo**: Margem combinada entre $0\text{ dB}$ e $3\text{ dB}$ (limiar).
    *   🔴 **Vermelho**: Margem combinada $< 0\text{ dB}$ (inviável).
3.  **Análise Detalhada**: Use a aba expansível à direita para alternar entre as visualizações detalhadas de **Link**, **Ruído** (com tabelas de cascata de Friis), **Desempenho** (onde você pode mudar a modulação e a taxa de bits em tempo real e ver a curva BER mudar) e **PDF**.
4.  **Exportar Relatório**: Vá na aba **PDF** e clique em **Baixar Relatório PDF** para salvar um arquivo técnico detalhado de duas páginas contendo todo o dimensionamento.
