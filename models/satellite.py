from dataclasses import dataclass

@dataclass
class Satellite:
    name: str
    orbit_type: str        # 'GEO', 'MEO', 'LEO'
    longitude_deg: float   # ex: -70.0 para 70°W (usado para GEO)
    tx_power_w: float      # Potência de transmissão
    tx_gain_dbi: float     # Ganho da antena transmissora
    frequency_ghz: float   # Frequência central de operação
