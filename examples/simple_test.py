#!/usr/bin/env python3
"""
Simple test dashboard that doesn't use the visualization module
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

# Import only the core heat_transfer module
import heat_transfer

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Global variables
point_cloud = None
solver = None

app.layout = dbc.Container([
    html.H1("Heat Transfer Simulation - Simple Version"),
    
    dbc.Button("Generate Geometry", id="generate-btn", color="primary", className="mb-3"),
    
    dcc.Graph(id="geometry-plot"),
    
    html.Div(id="status", className="mt-3")
], fluid=True)

@app.callback(
    [Output("geometry-plot", "figure"),
     Output("status", "children")],
    [Input("generate-btn", "n_clicks")]
)
def update_visualization(n_clicks):
    if not n_clicks:
        return {}, "Click 'Generate Geometry' to start"
    
    try:
        # Generate geometry
        generator = heat_transfer.CupGenerator()
        params = heat_transfer.CupParameters()
        params.point_spacing = 0.01  # Larger spacing for faster generation
        params.inner_radius = 0.03
        params.height = 0.08
        
        global point_cloud
        point_cloud = generator.generate(params)
        
        # Extract data for visualization
        points = []
        materials = []
        
        for i in range(point_cloud.size()):
            point = point_cloud.get_point(i)
            pos = point.get_position()
            points.append([pos.x, pos.y, pos.z])
            materials.append(int(point.get_material()))
        
        points = np.array(points)
        materials = np.array(materials)
        
        # Create 3D scatter plot
        fig = go.Figure(data=go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1], 
            z=points[:, 2],
            mode='markers',
            marker=dict(
                size=4,
                color=materials,
                colorscale='Viridis',
                showscale=True
            )
        ))
        
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Z (m)'
            ),
            height=600
        )
        
        return fig, f"✅ Generated {point_cloud.size()} points successfully!"
        
    except Exception as e:
        import traceback
        error_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
        return {}, error_msg

if __name__ == '__main__':
    print("Starting Simple Heat Transfer Dashboard...")
    print("Open http://localhost:8050 in your browser")
    # Fixed: use app.run() instead of app.run_server()
    app.run(host='0.0.0.0', port=8050, debug=True)