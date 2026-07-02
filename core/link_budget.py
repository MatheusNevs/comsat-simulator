import math

def calcular_tudo(params):
    """
    Função principal que orquestra os cálculos do Link Budget Básico.
    """
    freq_ghz = params['frequencia_ghz']
    ptx_w = params['potencia_tx_w']
    gtx_dbi = params['ganho_tx_dbi']
    perdas_tx = params['perdas_linha_tx_db']
    
    distancia_km = params['distancia_km']
    perda_atmos = params['perda_atmosferica_db']
    
    grx_dbi = params['ganho_rx_dbi']
    perdas_rx = params['perdas_linha_rx_db']

    # 1. Potência em dBW
    ptx_dbw = 10 * math.log10(ptx_w)

    # 2. EIRP (dBW) = Ptx(dBW) - Perdas_TX(dB) + Gtx(dBi)
    eirp = ptx_dbw - perdas_tx + gtx_dbi

    # 3. FSPL (Free Space Path Loss) em dB
    # FSPL = 20*log10(d_km) + 20*log10(f_GHz) + 92.45
    fspl = 20 * math.log10(distancia_km) + 20 * math.log10(freq_ghz) + 92.45

    # 4. Potência Recebida (dBW) = EIRP - FSPL - Perdas_Atmosféricas + Grx - Perdas_RX
    pot_recebida_dbw = eirp - fspl - perda_atmos + grx_dbi - perdas_rx
    
    # Converte para dBm
    pot_recebida_dbm = pot_recebida_dbw + 30

    return {
        "eirp": round(eirp, 2),
        "fspl": round(fspl, 2),
        "potencia_recebida": round(pot_recebida_dbm, 2)
    }
