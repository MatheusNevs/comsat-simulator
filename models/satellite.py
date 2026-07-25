"""
Modelo de Dados para Satélites de Comunicação (models/satellite.py)

Define a dataclass `Satellite` que armazena os parâmetros físicos, orbitais, de RF e de ruído
de um satélite de comunicação.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Satellite:
    """
    Representa um satélite de comunicação e suas propriedades técnicas.

    Atributos:
        name (str): Nome de identificação do satélite (ex: "Star One C2").
        orbit_type (str): Tipo de órbita ("GEO", "MEO", "LEO").
        longitude_deg (float): Longitude orbital no Equador em graus (-180.0 a 180.0).
        tx_power_w (float): Potência de transmissão RF do HPA (Watts).
        tx_gain_dbi (float): Ganho de pico da antena transmissora (dBi).
        frequency_ghz (float): Frequência da portadora de transmissão (Downlink em GHz).
        pattern_type (str): Modelo do diagrama de radiação ("Isotrópica", "Modelo Parabólico", "CSV").
        pattern_hpbw (float): Largura de feixe de meia potência θ_3dB (graus).
        pattern_data (Optional[List[List[float]]]): Matriz de dados de ganho off-axis proveniente de arquivo CSV.
        tx_line_loss_db (float): Perda na linha de guia de onda / transmissão no satélite (dB).
        rx_frequency_ghz (float): Frequência do canal de recepção (Uplink em GHz).
        rx_gain_dbi (float): Ganho da antena receptora do satélite (dBi).
        rx_line_loss_db (float): Perda na linha de guia de recepção no satélite (dB).
        sat_temp_antenna_k (float): Temperatura de ruído da antena do satélite apontada para a Terra (K).
        sat_temp_lna_k (float): Temperatura de ruído do LNA do receptor de bordo (K).
        sat_gain_lna_db (float): Ganho do LNA do receptor de bordo (dB).
        sat_temp_down_k (float): Temperatura de ruído do misturador/downconverter de bordo (K).
        sat_nf_rec_db (float): Figura de ruído (NF) do receptor interno do satélite (dB).
    """
    name: str
    orbit_type: str               # Tipo de órbita ('GEO', 'MEO', 'LEO')
    longitude_deg: float          # Longitude orbital em graus (ex: -70.0 para 70°W)
    tx_power_w: float             # Potência de transmissão RF (Watts)
    tx_gain_dbi: float            # Ganho de pico da antena transmissora (dBi)
    frequency_ghz: float          # Frequência central de operação do enlace de Downlink (GHz)
    
    # Diagrama de radiação da antena do satélite
    pattern_type: str = "Isotrópica"  # Tipo: "Isotrópica", "Modelo Parabólico", "CSV"
    pattern_hpbw: float = 2.0         # Largura de feixe (θ_3dB) em graus
    pattern_data: Optional[List[List[float]]] = None  # Lista de pontos [ângulo, ganho_relativo]
    tx_line_loss_db: float = 1.0      # Perda na guia de onda de transmissão no satélite (dB)
    
    # Parâmetros do enlace de recepção (Uplink)
    rx_frequency_ghz: float = 14.0    # Frequência do canal de recepção em GHz
    rx_gain_dbi: float = 30.0         # Ganho da antena receptora do satélite em dBi
    rx_line_loss_db: float = 1.0      # Perda de linha da recepção no satélite em dB
    
    # Parâmetros de ruído do transponder / receptor de bordo
    sat_temp_antenna_k: float = 290.0
    sat_temp_lna_k: float = 150.0
    sat_gain_lna_db: float = 50.0
    sat_temp_down_k: float = 290.0
    sat_nf_rec_db: float = 8.0
