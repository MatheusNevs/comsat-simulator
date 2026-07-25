"""
Módulo de Geometria Orbital e Conversão de Coordenadas (core/orbit.py)

Fornece constantes físicas e funções para cálculo de posições 3D cartesianas (x, y, z)
a partir de coordenadas geográficas (latitude, longitude, altitude), aplicadas a satélites
geoestacionários (anel de Clarke) e estações terrenas.
"""

import math

# Constantes geodésicas e orbitais básicas
R_EARTH_KM = 6371.0       # Raio médio da Terra em quilômetros
GEO_ALTITUDE_KM = 35786.0  # Altitude nominal da órbita geoestacionária (GEO) em km


def lat_lon_to_cartesian(lat_deg: float, lon_deg: float, altitude_km: float):
    """
    Converte coordenadas geográficas (latitude, longitude, altitude) para o sistema de
    coordenadas cartesianas geocêntricas (x, y, z) em quilômetros.

    Parâmetros:
        lat_deg (float): Latitude em graus (-90.0 a 90.0).
        lon_deg (float): Longitude em graus (-180.0 a 180.0).
        altitude_km (float): Altitude em relação à superfície da Terra em km.

    Retorna:
        tuple[float, float, float]: Posição cartesiana 3D (x, y, z) em km.
    """
    lat_rad = math.radians(lat_deg)
    lon_rad = math.radians(lon_deg)
    r = R_EARTH_KM + altitude_km
    
    x = r * math.cos(lat_rad) * math.cos(lon_rad)
    y = r * math.cos(lat_rad) * math.sin(lon_rad)
    z = r * math.sin(lat_rad)
    
    return x, y, z


def geo_satellite_position(lon_deg: float):
    """
    Calcula a posição 3D cartesiana de um satélite GEO sobre o anel de Clarke.
    Satélites GEO possuem latitude 0° (linha do equador) e altitude fixa de ~35.786 km.

    Parâmetros:
        lon_deg (float): Longitude orbital do satélite em graus.

    Retorna:
        tuple[float, float, float]: Posição cartesiana 3D (x, y, z) do satélite em km.
    """
    return lat_lon_to_cartesian(0.0, lon_deg, GEO_ALTITUDE_KM)


def station_position(lat_deg: float, lon_deg: float):
    """
    Calcula a posição 3D cartesiana de uma estação terrena instalada na superfície terrestre.
    A altitude é assumida como 0 km em relação ao nível do mar (superfície).

    Parâmetros:
        lat_deg (float): Latitude da estação terrena em graus.
        lon_deg (float): Longitude da estação terrena em graus.

    Retorna:
        tuple[float, float, float]: Posição cartesiana 3D (x, y, z) da estação em km.
    """
    return lat_lon_to_cartesian(lat_deg, lon_deg, 0.0)
