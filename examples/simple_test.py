#!/usr/bin/env python3
"""
Enhanced visualization with temperature debugging
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

# Import only the core heat_transfer module
import heat_transfer

# Updated material properties for better visualization
MATERIAL_VISUAL_PROPS = {
    0: {'size': 4, 'opacity': 0.8, 'color': 'brown'},    # Coffee - slightly transparent
    1: {'size': 3, 'opacity': 0.9, 'color': 'orange'},   # Ceramic - more opaque
    2: {'size': 2, 'opacity': 0.3, 'color': 'lightblue'} # Air - very transparent
}

MATERIAL_NAMES = {
    0: 'Coffee', 
    1: 'Ceramic', 
    2: 'Air'
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Global variables
point_cloud = None
solver = None

app.layout = dbc.Container([
    html.H1("Heat Transfer Simulation - Enhanced Debug Visualization"),
    
    dbc.Row([
        dbc.Col([
            dbc.Button("Generate Geometry", id="generate-btn", color="primary", className="mb-3"),
            dbc.Button("Run Simulation Step", id="sim-btn", color="success", className="mb-3"),
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="geometry-plot", style={'height': '600px'}),
        ], width=8),
        dbc.Col([
            html.H4("Visualization Controls"),
            html.Label("Point Size Multiplier:"),
            dcc.Slider(id="size-multiplier", min=0.1, max=2.0, value=1.0, step=0.1),
            html.Label("Air Opacity:"),
            dcc.Slider(id="air-opacity", min=0.0, max=1.0, value=0.1, step=0.05),
            html.Label("Color By:"),
            dcc.RadioItems(
                id="color-by",
                options=[
                    {'label': 'Temperature', 'value': 'temp'},
                    {'label': 'Material', 'value': 'material'}
                ],
                value='temp'
            ),
            html.Hr(),
            html.H5("Temperature Debug Info:"),
            html.Div(id="temp-debug", style={'background-color': '#f8f9fa', 'padding': '10px', 'border-radius': '5px'})
        ], width=4)
    ]),
    
    html.Div(id="status", className="mt-3")
], fluid=True)

@app.callback(
    [Output("geometry-plot", "figure"),
     Output("status", "children"),
     Output("temp-debug", "children")],
    [Input("generate-btn", "n_clicks"),
     Input("sim-btn", "n_clicks"),
     Input("size-multiplier", "value"),
     Input("air-opacity", "value"),
     Input("color-by", "value")]
)
def update_visualization(gen_clicks, sim_clicks, size_mult, air_opacity, color_by):
    global point_cloud, solver
    
    # Handle geometry generation
    if gen_clicks and not point_cloud:
        try:
            # Generate geometry with better parameters
            generator = heat_transfer.CupGenerator()
            params = heat_transfer.CupParameters()
            params.inner_radius = 0.03
            params.height = 0.08
            params.point_spacing = 0.008  # Slightly larger spacing to reduce overlap
            
            point_cloud = generator.generate(params)
            
            # Initialize solver
            materials = [
                heat_transfer.Material.coffee(),
                heat_transfer.Material.ceramic(),
                heat_transfer.Material.air()
            ]
            solver = heat_transfer.HeatSolver(point_cloud, materials, 0.1)
            
        except Exception as e:
            return {}, f"❌ Error generating geometry: {str(e)}", ""
    
    # Handle simulation step
    if sim_clicks and solver:
        try:
            solver.step()
        except Exception as e:
            return {}, f"❌ Error running simulation: {str(e)}", ""
    
    if not point_cloud:
        return {}, "Click 'Generate Geometry' to start", ""
    
    try:
        # Extract data for visualization
        points = []
        materials = []
        temperatures = []

        for i in range(point_cloud.size()):
            point = point_cloud.get_point(i)
            pos = point.get_position()
            points.append([pos.x, pos.y, pos.z])
            materials.append(int(point.get_material()))
            temperatures.append(point.get_temperature())
        
        points = np.array(points)
        materials = np.array(materials)
        temperatures = np.array(temperatures)
        
        # Debug information about temperatures
        temp_debug_info = []
        for mat_type in [0, 1, 2]:
            mat_temps = temperatures[materials == mat_type]
            if len(mat_temps) > 0:
                temp_debug_info.append(html.P([
                    html.Strong(f"{MATERIAL_NAMES[mat_type]}: "),
                    f"Count: {len(mat_temps)}, ",
                    f"Min: {np.min(mat_temps):.1f}K, ",
                    f"Max: {np.max(mat_temps):.1f}K, ",
                    f"Avg: {np.mean(mat_temps):.1f}K"
                ]))
        
        temp_debug_info.append(html.P([
            html.Strong("Overall: "),
            f"Min: {np.min(temperatures):.1f}K, ",
            f"Max: {np.max(temperatures):.1f}K"
        ]))
        
        # Create separate traces for each material type
        fig = go.Figure()
        
        # Add each material as a separate trace for better control
        for material_type in [0, 1, 2]:  # Coffee, Ceramic, Air
            mask = materials == material_type
            if not np.any(mask):
                continue
            
            # Adjust opacity for air
            opacity = air_opacity if material_type == 2 else MATERIAL_VISUAL_PROPS[material_type]['opacity']
            
            # Determine color and size
            if color_by == 'temp':
                colors = temperatures[mask]
                colorscale = 'Viridis'  # Changed to Viridis for better contrast
                showscale = True
                # Set explicit color range to show temperature differences
                cmin = np.min(temperatures)  # Use actual data range
                cmax = np.max(temperatures)
            else:
                colors = MATERIAL_VISUAL_PROPS[material_type]['color']
                colorscale = None
                showscale = False
                cmin = None
                cmax = None
            
            size = MATERIAL_VISUAL_PROPS[material_type]['size'] * size_mult
            
            # Create hover text
            hover_text = [f"Material: {MATERIAL_NAMES[material_type]}<br>" +
                         f"Temp: {temp:.1f}K ({temp-273.15:.1f}°C)<br>" +
                         f"Position: ({x:.3f}, {y:.3f}, {z:.3f})"
                         for temp, x, y, z in zip(temperatures[mask], 
                                                 points[mask, 0], 
                                                 points[mask, 1], 
                                                 points[mask, 2])]
            
            # Add trace
            fig.add_trace(go.Scatter3d(
                x=points[mask, 0],
                y=points[mask, 1],
                z=points[mask, 2],
                mode='markers',
                name=MATERIAL_NAMES[material_type],
                marker=dict(
                    size=size,
                    color=colors,
                    colorscale=colorscale,
                    cmin=cmin,
                    cmax=cmax,
                    showscale=showscale and material_type == 0,  # Only show colorbar for coffee
                    opacity=opacity,
                    colorbar=dict(title="Temperature (K)", x=0.9) if showscale and material_type == 0 else None
                ),
                text=hover_text,
                hovertemplate='%{text}<extra></extra>',
                showlegend=True
            ))
        
        # Update layout with better camera angle and styling
        fig.update_layout(
            scene=dict(
                xaxis=dict(title='X (m)', showgrid=True, gridwidth=1, gridcolor='lightgray'),
                yaxis=dict(title='Y (m)', showgrid=True, gridwidth=1, gridcolor='lightgray'),
                zaxis=dict(title='Z (m)', showgrid=True, gridwidth=1, gridcolor='lightgray'),
                bgcolor='white',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5),  # Better viewing angle
                    up=dict(x=0, y=0, z=1)
                )
            ),
            height=600,
            title="Heat Transfer Simulation - 3D Point Cloud",
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        status_msg = f"✅ Displaying {point_cloud.size()} points"
        if solver:
            try:
                avg_coffee_temp = solver.get_average_temperature(heat_transfer.MaterialType.COFFEE)
                status_msg += f" | Current time: {solver.get_current_time():.1f}s"
                status_msg += f" | Coffee temp: {avg_coffee_temp:.1f}K ({avg_coffee_temp-273.15:.1f}°C)"
            except:
                status_msg += " | Error getting temperatures"
        
        return fig, status_msg, temp_debug_info
        
    except Exception as e:
        import traceback
        error_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
        return {}, error_msg, ""

if __name__ == '__main__':
    print("Starting Enhanced Debug Heat Transfer Dashboard...")
    print("Open http://localhost:8050 in your browser")
    app.run(host='0.0.0.0', port=8050, debug=True)