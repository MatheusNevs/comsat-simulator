import io
import math
from fpdf import FPDF
from core.link_budget import calcular_distancia_e_elevacao, R_EARTH_KM, GEO_ALTITUDE_KM
from core.noise import calcular_temperatura_sistema, calcular_gt_e_ruido
from core.modulation import calcular_ber, calcular_eb_n0, erfc

def obter_ganho_real_sat(sat, off_axis_angle):
    peak = sat.tx_gain_dbi
    if sat.pattern_type == "Isotrópica" or not sat.pattern_type:
        return peak, 0.0
    elif sat.pattern_type == "Modelo Parabólico":
        hpbw = sat.pattern_hpbw
        att = -12.0 * ((off_axis_angle / hpbw) ** 2) if hpbw > 0 else 0.0
        att = max(-40.0, att)
        return peak + att, att
    elif sat.pattern_type == "CSV" and sat.pattern_data:
        data = sat.pattern_data
        if not data:
            return peak, 0.0
        if off_axis_angle <= data[0][0]:
            return peak + data[0][1], data[0][1]
        if off_axis_angle >= data[-1][0]:
            return peak + data[-1][1], data[-1][1]
        for i in range(len(data) - 1):
            if data[i][0] <= off_axis_angle <= data[i+1][0]:
                t = (off_axis_angle - data[i][0]) / (data[i+1][0] - data[i][0])
                att = data[i][1] + t * (data[i+1][1] - data[i][1])
                return peak + att, att
    return peak, 0.0

