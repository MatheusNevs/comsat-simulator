"""
Módulo de Cálculo de Balanço de Enlace (Link Budget) - (core/link_budget.py)

Implementa as equações de propagação e balanço de potência em RF para enlaces via satélite:
- Geometria esférica e distância oblíqua (slant range)
- Ângulo de elevação da antena da estação terrena
- Perda no espaço livre (FSPL - Free Space Path Loss)
- Atenuação atmosférica e por chuva (Modelos estatísticos ITU-R P.618 / ITU-R P.838)
- Potência Isotrópica Radiada Efetiva (EIRP) e Potência Recebida (Prx em dBW e dBm)
"""

import math

# Constantes geodésicas e orbitais
R_EARTH_KM = 6371.0       # Raio médio da Terra em km
GEO_ALTITUDE_KM = 35786.0  # Altitude da órbita GEO em km


def calcular_distancia_e_elevacao(lat_st: float, lon_st: float, lon_sat: float, alt_sat_km: float = GEO_ALTITUDE_KM):
    """
    Calcula a distância 3D em linha de visada (slant range) e o ângulo de elevação da antena da estação
    terrena em relação a um satélite geoestacionário.

    Parâmetros:
        lat_st (float): Latitude da estação terrena (graus).
        lon_st (float): Longitude da estação terrena (graus).
        lon_sat (float): Longitude orbital do satélite GEO (graus).
        alt_sat_km (float): Altitude do satélite em km (default: 35786 km).

    Retorna:
        tuple[float, float]:
            - distancia (float): Distância no espaço livre (slant range) em km.
            - elevacao (float): Ângulo de elevação da antena em graus.
    """
    r_sat = R_EARTH_KM + alt_sat_km
    
    lat_rad = math.radians(lat_st)
    lon_st_rad = math.radians(lon_st)
    lon_sat_rad = math.radians(lon_sat)
    
    # Conversão para coordenadas cartesianas geocêntricas
    x_st = R_EARTH_KM * math.cos(lat_rad) * math.cos(lon_st_rad)
    y_st = R_EARTH_KM * math.cos(lat_rad) * math.sin(lon_st_rad)
    z_st = R_EARTH_KM * math.sin(lat_rad)
    
    x_sat = r_sat * math.cos(lon_sat_rad)
    y_sat = r_sat * math.sin(lon_sat_rad)
    z_sat = 0.0
    
    # Distância Euclidiana 3D (slant range)
    dx = x_sat - x_st
    dy = y_sat - y_st
    dz = z_sat - z_st
    distancia = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # Cálculo do Ângulo de Elevação (geometria esférica)
    delta_lon = lon_st_rad - lon_sat_rad
    cos_beta = math.cos(lat_rad) * math.cos(delta_lon)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    sin_beta = math.sqrt(max(0.0, 1.0 - cos_beta*cos_beta))
    
    if sin_beta < 1e-9:
        elevacao = 90.0 if cos_beta > 0 else -90.0
    else:
        elev_rad = math.atan((cos_beta - R_EARTH_KM / r_sat) / sin_beta)
        elevacao = math.degrees(elev_rad)
        
    return distancia, elevacao


def obter_coeficientes_chuva(freq_ghz: float):
    """
    Obtém os coeficientes a e b da tabela ITU-R P.838 para cálculo da atenuação por chuva
    específica (gamma = a * R^b) via interpolação logarítmica para a frequência dada em GHz.

    Parâmetros:
        freq_ghz (float): Frequência da onda portadora em GHz.

    Retorna:
        tuple[float, float]: Coeficientes (a, b) interpolados.
    """
    freqs = [4, 6, 12, 20, 30]
    a_vals = [0.00075, 0.0028, 0.024, 0.092, 0.24]
    b_vals = [1.08, 1.12, 1.15, 1.08, 0.98]
    
    if freq_ghz <= freqs[0]:
        return a_vals[0], b_vals[0]
    if freq_ghz >= freqs[-1]:
        return a_vals[-1], b_vals[-1]
    
    for i in range(len(freqs) - 1):
        if freqs[i] <= freq_ghz <= freqs[i+1]:
            t = (freq_ghz - freqs[i]) / (freqs[i+1] - freqs[i])
            log_a = math.log10(a_vals[i]) + t * (math.log10(a_vals[i+1]) - math.log10(a_vals[i]))
            a = 10**log_a
            b = b_vals[i] + t * (b_vals[i+1] - b_vals[i])
            return a, b
    return 0.024, 1.15


