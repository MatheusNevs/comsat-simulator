import math

R_EARTH_KM = 6371.0
GEO_ALTITUDE_KM = 35786.0

def lat_lon_to_cartesian(lat_deg, lon_deg, altitude_km):
    """
    Converte coordenadas geográficas para cartesianas (x, y, z).
    Útil para plotar em 3D.
    """
    lat_rad = math.radians(lat_deg)
    lon_rad = math.radians(lon_deg)
    r = R_EARTH_KM + altitude_km
    
    x = r * math.cos(lat_rad) * math.cos(lon_rad)
    y = r * math.cos(lat_rad) * math.sin(lon_rad)
    z = r * math.sin(lat_rad)
    
    return x, y, z

def geo_satellite_position(lon_deg):
    """
    Retorna a posição (x,y,z) de um satélite GEO no anel de Clarke.
    """
    # GEO satélites têm latitude 0 (na linha do Equador)
    return lat_lon_to_cartesian(0.0, lon_deg, GEO_ALTITUDE_KM)

def station_position(lat_deg, lon_deg):
    """
    Retorna a posição (x,y,z) de uma estação terrena.
    """
    # A estação está na superfície da Terra, logo altitude ~0
    return lat_lon_to_cartesian(lat_deg, lon_deg, 0.0)
