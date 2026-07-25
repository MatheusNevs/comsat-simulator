"""
Catálogo de Satélites Pré-definidos (data/satellites.py)

Contém uma lista de dicionários com especificações técnicas e parâmetros reais de satélites
comerciais geoestacionários (como Star One C2, Star One D1 e Amazonas 2) para rápido carregamento no simulador.
"""

# Catálogo de satélites pré-definidos (baseado em especificações comerciais e acadêmicas)
CATALOGO_SATELITES = [
    {
        "name": "Star One C2",
        "orbit_type": "GEO",
        "longitude_deg": -70.0,
        "tx_power_w": 100.0,
        "tx_gain_dbi": 35.0,
        "frequency_ghz": 4.0,  # Operação em Banda C (4 GHz Downlink)
        "pattern_type": "Modelo Parabólico",
        "pattern_hpbw": 4.0
    },
    {
        "name": "Star One D1",
        "orbit_type": "GEO",
        "longitude_deg": -84.0,
        "tx_power_w": 120.0,
        "tx_gain_dbi": 40.0,
        "frequency_ghz": 12.0, # Operação em Banda Ku (12 GHz Downlink)
        "pattern_type": "Modelo Parabólico",
        "pattern_hpbw": 2.0
    },
    {
        "name": "Amazonas 2",
        "orbit_type": "GEO",
        "longitude_deg": -61.0,
        "tx_power_w": 80.0,
        "tx_gain_dbi": 38.0,
        "frequency_ghz": 12.0, # Operação em Banda Ku (12 GHz Downlink)
        "pattern_type": "Modelo Parabólico",
        "pattern_hpbw": 2.5
    }
]
