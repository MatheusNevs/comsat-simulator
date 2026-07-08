import json

GEO_ALT = 0.6  # altitude relativa no globe.gl (0 = superfície, 1 = raio acima)


def _satellites_json(satellites):
    return json.dumps([{
        "id": i,
        "name": s.name,
        "lat": 0.0,
        "lng": s.longitude_deg,
        "alt": GEO_ALT,
        "kind": "satellite",
        "orbit": s.orbit_type,
        "tx_power": s.tx_power_w,
        "tx_gain": s.tx_gain_dbi,
        "frequency": s.frequency_ghz,
        "pattern_type": s.pattern_type,
        "pattern_hpbw": s.pattern_hpbw,
        "pattern_data": s.pattern_data,
        "tx_line_loss": s.tx_line_loss_db,
        
        # Uplink/Rx Parameters
        "rx_frequency": s.rx_frequency_ghz,
        "rx_gain": s.rx_gain_dbi,
        "rx_line_loss": s.rx_line_loss_db,
        "sat_temp_antenna": s.sat_temp_antenna_k,
        "sat_temp_lna": s.sat_temp_lna_k,
        "sat_gain_lna": s.sat_gain_lna_db,
        "sat_temp_down": s.sat_temp_down_k,
        "sat_nf_rec": s.sat_nf_rec_db
    } for i, s in enumerate(satellites)])


def _stations_json(stations):
    return json.dumps([{
        "id": i,
        "name": s.name,
        "lat": s.latitude_deg,
        "lng": s.longitude_deg,
        "alt": 0.0,
        "kind": "station",
        "rx_gain": s.rx_gain_dbi,
        "gain_mode": s.gain_mode,
        "antenna_diameter": s.antenna_diameter_m,
        "antenna_efficiency": s.antenna_efficiency_pct,
        
        # Ruído do Terminal
        "temp_antenna": s.temp_antenna_k,
        "temp_lna": s.temp_lna_k,
        "gain_lna": s.gain_lna_db,
        "temp_down": s.temp_down_k,
        "nf_rec": s.nf_rec_db,
        
        # Transmissão (Uplink)
        "tx_power": s.tx_power_w,
        "tx_gain": s.tx_gain_dbi,
        "tx_line_loss": s.tx_line_loss_db
    } for i, s in enumerate(stations)])


def _links_json(satellites, stations):
    links = []
    for station in stations:
        if not satellites:
            break
        nearest = min(satellites, key=lambda s: abs(s.longitude_deg - station.longitude_deg))
        links.append({
            "path": [[0.0, nearest.longitude_deg, GEO_ALT],
                     [station.latitude_deg, station.longitude_deg, 0.0]],
            "color": "#00ff88", "isNadir": False, "isOrbit": False,
            "label": station.name + " -> " + nearest.name
        })
    return json.dumps(links)


def _orbit_json():
    points = [[0, lon, GEO_ALT] for lon in range(-180, 185, 5)]
    return json.dumps([{
        "path": points, "color": "rgba(255, 210, 60, 0.85)",
        "isOrbit": True, "isNadir": False
    }])


def render_globe_html(satellites, stations, height=900):
    sats_j  = _satellites_json(satellites)
    stns_j  = _stations_json(stations)
    lnks_j  = _links_json(satellites, stations)
    orbit_j = _orbit_json()

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:100%; height:100%; background:#000011; overflow:hidden; font-family:'Segoe UI',system-ui,sans-serif; }}
#globeViz {{ position:absolute; top:0; left:0; width:100%; height:100%; }}

