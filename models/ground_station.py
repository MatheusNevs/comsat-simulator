from dataclasses import dataclass

@dataclass
class GroundStation:
    name: str
    latitude_deg: float
    longitude_deg: float
    rx_gain_dbi: float
    
    # Parâmetros de antena física
    gain_mode: str = "Valor Direto"       # "Valor Direto", "Diâmetro e Eficiência"
    antenna_diameter_m: float = 1.8
    antenna_efficiency_pct: float = 60.0
    
    # Parâmetros da cascata de ruído
    temp_antenna_k: float = 50.0
    temp_lna_k: float = 80.0
    gain_lna_db: float = 50.0
    temp_down_k: float = 290.0
    nf_rec_db: float = 8.0
    
    # Parâmetros de transmissão (Uplink)
    tx_power_w: float = 120.0
    tx_gain_dbi: float = 40.0
    tx_line_loss_db: float = 0.5

