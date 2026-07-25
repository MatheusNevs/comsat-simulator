"""
Módulo de Análise de Ruído e Temperatura de Sistema (core/noise.py)

Implementa a Equação de Cascata de Friis para receptores RF de telecomunicações via satélite:
- Temperatura de ruído efetiva do receptor (Teff)
- Temperatura de ruído total do sistema (Tsys)
- Figura de Mérito (G/T) da estação recepção em dB/K
- Densidade espectral de ruído N0 em dBW/Hz
- Relação Portadora/Ruído (C/N) e Portadora/Densidade de Ruído (C/N0)
"""

import math


def calcular_temperatura_sistema(t_antena_k: float, t_lna_k: float, g_lna_db: float,
                                 t_down_k: float, nf_rec_db: float):
    """
    Calcula a temperatura de ruído efetiva do receptor e a temperatura total do sistema (Tsys)
    usando a Fórmula de Cascata de Friis para múltiplos estágios em série.

    Fórmula:
        Trec_k = T0 * (F - 1)  (onde T0 = 290 K, F = 10^(NF/10))
        Teff = T_LNA + (T_down / G_LNA) + (Trec / G_LNA)
        Tsys = T_antena + Teff

    Parâmetros:
        t_antena_k (float): Temperatura de ruído da antena receptora (Kelvin).
        t_lna_k (float): Temperatura equivalente de ruído do LNA (Kelvin).
        g_lna_db (float): Ganho de potência do LNA em dB.
        t_down_k (float): Temperatura de ruído do Downconverter / Mixer (Kelvin).
        nf_rec_db (float): Figura de ruído (Noise Figure - NF) do receptor em dB.

    Retorna:
        tuple[float, float]:
            - t_rec_efetiva (float): Temperatura efetiva do receptor referenciada à entrada (K).
            - t_sistema (float): Temperatura total do sistema Tsys (K).
    """
    # Conversão do ganho do LNA de dB para escala linear
    g_lna_lin = 10 ** (g_lna_db / 10.0)
    
    # Converte Figura de Ruído (NF) em Fator de Ruído (F) e calcula a Temperatura do Demodulador
    # T = T0 * (F - 1), onde T0 = 290 K (temperatura de referência padrão IEEE)
    f_rec = 10 ** (nf_rec_db / 10.0)
    t_rec_k = 290.0 * (f_rec - 1.0)
    
    # Temperatura efetiva de ruído referenciada à entrada do LNA (Cascata de Friis)
    t_rec_efetiva = t_lna_k + (t_down_k / g_lna_lin) + (t_rec_k / g_lna_lin)
    
    # Temperatura total de ruído do sistema (Tsys = Tantena + Teff)
    t_sistema = t_antena_k + t_rec_efetiva
    
    return t_rec_efetiva, t_sistema


def calcular_gt_e_ruido(ganho_rx_dbi: float, t_sistema_k: float, bandwidth_mhz: float, pot_recebida_dbw: float):
    """
    Calcula a Figura de Mérito (G/T), a densidade espectral de ruído (N0), C/N0 e a relação C/N.

    Constante de Boltzmann: k = 1.38e-23 J/K => 10 * log10(k) = -228.6 dBW/(Hz K)

    Parâmetros:
        ganho_rx_dbi (float): Ganho da antena receptora em dBi.
        t_sistema_k (float): Temperatura total do sistema (Tsys) em Kelvin.
        bandwidth_mhz (float): Largura de banda do canal em MHz.
        pot_recebida_dbw (float): Potência do sinal recebido em dBW.

    Retorna:
        dict:
            - "g_t" (float): Figura de Mérito G/T em dB/K.
            - "n0" (float): Densidade de ruído N0 em dBW/Hz.
            - "c_n0" (float): Relação C/N0 em dB-Hz.
            - "c_n" (float): Relação C/N da portadora na banda do canal em dB.
    """
    # G/T da estação terrena (dB/K)
    g_t = ganho_rx_dbi - 10 * math.log10(t_sistema_k) if t_sistema_k > 0 else -99.0
    
    # Constante de Boltzmann em dBW/(Hz K)
    K_DB = -228.6
    
    # Densidade espectral de ruído N0 (dBW/Hz) -> N0 = k * Tsys
    n0 = K_DB + 10 * math.log10(t_sistema_k) if t_sistema_k > 0 else -228.6
    
    # C/N0 (Carrier-to-Noise density ratio) em dB-Hz
    c_n0 = pot_recebida_dbw - n0
    
    # C/N (Carrier-to-Noise ratio) em dB para a largura de banda (B em Hz)
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
