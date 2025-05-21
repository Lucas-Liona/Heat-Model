#!/usr/bin/env python3
"""
Test script to verify thermal conductivity calculation and material properties
"""

import heat_transfer
import numpy as np

def main():
    print("Heat Transfer Material Properties Test")
    print("=" * 50)
    
    # Create materials
    print("\nCreating materials...")
    materials = [
        heat_transfer.Material.coffee(),       # COFFEE - Index 0
        heat_transfer.Material.ceramic(),      # CUP_MATERIAL - Index 1
        heat_transfer.Material.air()           # AIR - Index 2
    ]

    # Print material properties for verification
    for i, material_name in enumerate(["Coffee", "Ceramic", "Air"]):
        material = materials[i]
        print(f"{material_name}: k={material.get_thermal_conductivity():.3f} W/(m·K), "
              f"ρ={material.get_density():.1f} kg/m³, "
              f"c={material.get_specific_heat():.1f} J/(kg·K), "
              f"T={material.get_ambient_temperature():.1f}K")

    # Create a simple test geometry
    print("\nGenerating test geometry...")
    generator = heat_transfer.CupGenerator()
    params = heat_transfer.CupParameters()
    params.point_spacing = 0.02  # Large spacing for quick test
    
    point_cloud = generator.generate(params)
    print(f"Generated {point_cloud.size()} points")
    
    # Create solver
    print("\nCreating solver...")
    solver = heat_transfer.HeatSolver(point_cloud, materials, 0.5)  # Larger time step for quick test
    
    # Check initial temperatures
    coffee_temp = solver.get_average_temperature(heat_transfer.MaterialType.COFFEE)
    cup_temp = solver.get_average_temperature(heat_transfer.MaterialType.CUP_MATERIAL)
    air_temp = solver.get_average_temperature(heat_transfer.MaterialType.AIR)
    
    print(f"Initial temperatures - Coffee: {coffee_temp:.1f}K ({coffee_temp-273.15:.1f}°C), "
          f"Cup: {cup_temp:.1f}K ({cup_temp-273.15:.1f}°C), "
          f"Air: {air_temp:.1f}K ({air_temp-273.15:.1f}°C)")
    
    # Run a few steps and check temperatures again
    print("\nRunning 5 simulation steps...")
    for i in range(5):
        solver.step()
        
        # Report temperatures after each step
        coffee_temp = solver.get_average_temperature(heat_transfer.MaterialType.COFFEE)
        cup_temp = solver.get_average_temperature(heat_transfer.MaterialType.CUP_MATERIAL)
        air_temp = solver.get_average_temperature(heat_transfer.MaterialType.AIR)
        
        print(f"Step {i+1} - Time: {solver.get_current_time():.1f}s")
        print(f"  Coffee: {coffee_temp:.1f}K ({coffee_temp-273.15:.1f}°C)")
        print(f"  Cup: {cup_temp:.1f}K ({cup_temp-273.15:.1f}°C)")
        print(f"  Air: {air_temp:.1f}K ({air_temp-273.15:.1f}°C)")
    
    print("\nTest completed. If temperature values are changing, heat transfer is working!")

if __name__ == "__main__":
    main()