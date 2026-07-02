# Catálogo de satélites pré-definidos (baseado nos slides e especificações)
CATALOGO_SATELITES = [
    {
        "name": "Star One C2",
        "orbit_type": "GEO",
        "longitude_deg": -70.0,
        "tx_power_w": 100.0,
        "tx_gain_dbi": 35.0,
        "frequency_ghz": 4.0,  # Banda C
        "pattern_type": "Modelo Parabólico",
        "pattern_hpbw": 4.0
    },
    {
        "name": "Star One D1",
        "orbit_type": "GEO",
        "longitude_deg": -84.0,
        "tx_power_w": 120.0,
        "tx_gain_dbi": 40.0,
        "frequency_ghz": 12.0, # Banda Ku
        "pattern_type": "Modelo Parabólico",
        "pattern_hpbw": 2.0
    },
    {
        "name": "Amazonas 2",
        "orbit_type": "GEO",
        "longitude_deg": -61.0,
        "tx_power_w": 80.0,
        "tx_gain_dbi": 38.0,
        "frequency_ghz": 12.0, # Banda Ku
        "pattern_type": "Modelo Parabólico",
        "pattern_hpbw": 2.5
    }
]
