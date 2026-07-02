import json

GEO_ALT = 0.6  # altitude relativa no globe.gl (0 = superfície, 1 = raio acima)


def _satellites_json(satellites):
    return json.dumps([{
        "id": i, "name": s.name, "lat": 0.0, "lng": s.longitude_deg,
        "alt": GEO_ALT, "kind": "satellite", "orbit": s.orbit_type,
        "tx_power": s.tx_power_w, "tx_gain": s.tx_gain_dbi,
        "frequency": s.frequency_ghz
    } for i, s in enumerate(satellites)])


def _stations_json(stations):
    return json.dumps([{
        "id": i, "name": s.name, "lat": s.latitude_deg, "lng": s.longitude_deg,
        "alt": 0.0, "kind": "station", "rx_gain": s.rx_gain_dbi
    } for i, s in enumerate(stations)])


def _links_json(satellites, stations):
    links = []
    for station in stations:
        if not satellites:
            break
        nearest = min(satellites, key=lambda s: abs(s.longitude_deg - station.longitude_deg))
        links.append({
            "path": [[station.latitude_deg, station.longitude_deg, 0.0],
                     [0.0, nearest.longitude_deg, GEO_ALT]],
            "color": "#00e5ff", "isNadir": False, "isOrbit": False,
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
  display:none; position:absolute; top:16px; left:16px; width:285px;
  background:rgba(6,12,24,0.95); color:#cdd6f4; border-radius:12px;
  border:1px solid #1e5f8a; box-shadow:0 4px 30px rgba(0,180,255,0.18);
  z-index:200; overflow:hidden;
}}
#infoPanelHead {{
  background:rgba(14,28,56,0.98); padding:11px 15px;
  display:flex; justify-content:space-between; align-items:center;
  border-bottom:1px solid #1e5f8a;
}}
#infoPanelHead h3 {{ font-size:13px; color:#89dceb; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:215px; }}
#closeInfo {{ background:transparent; border:none; color:#6c7086; cursor:pointer; font-size:20px; line-height:1; }}
#closeInfo:hover {{ color:#fff; }}
#infoBody {{ padding:13px 15px; font-size:12.5px; max-height:440px; overflow-y:auto; }}
.field {{ margin-bottom:9px; }}
.field label {{ display:block; color:#7a9cc0; font-size:10.5px; margin-bottom:3px; text-transform:uppercase; letter-spacing:0.5px; }}
.field input {{ width:100%; background:rgba(20,40,80,0.65); border:1px solid #1e5f8a; border-radius:5px; color:#cdd6f4; font-size:13px; padding:6px 9px; transition:border-color .15s; }}
.field input:focus {{ outline:none; border-color:#89dceb; background:rgba(30,60,120,0.8); }}
.save-btn {{ width:100%; margin-top:11px; background:rgba(0,120,200,0.75); color:#fff; border:1px solid #1e5f8a; border-radius:7px; padding:8px; cursor:pointer; font-size:13px; font-weight:600; transition:background .2s; }}
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
</style>
</head>
<body>

<div id="globeViz"></div>

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
  <div id="tab-link"  class="rtab-body active"><p class="placeholder">Adicione satelites e estacoes para calcular o Link Budget.</p></div>
  <div id="tab-noise" class="rtab-body"><p class="placeholder">Configure a cascata de ruido no painel esquerdo.</p></div>
  <div id="tab-perf"  class="rtab-body"><p class="placeholder">Selecione modulacao para estimar BER e Eb/N0.</p></div>
  <div id="tab-pdf"   class="rtab-body"><p class="placeholder">Gere um relatorio PDF do cenario.</p></div>
</div>

<script src="https://unpkg.com/globe.gl/dist/globe.gl.min.js"></script>
<script>
var SATS  = {sats_j};
var STNS  = {stns_j};
var LINKS = {lnks_j};
var ORBIT = {orbit_j};
var ALL_PATHS = LINKS.concat(ORBIT);

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
  .pointAltitude(0)
  .pointRadius(0.40)
  .pointColor(function() {{ return '#00ff88'; }})
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
  // 100% estável e compatível nativamente sem precisar carregar Three.js externo
  .labelsData(SATS)
  .labelLat('lat')
  .labelLng('lng')
  .labelAltitude('alt')          // Altitude GEO orbital (0.6)
  .labelText('name')
  .labelSize(1.2)
  .labelDotRadius(0.6)           // Bolinha verde bidimensional bem pequenininha, mas perfeitamente visível
  .labelDotOrientation('bottom') // Ponto verde posicionado abaixo do texto
  .labelColor(function() {{ return '#00ff88'; }}) // Nome e bolinha verdes
  .labelResolution(4)

  // Links + anel orbital GEO
  .pathsData(ALL_PATHS)
  .pathPoints('path')
  .pathPointLat(function(p) {{ return p[0]; }})
  .pathPointLng(function(p) {{ return p[1]; }})
  .pathPointAlt(function(p) {{ return p[2]; }})
  .pathColor(function(d) {{ return d.isNadir ? '#ffff00' : (d.isOrbit ? 'rgba(255,210,60,0.85)' : '#00e5ff'); }})
  .pathDashLength(function(d) {{ return d.isOrbit ? 0.03 : (d.isNadir ? 0.015 : 0.08); }})
  .pathDashGap(function(d)    {{ return d.isOrbit ? 0.02  : (d.isNadir ? 0.015 : 0.04); }})
  .pathDashAnimateTime(function(d) {{ return (d.isOrbit || d.isNadir) ? 0 : 2500; }})
  .pathStroke(function(d)    {{ return d.isOrbit ? 0.6   : (d.isNadir ? 0.35 : 0.9); }})

  .width(window.innerWidth)
  .height(window.innerHeight);

globe.controls().autoRotate = true;
globe.controls().autoRotateSpeed = 0.2;
globe.pointOfView({{ altitude: 2.5 }});

// ── Hover no satélite: exibe linha nadir dinamicamente ──
globe.onLabelHover(function(d) {{
  if (d && d.kind === 'satellite') {{
    globe.controls().autoRotate = false;
    globe.pathsData(ALL_PATHS.concat([{{
      path: [[d.lat, d.lng, d.alt], [d.lat, d.lng, 0]],
      isNadir: true, isOrbit: false
    }}]));
  }} else {{
    globe.controls().autoRotate = !!(d === null || d === undefined);
    globe.pathsData(ALL_PATHS);
  }}
}});

// ── Click no satélite: abre painel de edição ──
globe.onLabelClick(function(d) {{
  if (d) showSatPanel(d);
}});

// ── Click na estação terrena ──
globe.onPointClick(function(point) {{
  showStationPanel(point);
}});

// ── Painéis de edição ──
var currentSat = null;
var currentStation = null;

function showInfo(title, bodyHtml) {{
  document.getElementById('infoTitle').textContent = title;
  document.getElementById('infoBody').innerHTML    = bodyHtml;
  document.getElementById('infoPanel').style.display = 'block';
}}

function showSatPanel(d) {{
  currentSat = d;
  showInfo('Satelite: ' + d.name,
    '<form onsubmit="saveSat(event)">' +
    '<div class="field"><label>Nome</label><input type="text" id="f_name" value="' + d.name + '"></div>' +
    '<div class="field"><label>Longitude Orbital (graus)</label><input type="number" id="f_lng" step="0.1" value="' + d.lng + '"></div>' +
    '<div class="field"><label>Frequencia (GHz)</label><input type="number" id="f_freq" step="0.1" value="' + d.frequency + '"></div>' +
    '<div class="field"><label>Potencia TX (W)</label><input type="number" id="f_power" step="1" value="' + d.tx_power + '"></div>' +
    '<div class="field"><label>Ganho Antena TX (dBi)</label><input type="number" id="f_gain" step="0.5" value="' + d.tx_gain + '"></div>' +
    '<button class="save-btn" type="submit">&#128190; Salvar</button>' +
    '</form><div id="saveMsg">&#9989; Salvo!</div>'
  );
}}

function showStationPanel(d) {{
  currentStation = d;
  showInfo('Estacao: ' + d.name,
    '<form onsubmit="saveStation(event)">' +
    '<div class="field"><label>Nome</label><input type="text" id="s_name" value="' + d.name + '"></div>' +
    '<div class="field"><label>Latitude</label><input type="number" id="s_lat" step="0.0001" value="' + d.lat.toFixed(4) + '"></div>' +
    '<div class="field"><label>Longitude</label><input type="number" id="s_lng" step="0.0001" value="' + d.lng.toFixed(4) + '"></div>' +
    '<div class="field"><label>Ganho Antena RX (dBi)</label><input type="number" id="s_gain" step="0.5" value="' + d.rx_gain + '"></div>' +
    '<button class="save-btn" type="submit">&#128190; Salvar</button>' +
    '</form><div id="saveMsg">&#9989; Salvo!</div>'
  );
}}

function saveSat(e) {{
  e.preventDefault();
  if (!currentSat) return;
  currentSat.name      = document.getElementById('f_name').value;
  currentSat.lng       = parseFloat(document.getElementById('f_lng').value);
  currentSat.frequency = parseFloat(document.getElementById('f_freq').value);
  currentSat.tx_power  = parseFloat(document.getElementById('f_power').value);
  currentSat.tx_gain   = parseFloat(document.getElementById('f_gain').value);
  globe.labelsData(SATS.slice());
  ALL_PATHS = recalcLinks();
  globe.pathsData(ALL_PATHS);
  document.getElementById('saveMsg').style.display = 'block';
}}

function saveStation(e) {{
  e.preventDefault();
  if (!currentStation) return;
  currentStation.name    = document.getElementById('s_name').value;
  currentStation.lat     = parseFloat(document.getElementById('s_lat').value);
  currentStation.lng     = parseFloat(document.getElementById('s_lng').value);
  currentStation.rx_gain = parseFloat(document.getElementById('s_gain').value);
  globe.pointsData(STNS.slice());
  globe.ringsData(STNS.slice());
  ALL_PATHS = recalcLinks();
  globe.pathsData(ALL_PATHS);
  document.getElementById('saveMsg').style.display = 'block';
}}

function recalcLinks() {{
  var links = STNS.map(function(st) {{
    if (!SATS.length) return null;
    var nearest = SATS.reduce(function(p, c) {{
      return Math.abs(c.lng - st.lng) < Math.abs(p.lng - st.lng) ? c : p;
    }});
    return {{
      path: [[st.lat, st.lng, 0.0], [0.0, nearest.lng, {GEO_ALT}]],
      color: '#00e5ff', isNadir: false, isOrbit: false
    }};
  }}).filter(Boolean);
  return links.concat(ORBIT);
}}

window.addEventListener('resize', function() {{
  globe.width(window.innerWidth).height(window.innerHeight);
}});
</script>
</body>
</html>"""
