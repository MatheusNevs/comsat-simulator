"""
Módulo de Modulação Digital e Desempenho de BER (core/modulation.py)

Implementa o cálculo teórico da Taxa de Erro de Bit (BER - Bit Error Rate) e Eb/N0
para esquemas de modulação digital utilizados em redes de comunicação via satélite
(BPSK, QPSK, 8PSK, 16QAM).
"""

import math


def erfc(x: float) -> float:
    """
    Calcula a Função de Erro Complementar (erfc) aproximada via polinômios de Chebyshev
    de alta precisão, evitando dependência de bibliotecas externas pesadas como scipy.

    Parâmetros:
        x (float): Valor de entrada real.

    Retorna:
        float: Valor de erfc(x) no intervalo [0, 2].
    """
    try:
        t = 1.0 / (1.0 + 0.5 * abs(x))
        # Aproximação polinomial de Chebyshev
        ans = t * math.exp(-x*x - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 +
                  t * (-0.18628806 + t * 0.27886807 + t * (-1.13520398 + t * 1.48851587 +
                  t * (-0.82215223 + t * 0.17087277)))))))
        return ans if x >= 0 else 2.0 - ans
    except OverflowError:
        return 0.0 if x >= 0 else 2.0


def calcular_ber(eb_n0_db: float, mod_type: str) -> float:
    """
    Calcula a Taxa de Erro de Bit (BER - Bit Error Rate) teórica para o esquema de modulação
    digital selecionado em função da relação Eb/N0 em dB.

    Parâmetros:
        eb_n0_db (float): Relação Energia de Bit por Densidade de Ruído (Eb/N0) em dB.
        mod_type (str): Tipo de modulação ('BPSK', 'QPSK', '8PSK', '16QAM').

    Retorna:
        float: Taxa de Erro de Bit (BER) teórica.

    Exceções:
        ValueError: Caso a modulação informada não seja suportada.
    """
    eb_n0_lin = 10 ** (eb_n0_db / 10.0)
    
    if mod_type in ['BPSK', 'QPSK']:
        # BER = 0.5 * erfc(sqrt(Eb/N0))
        return 0.5 * erfc(math.sqrt(eb_n0_lin))
    elif mod_type == '8PSK':
        # BER ~ (1/3) * erfc(sqrt(3 * Eb/N0) * sin(pi/8))
        return (1.0 / 3.0) * erfc(math.sqrt(3.0 * eb_n0_lin) * math.sin(math.pi / 8.0))
    elif mod_type == '16QAM':
        # BER ~ (3/8) * erfc(sqrt(0.4 * Eb/N0))
        return 0.375 * erfc(math.sqrt(0.4 * eb_n0_lin))
    else:
        raise ValueError(f"Modulação não suportada: {mod_type}")


def calcular_eb_n0(c_n0_db_hz: float, bit_rate_mbps: float) -> float:
    """
    Calcula a relação Eb/N0 (dB) a partir da relação Portadora/Densidade de Ruído (C/N0 em dB-Hz)
    e da taxa de transmissão de bits (Rb em Mbps).

    Equação:
        Eb/N0 (dB) = C/N0 (dB-Hz) - 10 * log10(Rb_bps)

    Parâmetros:
        c_n0_db_hz (float): Relação C/N0 em dB-Hz.
        bit_rate_mbps (float): Taxa de transmissão de dados em Megabits por segundo (Mbps).

    Retorna:
        float: Relação Eb/N0 em dB.
    """
    bit_rate_bps = bit_rate_mbps * 1e6
    if bit_rate_bps > 0:
        return c_n0_db_hz - 10 * math.log10(bit_rate_bps)
    return -99.0
