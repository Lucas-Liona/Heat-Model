#include <gtest/gtest.h>
#include "HeatSolver.hpp"
#include "CupGenerator.hpp"
#include <cmath>

class HeatSolverTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Create small test geometry
        CupGenerator generator;
        CupGenerator::Parameters params;
        params.pointSpacing = 0.01;  // 1cm spacing for fast test
        params.innerRadius = 0.05;   // 5cm radius
        params.height = 0.1;         // 10cm height
        
        point_cloud = generator.generate(params);
        
        // Create materials
        materials = {
            Material::Coffee(),
            Material::Ceramic(),
            Material::Air()
        };
        
        // Create solver
        solver = std::make_unique<HeatSolver>(point_cloud, materials, 0.001);
    }
    
    PointCloud point_cloud;
    std::vector<Material> materials;
    std::unique_ptr<HeatSolver> solver;
};

TEST_F(HeatSolverTest, InitialTemperatures) {
    // Check that initial temperatures are set correctly
    double coffee_temp = solver->getAverageTemperature(MaterialType::COFFEE);
    double cup_temp = solver->getAverageTemperature(MaterialType::CUP_MATERIAL);
    double air_temp = solver->getAverageTemperature(MaterialType::AIR);
    
    EXPECT_NEAR(coffee_temp, 363.15, 1.0);  // ~90°C
    EXPECT_NEAR(cup_temp, 293.15, 1.0);     // ~20°C
    EXPECT_NEAR(air_temp, 293.15, 1.0);     // ~20°C
}

TEST_F(HeatSolverTest, TemperatureDecrease) {
    // Coffee should cool down over time
    double initial_temp = solver->getAverageTemperature(MaterialType::COFFEE);
    
    // Run simulation for 10 seconds
    solver->run(10.0);
    
    double final_temp = solver->getAverageTemperature(MaterialType::COFFEE);
    
    EXPECT_LT(final_temp, initial_temp);
    EXPECT_GT(final_temp, 293.15);  // Should still be above room temperature
}

TEST_F(HeatSolverTest, EnergyConservation) {
    // Total energy should be conserved (or decrease with cooling)
    double initial_energy = calculateTotalEnergy();
    
    solver->run(5.0);
    
    double final_energy = calculateTotalEnergy();
    
    // Energy should decrease (cooling to environment)
    EXPECT_LE(final_energy, initial_energy);
}

double HeatSolverTest::calculateTotalEnergy() {
    double total_energy = 0.0;
    
    for (size_t i = 0; i < point_cloud.size(); i++) {
        const Point& point = point_cloud.getPoint(i);
        const Material& material = materials[static_cast<int>(point.getMaterial())];
        
        // Assume unit volume per point for simplicity
        total_energy += material.getDensity() * material.getSpecificHeat() * 
                       point.getTemperature();
    }
    
    return total_energy;
}