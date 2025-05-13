import numpy as np
import pyvista as pv
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class HeatVisualizer:
    def __init__(self, point_cloud, solver=None):
        self.point_cloud = point_cloud
        self.solver = solver
        self.plotter = None
        
    def setup_3d_viewer(self):
        """Setup PyVista 3D viewer"""
        self.plotter = pv.Plotter()
        
        # Extract points and temperatures
        points = np.array([[self.point_cloud.get_point(i).get_position().x,
                           self.point_cloud.get_point(i).get_position().y,
                           self.point_cloud.get_point(i).get_position().z]
                          for i in range(self.point_cloud.size())])
        
        temperatures = np.array([self.point_cloud.get_point(i).get_temperature()
                               for i in range(self.point_cloud.size())])
        
        materials = np.array([int(self.point_cloud.get_point(i).get_material())
                            for i in range(self.point_cloud.size())])
        
        # Create point cloud
        cloud = pv.PolyData(points)
        cloud["temperature"] = temperatures
        cloud["material"] = materials
        
        # Add to plotter with color mapping
        self.plotter.add_mesh(cloud, 
                             scalars="temperature",
                             cmap="plasma",
                             point_size=5,
                             render_points_as_spheres=True)
        
        # Add scalar bar
        self.plotter.add_scalar_bar("Temperature (K)")
        
        # Set camera
        self.plotter.camera_position = [(0.1, -0.2, 0.15), (0, 0, 0.05), (0, 0, 1)]
        self.plotter.add_axes()
        
        return self.plotter
    
    def animate_simulation(self, num_steps=100, step_interval=0.1, save_gif=None):
        """Create animation of temperature evolution"""
        if self.solver is None:
            raise ValueError("Solver must be provided for animation")
        
        plotter = self.setup_3d_viewer()
        
        if save_gif:
            plotter.open_gif(save_gif)
        
        # Animation loop
        for step in range(num_steps):
            # Update simulation
            self.solver.step()
            
            # Update temperatures
            temperatures = np.array([self.point_cloud.get_point(i).get_temperature()
                                   for i in range(self.point_cloud.size())])
            
            # Update visualization
            plotter.update_scalars(temperatures)
            plotter.add_text(f"Time: {self.solver.get_current_time():.1f}s", 
                           position='upper_left')
            
            if save_gif:
                plotter.write_frame()
            else:
                plotter.update()
        
        if save_gif:
            plotter.close()
        else:
            plotter.show()
    
    def plot_temperature_profile(self, axis='z', position=0):
        """Plot temperature profile along specified axis"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract points and temperatures
        points = []
        temps = []
        materials = []
        
        for i in range(self.point_cloud.size()):
            point = self.point_cloud.get_point(i)
            pos = point.get_position()
            
            if axis == 'z':
                coord = pos.z
            elif axis == 'y':
                coord = pos.y  
            else:
                coord = pos.x
                
            points.append(coord)
            temps.append(point.get_temperature())
            materials.append(point.get_material())
        
        # Sort by coordinate
        sorted_indices = np.argsort(points)
        points = np.array(points)[sorted_indices]
        temps = np.array(temps)[sorted_indices]
        materials = np.array(materials)[sorted_indices]
        
        # Plot temperature profile
        scatter = ax.scatter(points, temps, c=materials, cmap='tab10', alpha=0.7)
        ax.set_xlabel(f'{axis.upper()} position (m)')
        ax.set_ylabel('Temperature (K)')
        ax.set_title(f'Temperature Profile along {axis.upper()}-axis')
        
        # Add colorbar for materials
        cbar = plt.colorbar(scatter)
        cbar.set_label('Material Type')
        
        plt.tight_layout()
        return fig, ax
    
    def create_cross_section(self, plane='xy', offset=0):
        """Create cross-section visualization"""
        # Filter points near the specified plane
        tolerance = 0.005  # 5mm tolerance
        filtered_points = []
        filtered_temps = []
        filtered_materials = []
        
        for i in range(self.point_cloud.size()):
            point = self.point_cloud.get_point(i)
            pos = point.get_position()
            
            if plane == 'xy' and abs(pos.z - offset) < tolerance:
                filtered_points.append([pos.x, pos.y])
                filtered_temps.append(point.get_temperature())
                filtered_materials.append(point.get_material())
            elif plane == 'xz' and abs(pos.y - offset) < tolerance:
                filtered_points.append([pos.x, pos.z])
                filtered_temps.append(point.get_temperature())
                filtered_materials.append(point.get_material())
            elif plane == 'yz' and abs(pos.x - offset) < tolerance:
                filtered_points.append([pos.y, pos.z])
                filtered_temps.append(point.get_temperature())
                filtered_materials.append(point.get_material())
        
        filtered_points = np.array(filtered_points)
        filtered_temps = np.array(filtered_temps)
        
        # Create scatter plot
        fig, ax = plt.subplots(figsize=(8, 8))
        scatter = ax.scatter(filtered_points[:, 0], filtered_points[:, 1], 
                           c=filtered_temps, cmap='plasma', s=30)
        
        ax.set_xlabel(f'{plane[0].upper()} (m)')
        ax.set_ylabel(f'{plane[1].upper()} (m)')
        ax.set_title(f'Cross-section: {plane.upper()} plane at {plane[2]}={offset}')
        ax.set_aspect('equal')
        
        cbar = plt.colorbar(scatter)
        cbar.set_label('Temperature (K)')
        
        plt.tight_layout()
        return fig, ax
    
    def plot_temperature_history(self, monitor_points=None):
        """Plot temperature history for selected points"""
        if monitor_points is None:
            # Default monitor points: center of coffee, cup wall, air
            monitor_points = [
                {'name': 'Coffee Center', 'pos': [0, 0, 0.04], 'material': 0},
                {'name': 'Cup Wall', 'pos': [0.037, 0, 0.04], 'material': 1},
                {'name': 'Air', 'pos': [0.05, 0, 0.04], 'material': 2}
            ]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # This would need to be implemented to track temperature history
        # For now, plot current temperatures
        for point_info in monitor_points:
            # Find closest point to specified position
            min_dist = float('inf')
            closest_temp = 0
            
            for i in range(self.point_cloud.size()):
                point = self.point_cloud.get_point(i)
                pos = point.get_position()
                dist = ((pos.x - point_info['pos'][0])**2 + 
                       (pos.y - point_info['pos'][1])**2 + 
                       (pos.z - point_info['pos'][2])**2)**0.5
                
                if dist < min_dist and point.get_material() == point_info['material']:
                    min_dist = dist
                    closest_temp = point.get_temperature()
            
            # Plot single point for now (would need history tracking)
            ax.plot([0], [closest_temp], 'o-', label=point_info['name'])
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Temperature (K)')
        ax.set_title('Temperature History at Monitor Points')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt://tight_layout()
        return fig, ax