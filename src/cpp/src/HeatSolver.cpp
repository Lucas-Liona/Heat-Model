#include "HeatSolver.hpp"
#include <algorithm>
#include <iostream>
#include <cmath>

HeatSolver::HeatSolver(PointCloud& pointCloud, const std::vector<Material>& materials, double timeStep)
    : pointCloud_(pointCloud), materials_(materials), timeStep_(timeStep), currentTime_(0.0) {}


double HeatSolver::calculate_K(MaterialType mat1, MaterialType mat2) {
    // Access thermal conductivity from materials vector using MaterialType as index
    double k1 = materials_[static_cast<int>(mat1)].getThermalConductivity();
    double k2 = materials_[static_cast<int>(mat2)].getThermalConductivity();
    
    if (mat1 == mat2) {
        return k1;  // same material
    }

    std::cout << "K1: " << k1 << " K2: " << k2 << "harmonic mean:" << 2.0 * k1 * k2 / (k1 + k2) << std::endl;

    // Different materials: harmonic mean
    return 2.0 * k1 * k2 / (k1 + k2);
}

/*
    So the way it stands I am somewhere between SoA and AoS. while the heatsolver code is architecturally built like
    Array of Structures, where you reference a single point, this is really an interface with the Structure of Arrays
    architecture in PointCloud. In the future I will change this to fully utilize the switch but for now this works

    I also want to change the way neighbors are calculated. Its currently n^2, with kd tree it can be nlogn, but with 
    this particular grid setup I think something O(1) is possible. But for future scaling with imperfect spacing then its
    better to use kd tree.

*/

void HeatSolver::step() {

    /*
    so the basic sudo code or idea is to apply fouriers law    q = k × A × (dT/dx)        and       dT/dt = Q / (ρ × heatcapacity × V)

    we first find the values, then set them all at once. This way we really skip in time so everything is fairly distributed

    important to note we shouldnt really do this for every particle, we should have  simulation bound arond the coffee cup and then outside of that is boundary condition
    or room temperature

    for each neighbor
        get the difference in temperature
        get distance between them

        calculate k (the effective conduction between two materials, ie, air to air VS air to coffee)

        then we need to handle contact area and volume, because were using a point cloud these should most likely be constants representing the volume of a particle and the area of a particle

    then set newTemperatures[i]

    */

    std::vector<double> newTemperatures(pointCloud_.size());

    for (size_t i = 0; i < pointCloud_.size(); ++i) {

        auto focal_point = pointCloud_.getPoint(i);

        //std::cout << focal_point.getIndex() << std::endl;
        
        double currentTemp = focal_point.getTemperature();

        //std::cout << currentTemp << std::endl;

        double totalHeatTransfer = 0.0;
        
        // brute force neighbor search, WILL BE IMPROVED LATER
        for (size_t j = 0; j < pointCloud_.size(); ++j) {
            if (i == j) continue;
            
            auto neighbor = pointCloud_.getPoint(j);
            Position currentPos = focal_point.getPosition();
            Position neighborPos = neighbor.getPosition();
            
            // CALCULATE DISTANCE
            double dx = neighborPos.x - currentPos.x;
            double dy = neighborPos.y - currentPos.y;
            double dz = neighborPos.z - currentPos.z;
            double distance = std::sqrt(dx*dx + dy*dy + dz*dz);
            
            if (distance > 0.01) continue; // 1cm cutoff
            
            // Calculate heat transfer rate between the two points
            double tempDiff = neighbor.getTemperature() - currentTemp;
            double k_eff = calculate_K(focal_point.getMaterial(), 
                                      neighbor.getMaterial());
                                      
            // Simple heat transfer: Q = k * A * dT/dx
            // using constant area and volume
            double area = 1e-6; // 1mm² contact area
            double heatTransferRate = k_eff * area * tempDiff / distance;
            totalHeatTransfer += heatTransferRate;

            std::cout << "Distance: " << distance << " k_eff: " << k_eff << "tempDiff:" << tempDiff <<std::endl;

        }
        // temperature change: dT = Q * dt / (rho * c * V)
        MaterialType material = focal_point.getMaterial();
        const Material& mat = materials_[static_cast<int>(material)];
        double rho = mat.getDensity();
        double c = mat.getSpecificHeat();
        double V = 1e-9; // 1mm³ volume per point

        double tempChange = totalHeatTransfer * timeStep_ / (rho * c * V);
        //std::cout << "Point " << i << " temp change: " << tempChange << "K" << std::endl;

        newTemperatures[i] = currentTemp + tempChange;
                
    }
    
    // Apply all temperature changes at once
    for (size_t i = 0; i < pointCloud_.size(); ++i) {

        auto point = pointCloud_.getPoint(i);
        point.setTemperature(newTemperatures[i]);
    }
    
    currentTime_ += timeStep_;
    
    std::cout << "Step completed, time: " << currentTime_ << std::endl;
}

void HeatSolver::run_for_time(double duration) {
    double endTime = currentTime_ + duration;
    
    while (currentTime_ < endTime) {
        step();
    }
}

double HeatSolver::getCurrentTime() const {
    return currentTime_;
}

double HeatSolver::getAverageTemperature(MaterialType material) const {
    double sum = 0.0;
    size_t count = 0;
    
    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        const auto point = pointCloud_.getPoint(i);
        if (point.getMaterial() == material) {
            sum += point.getTemperature();
            count++;
        }
    }
    
    return count > 0 ? sum / count : 0.0;
}

double HeatSolver::getMaxTemperature() const {
    double maxTemp = 0.0;
    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        maxTemp = std::max(maxTemp, pointCloud_.getPoint(i).getTemperature());
    }
    return maxTemp;
}

double HeatSolver::getMinTemperature() const {
    if (pointCloud_.size() == 0) return 0.0;
    
    auto minTemp = double{pointCloud_.getPoint(0).getTemperature()};
    for (auto i = size_t{1}; i < pointCloud_.size(); ++i) {
        minTemp = std::min(minTemp, pointCloud_.getPoint(i).getTemperature());
    }
    return minTemp;
}