#!/usr/bin/env python3
"""Simple test to verify Python bindings work"""

try:
    import heat_transfer
    print("SUCCESS: heat_transfer module imported successfully!")
    
    # Test basic functionality
    generator = heat_transfer.CupGenerator()
    params = heat_transfer.CupParameters()
    print("SUCCESS: CupGenerator and CupParameters created!")
    
    # Generate a small test geometry
    params.point_spacing = 0.02  # Large spacing for quick test
    params.inner_radius = 0.03
    params.height = 0.05
    
    point_cloud = generator.generate(params)
    print(f"SUCCESS: Generated {point_cloud.size()} points!")
    
    # Test Materials
    materials = [
        heat_transfer.Material.coffee(),
        heat_transfer.Material.ceramic(),
        heat_transfer.Material.air()
    ]
    print("SUCCESS: Materials created!")
    
    # Test HeatSolver
    solver = heat_transfer.HeatSolver(point_cloud, materials, 0.1)
    print("SUCCESS: HeatSolver created!")
    
    # Run a few simulation steps
    for _ in range(5):
        solver.step()
    
    print(f"SUCCESS: Simulation ran, current time: {solver.get_current_time():.2f}s")
    print(f"Coffee temperature: {solver.get_average_temperature(0):.1f}K")
    
    print("\n✅ All tests passed! Your C++ core with Python bindings is working!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure to build the project first with ./scripts/build.sh")
except Exception as e:
    print(f"❌ Error: {e}")
    print("There might be an issue with the implementation")
