# 🛰️ ComSat Simulator — Ferramenta Open-Source de Dimensionamento de Comunicação via Satélite

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg)](https://streamlit.io/)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/)

O **ComSat Simulator** é uma ferramenta computacional open-source tridimensional e interativa projetada para o dimensionamento, análise e simulação de enlaces de sistemas de comunicação via satélite geoestacionários (GEO). 

O projeto combina modelos matemáticos rigorosos de propagação de radiofrequência (RF), ruído térmico em cascata (fórmula de Friis), atenuação atmosférica e pluviométrica (ITU-R) e modulação digital com uma interface gráfica WebGL 3D de alta performance integrada ao framework Streamlit.

---

## 🌟 Funcionalidades Principais

* **Modelo Completo de Transponder (Uplink + Downlink):** Avaliação simultânea e independente de ambos os enlaces com suporte a perdas de linha, antenas e ganhos off-axis.
* **Atenuações Atmosféricas e por Chuva Dinâmicas:** Implementação das recomendações internacionais **ITU-R P.618** (propagações em trajetos inclinados) e **ITU-R P.838** (coeficientes de chuva para polarização em função da frequência), com parâmetros ajustáveis de taxa de precipitação ($R_{0.01}$) e probabilidade de excedência ($P$).
* **Análise de Ruído em Cascata (Fórmula de Friis):** Cálculo da temperatura de ruído equivalente do receptor ($T_{eff}$) e do sistema ($T_{sys}$), avaliando antena, LNA, cabos/guias de onda, downconverter e receptor para estimar a Figura de Mérito ($G/T$) e a densidade espectral de ruído ($N_0$).
* **Modelagem de Modulação Digital & Taxa de Erro de Bit (BER):** Suporte às modulações **BPSK, QPSK, 8PSK e 16QAM**, com cálculo dinâmico da relação $E_b/N_0$ e plotagem em tempo real das curvas teóricas de BER.
* **Visualização Tridimensional Interativa (WebGL / Globe.gl):** Renderização tridimensional da Terra, do anel de Clarke (órbita GEO), estações terrenas e linhas de enlace codificadas por cores em função da margem do link. Exibição da pegada de sinal (footprint) e feixes de radiação.
* **Geração e Exportação de Relatório Técnico (PDF):** Emissão client-side de relatório técnico completo contendo tabelas detalhadas de balanço de potência, temperatura de ruído, parâmetros de visibilidade e gráfico vetorizado de BER.

---

## 🏗️ Arquitetura e Estrutura de Diretórios

O código é estruturado de forma modular para facilitar a manutenção e a inclusão de novas funcionalidades pela comunidade open-source:

```text
comsat/
│
├── app.py                     # Script principal e ponto de entrada da aplicação Streamlit
├── requirements.txt           # Dependências do projeto (Streamlit, fpdf2, pandas, numpy)
├── .gitignore                 # Arquivos ignorados pelo Git (.venv, .agents, temporários)
├── README.md                  # Documentação do projeto
│
├── data/                      # Catálogos de dados pré-definidos
│   └── satellites.py          # Catálogo de satélites comerciais (Star One C2, D1, Amazonas 2)
│
├── models/                    # Modelos e estruturas de dados (Dataclasses)
│   ├── satellite.py           # Classe Satellite (parâmetros de RF, órbita e receptor)
│   └── ground_station.py      # Classe GroundStation (parâmetros da estação terrena)
│
├── core/                      # Motores de cálculo de telecomunicações
│   ├── orbit.py               # Conversão de coordenadas geográficas/cartesianas 3D
│   ├── link_budget.py         # Cálculos de distância, elevação, EIRP, FSPL e perdas
│   ├── noise.py               # Cascata de ruído de Friis, Tsys, G/T, N0 e C/N
│   ├── modulation.py          # Equações de BER teóricas (BPSK, QPSK, 8PSK, 16QAM) e Eb/N0
│   └── pdf_generator.py       # Motor de geração de relatórios técnicos em PDF (fpdf2)
│
└── ui/                        # Camada de Interface do Usuário (Streamlit & Frontend)
    ├── input_sidebar.py       # Menus de entrada de parâmetros gerais
    ├── results_panel.py       # Painéis de exibição de métricas
    ├── sidebar/               # Formulários da barra lateral
    │   ├── satellite_panel.py # Painel de cadastro/gestão de satélites
    │   └── station_panel.py   # Painel de cadastro/gestão de estações terrenas
    ├── tabs/                  # Abas principais da interface
    │   └── tab_globe.py       # Container do mapa 3D
    └── components/            # Renderizador WebGL e motor JS no cliente
        └── globe_renderer.py  # Renderização interativa do globo 3D (Globe.gl & Three.js)
```

---

## 💻 Requisitos e Instalação

### Pré-requisitos
* **Python 3.9** ou superior.
* Navegador Web moderno (Google Chrome, Mozilla Firefox, Microsoft Edge, Safari) com aceleração de hardware ativa (WebGL).

### Passo a Passo de Instalação

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/MatheusNevs/comsat.git
   cd comsat
   ```

2. **Criar e ativar o ambiente virtual (`.venv`):**

   * **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

   * **Windows (CMD):**
     ```cmd
     python -m venv .venv
     .venv\Scripts\activate.bat
     ```

   * **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

3. **Instalar as dependências:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Executar a aplicação:**
   ```bash
   streamlit run app.py
   ```
   Acesse a aplicação no navegador através do endereço `http://localhost:8501`.

---

## 📖 Como Usar o Simulador

1. **Adicionar Satélites e Estações:**
   Use o menu lateral esquerdo para selecionar satélites do catálogo ou cadastrar novas entidades com parâmetros customizados (frequências de transmissão/recepção, diagramas de radiação, potência e temperaturas de ruído).

2. **Visualizar e Interagir no Globo 3D:**
   A rotação e o zoom no globo 3D são controlados via mouse. Ao clicar em um satélite ou estação terrena, um painel interativo de edição é aberto. A cor da linha do enlace indica a viabilidade:
   * 🟢 **Verde:** Enlace adequado (Margem $\ge 3\text{ dB}$).
   * 🟡 **Amarelo:** Enlace no limiar de operação ($0\text{ dB} \le \text{Margem} < 3\text{ dB}$).
   * 🔴 **Vermelho:** Enlace inviável ($\text{Margem} < 0\text{ dB}$).

3. **Analisar Enlaces em Tempo Real:**
   Clique no botão **📊 ANÁLISE** no canto superior direito para abrir a gaveta de métricas. Alterne entre as abas **Link**, **Ruído**, **BER** e **PDF**.

4. **Exportar Relatório PDF:**
   Na aba **PDF**, clique no botão para gerar e baixar um relatório completo contendo todos os dados técnicos e o gráfico vetorizado de desempenho.

---

## 🤝 Como Contribuir

Contribuições da comunidade open-source são muito bem-vindas! Se você deseja propor melhorias, corrigir bugs ou adicionar novos modelos de comunicação (ex: órbitas LEO/MEO, novas recomendações ITU-R ou códigos de correção de erros FEC):

1. **Faça um Fork** do repositório.
2. **Crie uma Branch** para sua feature/correção:
   ```bash
   git checkout -b feature/minha-nova-funcionalidade
   ```
3. **Faça os Commits** com mensagens claras:
   ```bash
   git commit -m "feat: Adiciona modelo de atenuação por nuvens ITU-R P.840"
   ```
4. **Envie as alterações** para o seu repositório remoto:
   ```bash
   git push origin feature/minha-nova-funcionalidade
   ```
5. **Abra um Pull Request (PR)** detalhando as modificações realizadas.
