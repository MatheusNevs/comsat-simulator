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
        "pattern_data": s.pattern_data
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
        "temp_antenna": s.temp_antenna_k,
        "temp_lna": s.temp_lna_k,
        "gain_lna": s.gain_lna_db,
        "temp_down": s.temp_down_k,
        "nf_rec": s.nf_rec_db
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
.field label {{ display:block; color:#7a9cc0; font-size:10px; margin-bottom:3px; text-transform:uppercase; letter-spacing:0.5px; }}
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
.res-row {{ display:flex; justify-content:space-between; font-size:12px; margin-bottom:5px; }}
.res-row:last-child {{ margin-bottom:0; }}
.res-label {{ color:#7a9cc0; }}
.res-val {{ color:#cdd6f4; font-weight:600; font-family:monospace; }}
.badge {{ display:inline-block; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; text-transform:uppercase; }}
.badge-green {{ background:rgba(166,227,161,0.2); color:#a6e3a1; border:1px solid #a6e3a1; }}
.badge-yellow {{ background:rgba(249,226,175,0.2); color:#f9e2af; border:1px solid #f9e2af; }}
.badge-red {{ background:rgba(243,139,168,0.2); color:#f38ba8; border:1px solid #f38ba8; }}

/* ── Estilos de Impressão (Etapa 6 PDF) ── */
#printTitle {{ display:none; }}
@media print {{
  html, body {{ background:#fff !important; color:#000 !important; overflow:visible !important; }}
  #globeViz, #toggleBtn, #infoPanel, #linkSelectorContainer, .rtabs, #closePanelBtn, #rightPanelHead {{ display:none !important; }}
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
var LOSS_TX_LINE = 1.0;

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
    '<div class="field"><label>Diagrama de Radiacao</label>' +
    '<select id="f_pat_type" onchange="onSatPatternChange()">' +
      '<option value="Isotrópica"' + (d.pattern_type === 'Isotrópica' ? ' selected' : '') + '>Isotrópica</option>' +
      '<option value="Modelo Parabólico"' + (d.pattern_type === 'Modelo Parabólico' ? ' selected' : '') + '>Modelo Parabólico</option>' +
      '<option value="CSV"' + (d.pattern_type === 'CSV' ? ' selected' : '') + ' disabled>Carregado por CSV (' + (d.pattern_data ? 'Ativo' : 'Nenhum') + ')</option>' +
    '</select></div>';

  var hpbwStyle = d.pattern_type === 'Modelo Parabólico' ? 'block' : 'none';

  showInfo('Satelite: ' + d.name,
    '<form onsubmit="saveSat(event)">' +
    '<div class="field"><label>Nome</label><input type="text" id="f_name" value="' + d.name + '"></div>' +
    '<div class="field"><label>Longitude Orbital (graus)</label><input type="number" id="f_lng" step="0.1" value="' + d.lng + '"></div>' +
    '<div class="field"><label>Frequencia (GHz)</label><input type="number" id="f_freq" step="0.1" value="' + d.frequency + '"></div>' +
    '<div class="field"><label>Potencia TX (W)</label><input type="number" id="f_power" step="1" value="' + d.tx_power + '"></div>' +
    '<div class="field"><label>Ganho Antena TX Pico (dBi)</label><input type="number" id="f_gain" step="0.5" value="' + d.tx_gain + '"></div>' +
    selectHtml +
    '<div class="field" id="f_pat_hpbw_field" style="display:' + hpbwStyle + ';"><label>Largura de Feixe θ_3dB (graus)</label><input type="number" id="f_pat_hpbw" step="0.1" value="' + (d.pattern_hpbw || 2.0) + '"></div>' +
    '<button class="save-btn" type="submit">&#128190; Salvar</button>' +
    '</form><div id="saveMsg">&#9989; Salvo!</div>'
  );
}}

function showStationPanel(d) {{
  currentStation = d;
  
  var modeSelect = 
    '<div class="field"><label>Definicao do Ganho</label>' +
    '<select id="s_gain_mode" onchange="onStationGainModeChange()">' +
      '<option value="Valor Direto"' + (d.gain_mode === 'Valor Direto' ? ' selected' : '') + '>Valor Direto (dBi)</option>' +
      '<option value="Diâmetro e Eficiência"' + (d.gain_mode === 'Diâmetro e Eficiência' ? ' selected' : '') + '>Diâmetro e Eficiência</option>' +
    '</select></div>';
    
  var directStyle = (d.gain_mode === 'Valor Direto' || !d.gain_mode) ? 'block' : 'none';
  var physStyle = d.gain_mode === 'Diâmetro e Eficiência' ? 'block' : 'none';

  showInfo('Estacao: ' + d.name,
    '<form onsubmit="saveStation(event)">' +
    '<div class="field"><label>Nome</label><input type="text" id="s_name" value="' + d.name + '"></div>' +
    '<div class="field"><label>Latitude</label><input type="number" id="s_lat" step="0.0001" value="' + d.lat.toFixed(4) + '"></div>' +
    '<div class="field"><label>Longitude</label><input type="number" id="s_lng" step="0.0001" value="' + d.lng.toFixed(4) + '"></div>' +
    
    modeSelect +
    
    '<div id="s_gain_direct_field" style="display:' + directStyle + ';">' +
      '<div class="field"><label>Ganho Antena RX (dBi)</label><input type="number" id="s_gain" step="0.5" value="' + d.rx_gain + '"></div>' +
    '</div>' +
    
    '<div id="s_gain_phys_field" style="display:' + physStyle + ';">' +
      '<div class="field"><label>Diâmetro da Antena (m)</label><input type="number" id="s_diam" step="0.1" value="' + (d.antenna_diameter || 1.8) + '"></div>' +
      '<div class="field"><label>Eficiência da Antena (%)</label><input type="number" id="s_eff" step="5" value="' + (d.antenna_efficiency || 60.0) + '"></div>' +
    '</div>' +
    
    '<h4 style="margin-top:12px; margin-bottom:6px; color:#89dceb; font-size:11px; border-bottom:1px solid #1e5f8a; padding-bottom:3px; text-transform:uppercase;">Parâmetros de Ruído</h4>' +
    '<div class="field"><label>Temp. Antena (K)</label><input type="number" id="s_t_ant" step="5" value="' + (d.temp_antenna || 50.0) + '"></div>' +
    '<div class="field"><label>Temp. LNA (K)</label><input type="number" id="s_t_lna" step="5" value="' + (d.temp_lna || 80.0) + '"></div>' +
    '<div class="field"><label>Ganho LNA (dB)</label><input type="number" id="s_g_lna" step="1" value="' + (d.gain_lna || 50.0) + '"></div>' +
    '<div class="field"><label>Temp. Downconverter (K)</label><input type="number" id="s_t_down" step="10" value="' + (d.temp_down || 290.0) + '"></div>' +
    '<div class="field"><label>Rec. Noise Figure (dB)</label><input type="number" id="s_nf_rec" step="0.5" value="' + (d.nf_rec || 8.0) + '"></div>' +

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
  
  if (currentStation.gain_mode === 'Valor Direto') {{
    currentStation.rx_gain          = parseFloat(document.getElementById('s_gain').value);
  }} else {{
    currentStation.antenna_diameter = parseFloat(document.getElementById('s_diam').value);
    currentStation.antenna_efficiency = parseFloat(document.getElementById('s_eff').value);
    
    // Cálculo do ganho com base no diâmetro, freq e ef
    var freq = SATS.length ? SATS[0].frequency : 12.0;
    var d_m = currentStation.antenna_diameter;
    var eff = currentStation.antenna_efficiency / 100.0;
    var g_dbi = 20 * Math.log10(d_m) + 20 * Math.log10(freq) + 20.4 + 10 * Math.log10(eff);
    currentStation.rx_gain = parseFloat(g_dbi.toFixed(2));
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
    
    // CÁLCULO DA POTÊNCIA RECEBIDA PARA COR DO ENLACE NO GLOBO
    var geo = calcularApontamento(st.lat, st.lng, nearest.lng);
    var satAnt = obterGanhoRealSat(nearest, geo.offAxis);
    var ptx_dbw = 10 * Math.log10(nearest.tx_power);
    var eirp = ptx_dbw - LOSS_TX_LINE + satAnt.gain;
    var fspl = 20 * Math.log10(geo.distance) + 20 * Math.log10(nearest.frequency) + 92.45;
    var totalLosses = LOSS_ATM + LOSS_RAIN + LOSS_POINT + LOSS_POL + LOSS_RX_LINE;
    var prx_dbw = eirp - fspl - totalLosses + st.rx_gain;
    var prx_dbm = prx_dbw + 30.0;
    
    // Cor dinâmica: Verde (ótimo), Amarelo (regular), Vermelho (ruim)
    var col = '#00ff88'; // > -90 dBm
    if (prx_dbm < -100.0) {{
      col = '#ff3333';
    }} else if (prx_dbm < -90.0) {{
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
          '<span style="color:#a6adc8;">1. Potência do Transmissor (Pt)</span>' +
          '<span class="res-val">' + ptx_dbw.toFixed(1) + ' dBW</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#89dceb; width:' + getWidth(ptx_dbw) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // Gt
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#a6e3a1;">2. Ganho Antena Sat (Gt)</span>' +
          '<span class="res-val" style="color:#a6e3a1;">+' + g_tx.toFixed(1) + ' dBi</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#a6e3a1; width:' + getWidth(g_tx) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // Ltx
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#f38ba8;">3. Perda Linha Guia Sat (Ltx)</span>' +
          '<span class="res-val" style="color:#f38ba8;">-' + l_tx.toFixed(1) + ' dB</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#f38ba8; width:' + getWidth(l_tx) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // FSPL
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#f38ba8;">4. Perda por Espaço Livre (FSPL)</span>' +
          '<span class="res-val" style="color:#f38ba8;">-' + fspl.toFixed(1) + ' dB</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#f38ba8; width:' + getWidth(fspl) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // L_other
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#f38ba8;">5. Outras Perdas (Atmos/Chuva/Apont/Pol/Lrx)</span>' +
          '<span class="res-val" style="color:#f38ba8;">-' + l_other.toFixed(1) + ' dB</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#f38ba8; width:' + getWidth(l_other) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // Grx
      '<div>' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#a6e3a1;">6. Ganho Antena Receptor (Grx)</span>' +
          '<span class="res-val" style="color:#a6e3a1;">+' + g_rx.toFixed(1) + ' dBi</span>' +
        '</div>' +
        '<div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px;">' +
          '<div style="background:#a6e3a1; width:' + getWidth(g_rx) + '; height:100%; border-radius:3px;"></div>' +
        '</div>' +
      '</div>' +
      // Prx
      '<div style="border-top:1px solid rgba(255,255,255,0.1); padding-top:6px;">' +
        '<div style="display:flex; justify-content:space-between; margin-bottom:2px;">' +
          '<span style="color:#f9e2af; font-weight:700;">7. Potência Final Recebida (Prx)</span>' +
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
  
  // A. Cálculo Geométrico
  var geo = calcularApontamento(st.lat, st.lng, sat.lng);
  
  // B. Ganhos e Perdas de Antena
  var satAnt = obterGanhoRealSat(sat, geo.offAxis);
  var ptx_dbw = 10 * Math.log10(sat.tx_power);
  var eirp = ptx_dbw - LOSS_TX_LINE + satAnt.gain;
  
  // C. FSPL (Free Space Path Loss)
  var fspl = 20 * Math.log10(geo.distance) + 20 * Math.log10(sat.frequency) + 92.45;
  
  // D. Potência Recebida e Margem de Link (Target BER 10^-6)
  var totalLosses = LOSS_ATM + LOSS_RAIN + LOSS_POINT + LOSS_POL + LOSS_RX_LINE;
  var prx_dbw = eirp - fspl - totalLosses + st.rx_gain;
  var prx_dbm = prx_dbw + 30.0;
  
  // E. Ruído e Cascata de Friis
  var g_lna_lin = Math.pow(10, (st.gain_lna || 50.0) / 10.0);
  var f_rec = Math.pow(10, (st.nf_rec || 8.0) / 10.0);
  var t_rec_k = 290.0 * (f_rec - 1.0);
  var t_eff = (st.temp_lna || 80.0) + ((st.temp_down || 290.0) / g_lna_lin) + (t_rec_k / g_lna_lin);
  var t_sys = (st.temp_antenna || 50.0) + t_eff;
  
  var gt = st.rx_gain - 10 * Math.log10(t_sys);
  var K_DB = -228.6;
  var n0 = K_DB + 10 * Math.log10(t_sys);
  var cn0 = prx_dbw - n0;
  var cn = cn0 - 10 * Math.log10(BW_MHZ * 1e6);
  
  // F. Modulação, Eb/N0, Margem e BER
  var ebn0 = cn0 - 10 * Math.log10(RB_MBPS * 1e6);
  var ber = calcularBER(ebn0, MOD_TYPE);
  
  // Eb/N0 requerido para BER = 10^-6 conforme a modulação
  var ebn0_req = 10.5; // BPSK/QPSK
  if (MOD_TYPE === '8PSK') ebn0_req = 14.0;
  else if (MOD_TYPE === '16QAM') ebn0_req = 14.5;
  
  var margem = ebn0 - ebn0_req;
  var margemBadge = margem >= 0 ? 
    '<span class="badge badge-green">Margem Positiva (+' + margem.toFixed(2) + ' dB)</span>' :
    '<span class="badge badge-red">Margem Negativa (' + margem.toFixed(2) + ' dB)</span>';
  
  // Renderização ── TAB: LINK
  var waterfallHtml = gerarWaterfallHtml(ptx_dbw, LOSS_TX_LINE, satAnt.gain, fspl, totalLosses, st.rx_gain, prx_dbw);
  
  var linkHtml = 
    '<div class="res-card"><h4>Geometria & Apontamento</h4>' +
      '<div class="res-row"><span class="res-label">Distancia (Slant Range)</span><span class="res-val">' + geo.distance.toFixed(2) + ' km</span></div>' +
      '<div class="res-row"><span class="res-label">Angulo de Elevacao</span><span class="res-val">' + geo.elevation.toFixed(2) + '&deg;</span></div>' +
      '<div class="res-row"><span class="res-label">Off-Axis da Antena (Sat.)</span><span class="res-val">' + geo.offAxis.toFixed(2) + '&deg;</span></div>' +
    '</div>' +
    waterfallHtml +
    '<div class="res-card"><h4>Nivel de Sinal Recebido & Margem</h4>' +
      '<div class="res-row"><span class="res-label">Ganho Antena Receptor</span><span class="res-val">' + st.rx_gain.toFixed(2) + ' dBi</span></div>' +
      '<div class="res-row"><span class="res-label">Potencia Recebida (Prx)</span><span class="res-val" style="color:#a6e3a1;">' + prx_dbm.toFixed(2) + ' dBm</span></div>' +
      '<div style="text-align:center; margin-top:10px;">' + margemBadge + '</div>' +
    '</div>';
  document.getElementById('tab-link').innerHTML = linkHtml;
  
  // Contribuições individuais dos componentes na cascata de ruído
  var c_ant = st.temp_antenna;
  var c_lna = st.temp_lna;
  var c_other = t_eff - c_lna;
  
  // Renderização ── TAB: RUIDO (Com Tabela de Cascata de Componentes)
  var noiseHtml = 
    '<div class="res-card"><h4>Temperatura de Ruido do Sistema (Tsys)</h4>' +
      '<div class="res-row"><span class="res-label">Temp. Ruido Sistema (Tsys)</span><span class="res-val" style="color:#f9e2af;">' + t_sys.toFixed(1) + ' K</span></div>' +
      '<table style="width:100%; border-collapse:collapse; margin-top:10px; font-size:11px; text-align:left;">' +
        '<thead>' +
          '<tr style="border-bottom:1px solid rgba(137,220,235,0.3); color:#89dceb; font-weight:bold;">' +
            '<th style="padding:4px 0;">Estagio</th>' +
            '<th style="padding:4px 0; text-align:right;">Temp. (K)</th>' +
            '<th style="padding:4px 0; text-align:right;">Ganho (dB)</th>' +
            '<th style="padding:4px 0; text-align:right;">Contrib. (K)</th>' +
          '</tr>' +
        '</thead>' +
        '<tbody>' +
          '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">' +
            '<td style="padding:4px 0;">Antena</td>' +
            '<td style="padding:4px 0; text-align:right;">' + st.temp_antenna.toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">-</td>' +
            '<td style="padding:4px 0; text-align:right;">' + c_ant.toFixed(1) + '</td>' +
          '</tr>' +
          '<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">' +
            '<td style="padding:4px 0;">LNA</td>' +
            '<td style="padding:4px 0; text-align:right;">' + st.temp_lna.toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">' + st.gain_lna.toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">' + c_lna.toFixed(1) + '</td>' +
          '</tr>' +
          '<tr>' +
            '<td style="padding:4px 0;">Rec/Mixer</td>' +
            '<td style="padding:4px 0; text-align:right;">' + (t_rec_k + st.temp_down).toFixed(1) + '</td>' +
            '<td style="padding:4px 0; text-align:right;">-</td>' +
            '<td style="padding:4px 0; text-align:right;">' + c_other.toFixed(3) + '</td>' +
          '</tr>' +
        '</tbody>' +
      '</table>' +
    '</div>' +
    '<div class="res-card"><h4>Figura de Merito & Densidades</h4>' +
      '<div class="res-row"><span class="res-label">Figura de Merito G/T</span><span class="res-val">' + gt.toFixed(2) + ' dB/K</span></div>' +
      '<div class="res-row"><span class="res-label">Densidade de Ruido N0</span><span class="res-val">' + n0.toFixed(1) + ' dBW/Hz</span></div>' +
      '<div class="res-row"><span class="res-label">Relacao C/N0</span><span class="res-val" style="color:#89dceb;">' + cn0.toFixed(2) + ' dB-Hz</span></div>' +
    '</div>' +
    '<div class="res-card"><h4>Ruido no Canal</h4>' +
      '<div class="field"><label>Largura de Banda do Canal (MHz)</label>' +
      '<input type="number" id="inp_bw" step="1" value="' + BW_MHZ + '" oninput="changeBW(this.value)"></div>' +
      '<div class="res-row"><span class="res-label">Relacao C/N no Canal</span><span class="res-val">' + cn.toFixed(2) + ' dB</span></div>' +
    '</div>';
  document.getElementById('tab-noise').innerHTML = noiseHtml;
  
  // Renderização ── TAB: BER
  var berBadge = ber < 1e-6 ? '<span class="badge badge-green">Excelente (BER < 10⁻⁶)</span>' :
                 (ber <= 1e-3 ? '<span class="badge badge-yellow">Limiar (10⁻⁶ a 10⁻³)</span>' :
                               '<span class="badge badge-red">Inviavel (BER > 10⁻³)</span>');
                               
  var chartSvg = gerarBerChart(ebn0, ber, MOD_TYPE);
                               
  var perfHtml = 
    '<div class="res-card"><h4>Configuracoes de Transmissao</h4>' +
      '<div class="field"><label>Taxa de Bits Rb (Mbps)</label>' +
      '<input type="number" id="inp_rb" step="1" value="' + RB_MBPS + '" oninput="changeRB(this.value)"></div>' +
      '<div class="field"><label>Modulacao</label>' +
      '<select id="inp_mod" onchange="changeMod(this.value)">' +
        '<option value="BPSK"' + (MOD_TYPE === 'BPSK' ? ' selected' : '') + '>BPSK</option>' +
        '<option value="QPSK"' + (MOD_TYPE === 'QPSK' ? ' selected' : '') + '>QPSK</option>' +
        '<option value="8PSK"' + (MOD_TYPE === '8PSK' ? ' selected' : '') + '>8PSK</option>' +
        '<option value="16QAM"' + (MOD_TYPE === '16QAM' ? ' selected' : '') + '>16QAM</option>' +
      '</select></div>' +
    '</div>' +
    '<div class="res-card"><h4>Desempenho Estimado</h4>' +
      '<div class="res-row"><span class="res-label">Relacao Eb/N0 calculada</span><span class="res-val" style="color:#a6e3a1;">' + ebn0.toFixed(2) + ' dB</span></div>' +
      '<div class="res-row"><span class="res-label">Bit Error Rate (BER)</span><span class="res-val" style="color:#f38ba8;">' + ber.toExponential(3) + '</span></div>' +
      '<div style="text-align:center; margin-top:10px;">' + berBadge + '</div>' +
      '<div style="text-align:center; margin-top:12px;">' + chartSvg + '</div>' +
    '</div>';
  document.getElementById('tab-perf').innerHTML = perfHtml;
  
  // Renderização ── TAB: PDF
  var pdfHtml = 
    '<div class="res-card" style="text-align:center; padding:25px 15px;">' +
      '<h4 style="border:none;">Relatorio Consolidado</h4>' +
      '<p style="font-size:12px; margin-bottom:18px; line-height:1.5; color:#a6adc8;">Imprima ou salve os calculos consolidados deste enlace de comunicacao.</p>' +
      '<button class="save-btn" onclick="window.print()">&#128196; Imprimir Relatorio</button>' +
    '</div>';
  document.getElementById('tab-pdf').innerHTML = pdfHtml;
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
