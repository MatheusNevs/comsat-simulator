import math

def calcular_temperatura_sistema(t_antena_k, t_lna_k, g_lna_db, t_down_k, nf_rec_db):
    """
    Calcula a temperatura de ruído efetiva do receptor e a temperatura do sistema (Tsys)
    usando a fórmula de cascata de Friis.
    """
    # Converter ganhos de dB para linear
    g_lna_lin = 10 ** (g_lna_db / 10.0)
    
    # Calcular temperatura de ruído do receiver a partir da figura de ruído (NF)
    # T = T0 * (F - 1) onde T0 = 290 K
    f_rec = 10 ** (nf_rec_db / 10.0)
    t_rec_k = 290.0 * (f_rec - 1.0)
    
    # Temperatura efetiva do receptor na entrada do LNA
    # Teff = T_LNA + T_down/G_LNA + T_rec/(G_LNA * G_down)
    # Para simplificar (e assumindo que G_down não afeta significativamente devido ao alto ganho do LNA):
    t_rec_efetiva = t_lna_k + (t_down_k / g_lna_lin) + (t_rec_k / g_lna_lin)
    
    # Temperatura do sistema (Tsys)
    t_sistema = t_antena_k + t_rec_efetiva
    
    return t_rec_efetiva, t_sistema

def calcular_gt_e_ruido(ganho_rx_dbi, t_sistema_k, bandwidth_mhz, pot_recebida_dbw):
    """
    Calcula G/T, densidade de ruído N0, C/N0 e C/N do enlace.
    """
    # G/T da estação terrena (dB/K)
    g_t = ganho_rx_dbi - 10 * math.log10(t_sistema_k) if t_sistema_k > 0 else -99.0
    
    # Constante de Boltzmann em dBW/(Hz K)
    K_DB = -228.6
    
    # Densidade espectral de ruído N0 (dBW/Hz)
    n0 = K_DB + 10 * math.log10(t_sistema_k) if t_sistema_k > 0 else -228.6
    
    # C/N0 (Carrier-to-Noise density ratio) in dB-Hz
    c_n0 = pot_recebida_dbw - n0
    
    # C/N (Carrier-to-Noise ratio) in dB para a largura de banda especificada
    bandwidth_hz = bandwidth_mhz * 1e6
    if bandwidth_hz > 0:
        c_n = c_n0 - 10 * math.log10(bandwidth_hz)
    else:
        c_n = 0.0
        
    return {
        "g_t": round(g_t, 2),
        "n0": round(n0, 2),
        "c_n0": round(c_n0, 2),
        "c_n": round(c_n, 2)
    }
