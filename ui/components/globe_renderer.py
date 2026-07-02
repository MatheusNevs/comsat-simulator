import json

GLOBE_HEIGHT_PX = 780


def _satellites_payload(satellites):
    return [
        {"name": sat.name, "lat": 0.0, "lng": sat.longitude_deg, "alt": 0.6}
        for sat in satellites
    ]


def _stations_payload(stations):
    return [
        {"name": station.name, "lat": station.latitude_deg, "lng": station.longitude_deg, "alt": 0.0}
        for station in stations
    ]


def _links_payload(satellites, stations):
    return [
        {
            "startLat": 0.0,
            "startLng": sat.longitude_deg,
            "endLat": station.latitude_deg,
            "endLng": station.longitude_deg,
            "name": f"{sat.name} → {station.name}",
            "color": "#00e5ff",
        }
        for sat in satellites
        for station in stations
    ]


def render_globe_html(satellites, stations, height=GLOBE_HEIGHT_PX):
    """
    Monta o HTML/JS autocontido que renderiza um globo 3D realista
    (textura de satélite, atmosfera, nuvens) usando globe.gl (Three.js),
    para ser exibido via streamlit.components.v1.html.
    """
    satellites_points = [dict(p, kind="satellite") for p in _satellites_payload(satellites)]
    station_points = [dict(p, kind="station") for p in _stations_payload(stations)]
    points_json = json.dumps(satellites_points + station_points)
    links_json = json.dumps(_links_payload(satellites, stations))

    return f"""
<div id="globeViz" style="width: 100%; height: {height}px; background: #000010;"></div>
<script src="https://unpkg.com/globe.gl/dist/globe.gl.min.js"></script>
<script>
    const points = {points_json};
    const links = {links_json};
    const container = document.getElementById('globeViz');

    const globe = Globe()
        (container)
        .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
        .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
        .showAtmosphere(true)
        .atmosphereColor('#3a9bdc')
        .atmosphereAltitude(0.22)
        .pointsData(points)
        .pointLat('lat')
        .pointLng('lng')
        .pointAltitude('alt')
        .pointRadius(d => d.kind === 'satellite' ? 0.5 : 0.35)
        .pointColor(d => d.kind === 'satellite' ? '#ffcc00' : '#00ff88')
        .pointLabel('name')
        .arcsData(links)
        .arcStartLat('startLat')
        .arcStartLng('startLng')
        .arcEndLat('endLat')
        .arcEndLng('endLng')
        .arcColor('color')
        .arcDashLength(0.4)
        .arcDashGap(0.2)
        .arcDashAnimateTime(2000)
        .arcStroke(0.5)
        .arcLabel('name')
        .labelsData(points)
        .labelLat('lat')
        .labelLng('lng')
        .labelText('name')
        .labelSize(1.1)
        .labelDotRadius(0)
        .labelColor(() => 'rgba(255, 255, 255, 0.85)')
        .labelAltitude(d => (d.alt || 0) + 0.01)
        .width(container.clientWidth)
        .height({height});

    globe.controls().autoRotate = true;
    globe.controls().autoRotateSpeed = 0.35;

    window.addEventListener('resize', () => {{
        globe.width(container.clientWidth);
    }});
</script>
"""
