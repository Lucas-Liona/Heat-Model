#!/usr/bin/env python3
"""
Basic heat transfer simulation example
"""

import heat_transfer
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def main():
    print("Heat Transfer Simulation - Basic Example")
    print("=" * 40)
    
    # Setup geometry
    print("Generating geometry...")
    generator = heat_transfer.CupGenerator()
    params = heat_transfer.CupParameters()
    
    # Customize parameters
    params.inner_radius = 0.035      # 3.5 cm
    params.wall_thickness = 0.003    # 3 mm
    params.height = 0.09            # 9 cm
    params.coffee_height = 0.08     # 8 cm
    params.point_spacing = 0.005    # 5 mm (coarse for quick demo)
    params.coffee_temp = 363.15     # 90°C
    params.cup_temp = 293.15        # 20°C
    params.air_temp = 293.15        # 20°C
    
    # Generate point cloud
    point_cloud = generator.generate(params)
    print(f"Generated {point_cloud.size()} points")
    
    # Setup materials
    materials = [
        heat_transfer.Material.coffee(),
        heat_transfer.Material.ceramic(),
        heat_transfer.Material.air()
    ]
    
    # Create solver
    print("Initializing solver...")
    solver = heat_transfer.HeatSolver(point_cloud, materials, 0.1)  # 0.1s time step
    
    # Run simulation
    print("Running simulation...")
    simulation_time = 600.0  # 10 minutes
    num_steps = int(simulation_time / 0.1)
    
    # Track temperature history
    time_points = []
    coffee_temps = []
    cup_temps = []
    air_temps = []
    
    for step in tqdm(range(num_steps)):
        solver.step()
        
        if step % 10 == 0:  # Record every second
            time_points.append(solver.get_current_time())
            coffee_temps.append(solver.get_average_temperature(0))  # Coffee
            cup_temps.append(solver.get_average_temperature(1))     # Cup
            air_temps.append(solver.get_average_temperature(2))     # Air
    
    # Plot results
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(time_points, coffee_temps, 'o-', color='brown', label='Coffee')
    plt.plot(time_points, cup_temps, 's-', color='orange', label='Cup')
    plt.plot(time_points, air_temps, '^-', color='lightblue', label='Air')
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (K)')
    plt.title('Average Temperature by Material')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 2)
    # Temperature profile along vertical axis (z)
    z_positions = []
    z_temperatures = []
    for i in range(point_cloud.size()):
        point = point_cloud.get_point(i)
        if point.get_material() == 0:  # Coffee only
            pos = point.get_position()
            z_positions.append(pos.z)
            z_temperatures.append(point.get_temperature())
    
    plt.scatter(z_positions, z_temperatures, alpha=0.6)
    plt.xlabel('Z position (m)')
    plt.ylabel('Temperature (K)')
    plt.title('Coffee Temperature vs Height')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 3)
    # Final temperature distribution
    final_temps = []
    for i in range(point_cloud.size()):
        final_temps.append(point_cloud.get_point(i).get_temperature())
    
    plt.hist(final_temps, bins=50, alpha=0.7)
    plt.xlabel('Temperature (K)')
    plt.ylabel('Number of Points')
    plt.title('Final Temperature Distribution')
    
    plt.subplot(2, 2, 4)
    # Cooling rate
    cooling_rate = -np.gradient(coffee_temps, time_points)
    plt.plot(time_points[:-1], cooling_rate[:-1], 'r-')
    plt.xlabel('Time (s)')
    plt.ylabel('Cooling Rate (K/s)')
    plt.title('Coffee Cooling Rate')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('heat_transfer_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save final state
    print("Saving results...")
    point_cloud.save_to_vtk('final_state.vtk')
    
    print("\nSimulation complete!")
    print(f"Initial coffee temperature: {coffee_temps[0]:.1f} K ({coffee_temps[0]-273.15:.1f} °C)")
    print(f"Final coffee temperature: {coffee_temps[-1]:.1f} K ({coffee_temps[-1]-273.15:.1f} °C)")
    print(f"Temperature drop: {coffee_temps[0]-coffee_temps[-1]:.1f} K")

if __name__ == '__main__':
    main()