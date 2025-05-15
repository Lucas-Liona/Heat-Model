#!/usr/bin/env python3
"""
Simple visualization test for heat transfer simulation
You can modify this to display whatever you want to debug
"""

import heat_transfer
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def create_test_visualization():
    """Create a simple test visualization that you can modify for debugging"""
    
    # Generate test geometry
    generator = heat_transfer.CupGenerator()
    params = heat_transfer.CupParameters()
    
    # Adjust these parameters for your tests
    params.point_spacing = 0.01      # 1cm spacing for quick test
    params.inner_radius = 0.035      # 3.5cm radius
    params.wall_thickness = 0.003    # 3mm wall
    params.height = 0.08            # 8cm height
    params.coffee_height = 0.06     # 6cm coffee height
    
    # Generate point cloud
    point_cloud = generator.generate(params)
    print(f"Generated {point_cloud.size()} points")
    
    # Extract data for visualization
    positions = []
    temperatures = []
    materials = []
    
    for i in range(point_cloud.size()):
        point = point_cloud.get_point(i)
        pos = point.get_position()
        positions.append([pos.x, pos.y, pos.z])
        temperatures.append(point.get_temperature())
        materials.append(int(point.get_material()))
    
    positions = np.array(positions)
    temperatures = np.array(temperatures)
    materials = np.array(materials)
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(15, 10))
    
    # 3D scatter plot
    ax1 = fig.add_subplot(2, 3, 1, projection='3d')
    scatter = ax1.scatter(positions[:, 0], positions[:, 1], positions[:, 2], 
                         c=temperatures, cmap='plasma', s=20)
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_zlabel('Z (m)')
    ax1.set_title('3D Point Cloud (colored by temperature)')
    plt.colorbar(scatter, ax=ax1, label='Temperature (K)')
    
    # Top-down view (coffee surface)
    ax2 = fig.add_subplot(2, 3, 2)
    coffee_points = positions[materials == 0]  # Coffee material
    coffee_temps = temperatures[materials == 0]
    if len(coffee_points) > 0:
        scatter2 = ax2.scatter(coffee_points[:, 0], coffee_points[:, 1], 
                              c=coffee_temps, cmap='plasma', s=30)
        ax2.set_xlabel('X (m)')
        ax2.set_ylabel('Y (m)')
        ax2.set_title('Coffee Surface (top view)')
        ax2.set_aspect('equal')
        plt.colorbar(scatter2, ax=ax2, label='Temperature (K)')
    
    # Side view cross-section
    ax3 = fig.add_subplot(2, 3, 3)
    side_points = positions[np.abs(positions[:, 1]) < 0.005]  # Points near y=0
    side_temps = temperatures[np.abs(positions[:, 1]) < 0.005]
    side_materials = materials[np.abs(positions[:, 1]) < 0.005]
    
    if len(side_points) > 0:
        scatter3 = ax3.scatter(side_points[:, 0], side_points[:, 2], 
                              c=side_temps, cmap='plasma', s=30)
        ax3.set_xlabel('X (m)')
        ax3.set_ylabel('Z (m)')
        ax3.set_title('Cross-section (y≈0)')
        ax3.set_aspect('equal')
        plt.colorbar(scatter3, ax=ax3, label='Temperature (K)')
    
    # Material distribution
    ax4 = fig.add_subplot(2, 3, 4)
    material_names = ['Coffee', 'Ceramic', 'Air']
    material_counts = [np.sum(materials == i) for i in range(3)]
    bars = ax4.bar(material_names, material_counts, color=['brown', 'orange', 'lightblue'])
    ax4.set_ylabel('Number of Points')
    ax4.set_title('Material Distribution')
    
    # Add count labels on bars
    for bar, count in zip(bars, material_counts):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2, height + count*0.01,
                f'{count}', ha='center', va='bottom')
    
    # Temperature distribution histogram
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.hist(temperatures, bins=30, alpha=0.7, color='red', edgecolor='black')
    ax5.set_xlabel('Temperature (K)')
    ax5.set_ylabel('Number of Points')
    ax5.set_title('Temperature Distribution')
    ax5.axvline(np.mean(temperatures), color='black', linestyle='--', 
                label=f'Mean: {np.mean(temperatures):.1f}K')
    ax5.legend()
    
    # Radial temperature profile
    ax6 = fig.add_subplot(2, 3, 6)
    # Calculate radial distance from center
    radial_distances = np.sqrt(positions[:, 0]**2 + positions[:, 1]**2)
    
    # Bin by radial distance and calculate mean temperature
    r_bins = np.linspace(0, np.max(radial_distances), 20)
    r_centers = (r_bins[:-1] + r_bins[1:]) / 2
    temp_profile = []
    
    for i in range(len(r_bins)-1):
        mask = (radial_distances >= r_bins[i]) & (radial_distances < r_bins[i+1])
        if np.any(mask):
            temp_profile.append(np.mean(temperatures[mask]))
        else:
            temp_profile.append(np.nan)
    
    ax6.plot(r_centers, temp_profile, 'o-', linewidth=2, markersize=6)
    ax6.set_xlabel('Radial Distance (m)')
    ax6.set_ylabel('Average Temperature (K)')
    ax6.set_title('Radial Temperature Profile')
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test_visualization.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return point_cloud

