#pragma once
#include "PointCloud.hpp"
#include "Material.hpp"
#include <vector>

class HeatSolver {
public:
    HeatSolver(PointCloud& pointCloud, const std::vector<Material>& materials, double timeStep);

    double calculate_K(MaterialType mat1, MaterialType mat2);
    void step();
    void run_for_time(double duration);
    
    double getCurrentTime() const;
    double getAverageTemperature(MaterialType material) const;
    double getMaxTemperature() const;
    double getMinTemperature() const;

private:
    PointCloud& pointCloud_;
    const std::vector<Material> materials_;
    double timeStep_;
    double currentTime_;
};