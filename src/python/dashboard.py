import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import threading
import time

import heat_transfer
from heat_transfer.visualization import HeatVisualizer

class HeatTransferDashboard:
    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.point_cloud = None
        self.solver = None
        self.visualizer = None
        self.simulation_running = False
        self.simulation_thread = None
        self.temp_history = {'time': [], 'coffee': [], 'cup': [], 'air': []}
        
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Create dashboard layout"""
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Heat Transfer Simulation Dashboard", className="mb-4"),
                    html.P("Interactive simulation of heat transfer in a coffee cup")
                ])
            ]),
            
            # Parameters Card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Simulation Parameters"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Point Spacing (mm)"),
                                    dcc.Slider(id='point-spacing', min=1, max=10, 
                                             value=3, marks={i: str(i) for i in range(1, 11)})
                                ], width=6),
                                dbc.Col([
                                    html.Label("Simulation Speed"),
                                    dcc.Slider(id='sim-speed', min=0.1, max=2.0, 
                                             value=1.0, step=0.1)
                                ], width=6)
                            ]),
                            html.Hr(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Generate Geometry", id='generate-btn', 
                                             color="primary", className='me-2'),
                                    dbc.Button("Start Simulation", id='start-btn', 
                                             color="success", className='me-2'),
                                    dbc.Button("Stop Simulation", id='stop-btn', 
                                             color="danger", className='me-2'),
                                    dbc.Button("Reset", id='reset-btn', 
                                             color="secondary")
                                ])
                            ])
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Visualization Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("3D Visualization"),
                        dbc.CardBody([
                            dcc.Graph(id='3d-plot', style={'height': '500px'})
                        ])
                    ])
                ], width=8),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Temperature Profile"),
                        dbc.CardBody([
                            dcc.Graph(id='temp-profile', style={'height': '500px'})
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            # Statistics Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Statistics"),
                        dbc.CardBody([
                            html.Div(id='statistics')
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Temperature History"),
                        dbc.CardBody([
                            dcc.Graph(id='temp-history', style={'height': '300px'})
                        ])
                    ])
                ], width=6)
            ]),
            
            # Interval component for updates
            dcc.Interval(id='interval-component', interval=1000, n_intervals=0, disabled=True)
        ], fluid=True)
    
    def setup_callbacks(self):
        """Setup Dash callbacks"""
        
        @self.app.callback(
            [Output('start-btn', 'disabled'),
             Output('stop-btn', 'disabled'),
             Output('interval-component', 'disabled')],
            [Input('generate-btn', 'n_clicks'),
             Input('start-btn', 'n_clicks'),
             Input('stop-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def update_simulation_state(generate_clicks, start_clicks, stop_clicks):
            ctx = dash.callback_context
            
            if not ctx.triggered:
                return True, True, True
            
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if trigger_id == 'generate-btn':
                self.generate_geometry()
                return False, True, True
            elif trigger_id == 'start-btn':
                self.start_simulation()
                return True, False, False
            elif trigger_id == 'stop-btn':
                self.stop_simulation()
                return False, True, True
            
            return True, True, True
        
        @self.app.callback(
            [Output('3d-plot', 'figure'),
             Output('temp-profile', 'figure'),
             Output('statistics', 'children'),
             Output('temp-history', 'figure')],
            [Input('interval-component', 'n_intervals')],
            prevent_initial_call=True
        )
        def update_plots(n_intervals):
            if self.point_cloud is None:
                return {}, {}, "", {}
            
            # Update 3D plot
            fig_3d = self.create_3d_plot()
            
            # Update temperature profile
            fig_profile = self.create_temp_profile()
            
            # Update statistics
            stats = self.create_statistics()
            
            # Update temperature history
            fig_history = self.create_temp_history()
            
            return fig_3d, fig_profile, stats, fig_history
    
    def generate_geometry(self):
        """Generate coffee cup geometry"""
        generator = heat_transfer.CupGenerator()
        params = heat_transfer.CupParameters()
        params.point_spacing = 0.003  # 3mm spacing
        
        self.point_cloud = generator.generate(params)
        
        # Initialize solver
        materials = [heat_transfer.Material.coffee(), 
                    heat_transfer.Material.ceramic(),
                    heat_transfer.Material.air()]
        self.solver = heat_transfer.HeatSolver(self.point_cloud, materials, 0.1)
        self.visualizer = HeatVisualizer(self.point_cloud, self.solver)
    
    def start_simulation(self):
        """Start simulation in separate thread"""
        if self.simulation_running:
            return
        
        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self.run_simulation)
        self.simulation_thread.start()
    
    def stop_simulation(self):
        """Stop simulation"""
        self.simulation_running = False
        if self.simulation_thread:
            self.simulation_thread.join()
    
    def run_simulation(self):
        """Run simulation loop"""
        while self.simulation_running:
            self.solver.step()
            
            # Update temperature history
            current_time = self.solver.get_current_time()
            self.temp_history['time'].append(current_time)
            
            # Get average temperatures by material
            coffee_temp = self.solver.get_average_temperature(0)  # Coffee
            cup_temp = self.solver.get_average_temperature(1)    # Cup
            air_temp = self.solver.get_average_temperature(2)    # Air
            
            self.temp_history['coffee'].append(coffee_temp)
            self.temp_history['cup'].append(cup_temp)
            self.temp_history['air'].append(air_temp)
            
            time.sleep(0.1)  # Control simulation speed
    
    def create_3d_plot(self):
        """Create 3D scatter plot of point cloud"""
        points = []
        temps = []
        materials = []
        
        for i in range(self.point_cloud.size()):
            point = self.point_cloud.get_point(i)
            pos = point.get_position()
            points.append([pos.x, pos.y, pos.z])
            temps.append(point.get_temperature())
            materials.append(point.get_material())
        
        points = np.array(points)
        temps = np.array(temps)
        
        # Create 3D scatter plot
        fig = go.Figure(data=go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='markers',
            marker=dict(
                size=3,
                color=temps,
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title="Temperature (K)")
            ),
            text=[f"Material: {mat}, Temp: {temp:.1f}K" for mat, temp in zip(materials, temps)]
        ))
        
        fig.update_layout(
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Z (m)'
            ),
            height=500
        )
        
        return fig
    
    def create_temp_profile(self):
        """Create temperature profile cross-section"""
        # Get points near z=0.04 (middle of coffee)
        z_target = 0.04
        tolerance = 0.005
        
        profile_points = []
        profile_temps = []
        
        for i in range(self.point_cloud.size()):
            point = self.point_cloud.get_point(i)
            pos = point.get_position()
            
            if abs(pos.z - z_target) < tolerance:
                profile_points.append([pos.x, pos.y])
                profile_temps.append(point.get_temperature())
        
        profile_points = np.array(profile_points)
        profile_temps = np.array(profile_temps)
        
        # Create 2D scatter plot
        fig = go.Figure(data=go.Scatter(
            x=profile_points[:, 0],
            y=profile_points[:, 1],
            mode='markers',
            marker=dict(
                color=profile_temps,
                colorscale='Plasma',
                showscale=True,
                size=8
            ),
            text=[f"Temp: {temp:.1f}K" for temp in profile_temps]
        ))
        
        fig.update_layout(
            title=f"Temperature Cross-section at z={z_target}m",
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            showlegend=False
        )
        
        return fig
    
    def create_statistics(self):
        """Create statistics summary"""
        if self.solver is None:
            return html.P("No simulation running")
        
        stats = [
            html.H5("Current Statistics"),
            html.P([
                html.Strong("Simulation Time: "),
                f"{self.solver.get_current_time():.1f} seconds"
            ]),
            html.P([
                html.Strong("Maximum Temperature: "),
                f"{self.solver.get_max_temperature():.1f} K"
            ]),
            html.P([
                html.Strong("Minimum Temperature: "),
                f"{self.solver.get_min_temperature():.1f} K"
            ]),
            html.P([
                html.Strong("Total Points: "),
                f"{self.point_cloud.size():,}"
            ])
        ]
        
        return stats
    
    def create_temp_history(self):
        """Create temperature history plot"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.temp_history['time'],
            y=self.temp_history['coffee'],
            mode='lines+markers',
            name='Coffee',
            line=dict(color='orange')
        ))
        
        fig.add_trace(go.Scatter(
            x=self.temp_history['time'],
            y=self.temp_history['cup'],
            mode='lines+markers',
            name='Cup',
            line=dict(color='brown')
        ))
        
        fig.add_trace(go.Scatter(
            x=self.temp_history['time'],
            y=self.temp_history['air'],
            mode='lines+markers',
            name='Air',
            line=dict(color='lightblue')
        ))
        
        fig.update_layout(
            title="Average Temperature by Material",
            xaxis_title="Time (s)",
            yaxis_title="Temperature (K)",
            showlegend=True
        )
        
        return fig
    
    def run(self, host='0.0.0.0', port=8050, debug=False):
        """Run the dashboard"""
        self.app.run_server(host=host, port=port, debug=debug)


if __name__ == '__main__':
    dashboard = HeatTransferDashboard()
    dashboard.run(debug=True)