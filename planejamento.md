# 🛰️ ComSat Simulator — Plano de Desenvolvimento

## Filosofia
> **Faça o básico funcionar muito bem. Depois adicione mais.**
> Cada etapa termina com algo rodando e funcional. Nunca quebramos o que já está funcionando.

---

## O que é o MVP (o que tem que funcionar perfeitamente)

1. **Um globo 3D** com a Terra e um satélite GEO posicionado.
2. **Uma estação terrena** configurável (lat/lon, antena, receptor).
3. **Link Budget de Downlink** completo: EIRP → FSPL → Prx → C/N → Margem.
4. **Tabela + Gráfico Waterfall** do link budget.
5. **Enlace visível no globo** com cor indicando qualidade (verde/amarelo/vermelho).

Se o MVP estiver funcionando bem → adicionamos mais features em cima, uma por vez.

---

## Etapas de Desenvolvimento

### ✅ Etapa 1 — Esqueleto
Criar a estrutura de arquivos, instalar dependências e ter o app abrindo no browser com a sidebar e as abas vazias.

**Status:** Concluído

---

### ✅ Etapa 2 — Globo + Satélite GEO
- Renderizar o globo 3D no Three.js/Globe.gl.
- Posicionar um satélite GEO (ponto luminoso estável e discreto na órbita, sem linhas de haste longas).
- Posicionar a estação terrena (marcador de círculo na superfície).
- Desenhar a linha de enlace entre os dois (com animação orientada no sentido físico do Downlink, do satélite para a estação terrena).

**Status:** Concluído

---

### ✅ Etapa 3 — Link Budget Downlink
- Calcular a distância real de visada (geometria esférica).
- Calcular EIRP, FSPL, Perdas, Potência Recebida, C/N.
- Calcular a **Margem de Link** (com base em um limiar requerido para BER = 10⁻⁶).
- Exibir tabela e detalhamento em tempo real.
- Colorir e calcular dinamicamente os enlaces no globo (Verde = Ótimo, Amarelo = Regular, Vermelho = Crítico).
- Exibir um **Gráfico de Cascata (Waterfall)** estilizado via CSS mostrando as etapas de ganhos/perdas.

**Status:** Concluído

---

### ✅ Etapa 4 — Análise de Ruído
- Cascata de ruído via Fórmula de Friis.
- Calcular G/T e Temperatura do Sistema (Tsys).
- Exibir ruído espectral e cálculo de C/N no canal.
- Exibir a **Tabela de Cascata de Componentes** (Antena, LNA e Receptor/Mixer) detalhando a contribuição individual de ruído de cada estágio.

**Status:** Concluído

---

### ✅ Etapa 5 — Desempenho e BER
- Calcular Eb/N₀ a partir do enlace.
- Estimar BER para BPSK, QPSK, 8PSK, 16QAM.
- Exibir classificação de viabilidade do enlace.
- Exibir o **Gráfico de Curvas de BER (SVG)** mostrando as modulações BPSK/QPSK, 8PSK e 16QAM com o ponto de operação ativo (LINK OP) se deslocando e pulsando em tempo real.

**Status:** Concluído

---

### ✅ Etapa 6 — Relatório PDF
- Gerar um relatório técnico de impressão.
- Opção para Imprimir / Salvar como PDF nativo do navegador.
- Incluir folha de estilo dedicada de impressão (`@media print`) para gerar um layout de PDF de engenharia limpo (fundo branco, ocultando elementos de interface como o globo 3D e botões de navegação).

**Status:** Concluído

---

## Estrutura de Arquivos

```
comsat/
├── app.py                  # Orquestrador — monta a página, não tem lógica
├── requirements.txt
│
├── models/                 # Dataclasses: Satellite, GroundStation, Environment, LinkResult
├── core/                   # Matemática pura: orbit, link_budget, noise, modulation, atmosphere
├── data/                   # Catálogos estáticos: satélites, cidades, zonas ITU
└── ui/
    ├── sidebar/            # Painéis de configuração (satellite, station, environment)
    ├── tabs/               # Uma aba por módulo (globe, link_budget, noise, performance, pdf)
    └── components/         # Funções de renderização reutilizáveis (globe, waterfall, ber_chart)
```

> **Regra:** `core/` não sabe que o Streamlit existe. `ui/` não faz cálculos. `app.py` apenas conecta os dois.

---

*Última atualização: 2026-07-02*
