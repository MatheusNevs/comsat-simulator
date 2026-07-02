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
- Renderizar o globo 3D no Plotly.
- Posicionar um satélite GEO (ponto luminoso na órbita).
- Posicionar a estação terrena (marcador na superfície).
- Desenhar a linha de enlace entre os dois.

**Status:** Concluído

---

### ⬜ Etapa 3 — Link Budget Downlink
- Calcular a distância real de visada (geometria esférica).
- Calcular EIRP, FSPL, Perdas, Potência Recebida, C/N, Margem.
- Exibir tabela e gráfico Waterfall.
- Colorir a linha de enlace no globo conforme a margem.

**Status:** Pendente

---

### ⬜ Etapa 4 — Análise de Ruído
- Cascata de ruído via Fórmula de Friis.
- Calcular G/T e Temperatura do Sistema.
- Exibir tabela de cascata de componentes.

**Status:** Pendente

---

### ⬜ Etapa 5 — Desempenho e BER
- Calcular Eb/N₀ a partir do enlace.
- Estimar BER para BPSK, QPSK, 8PSK, 16QAM.
- Gráfico de curvas BER com ponto de operação marcado.

**Status:** Pendente

---

## Features Adicionais (após MVP)

Cada item abaixo é independente — pode ser adicionado sem tocar no resto:

- [ ] **Uplink** (Estação → Satélite): segunda direção do enlace, com parâmetros próprios.
- [ ] **Footprint**: calcular e desenhar a cobertura do feixe no globo, com gradiente de cor.
- [ ] **Satélites LEO com animação**: movimento ao longo da órbita + footprint deslizando.
- [ ] **Atmosfera e Chuva (ITU-R P.618)**: atenuação por chuva com zonas climáticas.
- [ ] **Múltiplos satélites e estações**: catálogo, seleção de par para análise.
- [ ] **Relatório PDF**: exportar tudo (tabelas + gráficos + imagem do globo).
- [ ] **Disponibilidade do enlace**: X% do tempo com atenuação de chuva configurada.

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

*Última atualização: 2026-07-01*