class ComSatReportPDF(FPDF):
    def header(self):
        # Draw header band
        self.set_fill_color(14, 28, 56) # Deep blue/grey
        self.rect(0, 0, 210, 28, "F")
        
        self.set_y(5)
        self.set_text_color(137, 220, 235) # Neon light blue
        self.set_font("helvetica", "B", 14)
        self.cell(0, 8, "COMSAT SIMULATOR - RELATORIO TECNICO DE ENLACE", align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_text_color(200, 200, 200)
        self.set_font("helvetica", "I", 9)
        self.cell(0, 5, "Calculos de Balanco de Potencia, Ruido e Desempenho de Downlink", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def draw_section_header(self, title):
        self.ln(4)
        self.set_font("helvetica", "B", 11)
        self.set_text_color(14, 28, 56)
        self.cell(0, 6, title, border="B", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def draw_key_value_row(self, items, widths):
        self.set_font("helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        
        # Calculate max height
        max_h = 5
        
        # Draw cells
        for i, (key, val) in enumerate(items):
            w = widths[i]
            # Key
            self.set_font("helvetica", "", 8.5)
            self.set_text_color(100, 100, 100)
            self.cell(w * 0.55, max_h, f"{key}: ", border=0)
            
            # Value
            self.set_font("helvetica", "B", 9)
            self.set_text_color(20, 20, 20)
            self.cell(w * 0.45, max_h, str(val), border=0)
        
        self.ln(max_h + 1)

    def draw_ber_chart(self, x, y, w, h, active_ebn0, active_ber, active_mod):
        # Draw background and border
        self.set_fill_color(245, 248, 252)
        self.rect(x, y, w, h, "F")
        self.set_draw_color(30, 95, 138)
        self.set_line_width(0.3)
        self.rect(x, y, w, h, "D")
        
        # Grid lines horizontal (decades 10^0 to 10^-8)
        self.set_font("helvetica", "", 7)
        self.set_text_color(80, 80, 80)
        for log_y in range(0, -9, -1):
            py = y + (log_y / -8.0) * h
            self.set_draw_color(210, 220, 230)
            self.line(x, py, x + w, py)
            
            # Decades label
            lbl = "1" if log_y == 0 else f"10^-{abs(log_y)}"
            self.text(x - 11, py + 1.5, lbl)
            
        # Grid lines vertical (Eb/N0 in dB)
        for db in range(0, 17, 2):
            px = x + (db / 16.0) * w
            self.line(px, y, px, y + h)
            self.text(px - 1.5, y + h + 4.0, f"{db}")
            
        # Axis label
        self.set_font("helvetica", "B", 7)
        self.set_text_color(50, 50, 50)
        self.text(x + w/2 - 8, y + h + 9.5, "Eb/N0 (dB)")
        
        # Curves
        mods = ['BPSK', '8PSK', '16QAM']
        colors = {
            'BPSK': (0, 120, 200),    # Blue
            '8PSK': (220, 150, 0),    # Yellow/Orange
            '16QAM': (0, 140, 70)     # Green
        }
        
        # Helper logic to compute curves
        def compute_ber(eb_n0_db, mod):
            eb_n0_lin = 10 ** (eb_n0_db / 10.0)
            if mod in ['BPSK', 'QPSK']:
                return 0.5 * erfc(math.sqrt(eb_n0_lin))
            elif mod == '8PSK':
                return (1.0 / 3.0) * erfc(math.sqrt(3.0 * eb_n0_lin) * math.sin(math.pi / 8.0))
            elif mod == '16QAM':
                return 0.375 * erfc(math.sqrt(0.4 * eb_n0_lin))
            return 0.0

        for mod in mods:
            self.set_draw_color(*colors[mod])
            is_active = (active_mod == mod or (active_mod == 'QPSK' and mod == 'BPSK'))
            self.set_line_width(0.7 if is_active else 0.25)
            
            last_px, last_py = None, None
            for i in range(33):
                db = (i / 32.0) * 16.0
                ber_val = compute_ber(db, mod)
                px = x + (db / 16.0) * w
                
                log_ber = math.log10(ber_val) if ber_val > 0 else -8.0
                log_ber = max(-8.0, min(0.0, log_ber))
                py = y + (log_ber / -8.0) * h
                
                if last_px is not None:
                    self.line(last_px, last_py, px, py)
                last_px, last_py = px, py
                
        # Draw active operating point
        px_active = x + (active_ebn0 / 16.0) * w
        log_ber_active = math.log10(active_ber) if active_ber > 0 else -8.0
        log_ber_active = max(-8.0, min(0.0, log_ber_active))
        py_active = y + (log_ber_active / -8.0) * h
        
        # Pink/red active point dot
        self.set_fill_color(243, 100, 120)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.4)
        self.circle(px_active - 1.8, py_active - 1.8, 3.6, "FD")
        
        # Draw Legend inside chart area
        self.set_font("helvetica", "", 6)
        self.set_text_color(40, 40, 40)
        
        # BPSK
        self.set_fill_color(*colors['BPSK'])
        self.rect(x + 4, y + 4, 3, 2.2, "F")
        self.text(x + 8, y + 6, "BPSK/QPSK")
        
        # 8PSK
        self.set_fill_color(*colors['8PSK'])
        self.rect(x + 40, y + 4, 3, 2.2, "F")
        self.text(x + 44, y + 6, "8PSK")
        
        # 16QAM
        self.set_fill_color(*colors['16QAM'])
        self.rect(x + 70, y + 4, 3, 2.2, "F")
        self.text(x + 74, y + 6, "16QAM")
        
        # LINK OP
        self.set_fill_color(243, 100, 120)
        self.circle(x + 105, y + 4.8, 1.4, "F")
        self.set_font("helvetica", "B", 6)
        self.text(x + 108, y + 6, "LINK OP")


def gerar_pdf_report_bytes(sat, stn, bw_mhz, rb_mbps, mod_type):
    """
    Gera o relatório técnico PDF com todas as contas de enlace e o gráfico de BER
    utilizando a biblioteca fpdf2 e salvando-o em um buffer de memória bytes.
    """
    # ── 1. Cálculos de Enlace no Backend Python ──
    # A. Geometria e Apontamento
    distancia_km, elevacao = calcular_distancia_e_elevacao(stn.latitude_deg, stn.longitude_deg, sat.longitude_deg)
    
    # Off-Axis Ângulo do Satélite (Nadir pointing)
    Re = R_EARTH_KM
    Rsat = Re + GEO_ALTITUDE_KM
    lat_rad = math.radians(stn.latitude_deg)
    delta_lon = math.radians(stn.longitude_deg - sat.longitude_deg)
    cos_beta = math.cos(lat_rad) * math.cos(delta_lon)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    
    cos_theta = (Rsat - Re * cos_beta) / distancia_km if distancia_km > 0 else 1.0
    cos_theta = max(-1.0, min(1.0, cos_theta))
    off_axis = math.degrees(math.acos(cos_theta))
    
    # B. Ganhos e Perdas de Antena
    sat_gain_real, sat_att = obter_ganho_real_sat(sat, off_axis)
    ptx_dbw = 10 * math.log10(sat.tx_power_w) if sat.tx_power_w > 0 else 0.0
    
    LOSS_TX_LINE = 1.0
    LOSS_ATM = 0.5
    LOSS_RAIN = 1.5
    LOSS_POINT = 0.5
    LOSS_POL = 0.3
    LOSS_RX_LINE = 0.5
    
    eirp = ptx_dbw - LOSS_TX_LINE + sat_gain_real
    fspl = 20 * math.log10(distancia_km) + 20 * math.log10(sat.frequency_ghz) + 92.45
    total_losses = LOSS_ATM + LOSS_RAIN + LOSS_POINT + LOSS_POL + LOSS_RX_LINE
    prx_dbw = eirp - fspl - total_losses + stn.rx_gain_dbi
    prx_dbm = prx_dbw + 30.0
    
    # C. Ruído e Friis
    g_lna_lin = 10 ** (stn.gain_lna_db / 10.0)
    f_rec = 10 ** (stn.nf_rec_db / 10.0)
    t_rec_k = 290.0 * (f_rec - 1.0)
    t_eff = stn.temp_lna_k + (stn.temp_down_k / g_lna_lin) + (t_rec_k / g_lna_lin)
    t_sys = stn.temp_antenna_k + t_eff
    
    gt = stn.rx_gain_dbi - 10 * math.log10(t_sys)
    K_DB = -228.6
    n0 = K_DB + 10 * math.log10(t_sys)
    cn0 = prx_dbw - n0
    cn = cn0 - 10 * math.log10(bw_mhz * 1e6)
    
    # D. Modulação e BER
    ebn0 = cn0 - 10 * math.log10(rb_mbps * 1e6)
    ber = calcular_ber(ebn0, mod_type)
    
    # Margem de Link (Target BER 10^-6)
    ebn0_req = 10.5
    if mod_type == '8PSK':
        ebn0_req = 14.0
    elif mod_type == '16QAM':
        ebn0_req = 14.5
    margem = ebn0 - ebn0_req

    # ── 2. Inicialização do PDF ──
    pdf = ComSatReportPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ── Seção 1: Informações Gerais do Enlace ──
    pdf.draw_section_header("1. INFORMACOES GERAIS")
    pdf.draw_key_value_row([
        ("Satelite", sat.name),
        ("Tipo de Orbita", sat.orbit_type),
        ("Longitude Orbital", f"{sat.longitude_deg}°")
    ], [60, 60, 60])
    
    pdf.draw_key_value_row([
        ("Estacao Terrena", stn.name),
        ("Latitude Est.", f"{stn.latitude_deg:.4f}°"),
        ("Longitude Est.", f"{stn.longitude_deg:.4f}°")
    ], [60, 60, 60])
    
    # ── Seção 2: Geometria e Apontamento ──
    pdf.draw_section_header("2. GEOMETRIA E APONTAMENTO")
    pdf.draw_key_value_row([
        ("Distancia (Slant Range)", f"{distancia_km:.2f} km"),
        ("Angulo de Elevacao", f"{elevacao:.2f}°"),
        ("Off-Axis (Apontamento)", f"{off_axis:.2f}°")
    ], [60, 60, 60])
    
    # ── Seção 3: Balanço de Potência (Link Budget) ──
    pdf.draw_section_header("3. BALANCO DE POTENCIA (LINK BUDGET)")
    pdf.draw_key_value_row([
        ("Potencia do HPA", f"{ptx_dbw:.1f} dBW ({sat.tx_power_w:.1f} W)"),
        ("Ganho Antena Sat", f"{sat_gain_real:.1f} dBi ({sat_att:.1f} dB at.)"),
        ("EIRP do Satelite", f"{eirp:.2f} dBW")
    ], [60, 60, 60])
    
    pdf.draw_key_value_row([
        ("Atenuacao por FSPL", f"{fspl:.2f} dB"),
        ("Outras Perdas (Atmos/Chuva)", f"{total_losses:.2f} dB"),
        ("Ganho Antena Receptor", f"{stn.rx_gain_dbi:.2f} dBi")
    ], [60, 60, 60])
    
    pdf.draw_key_value_row([
        ("Potencia Recebida (Prx)", f"{prx_dbw:.2f} dBW ({prx_dbm:.2f} dBm)"),
        ("Meta de BER do Projeto", "10^-6"),
        ("Margem de Link", f"{margem:+.2f} dB ({'Aprovado' if margem >= 0 else 'Falhou'})")
    ], [60, 60, 60])
    
    # ── Seção 4: Análise de Ruído (Friis) ──
    pdf.draw_section_header("4. ANALISE DE RUIDO E TEMPERATURA")
    pdf.draw_key_value_row([
        ("Temp. Ruido Antena", f"{stn.temp_antenna_k:.1f} K"),
        ("Temp. Ef. Receptor", f"{t_eff:.1f} K"),
        ("Temp. do Sistema (Tsys)", f"{t_sys:.1f} K")
    ], [60, 60, 60])
    
    pdf.draw_key_value_row([
        ("Figura de Merito G/T", f"{gt:.2f} dB/K"),
        ("Banda do Canal", f"{bw_mhz:.1f} MHz"),
        ("Relação C/N no Canal", f"{cn:.2f} dB")
    ], [60, 60, 60])
    
    # Tabela de Cascata de Ruído no PDF
    pdf.ln(1)
    pdf.set_font("helvetica", "B", 8)
    pdf.set_fill_color(225, 235, 245)
    pdf.set_text_color(14, 28, 56)
    
    # Table Header
    pdf.cell(50, 5, "Estagio Cascata (Friis)", border=1, fill=True)
    pdf.cell(40, 5, "Temperatura Estagio (K)", border=1, fill=True, align="R")
    pdf.cell(40, 5, "Ganho Estagio (dB)", border=1, fill=True, align="R")
    pdf.cell(50, 5, "Contribuicao para Tsys (K)", border=1, fill=True, align="R")
    pdf.ln(5)
    
    # Row 1
    pdf.set_font("helvetica", "", 8)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(50, 4.5, "Antena Receptora", border=1)
    pdf.cell(40, 4.5, f"{stn.temp_antenna_k:.1f}", border=1, align="R")
    pdf.cell(40, 4.5, "-", border=1, align="R")
    pdf.cell(50, 4.5, f"{stn.temp_antenna_k:.1f}", border=1, align="R")
    pdf.ln(4.5)
    
    # Row 2
    pdf.cell(50, 4.5, "Amplificador LNA", border=1)
    pdf.cell(40, 4.5, f"{stn.temp_lna_k:.1f}", border=1, align="R")
    pdf.cell(40, 4.5, f"{stn.gain_lna_db:.1f}", border=1, align="R")
    pdf.cell(50, 4.5, f"{stn.temp_lna_k:.1f}", border=1, align="R")
    pdf.ln(4.5)
    
    # Row 3
    pdf.cell(50, 4.5, "Estagios Seguintes (Rec/Mixer)", border=1)
    pdf.cell(40, 4.5, f"{(t_rec_k + stn.temp_down_k):.1f}", border=1, align="R")
    pdf.cell(40, 4.5, "-", border=1, align="R")
    pdf.cell(50, 4.5, f"{(t_eff - stn.temp_lna_k):.3f}", border=1, align="R")
    pdf.ln(6)
    
    # ── Seção 5: Desempenho do Canal e BER ──
    pdf.draw_section_header("5. DESEMPENHO E CURVAS DE BER")
    pdf.draw_key_value_row([
        ("Taxa de Dados (Rb)", f"{rb_mbps:.1f} Mbps"),
        ("Esquema de Modulacao", mod_type),
        ("Eb/N0 Recebido", f"{ebn0:.2f} dB")
    ], [60, 60, 60])
    
    pdf.draw_key_value_row([
        ("Eb/N0 Minimo Requerido", f"{ebn0_req:.1f} dB"),
        ("BER Estimado", f"{ber:.2e}"),
        ("Status de Qualidade", "ADEQUADO" if margem >= 0 else "INADEQUADO")
    ], [60, 60, 60])
    
    # Desenhar o gráfico de curvas de BER vetorizado nativo
    pdf.ln(3)
    pdf.draw_ber_chart(35, pdf.get_y(), 140, 75, ebn0, ber, mod_type)
    
    # Salva em buffer de bytes para download imediato
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.getvalue()
