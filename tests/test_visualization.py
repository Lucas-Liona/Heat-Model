import unittest
import numpy as np
import heat_transfer
from heat_transfer.visualization import HeatVisualizer

class TestVisualization(unittest.TestCase):
    def setUp(self):
        # Create small test geometry
        generator = heat_transfer.CupGenerator()
        params = heat_transfer.CupParameters()
        params.point_spacing = 0.01  # 1cm spacing
        params.inner_radius = 0.05   # 5cm radius
        params.height = 0.1          # 10cm height
        
        self.point_cloud = generator.generate(params)
        
        materials = [heat_transfer.Material.coffee(),
                    heat_transfer.Material.ceramic(),
                    heat_transfer.Material.air()]
        self.solver = heat_transfer.HeatSolver(self.point_cloud, materials, 0.001)
        self.visualizer = HeatVisualizer(self.point_cloud, self.solver)
    
    def test_temperature_profile_creation(self):
        """Test that temperature profiles can be created"""
        fig, ax = self.visualizer.plot_temperature_profile('z')
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
    
    def test_cross_section_creation(self):
        """Test that cross-sections can be created"""
        fig, ax = self.visualizer.create_cross_section('xy', 0.05)
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
    
    def test_3d_viewer_setup(self):
        """Test that 3D viewer can be set up"""
        plotter = self.visualizer.setup_3d_viewer()
        self.assertIsNotNone(plotter)

if __name__ == '__main__':
    unittest.main()