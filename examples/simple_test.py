#!/usr/bin/env python3
"""
Simplified Heat Transfer Dashboard with Reliable Real-time Updates
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

# Import only the core heat_transfer module
import heat_transfer

# Material properties for visualization
MATERIAL_VISUAL_PROPS = {
    0: {'size': 4, 'opacity': 0.8, 'color': 'brown'},    # Coffee
    1: {'size': 3, 'opacity': 0.9, 'color': 'orange'},   # Ceramic
    2: {'size': 2, 'opacity': 0.3, 'color': 'lightblue'} # Air
}

MATERIAL_NAMES = {0: 'Coffee', 1: 'Ceramic', 2: 'Air'}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Simple global state - much cleaner than complex state management
class SimulationState:
    def __init__(self):
        self.point_cloud = None
        self.solver = None
        self.running = False
        self.target_time = 0
        self.ui_revision = 0

state = SimulationState()

app.layout = dbc.Container([
    html.H1("Heat Transfer Simulation - Simplified Real-time"),
    
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("Generate", id="generate-btn", color="primary", size="sm"),
                dbc.Button("Step", id="step-btn", color="success", size="sm"),
                dbc.Button("Run 5min", id="run-btn", color="warning", size="sm"),
                dbc.Button("STOP", id="stop-btn", color="danger", size="sm"),
            ], className="mb-3"),
            
            html.Div(id="controls-status", className="mb-2")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="plot", style={'height': '500px'}),
        ], width=8),
        dbc.Col([
            html.H5("Controls"),
            html.Label("Point Size:"),
            dcc.Slider(id="size-mult", min=0.5, max=2.0, value=1.0, step=0.1),
            html.Label("Air Opacity:"),
            dcc.Slider(id="air-opacity", min=0.0, max=0.5, value=0.1, step=0.02),
            html.Hr(),
            html.Div(id="temp-info")
        ], width=4)
    ]),
    
    # Simple interval - only enabled when running
    dcc.Interval(id='interval', interval=100, n_intervals=0, disabled=True),
    
    # Store just for button states to avoid conflicts
    dcc.Store(id='button-states', data={'running': False})
], fluid=True)

@app.callback(
    [Output('interval', 'disabled'),
     Output('button-states', 'data'),
     Output('controls-status', 'children')],
    [Input('generate-btn', 'n_clicks'),
     Input('step-btn', 'n_clicks'), 
     Input('run-btn', 'n_clicks'),
     Input('stop-btn', 'n_clicks')],
    prevent_initial_call=True
)
def handle_controls(gen_clicks, step_clicks, run_clicks, stop_clicks):
    """Handle all button clicks and control simulation state"""
    ctx = callback_context
    if not ctx.triggered:
        return True, {'running': False}, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'generate-btn':
        try:
            print("🔄 Generating geometry...")
            generator = heat_transfer.CupGenerator()
            params = heat_transfer.CupParameters()
            params.inner_radius = 0.03
            params.height = 0.08
            params.point_spacing = 0.008
            
            state.point_cloud = generator.generate(params)
            print(f"✅ Generated {state.point_cloud.size()} points")
            
            materials = [
                heat_transfer.Material.coffee(),
                heat_transfer.Material.ceramic(), 
                heat_transfer.Material.air()
            ]
            state.solver = heat_transfer.HeatSolver(state.point_cloud, materials, 0.05)  # Larger timestep
            state.running = False
            state.ui_revision += 1
            
            return True, {'running': False}, f"✅ Generated {state.point_cloud.size()} points"
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return True, {'running': False}, f"❌ Error: {str(e)}"
    
    elif button_id == 'step-btn':
        if state.solver:
            try:
                state.solver.step()
                return True, {'running': False}, f"⏭️ Step complete - Time: {state.solver.get_current_time():.1f}s"
            except Exception as e:
                return True, {'running': False}, f"❌ Step error: {str(e)}"
        return True, {'running': False}, "❌ No simulation loaded"
    
    elif button_id == 'run-btn':
        if state.solver:
            state.running = True
            state.target_time = state.solver.get_current_time() + 300  # 5 minutes
            print(f"🚀 Starting simulation - target: {state.target_time:.1f}s")
            return False, {'running': True}, "🔄 Running simulation..."
        return True, {'running': False}, "❌ No simulation loaded"
    
    elif button_id == 'stop-btn':
        print("🛑 STOP button clicked")
        state.running = False
        return True, {'running': False}, "⏹️ Simulation stopped"
    
    return True, {'running': False}, ""

@app.callback(
    [Output('plot', 'figure'),
     Output('temp-info', 'children')],
    [Input('interval', 'n_intervals'),
     Input('generate-btn', 'n_clicks'),
     Input('step-btn', 'n_clicks'),
     Input('size-mult', 'value'),
     Input('air-opacity', 'value')],
    prevent_initial_call=True
)
def update_visualization(n_intervals, gen_clicks, step_clicks, size_mult, air_opacity):
    """Update visualization and run simulation steps"""
    
    ctx = callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ""
    
    # If triggered by interval, run simulation step
    if trigger == 'interval' and state.running and state.solver:
        try:
            state.solver.step()
            current_time = state.solver.get_current_time()
            
            # Check if simulation should stop
            if current_time >= state.target_time:
                print(f"🏁 Simulation complete at {current_time:.1f}s")
                state.running = False
                
        except Exception as e:
            print(f"❌ Simulation step error: {e}")
            state.running = False
    
    # Always update visualization if we have data
    if not state.point_cloud:
        fig = go.Figure()
        fig.update_layout(title="Click 'Generate' to start", height=500)
        return fig, "No data loaded"
    
    try:
        # Extract visualization data
        points = []
        materials = []
        temperatures = []
        
        for i in range(state.point_cloud.size()):
            point = state.point_cloud.get_point(i)
            pos = point.get_position()
            points.append([pos.x, pos.y, pos.z])
            materials.append(int(point.get_material()))
            temperatures.append(point.get_temperature())
        
        points = np.array(points)
        materials = np.array(materials)
        temperatures = np.array(temperatures)
        
        # Create 3D plot
        fig = go.Figure()
        
        for mat_type in [0, 1, 2]:
            mask = materials == mat_type
            if not np.any(mask):
                continue
            
            opacity = air_opacity if mat_type == 2 else MATERIAL_VISUAL_PROPS[mat_type]['opacity']
            size = MATERIAL_VISUAL_PROPS[mat_type]['size'] * size_mult
            
            fig.add_trace(go.Scatter3d(
                x=points[mask, 0],
                y=points[mask, 1], 
                z=points[mask, 2],
                mode='markers',
                name=MATERIAL_NAMES[mat_type],
                marker=dict(
                    size=size,
                    color=temperatures[mask],
                    colorscale='RdBu_r',
                    cmin=250,
                    cmax=400,
                    showscale=(mat_type == 0),  # Only show colorbar for coffee
                    opacity=opacity,
                    colorbar=dict(title="Temperature (K)") if mat_type == 0 else None
                ),
                showlegend=True
            ))
        
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)', 
                zaxis_title='Z (m)',
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2))
            ),
            height=500,
            title=f"Heat Transfer Simulation",
            uirevision=state.ui_revision
        )
        
        # Temperature info
        temp_info = []
        if state.solver:
            try:
                current_time = state.solver.get_current_time()
                coffee_temp = state.solver.get_average_temperature(heat_transfer.MaterialType.COFFEE)
                
                temp_info = [
                    html.P(f"⏱️ Time: {current_time:.1f}s"),
                    html.P(f"☕ Coffee: {coffee_temp:.1f}K ({coffee_temp-273.15:.1f}°C)"),
                    html.P(f"🔥 Max: {np.max(temperatures):.1f}K"),
                    html.P(f"❄️ Min: {np.min(temperatures):.1f}K")
                ]
                
                if state.running:
                    progress = (current_time / state.target_time * 100) if state.target_time > 0 else 0
                    temp_info.append(html.P(f"📊 Progress: {progress:.1f}%"))
                    
            except Exception as e:
                temp_info = [html.P(f"❌ Error getting temps: {e}")]
        
        return fig, temp_info
        
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        fig = go.Figure()
        fig.update_layout(title=f"Error: {str(e)}", height=500)
        return fig, [html.P(f"❌ Error: {e}")]

if __name__ == '__main__':
    print("🚀 Starting Simplified Heat Transfer Dashboard...")
    print("📱 Open http://localhost:8050")
    app.run(host='0.0.0.0', port=8050, debug=True)