/* ── Info / Edit Panel ── */
#infoPanel {{
  display:none; position:absolute; top:16px; left:16px; width:310px;
  background:rgba(6,12,24,0.96); color:#cdd6f4; border-radius:12px;
  border:1px solid #1e5f8a; box-shadow:0 4px 30px rgba(0,180,255,0.22);
  z-index:200; overflow:hidden;
}}
#infoPanelHead {{
  background:rgba(14,28,56,0.98); padding:12px 15px;
  display:flex; justify-content:space-between; align-items:center;
  border-bottom:1px solid #1e5f8a;
}}
#infoPanelHead h3 {{ font-size:13px; color:#89dceb; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:240px; }}
#closeInfo {{ background:transparent; border:none; color:#6c7086; cursor:pointer; font-size:20px; line-height:1; }}
#closeInfo:hover {{ color:#fff; }}
#infoBody {{ padding:15px; font-size:12px; max-height:550px; overflow-y:auto; }}
.field {{ margin-bottom:10px; }}
.field label {{ display:flex; align-items:center; color:#7a9cc0; font-size:10px; margin-bottom:3px; text-transform:uppercase; letter-spacing:0.5px; }}
.field input, .field select {{ width:100%; background:rgba(20,40,80,0.65); border:1px solid #1e5f8a; border-radius:5px; color:#cdd6f4; font-size:12.5px; padding:6px 9px; transition:border-color .15s; outline:none; }}
.field input:focus, .field select:focus {{ border-color:#89dceb; background:rgba(30,60,120,0.8); }}
.save-btn {{ width:100%; margin-top:12px; background:rgba(0,120,200,0.75); color:#fff; border:1px solid #1e5f8a; border-radius:7px; padding:8px; cursor:pointer; font-size:12.5px; font-weight:600; transition:background .2s; }}
.save-btn:hover {{ background:rgba(0,160,255,0.9); }}
#saveMsg {{ display:none; color:#a6e3a1; text-align:center; margin-top:9px; font-size:12px; font-style:italic; }}

/* ── Toggle btn ── */
#toggleBtn {{
  position:absolute; right:0; top:50%; transform:translateY(-50%);
  background:rgba(14,28,80,0.88); color:#89dceb;
  border:1px solid #1e5f8a; border-right:none; border-radius:8px 0 0 8px;
  padding:14px 9px; cursor:pointer; z-index:149; font-size:11px;
  writing-mode:vertical-lr; letter-spacing:1.5px; font-weight:700; transition:background .2s;
}}
#toggleBtn:hover {{ background:rgba(30,60,140,0.95); }}

/* ── Right Drawer ── */
#rightPanel {{
  position:absolute; top:0; right:-375px; width:360px; height:100%;
  background:rgba(6,12,24,0.96); border-left:1px solid #1e5f8a;
  box-shadow:-6px 0 30px rgba(0,0,0,0.6); transition:right .3s ease;
  z-index:150; display:flex; flex-direction:column;
}}
#rightPanel.open {{ right:0; }}
#rightPanelHead {{
  background:rgba(14,28,56,0.98); padding:13px 16px; border-bottom:1px solid #1e5f8a;
  color:#89dceb; font-size:14px; font-weight:700; flex-shrink:0;
  display:flex; justify-content:space-between; align-items:center;
}}
#closePanelBtn {{ background:transparent; border:none; color:#6c7086; cursor:pointer; font-size:18px; }}
#closePanelBtn:hover {{ color:#fff; }}
.rtabs {{ display:flex; background:rgba(10,20,44,0.8); border-bottom:1px solid #1a3a5c; flex-shrink:0; }}
.rtab {{ flex:1; padding:9px 2px; text-align:center; cursor:pointer; font-size:11px; color:#585b70; border-bottom:2px solid transparent; transition:all .2s; }}
.rtab:hover {{ color:#89dceb; }}
.rtab.active {{ color:#89dceb; border-bottom-color:#89dceb; background:rgba(20,40,80,0.5); }}
.rtab-body {{ display:none; flex:1; overflow-y:auto; padding:16px; font-size:13px; color:#a6adc8; }}
.rtab-body.active {{ display:block; }}
.placeholder {{ color:#45475a; font-style:italic; text-align:center; margin-top:40px; line-height:1.9; }}

/* ── Result display styling ── */
.res-card {{ background:rgba(14,28,56,0.5); border:1px solid #1e5f8a; border-radius:8px; padding:12px; margin-bottom:12px; }}
.res-card h4 {{ margin:0 0 8px 0; color:#89dceb; font-size:13px; font-weight:600; border-bottom:1px solid rgba(30,95,138,0.4); padding-bottom:4px; }}
.res-row {{ display:flex; justify-content:space-between; align-items:center; font-size:12px; margin-bottom:5px; }}
.res-row:last-child {{ margin-bottom:0; }}
.res-label {{ color:#7a9cc0; display:flex; align-items:center; }}
.res-val {{ color:#cdd6f4; font-weight:600; font-family:monospace; }}
.badge {{ display:inline-block; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; text-transform:uppercase; }}
.badge-green {{ background:rgba(166,227,161,0.2); color:#a6e3a1; border:1px solid #a6e3a1; }}
.badge-yellow {{ background:rgba(249,226,175,0.2); color:#f9e2af; border:1px solid #f9e2af; }}
.badge-red {{ background:rgba(243,139,168,0.2); color:#f38ba8; border:1px solid #f38ba8; }}

/* Elevando a linha em foco para que o tooltip fique por cima de todas as outras linhas */
.field:hover, .res-row:hover {{
  position:relative;
  z-index:9999;
}}

/* ── TOOLTIPS (ⓘ) ── */
.tooltip-info {{
  position:relative;
  display:inline-flex;
  justify-content:center;
  align-items:center;
  cursor:help;
  color:#89dceb;
  margin-left:5px;
  font-size:11px;
  background:rgba(137,220,235,0.1);
  border-radius:50%;
  width:14px;
  height:14px;
  font-weight:bold;
  z-index:99999;
}}
.tooltip-info .tooltiptext {{
  visibility:hidden;
  width:200px;
  background-color:rgba(14,28,56,0.98);
  color:#cdd6f4;
  text-align:left;
  border:1px solid #1e5f8a;
  border-radius:6px;
  padding:8px 10px;
  font-size:11px;
  font-weight:normal;
  text-transform:none;
  letter-spacing:0px;
  position:absolute;
  z-index:99999 !important;
  top:130%;
  left:50%;
  transform:translateX(-50%);
  opacity:0;
  transition:opacity 0.2s;
  box-shadow:0 4px 15px rgba(0,0,0,0.6);
  pointer-events:none;
}}
.tooltip-info .tooltiptext::after {{
  content:"";
  position:absolute;
  bottom:100%;
  left:50%;
  margin-left:-5px;
  border-width:5px;
  border-style:solid;
  border-color:transparent transparent #1e5f8a transparent;
}}
.tooltip-info:hover .tooltiptext {{
  visibility:visible;
  opacity:1;
}}

/* ── Estilos de Impressão ── */
#printTitle {{ display:none; }}
@media print {{
  html, body {{ background:#fff !important; color:#000 !important; overflow:visible !important; }}
  #globeViz, #toggleBtn, #infoPanel, #linkSelectorContainer, .rtabs, #closePanelBtn, #rightPanelHead, .tooltip-info {{ display:none !important; }}
  #rightPanel {{ position:static !important; width:100% !important; height:auto !important; box-shadow:none !important; border:none !important; background:#fff !important; color:#000 !important; display:block !important; }}
  .rtab-body {{ display:block !important; opacity:1 !important; color:#000 !important; background:#fff !important; page-break-after:auto !important; padding:0 !important; margin-bottom:30px !important; }}
  .res-card {{ border:1px solid #bbb !important; background:#fff !important; color:#000 !important; page-break-inside:avoid !important; box-shadow:none !important; }}
  .res-label {{ color:#444 !important; }}
  .res-val {{ color:#000 !important; }}
  #printTitle {{ display:block !important; text-align:center; margin-bottom:25px; border-bottom:2px solid #333; padding-bottom:10px; }}
}}
</style>
</head>
<body>

<div id="globeViz"></div>

<!-- Título visível apenas na impressão PDF -->
<div id="printTitle">
  <h2 style="font-family:'Segoe UI',sans-serif; color:#111; margin-bottom:5px;">COMSAT SIMULATOR - RELATÓRIO TÉCNICO</h2>
  <p style="font-family:'Segoe UI',sans-serif; color:#555; font-size:11px; text-transform:uppercase; letter-spacing:1px;">Cálculos Consolidados de Balanço de Potência, Ruído e Desempenho de Enlace</p>
</div>

<!-- ── Legenda de Potência ── -->
<div id="footprintLegend" style="
  display:none; position:absolute; bottom:20px; left:20px; width:195px;
  background:rgba(6,12,24,0.92); color:#cdd6f4; border-radius:10px;
  border:1px solid #1e5f8a; padding:10px 12px; font-family:'Segoe UI',system-ui,sans-serif;
  box-shadow:0 4px 20px rgba(0,180,255,0.18); z-index:200; pointer-events:none;
">
  <div style="font-size:10.5px; font-weight:700; color:#89dceb; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.5px; border-bottom:1px solid rgba(30,95,138,0.4); padding-bottom:3px;">
    📶 Potencia do Sinal
  </div>
  <div style="display:flex; flex-direction:column; gap:6px; font-size:11px;">
    <div style="display:flex; align-items:center; gap:8px;">
      <div style="width:14px; height:14px; border-radius:3px; background:rgba(255, 0, 100, 0.6); border:1px solid rgba(255,0,100,0.8);"></div>
      <span>Pico (0 a -3 dB)</span>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
      <div style="width:14px; height:14px; border-radius:3px; background:rgba(255, 160, 0, 0.5); border:1px solid rgba(255,160,0,0.7);"></div>
      <span>Forte (-3 a -10 dB)</span>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
      <div style="width:14px; height:14px; border-radius:3px; background:rgba(0, 255, 180, 0.4); border:1px solid rgba(0,255,180,0.6);"></div>
      <span>Medio (-10 a -20 dB)</span>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
      <div style="width:14px; height:14px; border-radius:3px; background:rgba(0, 100, 255, 0.3); border:1px solid rgba(0,100,255,0.5);"></div>
      <span>Fraco (-20 a -30 dB)</span>
    </div>
  </div>
</div>

<div id="infoPanel">
  <div id="infoPanelHead">
    <h3 id="infoTitle">Info</h3>
    <button id="closeInfo" onclick="document.getElementById('infoPanel').style.display='none'">&#x2715;</button>
  </div>
  <div id="infoBody"></div>
</div>

<button id="toggleBtn" onclick="toggleRight()">&#128202; ANALISE</button>

<div id="rightPanel">
  <div id="rightPanelHead">
    <span>&#128202; Analise do Enlace</span>
    <button id="closePanelBtn" onclick="toggleRight()">&#x2715;</button>
  </div>
  <div class="rtabs">
    <div class="rtab active" onclick="switchTab(this,'link')">&#128202; Link</div>
    <div class="rtab" onclick="switchTab(this,'noise')">&#128225; Ruido</div>
    <div class="rtab" onclick="switchTab(this,'perf')">&#128246; BER</div>
    <div class="rtab" onclick="switchTab(this,'pdf')">&#128196; PDF</div>
  </div>
  
  <!-- Seletor do link ativo compartilhado -->
  <div id="linkSelectorContainer" style="padding:12px 16px; border-bottom:1px solid #1e5f8a; background:rgba(10,20,44,0.5); flex-shrink:0;">
    <p class="placeholder" style="margin:0; font-size:11px;">Carregando enlaces...</p>
  </div>

  <!-- Corpo das abas -->
  <div id="tab-link"  class="rtab-body active"></div>
  <div id="tab-noise" class="rtab-body"></div>
  <div id="tab-perf"  class="rtab-body"></div>
  <div id="tab-pdf"   class="rtab-body"></div>
</div>

<script src="https://unpkg.com/globe.gl/dist/globe.gl.min.js"></script>
<script>
var SATS  = {sats_j};
var STNS  = {stns_j};
var LINKS = {lnks_j};
var ORBIT = {orbit_j};
var ALL_PATHS = LINKS.concat(ORBIT);

// Configurações globais mutáveis
var BW_MHZ = 36.0;      // Largura de banda default
var RB_MBPS = 50.0;     // Taxa de bits default
var MOD_TYPE = 'QPSK';  // Modulação default

// Outras perdas editáveis
var LOSS_ATM = 0.5;
var LOSS_RAIN = 1.5;
var LOSS_POINT = 0.5;
var LOSS_POL = 0.3;
var LOSS_RX_LINE = 0.5;

var USE_LOSS_ATM = true;
var USE_LOSS_RAIN = true;
var RAIN_RATE = 50.0;
var RAIN_PROB = 0.01;
var ATM_ZENITH = 0.15;

function obterCoeficientesChuvas(f) {{
  var freqs = [4, 6, 12, 20, 30];
  var a_vals = [0.00075, 0.0028, 0.024, 0.092, 0.24];
  var b_vals = [1.08, 1.12, 1.15, 1.08, 0.98];
  
  if (f <= freqs[0]) return {{ a: a_vals[0], b: b_vals[0] }};
  if (f >= freqs[freqs.length - 1]) return {{ a: a_vals[freqs.length - 1], b: b_vals[freqs.length - 1] }};
  
  for (var i = 0; i < freqs.length - 1; i++) {{
    if (f >= freqs[i] && f <= freqs[i+1]) {{
      var t = (f - freqs[i]) / (freqs[i+1] - freqs[i]);
      var log_a = Math.log10(a_vals[i]) + t * (Math.log10(a_vals[i+1]) - Math.log10(a_vals[i]));
      var a = Math.pow(10, log_a);
      var b = b_vals[i] + t * (b_vals[i+1] - b_vals[i]);
      return {{ a: a, b: b }};
    }}
  }}
  return {{ a: 0.024, b: 1.15 }};
}}

function calcularPerdasDinamicas(f, elev_deg, useAtm, useRain) {{
  var elev_rad = Math.max(5.0, elev_deg) * Math.PI / 180.0;
  var sin_elev = Math.sin(elev_rad);
  
  // 1. Perda Atmosférica Dinâmica (Gaseosa)
  var lossAtm = 0.0;
  if (useAtm) {{
    lossAtm = ATM_ZENITH / sin_elev;
    lossAtm = Math.min(3.0, lossAtm); // Limite físico para evitar infinito
  }}
  
  // 2. Perda por Chuva Dinâmica (ITU-R P.618 simplificada)
  var lossRain = 0.0;
  if (useRain) {{
    var h_s = 1.17; // Altitude de Brasília (km)
    var h_R = 4.0;  // Isoterma 0°C + 0.36km
    
    var L_s = (h_R - h_s) / sin_elev;
    var L_G = L_s * Math.cos(elev_rad);
    
    // Obter coeficientes a, b da ITU-R P.838
    var coef = obterCoeficientesChuvas(f);
    var gamma_001 = coef.a * Math.pow(RAIN_RATE, coef.b);
    
    // Fator de redução horizontal r_0.01
    var r_001 = 1.0 / (1.0 + 0.78 * Math.sqrt(L_G * gamma_001 / f) - 0.38 * (1.0 - Math.exp(-2.0 * L_G)));
    r_001 = Math.max(0.1, Math.min(1.0, r_001));
    
    // Fator de ajuste vertical v_0.01
    var v_001 = 1.0 / (1.0 + Math.sqrt(sin_elev) * (31.0 * Math.sqrt(L_G * gamma_001) / (f * f) - 0.45));
    v_001 = Math.max(0.1, Math.min(1.0, v_001));
    
    // Atenuação em 0.01%
    var A_001 = gamma_001 * L_s * r_001 * v_001;
    
    // Escalonamento para probabilidade P
    var log_p = Math.log(RAIN_PROB);
    var log_a = Math.log(A_001);
    var exp = 0.655 + 0.033 * log_p - 0.045 * log_a;
    exp = Math.max(0.3, Math.min(0.8, exp));
    
    lossRain = A_001 * Math.pow(RAIN_PROB / 0.01, -exp);
    if (isNaN(lossRain) || lossRain < 0) lossRain = 0.0;
  }}
  
  return {{
    atm: lossAtm,
    rain: lossRain
  }};
}}

function toggleLossAtm(val) {{
  USE_LOSS_ATM = val;
  ALL_PATHS = recalcLinks();
  globe.pathsData(ALL_PATHS);
  atualizarAnalise();
}}

function toggleLossRain(val) {{
  USE_LOSS_RAIN = val;
  ALL_PATHS = recalcLinks();
  globe.pathsData(ALL_PATHS);
  atualizarAnalise();
}}

function changeRainRate(val) {{
  RAIN_RATE = parseFloat(val) || 50.0;
  ALL_PATHS = recalcLinks();
  globe.pathsData(ALL_PATHS);
  atualizarAnalise();
}}

function changeRainProb(val) {{
  RAIN_PROB = parseFloat(val) || 0.01;
  ALL_PATHS = recalcLinks();
  globe.pathsData(ALL_PATHS);
  atualizarAnalise();
}}

// ── Helper para Tooltips ──
function tooltip(info) {{
  return '<span class="tooltip-info">i<span class="tooltiptext">' + info + '</span></span>';
}}

// ── Resize iframe ──
(function() {{
  function fit() {{
    try {{
      if (window.frameElement) {{
        window.frameElement.style.height    = window.parent.innerHeight + 'px';
        window.frameElement.style.minHeight = window.parent.innerHeight + 'px';
      }}
    }} catch(e) {{}}
  }}
  fit();
  try {{ window.parent.addEventListener('resize', fit); }} catch(e) {{}}
}})();

function toggleRight() {{ document.getElementById('rightPanel').classList.toggle('open'); }}
function switchTab(el, name) {{
  document.querySelectorAll('.rtab').forEach(function(t) {{ t.classList.remove('active'); }});
  document.querySelectorAll('.rtab-body').forEach(function(t) {{ t.classList.remove('active'); }});
  el.classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');
}}

// ── Globe ──
var globe = Globe()
  (document.getElementById('globeViz'))
  .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
  .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
  .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
  .showAtmosphere(true)
  .atmosphereColor('#4090c0')
  .atmosphereAltitude(0.20)

  // ── ESTAÇÕES: pointsData na superfície (alt=0 → sem haste) ──
  .pointsData(STNS)
  .pointLat('lat')
  .pointLng('lng')
  .pointAltitude('alt')
  .pointRadius(function(d) {{
    return d.kind === 'footprint' ? d.radius : 0.40;
  }})
  .pointColor(function(d) {{
    return d.kind === 'footprint' ? d.color : '#00ff88';
  }})
  .pointLabel('name')

  // Efeito radar nas estações
  .ringsData(STNS)
  .ringLat('lat')
  .ringLng('lng')
  .ringColor(function() {{ return function() {{ return 'rgba(0,255,136,0.2)'; }}; }})
  .ringMaxRadius(5)
  .ringPropagationSpeed(3)
  .ringRepeatPeriod(2200)

  // ── SATÉLITES: labelsData → Texto com um ponto bidimensional verde pequeno ──
  .labelsData(SATS)
  .labelLat('lat')
  .labelLng('lng')
  .labelAltitude('alt')          // Altitude GEO orbital (0.6)
  .labelText('name')
  .labelSize(1.2)
  .labelDotRadius(0.6)           // Bolinha verde bidimensional bem pequenininha
  .labelDotOrientation('bottom') // Ponto verde posicionado abaixo do texto
  .labelColor(function() {{ return '#00ff88'; }}) // Nome e bolinha verdes
  .labelResolution(4)

  // Links + anel orbital GEO
  .pathsData(ALL_PATHS)
  .pathPoints('path')
  .pathPointLat(function(p) {{ return p[0]; }})
  .pathPointLng(function(p) {{ return p[1]; }})
  .pathPointAlt(function(p) {{ return p[2]; }})
  .pathColor(function(d) {{
    if (d.isNadir) return '#ffff00';
    if (d.isOrbit) return 'rgba(255,210,60,0.85)';
    return d.color || '#00e5ff'; // Cor calculada baseada na qualidade do link
  }})
  .pathDashLength(function(d) {{ return d.isOrbit ? 0.03 : (d.isNadir ? 0.015 : 0.08); }})
  .pathDashGap(function(d)    {{ return d.isOrbit ? 0.02  : (d.isNadir ? 0.015 : 0.04); }})
  .pathDashAnimateTime(function(d) {{ return (d.isOrbit || d.isNadir) ? 0 : 2500; }})
  .pathStroke(function(d)    {{ return d.isOrbit ? 0.6   : (d.isNadir ? 0.35 : 0.9); }})

  .width(window.innerWidth)
  .height(window.innerHeight);

globe.controls().autoRotate = true;
globe.controls().autoRotateSpeed = 0.2;
globe.pointOfView({{ altitude: 2.5 }});

// ── Hover no satélite: exibe linha nadir + gradiente de potência + legenda ──
globe.onLabelHover(function(d) {{
  if (d && d.kind === 'satellite') {{
    globe.controls().autoRotate = false;
    
    // 1. Linha Nadir
    globe.pathsData(ALL_PATHS.concat([{{
      path: [[d.lat, d.lng, d.alt], [d.lat, d.lng, 0]],
      isNadir: true, isOrbit: false
    }}]));
    
    // 2. Pegada de Sinal (Footprint) com gradiente na superfície terrestre
    var footprint = gerarFootprint(d);
    globe.pointsData(STNS.concat(footprint));
    
    // 3. Exibe legenda flutuante
    document.getElementById('footprintLegend').style.display = 'block';
  }} else {{
    globe.controls().autoRotate = !!(d === null || d === undefined);
    globe.pathsData(ALL_PATHS);
    
    // Restaura pontos padrão (somente estações) and esconde legenda
    globe.pointsData(STNS);
    document.getElementById('footprintLegend').style.display = 'none';
  }}
}});

// ── Click no satélite: abre painel de edição ──
globe.onLabelClick(function(d) {{
  if (d) showSatPanel(d);
}});

// ── Click na estação terrena ──
globe.onPointClick(function(point) {{
  if (point && point.kind === 'station') {{
    showStationPanel(point);
  }}
}});

// ── Painéis de edição ──
var currentSat = null;
var currentStation = null;

function showInfo(title, bodyHtml) {{
  document.getElementById('infoTitle').textContent = title;
  document.getElementById('infoBody').innerHTML    = bodyHtml;
  document.getElementById('infoPanel').style.display = 'block';
  document.getElementById('saveMsg').style.display = 'none';
}}

function onSatPatternChange() {{
  var type = document.getElementById('f_pat_type').value;
  var hpbwField = document.getElementById('f_pat_hpbw_field');
  if (type === 'Modelo Parabólico') {{
    hpbwField.style.display = 'block';
  }} else {{
    hpbwField.style.display = 'none';
  }}
}}

// Ajusta o formulário de ganho do receptor dependendo do modo selecionado
function onStationGainModeChange() {{
  var mode = document.getElementById('s_gain_mode').value;
  var directField = document.getElementById('s_gain_direct_field');
  var physicalField = document.getElementById('s_gain_phys_field');
  if (mode === 'Valor Direto') {{
    directField.style.display = 'block';
    physicalField.style.display = 'none';
  }} else {{
    directField.style.display = 'none';
    physicalField.style.display = 'block';
  }}
}}

function showSatPanel(d) {{
  currentSat = d;
  
  var selectHtml = 
    '<div class="field"><label>Diagrama de Radiacao' + tooltip('Modelo de decaimento do ganho conforme o desvio angular (off-axis) do feixe.') + '</label>' +
    '<select id="f_pat_type" onchange="onSatPatternChange()">' +
      '<option value="Isotrópica"' + (d.pattern_type === 'Isotrópica' ? ' selected' : '') + '>Isotrópica</option>' +
      '<option value="Modelo Parabólico"' + (d.pattern_type === 'Modelo Parabólico' ? ' selected' : '') + '>Modelo Parabólico</option>' +
      '<option value="CSV"' + (d.pattern_type === 'CSV' ? ' selected' : '') + ' disabled>Carregado por CSV (' + (d.pattern_data ? 'Ativo' : 'Nenhum') + ')</option>' +
    '</select></div>';

  var hpbwStyle = d.pattern_type === 'Modelo Parabólico' ? 'block' : 'none';

  showInfo('Satelite: ' + d.name,
    '<form onsubmit="saveSat(event)">' +
    '<div class="field"><label>Nome' + tooltip('Identificador textual do satélite.') + '</label><input type="text" id="f_name" value="' + d.name + '"></div>' +
    '<div class="field"><label>Longitude Orbital (graus)' + tooltip('Posição do satélite na órbita geoestacionária sobre o equador (-180° a 180°).') + '</label><input type="number" id="f_lng" step="0.1" value="' + d.lng + '"></div>' +
    '<div class="field"><label>Frequencia TX / Downlink (GHz)' + tooltip('Frequência da portadora RF do canal de downlink.') + '</label><input type="number" id="f_freq" step="0.1" value="' + d.frequency + '"></div>' +
    '<div class="field"><label>Potencia TX (W)' + tooltip('Potência elétrica RF de transmissão gerada pelo amplificador HPA/SSPA.') + '</label><input type="number" id="f_power" step="1" value="' + d.tx_power + '"></div>' +
    '<div class="field"><label>Ganho Antena TX Pico (dBi)' + tooltip('Ganho máximo de diretividade da antena de transmissão do satélite no centro do apontamento.') + '</label><input type="number" id="f_gain" step="0.5" value="' + d.tx_gain + '"></div>' +
    '<div class="field"><label>Perda Guia de Onda TX (dB)' + tooltip('Perda de atenuação interna dos guias de onda ou cabos de transmissão no satélite antes da antena.') + '</label><input type="number" id="f_tx_loss" step="0.1" value="' + (d.tx_line_loss !== undefined ? d.tx_line_loss : 1.0) + '"></div>' +
    
    '<h4 style="margin-top:12px; margin-bottom:6px; color:#89dceb; font-size:11px; border-bottom:1px solid #1e5f8a; padding-bottom:3px; text-transform:uppercase;">Receptor do Satélite (Uplink)</h4>' +
    '<div class="field"><label>Frequencia RX / Uplink (GHz)' + tooltip('Frequência da portadora RF do canal de uplink.') + '</label><input type="number" id="f_rx_freq" step="0.1" value="' + (d.rx_frequency || 14.0) + '"></div>' +
    '<div class="field"><label>Ganho Antena RX (dBi)' + tooltip('Ganho máximo da antena receptora do satélite.') + '</label><input type="number" id="f_rx_gain" step="0.5" value="' + (d.rx_gain || 30.0) + '"></div>' +
    '<div class="field"><label>Perda Guia de Onda RX (dB)' + tooltip('Perda de atenuação na linha de transmissão receptora do satélite.') + '</label><input type="number" id="f_rx_loss" step="0.1" value="' + (d.rx_line_loss !== undefined ? d.rx_line_loss : 1.0) + '"></div>' +
    
    '<div class="field"><label>Temp. Antena Sat (K)' + tooltip('Temperatura equivalente de ruído da antena receptora do satélite (apontada para a Terra, geralmente 290 K).') + '</label><input type="number" id="f_sat_t_ant" step="10" value="' + (d.sat_temp_antenna || 290.0) + '"></div>' +
    '<div class="field"><label>Temp. LNA Sat (K)' + tooltip('Temperatura equivalente de ruído do LNA do receptor de bordo.') + '</label><input type="number" id="f_sat_t_lna" step="10" value="' + (d.sat_temp_lna || 150.0) + '"></div>' +
    '<div class="field"><label>Ganho LNA Sat (dB)' + tooltip('Ganho do LNA do receptor de bordo do satélite.') + '</label><input type="number" id="f_sat_g_lna" step="1" value="' + (d.sat_gain_lna || 50.0) + '"></div>' +
    '<div class="field"><label>Temp. Downconverter Sat (K)' + tooltip('Temperatura de ruído do misturador/conversor interno do transponder.') + '</label><input type="number" id="f_sat_t_down" step="10" value="' + (d.sat_temp_down || 290.0) + '"></div>' +
    '<div class="field"><label>Rec. Noise Figure Sat (dB)' + tooltip('Figura de ruído (NF) do receptor interno do transponder.') + '</label><input type="number" id="f_sat_nf_rec" step="0.5" value="' + (d.sat_nf_rec || 8.0) + '"></div>' +

    selectHtml +
    '<div class="field" id="f_pat_hpbw_field" style="display:' + hpbwStyle + ';"><label>Largura de Feixe θ_3dB (graus)' + tooltip('Abertura angular (HPBW) onde o ganho da antena cai 3 dB em relação ao pico.') + '</label><input type="number" id="f_pat_hpbw" step="0.1" value="' + (d.pattern_hpbw || 2.0) + '"></div>' +
    '<button class="save-btn" type="submit">&#128190; Salvar</button>' +
    '</form><div id="saveMsg">&#9989; Salvo!</div>'
  );
}}

function showStationPanel(d) {{
  currentStation = d;
  
  var modeSelect = 
    '<div class="field"><label>Definicao do Ganho' + tooltip('Escolha entre inserir o valor final em dBi diretamente ou calculá-lo a partir das dimensões físicas da antena.') + '</label>' +
    '<select id="s_gain_mode" onchange="onStationGainModeChange()">' +
      '<option value="Valor Direto"' + (d.gain_mode === 'Valor Direto' ? ' selected' : '') + '>Valor Direto (dBi)</option>' +
      '<option value="Diâmetro e Eficiência"' + (d.gain_mode === 'Diâmetro e Eficiência' ? ' selected' : '') + '>Diâmetro e Eficiência</option>' +
    '</select></div>';
    
  var directStyle = (d.gain_mode === 'Valor Direto' || !d.gain_mode) ? 'block' : 'none';
  var physStyle = d.gain_mode === 'Diâmetro e Eficiência' ? 'block' : 'none';

  showInfo('Estacao: ' + d.name,
    '<form onsubmit="saveStation(event)">' +
    '<div class="field"><label>Nome' + tooltip('Identificador da estação terrena.') + '</label><input type="text" id="s_name" value="' + d.name + '"></div>' +
    '<div class="field"><label>Latitude' + tooltip('Latitude geográfica de instalação da estação.') + '</label><input type="number" id="s_lat" step="0.0001" value="' + d.lat.toFixed(4) + '"></div>' +
    '<div class="field"><label>Longitude' + tooltip('Longitude geográfica de instalação da estação.') + '</label><input type="number" id="s_lng" step="0.0001" value="' + d.lng.toFixed(4) + '"></div>' +
    
    modeSelect +
    
    '<div id="s_gain_direct_field" style="display:' + directStyle + ';">' +
      '<div class="field"><label>Ganho Antena RX (dBi)' + tooltip('Ganho máximo de diretividade da antena receptora.') + '</label><input type="number" id="s_gain" step="0.5" value="' + d.rx_gain + '"></div>' +
      '<div class="field"><label>Ganho Antena TX (dBi)' + tooltip('Ganho máximo de diretividade da antena transmissora.') + '</label><input type="number" id="s_tx_gain" step="0.5" value="' + (d.tx_gain || 42.0) + '"></div>' +
    '</div>' +
    
    '<div id="s_gain_phys_field" style="display:' + physStyle + ';">' +
      '<div class="field"><label>Diâmetro da Antena (m)' + tooltip('Diâmetro físico da abertura refletora parabólica em metros.') + '</label><input type="number" id="s_diam" step="0.1" value="' + (d.antenna_diameter || 1.8) + '"></div>' +
      '<div class="field"><label>Eficiência da Antena (%)' + tooltip('Eficiência de conversão eletromagnética da abertura refletora (geralmente entre 50% e 75%).') + '</label><input type="number" id="s_eff" step="5" value="' + (d.antenna_efficiency || 60.0) + '"></div>' +
    '</div>' +
    
    '<h4 style="margin-top:12px; margin-bottom:6px; color:#89dceb; font-size:11px; border-bottom:1px solid #1e5f8a; padding-bottom:3px; text-transform:uppercase;">Transmissor (Uplink)</h4>' +
    '<div class="field"><label>Potência TX da Estação (W)' + tooltip('Potência elétrica RF entregue pelo HPA da estação terrena para o uplink.') + '</label><input type="number" id="s_tx_power" step="5" value="' + (d.tx_power || 120.0) + '"></div>' +
    '<div class="field"><label>Perda Guia de Onda TX (dB)' + tooltip('Perda de atenuação nos conectores e guia de onda do transmissor da estação.') + '</label><input type="number" id="s_tx_loss" step="0.1" value="' + (d.tx_line_loss !== undefined ? d.tx_line_loss : 0.5) + '"></div>' +

    '<h4 style="margin-top:12px; margin-bottom:6px; color:#89dceb; font-size:11px; border-bottom:1px solid #1e5f8a; padding-bottom:3px; text-transform:uppercase;">Parâmetros de Ruído (Terminal)</h4>' +
    '<div class="field"><label>Temp. Antena (K)' + tooltip('Temperatura equivalente de ruído térmico coletada do espaço/atmosfera pela antena receptora.') + '</label><input type="number" id="s_t_ant" step="5" value="' + (d.temp_antenna || 50.0) + '"></div>' +
    '<div class="field"><label>Temp. LNA (K)' + tooltip('Temperatura equivalente de ruído interno do Amplificador de Baixo Ruído (LNA).') + '</label><input type="number" id="s_t_lna" step="5" value="' + (d.temp_lna || 80.0) + '"></div>' +
    '<div class="field"><label>Ganho LNA (dB)' + tooltip('Ganho de amplificação de potência RF fornecido pelo LNA para atenuar o ruído dos estágios posteriores.') + '</label><input type="number" id="s_g_lna" step="1" value="' + (d.gain_lna || 50.0) + '"></div>' +
    '<div class="field"><label>Temp. Downconverter (K)' + tooltip('Temperatura de ruído do conversor de frequência RF para FI (Downconverter).') + '</label><input type="number" id="s_t_down" step="10" value="' + (d.temp_down || 290.0) + '"></div>' +
    '<div class="field"><label>Rec. Noise Figure (dB)' + tooltip('Figura de ruído (NF) intrínseca do receptor final demodulador.') + '</label><input type="number" id="s_nf_rec" step="0.5" value="' + (d.nf_rec || 8.0) + '"></div>' +

    '<button class="save-btn" type="submit">&#128190; Salvar</button>' +
    '</form><div id="saveMsg">&#9989; Salvo!</div>'
  );
}}

function saveSat(e) {{
  e.preventDefault();
  if (!currentSat) return;
  currentSat.name         = document.getElementById('f_name').value;
  currentSat.lng          = parseFloat(document.getElementById('f_lng').value);
  currentSat.frequency    = parseFloat(document.getElementById('f_freq').value);
  currentSat.tx_power     = parseFloat(document.getElementById('f_power').value);
  currentSat.tx_gain      = parseFloat(document.getElementById('f_gain').value);
  currentSat.tx_line_loss = parseFloat(document.getElementById('f_tx_loss').value);
  
  // Uplink/Rx Parameters
  currentSat.rx_frequency     = parseFloat(document.getElementById('f_rx_freq').value);
  currentSat.rx_gain          = parseFloat(document.getElementById('f_rx_gain').value);
  currentSat.rx_line_loss     = parseFloat(document.getElementById('f_rx_loss').value);
  currentSat.sat_temp_antenna = parseFloat(document.getElementById('f_sat_t_ant').value);
  currentSat.sat_temp_lna     = parseFloat(document.getElementById('f_sat_t_lna').value);
  currentSat.sat_gain_lna     = parseFloat(document.getElementById('f_sat_g_lna').value);
  currentSat.sat_temp_down    = parseFloat(document.getElementById('f_sat_t_down').value);
  currentSat.sat_nf_rec       = parseFloat(document.getElementById('f_sat_nf_rec').value);

  currentSat.pattern_type = document.getElementById('f_pat_type').value;
  if (currentSat.pattern_type === 'Modelo Parabólico') {{
    currentSat.pattern_hpbw = parseFloat(document.getElementById('f_pat_hpbw').value);
  }}
  
  globe.labelsData(SATS.slice());
  ALL_PATHS = recalcLinks();
  globe.pathsData(ALL_PATHS);
  document.getElementById('saveMsg').style.display = 'block';
  reconstruirSeletores();
  atualizarAnalise();
}}

function saveStation(e) {{
  e.preventDefault();
  if (!currentStation) return;
  currentStation.name               = document.getElementById('s_name').value;
  currentStation.lat                = parseFloat(document.getElementById('s_lat').value);
  currentStation.lng                = parseFloat(document.getElementById('s_lng').value);
  currentStation.gain_mode          = document.getElementById('s_gain_mode').value;
  
  currentStation.tx_power           = parseFloat(document.getElementById('s_tx_power').value);
  currentStation.tx_line_loss       = parseFloat(document.getElementById('s_tx_loss').value);

  if (currentStation.gain_mode === 'Valor Direto') {{
    currentStation.rx_gain          = parseFloat(document.getElementById('s_gain').value);
    currentStation.tx_gain          = parseFloat(document.getElementById('s_tx_gain').value);
  }} else {{
    currentStation.antenna_diameter = parseFloat(document.getElementById('s_diam').value);
    currentStation.antenna_efficiency = parseFloat(document.getElementById('s_eff').value);
    
    var f_down = SATS.length ? SATS[0].frequency : 12.0;
    var f_up = (SATS.length && SATS[0].rx_frequency) ? SATS[0].rx_frequency : 14.0;
    var d_m = currentStation.antenna_diameter;
    var eff = currentStation.antenna_efficiency / 100.0;
    
    var g_rx_dbi = 20 * Math.log10(d_m) + 20 * Math.log10(f_down) + 20.4 + 10 * Math.log10(eff);
    var g_tx_dbi = 20 * Math.log10(d_m) + 20 * Math.log10(f_up) + 20.4 + 10 * Math.log10(eff);
    
    currentStation.rx_gain = parseFloat(g_rx_dbi.toFixed(2));
    currentStation.tx_gain = parseFloat(g_tx_dbi.toFixed(2));
  }}
  
  currentStation.temp_antenna       = parseFloat(document.getElementById('s_t_ant').value);
  currentStation.temp_lna           = parseFloat(document.getElementById('s_t_lna').value);
  currentStation.gain_lna           = parseFloat(document.getElementById('s_g_lna').value);
  currentStation.temp_down          = parseFloat(document.getElementById('s_t_down').value);
  currentStation.nf_rec             = parseFloat(document.getElementById('s_nf_rec').value);
  
  globe.pointsData(STNS.slice());
  globe.ringsData(STNS.slice());
  ALL_PATHS = recalcLinks();
  globe.pathsData(ALL_PATHS);
  document.getElementById('saveMsg').style.display = 'block';
  reconstruirSeletores();
  atualizarAnalise();
}}

function recalcLinks() {{
  var links = STNS.map(function(st) {{
    if (!SATS.length) return null;
    var nearest = SATS.reduce(function(p, c) {{
      return Math.abs(c.lng - st.lng) < Math.abs(p.lng - st.lng) ? c : p;
    }});
    
    // CÁLCULO DO LINK COMPLETO (UPLINK + DOWNLINK) PARA COR DO ENLACE NO GLOBO
    var res = calcularLinkCompleto(st, nearest);
    var margem = res.total.margem;
    
    // Cor dinâmica baseada na margem combinada: Verde (>= 3dB), Amarelo (>= 0dB), Vermelho (< 0dB)
    var col = '#00ff88'; 
    if (margem < 0.0) {{
      col = '#ff3333';
    }} else if (margem < 3.0) {{
      col = '#ffcc00';
    }}
    
    return {{
      path: [[0.0, nearest.lng, {GEO_ALT}], [st.lat, st.lng, 0.0]],
      color: col, isNadir: false, isOrbit: false
    }};
  }}).filter(Boolean);
  return links.concat(ORBIT);
}}

// ── ⚙️ MOTOR DE CÁLCULO CIENTÍFICO (REAL-TIME NO FRONT-END) ──

// 1. Geometria Orbital e Apontamento
function calcularApontamento(latSt, lonSt, lonSat) {{
  var Re = 6371.0;
  var Rsat = Re + 35786.0;
  var latRad = latSt * Math.PI / 180.0;
  var lonStRad = lonSt * Math.PI / 180.0;
  var lonSatRad = lonSat * Math.PI / 180.0;
  
  // Distância 3D
  var cosBeta = Math.cos(latRad) * Math.cos(lonStRad - lonSatRad);
  var d2 = Re*Re + Rsat*Rsat - 2*Re*Rsat*cosBeta;
  var slantRange = Math.sqrt(Math.max(0.1, d2));
  
  // Elevação
  var sinBeta = Math.sqrt(Math.max(0.0, 1.0 - cosBeta*cosBeta));
  var el = 0.0;
  if (sinBeta < 1e-9) {{
    el = cosBeta > 0 ? 90.0 : -90.0;
  }} else {{
    var elevRad = Math.atan((cosBeta - Re / Rsat) / sinBeta);
    el = elevRad * 180.0 / Math.PI;
  }}
  
  // Ângulo Off-Axis do Satélite (Nadir pointing)
  var cosTheta = (Rsat - Re * cosBeta) / slantRange;
  cosTheta = Math.max(-1.0, Math.min(1.0, cosTheta));
  var offAxis = Math.acos(cosTheta) * 180.0 / Math.PI;
  
  return {{ distance: slantRange, elevation: el, offAxis: offAxis }};
}}

// 2. Diagrama de Radiação e Ganho Real
function obterGanhoRealSat(sat, offAxisAngle) {{
  var peak = sat.tx_gain;
  if (sat.pattern_type === 'Isotrópica' || !sat.pattern_type) {{
    return {{ gain: peak, att: 0.0 }};
  }} else if (sat.pattern_type === 'Modelo Parabólico') {{
    var hpbw = sat.pattern_hpbw || 2.0;
    var att = -12 * Math.pow(offAxisAngle / hpbw, 2);
    att = Math.max(-40.0, att); // limitador de atenuação máxima
    return {{ gain: peak + att, att: att }};
  }} else if (sat.pattern_type === 'CSV' && sat.pattern_data) {{
    var data = sat.pattern_data;
    if (!data.length) return {{ gain: peak, att: 0.0 }};
    if (offAxisAngle <= data[0][0]) return {{ gain: peak + data[0][1], att: data[0][1] }};
    if (offAxisAngle >= data[data.length - 1][0]) return {{ gain: peak + data[data.length - 1][1], att: data[data.length - 1][1] }};
    
    for (var i = 0; i < data.length - 1; i++) {{
      if (offAxisAngle >= data[i][0] && offAxisAngle <= data[i+1][0]) {{
        var t = (offAxisAngle - data[i][0]) / (data[i+1][0] - data[i][0]);
        var att = data[i][1] + t * (data[i+1][1] - data[i][1]);
        return {{ gain: peak + att, att: att }};
      }}
    }}
  }}
  return {{ gain: peak, att: 0.0 }};
}}

// 3. Geração de pegada de sinal na superfície terrestre
function gerarFootprint(sat) {{
  var points = [];
  var lonSat = sat.lng;
  
  // Define o tamanho da abrangência com base no HPBW
  var span = 45.0; // Padrão largo
  if (sat.pattern_type === 'Modelo Parabólico') {{
    span = Math.min(65.0, 9.0 * (sat.pattern_hpbw || 2.0));
  }} else if (sat.pattern_type === 'Isotrópica') {{
    span = 70.0;
  }}
  
  // Subdivisões do grid
  var steps = 14; 
  var stepSize = (2 * span) / steps;
  
  for (var i = 0; i <= steps; i++) {{
    var lat = -span + i * stepSize;
    for (var j = 0; j <= steps; j++) {{
      var lon = lonSat - span + j * stepSize;
      
      if (lat < -85 || lat > 85) continue;
      
      var geo = calcularApontamento(lat, lon, lonSat);
      
      // Apenas pontos visíveis
      if (geo.elevation < 0) continue;
      
      var satAnt = obterGanhoRealSat(sat, geo.offAxis);
      var att = satAnt.att; // Atenuação em dB (negativo)
      
      // Mapeamento de cor e transparência simulando calor/potência do sinal
      var color = 'rgba(0,0,0,0)';
      if (att >= -3.0) {{
        color = 'rgba(255, 0, 100, 0.40)'; // Pico: Magenta/Vermelho
      }} else if (att >= -10.0) {{
        color = 'rgba(255, 160, 0, 0.30)'; // Forte: Amarelo
      }} else if (att >= -20.0) {{
        color = 'rgba(0, 255, 180, 0.20)'; // Médio: Verde/Ciano
      }} else if (att >= -30.0) {{
        color = 'rgba(0, 100, 255, 0.10)'; // Fraco: Azul
      }} else {{
        continue; // Muito fraco
      }}
      
      points.push({{
        lat: lat,
        lng: lon,
        alt: 0.0,
        kind: 'footprint',
        color: color,
        radius: stepSize * 0.70, // Tamanho que sobrepõe ligeiramente as bordas
        name: 'Ponto Footprint | Atenuacao: ' + att.toFixed(1) + ' dB (Ganho: ' + satAnt.gain.toFixed(1) + ' dBi)'
      }});
    }}
  }}
  return points;
}}

// 4. Função complementar de erro (Chebyshev) para BER
function erfc(x) {{
  var t = 1.0 / (1.0 + 0.5 * Math.abs(x));
  var ans = t * Math.exp(-x*x - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 +
            t * (-0.18628806 + t * 0.27886807 + t * (-1.13520398 + t * 1.48851587 +
            t * (-0.82215223 + t * 0.17087277)))))));
  return x >= 0 ? ans : 2.0 - ans;
}}

function calcularBER(ebN0dB, modType) {{
  var ebN0Lin = Math.pow(10, ebN0dB / 10.0);
  if (modType === 'BPSK' || modType === 'QPSK') {{
    return 0.5 * erfc(Math.sqrt(ebN0Lin));
  }} else if (modType === '8PSK') {{
    return (1.0 / 3.0) * erfc(Math.sqrt(3.0 * ebN0Lin) * Math.sin(Math.PI / 8.0));
  }} else if (modType === '16QAM') {{
    return 0.375 * erfc(Math.sqrt(0.4 * ebN0Lin));
  }}
  return 0.0;
}}

function calcularLinkCompleto(st, sat) {{
  var geo = calcularApontamento(st.lat, st.lng, sat.lng);
  
  // ==========================================
  // 1. UPLINK (Subida: Estação -> Satélite)
  // ==========================================
  var f_up = sat.rx_frequency || 14.0;
  var ptx_w_up = st.tx_power || 120.0;
  var ptx_dbw_up = 10 * Math.log10(ptx_w_up);
  var txLoss_up = st.tx_line_loss !== undefined ? st.tx_line_loss : 0.5;
  var gtx_up = st.tx_gain || 42.0;
  var eirp_up = ptx_dbw_up - txLoss_up + gtx_up;
  
  var fspl_up = 20 * Math.log10(geo.distance) + 20 * Math.log10(f_up) + 92.45;
  
  var lossesDinamicas_up = calcularPerdasDinamicas(f_up, geo.elevation, USE_LOSS_ATM, USE_LOSS_RAIN);
  var rxLoss_up = sat.rx_line_loss !== undefined ? sat.rx_line_loss : 1.0;
  var totalLosses_up = lossesDinamicas_up.atm + lossesDinamicas_up.rain + LOSS_POINT + LOSS_POL + rxLoss_up;
  
  var sat_rx_gain = sat.rx_gain || 30.0;
  var prx_dbw_up = eirp_up - fspl_up - totalLosses_up + sat_rx_gain;
  var prx_dbm_up = prx_dbw_up + 30.0;
  
  // Cascata de Ruído do Satélite
  var sat_temp_ant = sat.sat_temp_antenna || 290.0;
  var sat_temp_lna_val = sat.sat_temp_lna || 150.0;
  var sat_gain_lna_val = sat.sat_gain_lna || 50.0;
  var sat_temp_down_val = sat.sat_temp_down || 290.0;
  var sat_nf_rec_val = sat.sat_nf_rec || 8.0;
  
  var g_lna_sat_lin = Math.pow(10, sat_gain_lna_val / 10.0);
  var f_rec_sat = Math.pow(10, sat_nf_rec_val / 10.0);
  var t_rec_sat = 290.0 * (f_rec_sat - 1.0);
  var t_eff_sat = sat_temp_lna_val + (sat_temp_down_val / g_lna_sat_lin) + (t_rec_sat / g_lna_sat_lin);
  var t_sys_sat = sat_temp_ant + t_eff_sat;
  
  var gt_sat = sat_rx_gain - 10 * Math.log10(t_sys_sat);
  var K_DB = -228.6;
  var n0_sat = K_DB + 10 * Math.log10(t_sys_sat);
  var cn0_up = prx_dbw_up - n0_sat;
  var cn_up = cn0_up - 10 * Math.log10(BW_MHZ * 1e6);
  
  // ==========================================
  // 2. DOWNLINK (Descida: Satélite -> Estação)
  // ==========================================
  var f_down = sat.frequency || 12.0;
  var ptx_w_down = sat.tx_power || 100.0;
  var ptx_dbw_down = 10 * Math.log10(ptx_w_down);
  var txLoss_down = sat.tx_line_loss !== undefined ? sat.tx_line_loss : 1.0;
  
  var satAnt = obterGanhoRealSat(sat, geo.offAxis);
  var eirp_down = ptx_dbw_down - txLoss_down + satAnt.gain;
  
  var fspl_down = 20 * Math.log10(geo.distance) + 20 * Math.log10(f_down) + 92.45;
  
  var lossesDinamicas_down = calcularPerdasDinamicas(f_down, geo.elevation, USE_LOSS_ATM, USE_LOSS_RAIN);
  var totalLosses_down = lossesDinamicas_down.atm + lossesDinamicas_down.rain + LOSS_POINT + LOSS_POL + LOSS_RX_LINE;
  
  var prx_dbw_down = eirp_down - fspl_down - totalLosses_down + st.rx_gain;
  var prx_dbm_down = prx_dbw_down + 30.0;
  
  // Cascata de Ruído da Estação
  var g_lna_lin = Math.pow(10, (st.gain_lna || 50.0) / 10.0);
  var f_rec = Math.pow(10, (st.nf_rec || 8.0) / 10.0);
  var t_rec_k = 290.0 * (f_rec - 1.0);
  var t_eff = (st.temp_lna || 80.0) + ((st.temp_down || 290.0) / g_lna_lin) + (t_rec_k / g_lna_lin);
  var t_sys = (st.temp_antenna || 50.0) + t_eff;
  
  var gt_gs = st.rx_gain - 10 * Math.log10(t_sys);
  var n0_gs = K_DB + 10 * Math.log10(t_sys);
  var cn0_down = prx_dbw_down - n0_gs;
  var cn_down = cn0_down - 10 * Math.log10(BW_MHZ * 1e6);
  
  // ==========================================
  // 3. COMBINADO (Total Uplink + Downlink)
  // ==========================================
  var cn0_up_lin = Math.pow(10, cn0_up / 10.0);
  var cn0_down_lin = Math.pow(10, cn0_down / 10.0);
  var cn0_total_lin = 1.0 / ((1.0 / cn0_up_lin) + (1.0 / cn0_down_lin));
  var cn0_total = 10 * Math.log10(cn0_total_lin);
  
  var cn_total = cn0_total - 10 * Math.log10(BW_MHZ * 1e6);
  
  var ebn0_total = cn0_total - 10 * Math.log10(RB_MBPS * 1e6);
  var ber_total = calcularBER(ebn0_total, MOD_TYPE);
  
  var ebn0_req = 10.5;
  if (MOD_TYPE === '8PSK') ebn0_req = 14.0;
  else if (MOD_TYPE === '16QAM') ebn0_req = 14.5;
  var margem_total = ebn0_total - ebn0_req;
  
  return {{
    geo: geo,
    up: {{
      frequency: f_up,
      ptx_w: ptx_w_up,
      ptx_dbw: ptx_dbw_up,
      tx_loss: txLoss_up,
      gtx: gtx_up,
      eirp: eirp_up,
      fspl: fspl_up,
      losses: lossesDinamicas_up,
      rx_loss: rxLoss_up,
      total_losses: totalLosses_up,
      rx_gain: sat_rx_gain,
      prx_dbw: prx_dbw_up,
      prx_dbm: prx_dbm_up,
      t_sys: t_sys_sat,
      t_eff: t_eff_sat,
      t_ant: sat_temp_ant,
      t_lna: sat_temp_lna_val,
      g_lna: sat_gain_lna_val,
      t_down: sat_temp_down_val,
      nf_rec: sat_nf_rec_val,
      t_rec: t_rec_sat,
      gt: gt_sat,
      n0: n0_sat,
      cn0: cn0_up,
      cn: cn_up
    }},
    down: {{
      frequency: f_down,
      ptx_w: ptx_w_down,
      ptx_dbw: ptx_dbw_down,
      tx_loss: txLoss_down,
      satAnt: satAnt,
      eirp: eirp_down,
      fspl: fspl_down,
      losses: lossesDinamicas_down,
      total_losses: totalLosses_down,
      rx_gain: st.rx_gain,
      prx_dbw: prx_dbw_down,
      prx_dbm: prx_dbm_down,
      t_sys: t_sys,
      t_eff: t_eff,
      t_ant: st.temp_antenna,
      t_lna: st.temp_lna,
      g_lna: st.gain_lna,
      t_down: st.temp_down,
      nf_rec: st.nf_rec,
      t_rec: t_rec_k,
      gt: gt_gs,
      n0: n0_gs,
      cn0: cn0_down,
      cn: cn_down
    }},
    total: {{
      cn0: cn0_total,
      cn: cn_total,
      ebn0: ebn0_total,
      ber: ber_total,
      ebn0_req: ebn0_req,
      margem: margem_total
    }}
  }};
}}

// 5. Função auxiliar para gerar gráfico de cascata (Waterfall) em HTML
function gerarWaterfallHtml(ptx_dbw, l_tx, g_tx, fspl, l_other, g_rx, prx_dbw) {{
  var maxVal = 210.0; // Normalizador da largura das barras
  
  function getWidth(val) {{
    var abs = Math.abs(val);
    return Math.min(100, (abs / maxVal) * 100).toFixed(1) + '%';
  }}
  
  return '<div class="res-card"><h4>Gráfico de Cascata (Waterfall)</h4>' +
    '<div style="display:flex; flex-direction:column; gap:9px; margin-top:8px; font-size:11px;">' +
      // Pt
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#a6adc8;">1. Potência do Transmissor (Pt) ' + tooltip('Potência eletromagnética RF efetiva de saída do transmissor (HPA).') + '</span>' +
          '<span class="res-val">' + ptx_dbw.toFixed(1) + ' dBW</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#89dceb; width:' + getWidth(ptx_dbw) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // Gt
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#a6e3a1;">2. Ganho Antena Sat (Gt) ' + tooltip('Ganho da antena transmissora do satélite na direção angular específica do terminal receptor.') + '</span>' +
          '<span class="res-val" style="color:#a6e3a1;">+' + g_tx.toFixed(1) + ' dBi</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#a6e3a1; width:' + getWidth(g_tx) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // Ltx
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#f38ba8;">3. Perda Linha Guia Sat (Ltx) ' + tooltip('Perda de atenuação nos conectores e guia de onda entre o transmissor e a antena do satélite.') + '</span>' +
          '<span class="res-val" style="color:#f38ba8;">-' + l_tx.toFixed(1) + ' dB</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#f38ba8; width:' + getWidth(l_tx) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // FSPL
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#f38ba8;">4. Perda por Espaço Livre (FSPL) ' + tooltip('Atenuação natural da energia devido à dispersão geométrica da onda esférica no vácuo.') + '</span>' +
          '<span class="res-val" style="color:#f38ba8;">-' + fspl.toFixed(1) + ' dB</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#f38ba8; width:' + getWidth(fspl) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // L_other
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#f38ba8;">5. Outras Perdas ' + tooltip('Soma das atenuações atmosféricas, atenuação por chuva, erros de apontamento, perdas de polarização e perdas de cabo no receptor.') + '</span>' +
          '<span class="res-val" style="color:#f38ba8;">-' + l_other.toFixed(1) + ' dB</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#f38ba8; width:' + getWidth(l_other) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // Grx
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#a6e3a1;">6. Ganho Antena Receptor (Grx) ' + tooltip('Ganho máximo de diretividade da antena refletora parabólica da estação terrena.') + '</span>' +
          '<span class="res-val" style="color:#a6e3a1;">+' + g_rx.toFixed(1) + ' dBi</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#a6e3a1; width:' + getWidth(g_rx) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // Prx
      '<div style="border-top:1px solid rgba(255,255,255,0.1); padding-top:6px;">' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#f9e2af; font-weight:700;">7. Potência Final Recebida (Prx) ' + tooltip('Potência útil final do portador eletromagnético RF captada pelo alimentador da estação terrena.') + '</span>' +
          '<span class="res-val" style="color:#f9e2af;">' + prx_dbw.toFixed(1) + ' dBW</span>' +
        '</div>' +
      '</div>' +
    '</div></div>';
}}

// 6. Geração de gráfico interativo SVG para curva BER
function gerarBerChart(activeEbN0, activeBer, activeMod) {{
  var width = 290;
  var height = 180;
  var paddingLeft = 32;
  var paddingRight = 10;
  var paddingTop = 12;
  var paddingBottom = 22;
  
  var chartW = width - paddingLeft - paddingRight;
  var chartH = height - paddingTop - paddingBottom;
  
  function getX(db) {{
    return paddingLeft + (db / 16.0) * chartW;
  }}
  
  function getY(ber) {{
    var log = ber > 0 ? Math.log10(ber) : -8.0;
    log = Math.max(-8.0, Math.min(0.0, log));
    return paddingTop + (log / -8.0) * chartH;
  }}
  
  var svg = '<svg width="' + width + '" height="' + height + '" style="background:rgba(10,20,44,0.45); border:1px solid #1e5f8a; border-radius:8px; margin-top:10px;">';
  
  // Linhas de Grade Horizontais (décadas 10^0 a 10^-8)
  for (var logY = 0; logY >= -8; logY--) {{
    var y = paddingTop + (logY / -8.0) * chartH;
    svg += '<line x1="' + paddingLeft + '" y1="' + y + '" x2="' + (width - paddingRight) + '" y2="' + y + '" stroke="rgba(30,95,138,0.15)" stroke-width="1" />';
    if (logY % 2 === 0) {{
      svg += '<text x="' + (paddingLeft - 4) + '" y="' + (y + 3) + '" fill="#7a9cc0" font-size="8" text-anchor="end" font-family="monospace">10' + (logY === 0 ? '⁰' : (logY === -2 ? '⁻²' : (logY === -4 ? '⁻⁴' : (logY === -6 ? '⁻⁶' : '⁻⁸')))) + '</text>';
    }}
  }}
  
  // Linhas de Grade Verticais (Eb/N0 em dB)
  for (var dbX = 0; dbX <= 16; dbX += 2) {{
    var x = paddingLeft + (dbX / 16.0) * chartW;
    svg += '<line x1="' + x + '" y1="' + paddingTop + '" x2="' + x + '" y2="' + (height - paddingBottom) + '" stroke="rgba(30,95,138,0.15)" stroke-width="1" />';
    svg += '<text x="' + x + '" y="' + (height - paddingBottom + 10) + '" fill="#7a9cc0" font-size="8" text-anchor="middle" font-family="monospace">' + dbX + '</text>';
  }}
  
  // Desenha as curvas de modulação
  var modulations = ['BPSK', '8PSK', '16QAM'];
  var colors = {{ 'BPSK': '#89dceb', '8PSK': '#f9e2af', '16QAM': '#a6e3a1' }};
  
  modulations.forEach(function(mod) {{
    var pathD = '';
    for (var db = 0; db <= 16; db += 0.5) {{
      var yBer = calcularBER(db, mod === 'BPSK' ? 'BPSK' : mod);
      var px = getX(db);
      var py = getY(yBer);
      if (db === 0) pathD += 'M ' + px + ' ' + py;
      else pathD += ' L ' + px + ' ' + py;
    }}
    var isActive = (activeMod === mod || (activeMod === 'QPSK' && mod === 'BPSK'));
    var strokeW = isActive ? 2.2 : 0.9;
    var strokeO = isActive ? 0.95 : 0.35;
    svg += '<path d="' + pathD + '" fill="none" stroke="' + colors[mod] + '" stroke-width="' + strokeW + '" stroke-opacity="' + strokeO + '" />';
  }});
  
  // Desenha o Ponto de Operação do Link Ativo (blinking red circle)
  var pxActive = getX(activeEbN0);
  var pyActive = getY(activeBer);
  svg += '<circle cx="' + pxActive + '" cy="' + pyActive + '" r="5.5" fill="#f38ba8" stroke="#fff" stroke-width="1.5">';
  svg += '<animate attributeName="r" values="4.5;6.5;4.5" dur="1.2s" repeatCount="indefinite" />';
  svg += '</circle>';
  
  // Legenda das Modulações
  svg += '<g transform="translate(' + (paddingLeft + 10) + ', 22)" font-size="7" font-family="sans-serif">';
  svg += '<rect x="0" y="0" width="8" height="5" fill="#89dceb" fill-opacity="0.8"/>';
  svg += '<text x="12" y="5" fill="#cdd6f4">BPSK/QPSK</text>';
  svg += '<rect x="68" y="0" width="8" height="5" fill="#f9e2af" fill-opacity="0.8"/>';
  svg += '<text x="80" y="5" fill="#cdd6f4">8PSK</text>';
  svg += '<rect x="114" y="0" width="8" height="5" fill="#a6e3a1" fill-opacity="0.8"/>';
  svg += '<text x="126" y="5" fill="#cdd6f4">16QAM</text>';
  svg += '<circle cx="178" cy="2.5" r="2.5" fill="#f38ba8"/>';
  svg += '<text x="184" y="5" fill="#f38ba8" font-weight="bold">LINK OP</text>';
  svg += '</g>';
  
  svg += '</svg>';
  return svg;
}}

// 7. Executa e renderiza os cálculos na UI
function atualizarAnalise() {{
  var sel = document.getElementById('link_selector');
  if (!sel || !sel.value) {{
    document.getElementById('tab-link').innerHTML = '<p class="placeholder">Adicione satelites e estacoes para calcular o Link Budget.</p>';
    document.getElementById('tab-noise').innerHTML = '<p class="placeholder">Configure a cascata de ruido no painel esquerdo.</p>';
    document.getElementById('tab-perf').innerHTML = '<p class="placeholder">Selecione modulacao para estimar BER e Eb/N0.</p>';
    document.getElementById('tab-pdf').innerHTML = '<p class="placeholder">Gere um relatorio PDF do cenario.</p>';
    return;
  }}
  
  var ids = sel.value.split('-');
  var stIdx = parseInt(ids[0]);
  var satIdx = parseInt(ids[1]);
  
  var st = STNS[stIdx];
  var sat = SATS[satIdx];
  
  if (!st || !sat) return;
  
  // Obter cálculos unificados (Uplink + Downlink)
  var res = calcularLinkCompleto(st, sat);
  var geo = res.geo;
  var up = res.up;
  var down = res.down;
  var total = res.total;
  
  // Renderização ── TAB: LINK
  var waterfallUp = gerarWaterfallHtml(up.ptx_dbw, up.tx_loss, up.gtx, up.fspl, up.total_losses - up.rx_loss, up.rx_gain, up.prx_dbw);
  var waterfallDown = gerarWaterfallHtml(down.ptx_dbw, down.tx_loss, down.satAnt.gain, down.fspl, down.total_losses - LOSS_RX_LINE, st.rx_gain, down.prx_dbw);
  
  var margemBadge = total.margem >= 0 ? 
    '<span class="badge badge-green">Margem Positiva (+' + total.margem.toFixed(2) + ' dB)</span>' :
    '<span class="badge badge-red">Margem Negativa (' + total.margem.toFixed(2) + ' dB)</span>';
  
  var rainControlsHtml = '';
  if (USE_LOSS_RAIN) {{
    rainControlsHtml = 
      '<div style="margin-top:8px; border-top:1px solid rgba(255,255,255,0.05); padding-top:6px; display:grid; grid-template-columns:1fr 1fr; gap:10px;">' +
        '<div class="field" style="margin:0;"><label style="font-size:8px; color:#a6adc8;">Taxa R0.01 (mm/h) ' + tooltip('Intensidade de chuva estatística excedida em 0.01% do ano na região.') + '</label><input type="number" step="5" style="font-size:11px; padding:3px 5px;" value="' + RAIN_RATE + '" oninput="changeRainRate(this.value)"></div>' +
        '<div class="field" style="margin:0;"><label style="font-size:8px; color:#a6adc8;">Indisp. P (%) ' + tooltip('Porcentagem de tempo de indisponibilidade desejada no ano (geralmente entre 0.001% e 1%).') + '</label><input type="number" step="0.001" style="font-size:11px; padding:3px 5px;" value="' + RAIN_PROB + '" oninput="changeRainProb(this.value)"></div>' +
      '</div>';
  }}
  
  var linkHtml = 
    '<div class="res-card"><h4>Geometria & Apontamento</h4>' +
      '<div class="res-row"><span class="res-label">Distancia (Slant Range) ' + tooltip('Distância geométrica em linha de visada direta entre o satélite e a estação terrena.') + '</span><span class="res-val">' + geo.distance.toFixed(2) + ' km</span></div>' +
      '<div class="res-row"><span class="res-label">Angulo de Elevacao ' + tooltip('Ângulo formado entre o horizonte local da estação e o satélite no céu.') + '</span><span class="res-val">' + geo.elevation.toFixed(2) + '&deg;</span></div>' +
      '<div class="res-row"><span class="res-label">Off-Axis da Antena (Sat.) ' + tooltip('Desvio angular da estação em relação à direção principal do feixe de transmissão do satélite.') + '</span><span class="res-val">' + geo.offAxis.toFixed(2) + '&deg;</span></div>' +
    '</div>' +
    
    '<div class="res-card" style="border-left: 4px solid #f5c2e7;"><h4>Enlace de Subida (Uplink) - Freq: ' + up.frequency.toFixed(2) + ' GHz</h4>' +
      '<div class="res-row"><span class="res-label">Potência TX Estação (Pt)</span><span class="res-val">' + up.ptx_w.toFixed(1) + ' W (' + up.ptx_dbw.toFixed(1) + ' dBW)</span></div>' +
      '<div class="res-row"><span class="res-label">Perda Guia de Onda TX</span><span class="res-val">' + up.tx_loss.toFixed(1) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Ganho Antena Estação (Tx)</span><span class="res-val">' + up.gtx.toFixed(1) + ' dBi</span></div>' +
      '<div class="res-row"><span class="res-label">EIRP Subida</span><span class="res-val">' + up.eirp.toFixed(1) + ' dBW</span></div>' +
      '<div class="res-row"><span class="res-label">Atenuação Espaço Livre (FSPL)</span><span class="res-val">' + up.fspl.toFixed(1) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Perda Atmosférica (Subida)</span><span class="res-val">' + up.losses.atm.toFixed(2) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Perda por Chuva (Subida)</span><span class="res-val">' + up.losses.rain.toFixed(2) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Ganho Antena Satélite (Rx)</span><span class="res-val">' + up.rx_gain.toFixed(1) + ' dBi</span></div>' +
      '<div class="res-row"><span class="res-label">Potência Recebida no Satélite</span><span class="res-val" style="color:#f5c2e7;">' + up.prx_dbm.toFixed(1) + ' dBm</span></div>' +
    '</div>' +
    waterfallUp +
    
    '<div class="res-card" style="border-left: 4px solid #89b4fa;"><h4>Enlace de Descida (Downlink) - Freq: ' + down.frequency.toFixed(2) + ' GHz</h4>' +
      '<div class="res-row"><span class="res-label">Potência TX Satélite (Pt)</span><span class="res-val">' + down.ptx_w.toFixed(1) + ' W (' + down.ptx_dbw.toFixed(1) + ' dBW)</span></div>' +
      '<div class="res-row"><span class="res-label">Perda Guia de Onda TX</span><span class="res-val">' + down.tx_loss.toFixed(1) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Ganho Antena Satélite (Tx)</span><span class="res-val">' + down.satAnt.gain.toFixed(1) + ' dBi</span></div>' +
      '<div class="res-row"><span class="res-label">EIRP Descida</span><span class="res-val">' + down.eirp.toFixed(1) + ' dBW</span></div>' +
      '<div class="res-row"><span class="res-label">Atenuação Espaço Livre (FSPL)</span><span class="res-val">' + down.fspl.toFixed(1) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Perda Atmosférica (Descida)</span><span class="res-val">' + down.losses.atm.toFixed(2) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Perda por Chuva (Descida)</span><span class="res-val">' + down.losses.rain.toFixed(2) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Ganho Antena Estação (Rx)</span><span class="res-val">' + down.rx_gain.toFixed(1) + ' dBi</span></div>' +
      '<div class="res-row"><span class="res-label">Potência Recebida na Estação</span><span class="res-val" style="color:#89b4fa;">' + down.prx_dbm.toFixed(1) + ' dBm</span></div>' +
    '</div>' +
    waterfallDown +
    
    '<div class="res-card"><h4>Condicoes Ambientais (Opcionais)</h4>' +
      '<div style="display:flex; justify-content:space-around; align-items:center; font-size:11px; padding:3px 0;">' +
        '<label style="display:flex; align-items:center; gap:5px; cursor:pointer;"><input type="checkbox" id="chk_loss_atm"' + (USE_LOSS_ATM ? ' checked' : '') + ' onchange="toggleLossAtm(this.checked)"> Atmosfera</label>' +
        '<label style="display:flex; align-items:center; gap:5px; cursor:pointer;"><input type="checkbox" id="chk_loss_rain"' + (USE_LOSS_RAIN ? ' checked' : '') + ' onchange="toggleLossRain(this.checked)"> Chuva</label>' +
      '</div>' +
      rainControlsHtml +
    '</div>' +
    
    '<div class="res-card" style="border-left: 4px solid #a6e3a1; background: rgba(166, 227, 161, 0.035);"><h4>Desempenho Combinado (Uplink + Downlink)</h4>' +
      '<div class="res-row"><span class="res-label">Eb/N0 Total Obtido</span><span class="res-val" style="color:#a6e3a1; font-weight:bold;">' + total.ebn0.toFixed(2) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Eb/N0 Requerido (BER 10⁻⁶)</span><span class="res-val">' + total.ebn0_req.toFixed(1) + ' dB</span></div>' +
      '<div style="text-align:center; margin-top:10px;">' + margemBadge + '</div>' +
    '</div>';
  document.getElementById('tab-link').innerHTML = linkHtml;
  
  // Contribuições de Ruído
  var c_ant_sat = up.t_ant;
  var c_lna_sat = up.t_lna;
  var c_other_sat = up.t_eff - c_lna_sat;
  
  var c_ant_gs = down.t_ant;
  var c_lna_gs = down.t_lna;
  var c_other_gs = down.t_eff - c_lna_gs;
  
  // Renderização ── TAB: RUIDO
  var noiseHtml = 
    '<div class="res-card" style="border-left: 4px solid #f5c2e7;"><h4>Receptor do Satelite (Uplink)</h4>' +
      '<div class="res-row"><span class="res-label">Temp. Ruido Sistema (Tsys)</span><span class="res-val" style="color:#f9e2af;">' + up.t_sys.toFixed(1) + ' K</span></div>' +
      '<div class="res-row"><span class="res-label">Figura de Merito G/T</span><span class="res-val">' + up.gt.toFixed(2) + ' dB/K</span></div>' +
      '<div class="res-row"><span class="res-label">Relacao C/N0 Subida</span><span class="res-val" style="color:#f5c2e7;">' + up.cn0.toFixed(2) + ' dB-Hz</span></div>' +
      '<table style="width:100%; border-collapse:collapse; margin-top:10px; font-size:10px; text-align:left;">' +
        '<thead>' +
          '<tr style="border-bottom:1px solid rgba(245,194,231,0.3); color:#f5c2e7; font-weight:bold;">' +
            '<th style="padding:4px 0;">Estagio</th>' +
            '<th style="padding:4px 0; text-align:right;">Temp (K)</th>' +
            '<th style="padding:4px 0; text-align:right;">Ganho (dB)</th>' +
            '<th style="padding:4px 0; text-align:right;">Contrib (K)</th>' +
          '</tr>' +
        '</thead>' +
        '<tbody>' +
          '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">' +
            '<td style="padding:4px 0;">Antena</td>' +
            '<td style="padding:4px 0; text-align:right;">' + up.t_ant.toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">-</td>' +
            '<td style="padding:4px 0; text-align:right;">' + c_ant_sat.toFixed(1) + '</td>' +
          '</tr>' +
          '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">' +
            '<td style="padding:4px 0;">LNA</td>' +
            '<td style="padding:4px 0; text-align:right;">' + up.t_lna.toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">' + up.g_lna.toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">' + c_lna_sat.toFixed(1) + '</td>' +
          '</tr>' +
          '<tr>' +
            '<td style="padding:4px 0;">Rec/Mixer</td>' +
            '<td style="padding:4px 0; text-align:right;">' + (up.t_rec + up.t_down).toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">-</td>' +
            '<td style="padding:4px 0; text-align:right;">' + c_other_sat.toFixed(3) + '</td>' +
          '</tr>' +
        '</tbody>' +
      '</table>' +
    '</div>' +
    
    '<div class="res-card" style="border-left: 4px solid #89b4fa;"><h4>Receptor da Estacao (Downlink)</h4>' +
      '<div class="res-row"><span class="res-label">Temp. Ruido Sistema (Tsys)</span><span class="res-val" style="color:#f9e2af;">' + down.t_sys.toFixed(1) + ' K</span></div>' +
      '<div class="res-row"><span class="res-label">Figura de Merito G/T</span><span class="res-val">' + down.gt.toFixed(2) + ' dB/K</span></div>' +
      '<div class="res-row"><span class="res-label">Relacao C/N0 Descida</span><span class="res-val" style="color:#89b4fa;">' + down.cn0.toFixed(2) + ' dB-Hz</span></div>' +
      '<table style="width:100%; border-collapse:collapse; margin-top:10px; font-size:10px; text-align:left;">' +
        '<thead>' +
          '<tr style="border-bottom:1px solid rgba(137,220,235,0.3); color:#89b4fa; font-weight:bold;">' +
            '<th style="padding:4px 0;">Estagio</th>' +
            '<th style="padding:4px 0; text-align:right;">Temp (K)</th>' +
            '<th style="padding:4px 0; text-align:right;">Ganho (dB)</th>' +
            '<th style="padding:4px 0; text-align:right;">Contrib (K)</th>' +
          '</tr>' +
        '</thead>' +
        '<tbody>' +
          '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">' +
            '<td style="padding:4px 0;">Antena</td>' +
            '<td style="padding:4px 0; text-align:right;">' + down.t_ant.toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">-</td>' +
            '<td style="padding:4px 0; text-align:right;">' + c_ant_gs.toFixed(1) + '</td>' +
          '</tr>' +
          '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">' +
            '<td style="padding:4px 0;">LNA</td>' +
            '<td style="padding:4px 0; text-align:right;">' + down.t_lna.toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">' + down.g_lna.toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">' + c_lna_gs.toFixed(1) + '</td>' +
          '</tr>' +
          '<tr>' +
            '<td style="padding:4px 0;">Rec/Mixer</td>' +
            '<td style="padding:4px 0; text-align:right;">' + (down.t_rec + down.t_down).toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">-</td>' +
            '<td style="padding:4px 0; text-align:right;">' + c_other_gs.toFixed(3) + '</td>' +
          '</tr>' +
        '</tbody>' +
      '</table>' +
    '</div>' +
    
    '<div class="res-card" style="border-left: 4px solid #a6e3a1;"><h4>Portadora & Ruído Combinado no Canal</h4>' +
      '<div class="res-row"><span class="res-label">C/N0 Combinado</span><span class="res-val" style="color:#a6e3a1; font-weight:bold;">' + total.cn0.toFixed(2) + ' dB-Hz</span></div>' +
      '<div class="field" style="margin-top:10px;"><label>Largura de Banda do Canal (MHz) ' + tooltip('Largura de banda do transponder RF ocupada pelo sinal transmitido.') + '</label>' +
      '<input type="number" id="inp_bw" step="1" value="' + BW_MHZ + '" oninput="changeBW(this.value)"></div>' +
      '<div class="res-row"><span class="res-label">C/N Combinado no Canal</span><span class="res-val" style="font-weight:bold;">' + total.cn.toFixed(2) + ' dB</span></div>' +
    '</div>';
  document.getElementById('tab-noise').innerHTML = noiseHtml;
  
  // Renderização ── TAB: BER
  var berBadge = total.ber < 1e-6 ? '<span class="badge badge-green">Excelente (BER < 10⁻⁶)</span>' :
                 (total.ber <= 1e-3 ? '<span class="badge badge-yellow">Limiar (10⁻⁶ a 10⁻³)</span>' :
                               '<span class="badge badge-red">Inviavel (BER > 10⁻³)</span>');
                               
  var chartSvg = gerarBerChart(total.ebn0, total.ber, MOD_TYPE);
                               
  var perfHtml = 
    '<div class="res-card"><h4>Configuracoes de Transmissao</h4>' +
      '<div class="field"><label>Taxa de Bits Rb (Mbps) ' + tooltip('Taxa de dados líquida efetiva transmitida por segundo.') + '</label>' +
      '<input type="number" id="inp_rb" step="1" value="' + RB_MBPS + '" oninput="changeRB(this.value)"></div>' +
      '<div class="field"><label>Modulacao ' + tooltip('Esquema de modulação de fase ou amplitude utilizado para formatar o fluxo digital.') + '</label>' +
      '<select id="inp_mod" onchange="changeMod(this.value)">' +
        '<option value="BPSK"' + (MOD_TYPE === 'BPSK' ? ' selected' : '') + '>BPSK</option>' +
        '<option value="QPSK"' + (MOD_TYPE === 'QPSK' ? ' selected' : '') + '>QPSK</option>' +
        '<option value="8PSK"' + (MOD_TYPE === '8PSK' ? ' selected' : '') + '>8PSK</option>' +
        '<option value="16QAM"' + (MOD_TYPE === '16QAM' ? ' selected' : '') + '>16QAM</option>' +
      '</select></div>' +
    '</div>' +
    '<div class="res-card"><h4>Desempenho Combinado (Uplink + Downlink)</h4>' +
      '<div class="res-row"><span class="res-label">Eb/N0 Combinado</span><span class="res-val" style="color:#a6e3a1; font-weight:bold;">' + total.ebn0.toFixed(2) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Bit Error Rate (BER)</span><span class="res-val" style="color:#f38ba8; font-weight:bold;">' + total.ber.toExponential(3) + '</span></div>' +
      '<div style="text-align:center; margin-top:10px;">' + berBadge + '</div>' +
      '<div style="text-align:center; margin-top:12px;">' + chartSvg + '</div>' +
    '</div>';
  document.getElementById('tab-perf').innerHTML = perfHtml;
  
  // Renderização ── TAB: PDF
  var pdfHtml = 
    '<div class="res-card" style="text-align:center; padding:15px 12px;">' +
      '<h4>Relatório PDF Customizado</h4>' +
      '<p style="font-size:11px; margin-bottom:12px; line-height:1.4; color:#a6adc8;">Relatório técnico consolidado do enlace completo de subida e descida com tabelas de perdas, cascata de ruído e gráficos de BER.</p>' +
      '<button class="save-btn" onclick="gerarPDFCliente()">💾 Baixar Relatório PDF</button>' +
    '</div>' +
    '<div class="res-card" style="text-align:center; padding:15px 12px;">' +
      '<h4>Impressão Rápida</h4>' +
      '<p style="font-size:11px; margin-bottom:12px; line-height:1.4; color:#a6adc8;">Ou imprima diretamente a visualização limpa A4 formatada pelo navegador.</p>' +
      '<button class="save-btn" style="background:rgba(50,70,90,0.5);" onclick="window.print()">&#128196; Imprimir Tela</button>' +
    '</div>';
  document.getElementById('tab-pdf').innerHTML = pdfHtml;
}}

function gerarPDFCliente() {{
  const {{ jsPDF }} = window.jspdf;
  const doc = new jsPDF();
  
  // Obter link ativo
  var sel = document.getElementById('link_selector');
  if (!sel || !sel.value) return;
  var ids = sel.value.split('-');
  var stIdx = parseInt(ids[0]);
  var satIdx = parseInt(ids[1]);
  var st = STNS[stIdx];
  var sat = SATS[satIdx];
  
  var res = calcularLinkCompleto(st, sat);
  var geo = res.geo;
  var up = res.up;
  var down = res.down;
  var total = res.total;
  
  // ── HEADER ──
  function drawHeader(pageTitle, pageNum) {{
    doc.setFillColor(14, 28, 56);
    doc.rect(0, 0, 210, 28, "F");
    
    doc.setTextColor(137, 220, 235);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.text("COMSAT SIMULATOR - RELATORIO TECNICO DE ENLACE", 105, 12, {{ align: "center" }});
    
    doc.setTextColor(200, 200, 200);
    doc.setFont("helvetica", "italic");
    doc.setFontSize(9);
    doc.text(pageTitle, 105, 20, {{ align: "center" }});
    
    doc.setFont("helvetica", "italic");
    doc.setFontSize(8);
    doc.setTextColor(128, 128, 128);
    doc.text("Pagina " + pageNum, 105, 285, {{ align: "center" }});
  }}
  
  // Helpers para seções e chaves/valores
  let currentY = 38;
  function drawSectionHeader(title) {{
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10.5);
    doc.setTextColor(14, 28, 56);
    doc.text(title, 15, currentY);
    doc.setDrawColor(14, 28, 56);
    doc.setLineWidth(0.3);
    doc.line(15, currentY + 1.5, 195, currentY + 1.5);
    currentY += 8;
  }}
  
  function drawKeyValueRow(items) {{
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8.5);
    let startX = 15;
    let step = 60;
    
    items.forEach(function(item) {{
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100, 100, 100);
      doc.text(item[0] + ": ", startX, currentY);
      let offset = doc.getTextWidth(item[0] + ": ");
      
      doc.setFont("helvetica", "bold");
      doc.setTextColor(20, 20, 20);
      doc.text(item[1].toString(), startX + offset, currentY);
      
      startX += step;
    }});
    currentY += 6;
  }}
  
  // ==========================================
  // PAGE 1: GERAL, GEOMETRIA E BALANÇOS
  // ==========================================
  drawHeader("Calculo Completo de Subida (Uplink), Descida (Downlink) e Margem Combinada", "1/2");
  
  // Seção 1
  drawSectionHeader("1. INFORMACOES GERAIS DO CENARIO");
  drawKeyValueRow([
    ["Satelite", sat.name],
    ["Tipo de Orbita", "GEO"],
    ["Longitude Orbital", sat.lng.toFixed(1) + "°"]
  ]);
  drawKeyValueRow([
    ["Estacao Terrena", st.name],
    ["Latitude Est.", st.lat.toFixed(4) + "°"],
    ["Longitude Est.", st.lng.toFixed(4) + "°"]
  ]);
  
  // Seção 2
  currentY += 2;
  drawSectionHeader("2. GEOMETRIA DE APONTAMENTO");
  drawKeyValueRow([
    ["Distancia (Slant Range)", geo.distance.toFixed(2) + " km"],
    ["Angulo de Elevacao", geo.elevation.toFixed(2) + "°"],
    ["Off-Axis (Apontamento)", geo.offAxis.toFixed(2) + "°"]
  ]);
  
  // Seção 3: Uplink
  currentY += 2;
  drawSectionHeader("3. BALANCO DE POTENCIA - ENLACE DE SUBIDA (UPLINK)");
  drawKeyValueRow([
    ["Frequencia Subida", up.frequency.toFixed(2) + " GHz"],
    ["Potencia HPA (Pt)", up.ptx_w.toFixed(1) + " W (" + up.ptx_dbw.toFixed(1) + " dBW)"],
    ["Perda Guia Estacao", up.tx_loss.toFixed(1) + " dB"]
  ]);
  drawKeyValueRow([
    ["Ganho Antena Est.", up.gtx.toFixed(1) + " dBi"],
    ["EIRP Subida", up.eirp.toFixed(1) + " dBW"],
    ["FSPL Subida", up.fspl.toFixed(1) + " dB"]
  ]);
  var statusAtm = USE_LOSS_ATM ? "ON" : "OFF";
  var statusRain = USE_LOSS_RAIN ? "ON" : "OFF";
  drawKeyValueRow([
    ["Absorcao Atmosfera", up.losses.atm.toFixed(2) + " dB (" + statusAtm + ")"],
    ["Atenuacao Chuva", up.losses.rain.toFixed(2) + " dB (" + statusRain + ")"],
    ["Ganho Antena Sat (Rx)", up.rx_gain.toFixed(1) + " dBi"]
  ]);
  drawKeyValueRow([
    ["Potencia Recebida", up.prx_dbm.toFixed(2) + " dBm"],
    ["Perdas Guia Sat (Lrx)", up.rx_loss.toFixed(1) + " dB"],
    ["C/N0 de Subida", up.cn0.toFixed(2) + " dB-Hz"]
  ]);
  
  // Seção 4: Downlink
  currentY += 2;
  drawSectionHeader("4. BALANCO DE POTENCIA - ENLACE DE DESCIDA (DOWNLINK)");
  drawKeyValueRow([
    ["Frequencia Descida", down.frequency.toFixed(2) + " GHz"],
    ["Potencia TX Sat (Pt)", down.ptx_w.toFixed(1) + " W (" + down.ptx_dbw.toFixed(1) + " dBW)"],
    ["Perda Guia Sat (Ltx)", down.tx_loss.toFixed(1) + " dB"]
  ]);
  drawKeyValueRow([
    ["Ganho Antena Sat.", down.satAnt.gain.toFixed(1) + " dBi"],
    ["EIRP Descida", down.eirp.toFixed(1) + " dBW"],
    ["FSPL Descida", down.fspl.toFixed(1) + " dB"]
  ]);
  drawKeyValueRow([
    ["Absorcao Atmosfera", down.losses.atm.toFixed(2) + " dB (" + statusAtm + ")"],
    ["Atenuacao Chuva", down.losses.rain.toFixed(2) + " dB (" + statusRain + ")"],
    ["Ganho Antena Est (Rx)", down.rx_gain.toFixed(1) + " dBi"]
  ]);
  drawKeyValueRow([
    ["Potencia Recebida", down.prx_dbm.toFixed(2) + " dBm"],
    ["Perdas Guia Est (Lrx)", LOSS_RX_LINE.toFixed(1) + " dB"],
    ["C/N0 de Descida", down.cn0.toFixed(2) + " dB-Hz"]
  ]);

  // Seção 5: Combinado
  currentY += 2;
  drawSectionHeader("5. DESEMPENHO COMBINADO (TOTAL)");
  drawKeyValueRow([
    ["C/N0 Combinado", total.cn0.toFixed(2) + " dB-Hz"],
    ["Largura de Banda", BW_MHZ.toFixed(1) + " MHz"],
    ["C/N no Canal", total.cn.toFixed(2) + " dB"]
  ]);
  drawKeyValueRow([
    ["Eb/N0 Total Obtido", total.ebn0.toFixed(2) + " dB"],
    ["Eb/N0 Requerido", total.ebn0_req.toFixed(1) + " dB"],
    ["Margem Combinada", total.margem.toFixed(2) + " dB (" + (total.margem >= 0 ? "Aprovado" : "Falhou") + ")"]
  ]);

  // ==========================================
  // PAGE 2: CASCATAS DE RUÍDO E CURVA DE BER
  // ==========================================
  doc.addPage();
  currentY = 38;
  drawHeader("Cascata de Temperatura de Ruido (Friis), Analise de Portadora/Ruido e BER", "2/2");
  
  // Seção 6: Cascata Satélite
  drawSectionHeader("6. CASCATA DE RUIDO - RECEPTOR DE BORDO DO SATELITE");
  doc.setFillColor(235, 240, 248);
  doc.rect(15, currentY, 180, 5, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(8);
  doc.setTextColor(14, 28, 56);
  doc.text("Estagio Receptor de Bordo (Sat)", 17, currentY + 3.5);
  doc.text("Temp. Estagio (K)", 80, currentY + 3.5);
  doc.text("Ganho (dB)", 125, currentY + 3.5);
  doc.text("Contrib. para Tsys (K)", 160, currentY + 3.5);
  
  currentY += 5;
  doc.setFont("helvetica", "normal");
  doc.setTextColor(20, 20, 20);
  
  // Contribuições de Ruído Satélite
  var c_ant_sat = up.t_ant;
  var c_lna_sat = up.t_lna;
  var c_other_sat = up.t_eff - c_lna_sat;
  
  doc.rect(15, currentY, 180, 4.5);
  doc.text("Antena Receptora (Sat)", 17, currentY + 3.2);
  doc.text(up.t_ant.toFixed(1), 80, currentY + 3.2);
  doc.text("-", 125, currentY + 3.2);
  doc.text(c_ant_sat.toFixed(1), 160, currentY + 3.2);
  currentY += 4.5;
  
  doc.rect(15, currentY, 180, 4.5);
  doc.text("Amplificador LNA (Sat)", 17, currentY + 3.2);
  doc.text(up.t_lna.toFixed(1), 80, currentY + 3.2);
  doc.text(up.g_lna.toFixed(1), 125, currentY + 3.2);
  doc.text(c_lna_sat.toFixed(1), 160, currentY + 3.2);
  currentY += 4.5;
  
  doc.rect(15, currentY, 180, 4.5);
  doc.text("Estagios Seguintes (Sat)", 17, currentY + 3.2);
  doc.text((up.t_rec + up.t_down).toFixed(1), 80, currentY + 3.2);
  doc.text("-", 125, currentY + 3.2);
  doc.text(c_other_sat.toFixed(3), 160, currentY + 3.2);
  currentY += 8;

  // Seção 7: Cascata Estação Terrena
  drawSectionHeader("7. CASCATA DE RUIDO - RECEPTOR DA ESTACAO TERRENA");
  doc.setFillColor(235, 240, 248);
  doc.rect(15, currentY, 180, 5, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(8);
  doc.setTextColor(14, 28, 56);
  doc.text("Estagio Receptor Terrestre (Estacao)", 17, currentY + 3.5);
  doc.text("Temp. Estagio (K)", 80, currentY + 3.5);
  doc.text("Ganho (dB)", 125, currentY + 3.5);
  doc.text("Contrib. para Tsys (K)", 160, currentY + 3.5);
  
  currentY += 5;
  doc.setFont("helvetica", "normal");
  doc.setTextColor(20, 20, 20);
  
  // Contribuições de Ruído Estação
  var c_ant_gs = down.t_ant;
  var c_lna_gs = down.t_lna;
  var c_other_gs = down.t_eff - c_lna_gs;
  
  doc.rect(15, currentY, 180, 4.5);
  doc.text("Antena Receptora (Estacao)", 17, currentY + 3.2);
  doc.text(down.t_ant.toFixed(1), 80, currentY + 3.2);
  doc.text("-", 125, currentY + 3.2);
  doc.text(c_ant_gs.toFixed(1), 160, currentY + 3.2);
  currentY += 4.5;
  
  doc.rect(15, currentY, 180, 4.5);
  doc.text("Amplificador LNA (Estacao)", 17, currentY + 3.2);
  doc.text(down.t_lna.toFixed(1), 80, currentY + 3.2);
  doc.text(down.g_lna.toFixed(1), 125, currentY + 3.2);
  doc.text(c_lna_gs.toFixed(1), 160, currentY + 3.2);
  currentY += 4.5;
  
  doc.rect(15, currentY, 180, 4.5);
  doc.text("Estagios Seguintes (Estacao)", 17, currentY + 3.2);
  doc.text((down.t_rec + down.t_down).toFixed(1), 80, currentY + 3.2);
  doc.text("-", 125, currentY + 3.2);
  doc.text(c_other_gs.toFixed(3), 160, currentY + 3.2);
  currentY += 8;

  // Seção 8: Gráfico de BER
  drawSectionHeader("8. DESEMPENHO E GRAFICO DE BER COMBINADO");
  drawKeyValueRow([
    ["Taxa de Bits (Rb)", RB_MBPS.toFixed(1) + " Mbps"],
    ["Modulacao Ativa", MOD_TYPE],
    ["Eb/N0 Combinado", total.ebn0.toFixed(2) + " dB"]
  ]);
  drawKeyValueRow([
    ["BER Combinada Estimada", total.ber.toExponential(3)],
    ["Status de Qualidade", (total.margem >= 0 ? "APROVADO" : "REPROVADO")]
  ]);
  
  currentY += 2;
  var chartX = 35;
  var chartY = currentY;
  var chartW = 140;
  var chartH = 58;
  
  doc.setFillColor(245, 248, 252);
  doc.rect(chartX, chartY, chartW, chartH, "F");
  doc.setDrawColor(30, 95, 138);
  doc.setLineWidth(0.3);
  doc.rect(chartX, chartY, chartW, chartH, "D");
  
  // Grid Lines Horizontais
  doc.setFont("helvetica", "normal");
  doc.setFontSize(7);
  doc.setTextColor(80, 80, 80);
  for (var logY = 0; logY >= -8; logY--) {{
    var py = chartY + (logY / -8.0) * chartH;
    doc.setDrawColor(210, 220, 230);
    doc.line(chartX, py, chartX + chartW, py);
    var lbl = logY === 0 ? "1" : "10^-" + Math.abs(logY);
    doc.text(lbl, chartX - 10, py + 1.5);
  }}
  
  // Grid Lines Verticais
  for (var db = 0; db <= 16; db += 2) {{
    var px = chartX + (db / 16.0) * chartW;
    doc.setDrawColor(210, 220, 230);
    doc.line(px, chartY, px, chartY + chartH);
    doc.text(db.toString(), px - 1.5, chartY + chartH + 4.0);
  }}
  
  doc.setFont("helvetica", "bold");
  doc.text("Eb/N0 (dB)", chartX + chartW/2 - 8, chartY + chartH + 8.5);
  
  // Função para curva teórica
  function computeCurveBer(eb_n0_db, mod) {{
    var eb_n0_lin = Math.pow(10, eb_n0_db / 10.0);
    if (mod === 'BPSK') {{
      return 0.5 * erfc(Math.sqrt(eb_n0_lin));
    }} else if (mod === '8PSK') {{
      return (1.0 / 3.0) * erfc(Math.sqrt(3.0 * eb_n0_lin) * Math.sin(Math.PI / 8.0));
    }} else if (mod === '16QAM') {{
      return 0.375 * erfc(Math.sqrt(0.4 * eb_n0_lin));
    }}
    return 0.0;
  }}
  
  var curves = ['BPSK', '8PSK', '16QAM'];
  var colors = {{
    'BPSK': [0, 120, 200],
    '8PSK': [220, 150, 0],
    '16QAM': [0, 140, 70]
  }};
  
  curves.forEach(function(cMod) {{
    var isActive = (MOD_TYPE === cMod || (MOD_TYPE === 'QPSK' && cMod === 'BPSK'));
    doc.setLineWidth(isActive ? 0.7 : 0.25);
    doc.setDrawColor(colors[cMod][0], colors[cMod][1], colors[cMod][2]);
    
    var lastPx = null, lastPy = null;
    for (var i = 0; i <= 32; i++) {{
      var db = (i / 32.0) * 16.0;
      var yBer = computeCurveBer(db, cMod);
      var px = chartX + (db / 16.0) * chartW;
      
      var logBer = yBer > 0 ? Math.log10(yBer) : -8.0;
      logBer = Math.max(-8.0, Math.min(0.0, logBer));
      var py = chartY + (logBer / -8.0) * chartH;
      
      if (lastPx !== null) {{
        doc.line(lastPx, lastPy, px, py);
      }}
      lastPx = px;
      lastPy = py;
    }}
  }});
  
  // Ponto de operação ativo
  var pxActive = chartX + (total.ebn0 / 16.0) * chartW;
  var logBerActive = total.ber > 0 ? Math.log10(total.ber) : -8.0;
  logBerActive = Math.max(-8.0, Math.min(0.0, logBerActive));
  var pyActive = chartY + (logBerActive / -8.0) * chartH;
  
  doc.setFillColor(243, 100, 120);
  doc.setDrawColor(0, 0, 0);
  doc.setLineWidth(0.4);
  doc.circle(pxActive, pyActive, 1.8, "FD");
  
  // Legenda
  doc.setFont("helvetica", "normal");
  doc.setFontSize(6);
  doc.setTextColor(40, 40, 40);
  
  doc.setFillColor(colors['BPSK'][0], colors['BPSK'][1], colors['BPSK'][2]);
  doc.rect(chartX + 4, chartY + 2, 3, 2, "F");
  doc.text("BPSK/QPSK", chartX + 8, chartY + 3.8);
  
  doc.setFillColor(colors['8PSK'][0], colors['8PSK'][1], colors['8PSK'][2]);
  doc.rect(chartX + 40, chartY + 2, 3, 2, "F");
  doc.text("8PSK", chartX + 44, chartY + 3.8);
  
  doc.setFillColor(colors['16QAM'][0], colors['16QAM'][1], colors['16QAM'][2]);
  doc.rect(chartX + 70, chartY + 2, 3, 2, "F");
  doc.text("16QAM", chartX + 74, chartY + 3.8);
  
  doc.setFillColor(243, 100, 120);
  doc.circle(chartX + 105, chartY + 2.8, 1.0, "F");
  doc.setFont("helvetica", "bold");
  doc.text("LINK OP", chartX + 108, chartY + 3.8);
  
  doc.save("ComSat_Relatorio_" + sat.name + "_" + st.name + ".pdf");
}}

function changeBW(val) {{
  BW_MHZ = parseFloat(val) || 36.0;
  atualizarAnalise();
}}

function changeRB(val) {{
  RB_MBPS = parseFloat(val) || 50.0;
  atualizarAnalise();
}}

function changeMod(val) {{
  MOD_TYPE = val;
  atualizarAnalise();
}}

function reconstruirSeletores() {{
  var container = document.getElementById('linkSelectorContainer');
  if (!SATS.length || !STNS.length) {{
    container.innerHTML = '<p class="placeholder" style="margin:0; font-size:11px;">Nenhum enlace ativo.</p>';
    return;
  }}
  
  var html = '<div class="field" style="margin:0;"><label style="font-size:9px; color:#89dceb;">Enlace Ativo</label>' +
             '<select id="link_selector" onchange="atualizarAnalise()" style="background:rgba(20,40,80,0.85); font-size:11.5px; padding:4px 6px;">';
  
  // Mapeia todas as conexões
  for (var i = 0; i < STNS.length; i++) {{
    for (var j = 0; j < SATS.length; j++) {{
      html += '<option value="' + i + '-' + j + '">' + STNS[i].name + ' &rarr; ' + SATS[j].name + '</option>';
    }}
  }}
  html += '</select></div>';
  container.innerHTML = html;
}}

// Inicialização dos seletores e cálculos na primeira carga
reconstruirSeletores();
atualizarAnalise();

window.addEventListener('resize', function() {{
  globe.width(window.innerWidth).height(window.innerHeight);
}});
</script>
</body>
</html>"""
