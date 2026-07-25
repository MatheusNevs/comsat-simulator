"""
Modelo de Dados para Estações Terrenas (models/ground_station.py)

Define a dataclass `GroundStation` que armazena a localização geográfica, configurações de antena,
parâmetros de transmissão (uplink) e cadeia de recepção de ruído (cascata de Friis) da estação terrena.
"""

from dataclasses import dataclass

@dataclass
class GroundStation:
    """
    Representa uma estação terrena de comunicação via satélite.

    Atributos:
        name (str): Nome da estação terrena (ex: "Estação Brasília").
        latitude_deg (float): Latitude geográfica da estação em graus (-90° a 90°).
        longitude_deg (float): Longitude geográfica da estação em graus (-180° a 180°).
        rx_gain_dbi (float): Ganho da antena receptora em dBi.
        gain_mode (str): Modo de definição de ganho ("Valor Direto", "Diâmetro e Eficiência").
        antenna_diameter_m (float): Diâmetro físico do refletor parabólico em metros.
        antenna_efficiency_pct (float): Eficiência da antena em porcentagem (ex: 60%).
        temp_antenna_k (float): Temperatura de ruído coletada pela antena (Kelvin).
        temp_lna_k (float): Temperatura equivalente de ruído do LNA (Kelvin).
        gain_lna_db (float): Ganho de amplificação do LNA (dB).
        temp_down_k (float): Temperatura de ruído do Downconverter / Mixer (Kelvin).
        nf_rec_db (float): Figura de ruído (Noise Figure - NF) do receptor final (dB).
        tx_power_w (float): Potência de transmissão RF do HPA da estação (Watts).
        tx_gain_dbi (float): Ganho da antena de transmissão no Uplink (dBi).
        tx_line_loss_db (float): Perda na linha de transmissão / guias de onda no terminal (dB).
    """
    name: str
    latitude_deg: float
    longitude_deg: float
    rx_gain_dbi: float
    
    # Parâmetros físicos da antena
    gain_mode: str = "Valor Direto"       # "Valor Direto" ou "Diâmetro e Eficiência"
    antenna_diameter_m: float = 1.8
    antenna_efficiency_pct: float = 60.0
    
    # Parâmetros da cascata de ruído do receptor (Friis)
    temp_antenna_k: float = 50.0
    temp_lna_k: float = 80.0
    gain_lna_db: float = 50.0
    temp_down_k: float = 290.0
    nf_rec_db: float = 8.0
    
    # Parâmetros de transmissão no enlace de subida (Uplink)
    tx_power_w: float = 120.0
    tx_gain_dbi: float = 42.0
    tx_line_loss_db: float = 0.5