def run_simple_simulation_test(point_cloud):
    """Run a simple simulation and show temperature evolution"""
    
    # Setup materials and solver
    materials = [
        heat_transfer.Material.coffee(),
        heat_transfer.Material.ceramic(),
        heat_transfer.Material.air()
    ]
    
    solver = heat_transfer.HeatSolver(point_cloud, materials, 0.1)  # 0.1s time step
    
    # Track temperature history
    time_points = []
    coffee_temps = []
    cup_temps = []
    air_temps = []
    
    print("Running simulation...")
    for step in range(100):  # Run for 10 seconds
        solver.step()
        
        if step % 10 == 0:  # Record every second
            time_points.append(solver.get_current_time())
            coffee_temps.append(solver.get_average_temperature(0))
            cup_temps.append(solver.get_average_temperature(1))
            air_temps.append(solver.get_average_temperature(2))
            
            print(f"Time: {solver.get_current_time():.1f}s, Coffee: {coffee_temps[-1]:.1f}K")
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, coffee_temps, 'o-', color='brown', linewidth=2, markersize=8, label='Coffee')
    plt.plot(time_points, cup_temps, 's-', color='orange', linewidth=2, markersize=8, label='Cup')
    plt.plot(time_points, air_temps, '^-', color='lightblue', linewidth=2, markersize=8, label='Air')
    
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Temperature (K)', fontsize=12)
    plt.title('Temperature Evolution During Simulation', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add temperature in Celsius on right y-axis
    ax2 = plt.gca().twinx()
    ax2.set_ylabel('Temperature (°C)', fontsize=12)
    ax2.set_ylim(np.array(plt.gca().get_ylim()) - 273.15)
    
    plt.tight_layout()
    plt.savefig('simulation_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save final state to VTK for external visualization
    point_cloud.save_to_vtk('final_state.vtk')
    print(f"Final state saved to final_state.vtk")
    print(f"You can view this file in ParaView or other VTK viewers")

def main():
    print("Heat Transfer Visualization Test")
    print("=" * 40)
    
    try:
        # Import heat_transfer module
        import heat_transfer
        print("✅ Successfully imported heat_transfer module")
        
        # Create test visualization
        print("\n1. Creating initial visualization...")
        point_cloud = create_test_visualization()
        
        # Run simulation test
        print("\n2. Running simulation test...")
        run_simple_simulation_test(point_cloud)
        
        print("\n✅ All tests completed successfully!")
        print("\nFiles created:")
        print("- test_visualization.png: Initial geometry visualization")
        print("- simulation_results.png: Temperature evolution plot")
        print("- final_state.vtk: Final simulation state (viewable in ParaView)")
        
    except ImportError as e:
        print(f"❌ Error importing heat_transfer: {e}")
        print("Make sure you've built the project with: ./scripts/build.sh")
    except Exception as e:
        print(f"❌ Error during visualization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()