def calcular_perdas_dinamicas(freq_ghz: float, elevacao_deg: float, rain_rate: float = 50.0,
                             rain_prob: float = 0.01, use_atm: bool = True, use_rain: bool = True):
    """
    Calcula as atenuações dinâmicas de sinal devido à atmosfera (gases) e precipitação pluviométrica (chuva).

    Parâmetros:
        freq_ghz (float): Frequência de operação em GHz.
        elevacao_deg (float): Ângulo de elevação da antena em graus.
        rain_rate (float): Taxa de chuva em mm/h (default: 50 mm/h).
        rain_prob (float): Probabilidade de excedência do tempo no ano (ex: 0.01 = 99.99% disponibilidade).
        use_atm (bool): Habilita/desabilita atenuação atmosférica por gases.
        use_rain (bool): Habilita/desabilita atenuação por chuva.

    Retorna:
        tuple[float, float]: Perda atmosférica (dB) e Perda por chuva (dB).
    """
    elev_rad = math.radians(max(5.0, elevacao_deg))
    sin_elev = math.sin(elev_rad)
    
    # 1. Atenuação Gasosa/Atmosférica no zênite
    loss_atm = 0.0
    if use_atm:
        loss_atm = 0.15 / sin_elev
        loss_atm = min(3.0, loss_atm)  # Limite máximo de atenuação padrão para segurança
        
    # 2. Atenuação por Chuva (Modelo ITU-R P.618 simplificado)
    loss_rain = 0.0
    if use_rain:
        h_s = 1.17  # Altitude de referência da estação (km)
        h_R = 4.0   # Altura da chuva acima do nível do mar (km)
        L_s = (h_R - h_s) / sin_elev
        L_G = L_s * math.cos(elev_rad)
        
        a, b = obter_coeficientes_chuva(freq_ghz)
        gamma_001 = a * (rain_rate ** b)
        
        r_001 = 1.0 / (1.0 + 0.78 * math.sqrt(L_G * gamma_001 / freq_ghz) - 0.38 * (1.0 - math.exp(-2.0 * L_G)))
        r_001 = max(0.1, min(1.0, r_001))
        
        v_001 = 1.0 / (1.0 + math.sqrt(sin_elev) * (31.0 * math.sqrt(L_G * gamma_001) / (freq_ghz * freq_ghz) - 0.45))
        v_001 = max(0.1, min(1.0, v_001))
        
        A_001 = gamma_001 * L_s * r_001 * v_001
        
        log_p = math.log(rain_prob)
        log_a = math.log(A_001) if A_001 > 0 else -10.0
        exp = 0.655 + 0.033 * log_p - 0.045 * log_a
        exp = max(0.3, min(0.8, exp))
        
        loss_rain = A_001 * (rain_prob / 0.01) ** (-exp)
        if math.isnan(loss_rain) or loss_rain < 0:
            loss_rain = 0.0
            
    return loss_atm, loss_rain


def calcular_tudo(params: dict):
    """
    Orquestrador completo dos cálculos de Link Budget (Balanço de Potência).

    Parâmetros:
        params (dict): Dicionário contendo parâmetros do sistema (frequência, potências, ganhos, coordenadas, etc.).

    Retorna:
        dict: Dicionário detalhado com os resultados do enlace (distância, elevação, EIRP, FSPL, Prx em dBW/dBm, perdas).
    """
    freq_ghz = params.get('frequencia_ghz', 12.0)
    ptx_w = params.get('potencia_tx_w', 100.0)
    gtx_dbi = params.get('ganho_tx_dbi', 30.0)
    perdas_tx = params.get('perdas_linha_tx_db', 1.0)
    
    lat_st = params.get('lat_estacao', 0.0)
    lon_st = params.get('lon_estacao', 0.0)
    lon_sat = params.get('lon_satelite', 0.0)
    
    use_atm = params.get('use_atm', True)
    use_rain = params.get('use_rain', True)
    rain_rate = params.get('rain_rate', 50.0)
    rain_prob = params.get('rain_prob', 0.01)
    
    perda_apont = params.get('perda_apontamento_db', 0.5)
    perda_pol = params.get('perda_polarizacao_db', 0.3)
    perdas_rx = params.get('perdas_linha_rx_db', 0.5)
    grx_dbi = params.get('ganho_rx_dbi', 40.0)
    
    # 1. Distância (Slant Range) e Elevação
    distancia_km, elevacao = calcular_distancia_e_elevacao(lat_st, lon_st, lon_sat)
    
    # 2. Potência Transmitida em dBW
    ptx_dbw = 10 * math.log10(ptx_w) if ptx_w > 0 else -100.0

    # 3. Potência Isotrópica Radiada Efetiva - EIRP (dBW)
    eirp = ptx_dbw - perdas_tx + gtx_dbi

    # 4. Perda no Espaço Livre - FSPL (Free Space Path Loss em dB)
    if distancia_km > 0 and freq_ghz > 0:
        fspl = 20 * math.log10(distancia_km) + 20 * math.log10(freq_ghz) + 92.45
    else:
        fspl = 0.0

    # 5. Perdas dinâmicas (Atmosfera, Chuva, Apontamento, Polarização, Linhas)
    loss_atm, loss_rain = calcular_perdas_dinamicas(freq_ghz, elevacao, rain_rate, rain_prob, use_atm, use_rain)
    outras_perdas = loss_atm + loss_rain + perda_apont + perda_pol + perdas_rx

    # 6. Potência Recebida (dBW e dBm)
    pot_recebida_dbw = eirp - fspl - outras_perdas + grx_dbi
    pot_recebida_dbm = pot_recebida_dbw + 30.0

    return {
        "distancia_km": round(distancia_km, 2),
        "elevacao_deg": round(elevacao, 2),
        "eirp": round(eirp, 2),
        "fspl": round(fspl, 2),
        "outras_perdas": round(outras_perdas, 2),
        "potencia_recebida_dbw": round(pot_recebida_dbw, 2),
        "potencia_recebida_dbm": round(pot_recebida_dbm, 2),
        "perda_atmosferica_db": round(loss_atm, 2),
        "perda_chuva_db": round(loss_rain, 2)
    }
