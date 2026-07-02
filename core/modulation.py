import math

def erfc(x):
    """
    Função de erro complementar aproximada para evitar dependência do scipy.
    """
    # Aproximação de alta precisão
    try:
        t = 1.0 / (1.0 + 0.5 * abs(x))
        # Coeficientes Chebyshev
        ans = t * math.exp(-x*x - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 +
                  t * (-0.18628806 + t * 0.27886807 + t * (-1.13520398 + t * 1.48851587 +
                  t * (-0.82215223 + t * 0.17087277)))))))
        return ans if x >= 0 else 2.0 - ans
    except OverflowError:
        return 0.0 if x >= 0 else 2.0

def calcular_ber(eb_n0_db, mod_type):
    """
    Calcula a Taxa de Erro de Bit (BER) teórica para diferentes modulações digitais.
    eb_n0_db: Eb/N0 em dB
    mod_type: 'BPSK', 'QPSK', '8PSK', '16QAM'
    """
    eb_n0_lin = 10 ** (eb_n0_db / 10.0)
    
    if mod_type in ['BPSK', 'QPSK']:
        # BER = 0.5 * erfc(sqrt(Eb/N0))
        return 0.5 * erfc(math.sqrt(eb_n0_lin))
    elif mod_type == '8PSK':
        # BER ~ 1/3 * erfc(sqrt(3 * Eb/N0) * sin(pi/8))
        return (1.0 / 3.0) * erfc(math.sqrt(3.0 * eb_n0_lin) * math.sin(math.pi / 8.0))
    elif mod_type == '16QAM':
        # BER ~ 3/8 * erfc(sqrt(0.4 * Eb/N0))
        return 0.375 * erfc(math.sqrt(0.4 * eb_n0_lin))
    else:
        raise ValueError(f"Modulação não suportada: {mod_type}")

def calcular_eb_n0(c_n0_db_hz, bit_rate_mbps):
    """
    Calcula Eb/N0 (dB) a partir de C/N0 e da Taxa de Bits (Mbps).
    Eb/N0 = C/N0 - 10*log10(Rb)
    """
    bit_rate_bps = bit_rate_mbps * 1e6
    if bit_rate_bps > 0:
        return c_n0_db_hz - 10 * math.log10(bit_rate_bps)
    return -99.0
