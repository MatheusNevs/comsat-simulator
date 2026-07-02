import math

R_EARTH_KM = 6371.0
GEO_ALTITUDE_KM = 35786.0

def calcular_distancia_e_elevacao(lat_st, lon_st, lon_sat, alt_sat_km=GEO_ALTITUDE_KM):
    """
    Calcula a distância 3D (slant range) e o ângulo de elevação da estação para o satélite GEO.
    """
    r_sat = R_EARTH_KM + alt_sat_km
    
    lat_rad = math.radians(lat_st)
    lon_st_rad = math.radians(lon_st)
    lon_sat_rad = math.radians(lon_sat)
    
    # Cartesianas
    x_st = R_EARTH_KM * math.cos(lat_rad) * math.cos(lon_st_rad)
    y_st = R_EARTH_KM * math.cos(lat_rad) * math.sin(lon_st_rad)
    z_st = R_EARTH_KM * math.sin(lat_rad)
    
    x_sat = r_sat * math.cos(lon_sat_rad)
    y_sat = r_sat * math.sin(lon_sat_rad)
    z_sat = 0.0
    
    dx = x_sat - x_st
    dy = y_sat - y_st
    dz = z_sat - z_st
    distancia = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # Ângulo de Elevação (de acordo com a geometria esférica)
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

def calcular_tudo(params):
    """
    Orquestra os cálculos do Link Budget.
    """
    freq_ghz = params.get('frequencia_ghz', 12.0)
    ptx_w = params.get('potencia_tx_w', 100.0)
    gtx_dbi = params.get('ganho_tx_dbi', 30.0)
    perdas_tx = params.get('perdas_linha_tx_db', 1.0)
    
    lat_st = params.get('lat_estacao', 0.0)
    lon_st = params.get('lon_estacao', 0.0)
    lon_sat = params.get('lon_satelite', 0.0)
    
    perda_atmos = params.get('perda_atmosferica_db', 0.5)
    perda_chuva = params.get('perda_chuva_db', 1.5)
    perda_apont = params.get('perda_apontamento_db', 0.5)
    perda_pol = params.get('perda_polarizacao_db', 0.3)
    perdas_rx = params.get('perdas_linha_rx_db', 0.5)
    grx_dbi = params.get('ganho_rx_dbi', 40.0)
    
    # 1. Distância e Elevação
    distancia_km, elevacao = calcular_distancia_e_elevacao(lat_st, lon_st, lon_sat)
    
    # 2. Potência em dBW
    ptx_dbw = 10 * math.log10(ptx_w) if ptx_w > 0 else -100.0

    # 3. EIRP (dBW)
    eirp = ptx_dbw - perdas_tx + gtx_dbi

    # 4. FSPL (Free Space Path Loss) em dB
    if distancia_km > 0 and freq_ghz > 0:
        fspl = 20 * math.log10(distancia_km) + 20 * math.log10(freq_ghz) + 92.45
    else:
        fspl = 0.0

    # 5. Soma de outras perdas
    outras_perdas = perda_atmos + perda_chuva + perda_apont + perda_pol + perdas_rx

    # 6. Potência Recebida (dBW)
    pot_recebida_dbw = eirp - fspl - outras_perdas + grx_dbi
    pot_recebida_dbm = pot_recebida_dbw + 30

    return {
        "distancia_km": round(distancia_km, 2),
        "elevacao_deg": round(elevacao, 2),
        "eirp": round(eirp, 2),
        "fspl": round(fspl, 2),
        "outras_perdas": round(outras_perdas, 2),
        "potencia_recebida_dbw": round(pot_recebida_dbw, 2),
        "potencia_recebida_dbm": round(pot_recebida_dbm, 2)
    }
