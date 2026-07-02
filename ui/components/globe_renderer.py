import plotly.graph_objects as go
import numpy as np

def create_globe_figure(satellites, stations):
    """
    Renderiza um globo 3D realista usando Plotly e desenha satélites,
    estações terrenas e os enlaces entre eles.
    """
    from core.orbit import geo_satellite_position, station_position, R_EARTH_KM
    
    fig = go.Figure()

    # Desenha a Terra (esfera básica)
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x_earth = R_EARTH_KM * np.outer(np.cos(u), np.sin(v))
    y_earth = R_EARTH_KM * np.outer(np.sin(u), np.sin(v))
    z_earth = R_EARTH_KM * np.outer(np.ones(np.size(u)), np.cos(v))
    
    fig.add_trace(go.Surface(
        x=x_earth, y=y_earth, z=z_earth,
        colorscale='Earth', showscale=False,
        opacity=0.9, name='Terra'
    ))

    # Desenha Satélites
    for sat in satellites:
        if sat.orbit_type == "GEO":
            sx, sy, sz = geo_satellite_position(sat.longitude_deg)
            fig.add_trace(go.Scatter3d(
                x=[sx], y=[sy], z=[sz],
                mode='markers+text',
                marker=dict(size=8, color='yellow', symbol='diamond'),
                text=[sat.name],
                textposition="top center",
                name=f"Sat: {sat.name}"
            ))

            # Conecta o satélite a todas as estações (visualmente)
            for station in stations:
                stx, sty, stz = station_position(station.latitude_deg, station.longitude_deg)
                fig.add_trace(go.Scatter3d(
                    x=[sx, stx], y=[sy, sty], z=[sz, stz],
                    mode='lines',
                    line=dict(color='cyan', width=2, dash='dash'),
                    name=f"Link {sat.name} - {station.name}"
                ))

    # Desenha Estações Terrenas
    for station in stations:
        stx, sty, stz = station_position(station.latitude_deg, station.longitude_deg)
        fig.add_trace(go.Scatter3d(
            x=[stx], y=[sty], z=[stz],
            mode='markers+text',
            marker=dict(size=6, color='red'),
            text=[station.name],
            textposition="top center",
            name=f"Est: {station.name}"
        ))

    # Configuração de layout do Plotly
    axis_range = [-40000, 40000] # Para acomodar a órbita GEO
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=axis_range, visible=False),
            yaxis=dict(range=axis_range, visible=False),
            zaxis=dict(range=axis_range, visible=False),
            aspectmode='cube'
        ),
        margin=dict(r=0, l=0, b=0, t=0),
        paper_bgcolor='black',
        plot_bgcolor='black',
        showlegend=False
    )
    
    return fig
