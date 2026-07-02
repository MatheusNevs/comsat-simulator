from dataclasses import dataclass

@dataclass
class GroundStation:
    name: str
    latitude_deg: float
    longitude_deg: float
    rx_gain_dbi: float
    # Adicionaremos parâmetros de cascata de ruído no futuro
