from dataclasses import dataclass

MATERIAL_VISUAL_PROPS = {
    0: {'size': 3},  # Coffee
    1: {'size': 4},  # Ceramic  
    2: {'size': 1}   # Air
}

MATERIAL_NAMES = {
    0: 'Coffee', 
    1: 'Ceramic', 
    2: 'Air'
}

@dataclass
class SimulationConfig:
    # Geometry
    inner_radius: float = 0.035      # meters
    wall_thickness: float = 0.003    # meters  
    height: float = 0.09            # meters
    coffee_height: float = 0.08     # meters
    point_spacing: float = 0.005    # meters
    
    # Initial temperatures (in Kelvin for C++, display in Celsius for UI)
    coffee_temp_c: float = 90.0     # Celsius
    cup_temp_c: float = 20.0        # Celsius  
    air_temp_c: float = 20.0        # Celsius
    
    # Simulation
    time_step: float = 0.1          # seconds
    
    @property
    def coffee_temp_k(self) -> float:
        return self.coffee_temp_c + 273.15
    
    @property
    def cup_temp_k(self) -> float:
        return self.cup_temp_c + 273.15
    
    @property
    def air_temp_k(self) -> float:
        return self.air_temp_c + 273.15
    
    # Add validation
    def validate(self):
        assert self.coffee_temp_c > self.cup_temp_c, "Coffee must be hotter than cup"
        assert self.point_spacing > 0, "Point spacing must be positive"
        assert self.inner_radius > 0, "Inner radius must be positive"
        assert self.wall_thickness > 0, "Wall thickness must be positive"