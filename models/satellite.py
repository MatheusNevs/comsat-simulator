from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Satellite:
    name: str
    orbit_type: str               # 'GEO', 'MEO', 'LEO'
    longitude_deg: float          # ex: -70.0 para 70°W (usado para GEO)
    tx_power_w: float             # Potência de transmissão
    tx_gain_dbi: float            # Ganho da antena transmissora (pico)
    frequency_ghz: float          # Frequência central de operação
    
    # Parâmetros do diagrama de radiação da antena
    pattern_type: str = "Isotrópica"  # "Isotrópica", "Modelo Parabólico", "CSV"
    pattern_hpbw: float = 2.0         # Largura de feixe (θ_3dB) em graus
    pattern_data: Optional[List[List[float]]] = None  # Lista de [angulo, ganho_relativo]
    tx_line_loss_db: float = 1.0      # Perda na linha de guia de onda/transmissão no satélite
    
    # Parâmetros de recepção (Uplink)
    rx_frequency_ghz: float = 14.0    # Frequência de recepção (Uplink)
    rx_gain_dbi: float = 30.0         # Ganho da antena receptora do satélite
    rx_line_loss_db: float = 1.0      # Perda de linha guia de recepção no satélite
    
    # Parâmetros da cascata de ruído do satélite (Receptor de Bordo)
    sat_temp_antenna_k: float = 290.0
    sat_temp_lna_k: float = 150.0
    sat_gain_lna_db: float = 50.0
    sat_temp_down_k: float = 290.0
    sat_nf_rec_db: float = 8.0


