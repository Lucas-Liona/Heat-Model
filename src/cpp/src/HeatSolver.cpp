#include "HeatSolver.hpp"
#include <algorithm>
#include <iostream>
#include <cmath>

HeatSolver::HeatSolver(PointCloud& pointCloud, const std::vector<Material>& materials, double timeStep)
    : pointCloud_(pointCloud), materials_(materials), timeStep_(timeStep), currentTime_(0.0) {
        // Verify material properties
        if (materials_.size() < 3) {
            std::cerr << "ERROR: Not enough materials provided. Expected at least 3." << std::endl;
            return;
        }
        
        // Check each material's thermal conductivity
        for (size_t i = 0; i < materials_.size(); i++) {
            double k = materials_[i].getThermalConductivity();
            if (k < 0.001) {
                std::cerr << "WARNING: Material " << i << " has very low thermal conductivity: " 
                        << k << std::endl;
            } else {
                std::cout << "Material " << i << " thermal conductivity: " << k << std::endl;
            }
        }
    }

double HeatSolver::calculate_K(MaterialType mat1, MaterialType mat2) {
    // Access thermal conductivity from materials vector using MaterialType as index
    double k1 = materials_[static_cast<int>(mat1)].getThermalConductivity();
    double k2 = materials_[static_cast<int>(mat2)].getThermalConductivity();
    
    if (mat1 == mat2) {
        return k1;  // same material
    }
    
    // Different materials: harmonic mean
    return 2.0 * k1 * k2 / (k1 + k2);
}

void HeatSolver::step() {
    // Build k-d tree on first step if not already built
    if (!pointCloud_.isKDTreeBuilt()) {
        std::cout << "Building k-d tree for neighbor search..." << std::endl;
        pointCloud_.buildKDTree();
    }
    
    std::cout << "Materials vector size: " << materials_.size() << std::endl;
    for (size_t i = 0; i < materials_.size(); i++) {
        std::cout << "Material " << i << " thermal conductivity: " 
                  << materials_[i].getThermalConductivity() << std::endl;
    }

    std::vector<double> newTemperatures(pointCloud_.size());

    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        auto focal_point = pointCloud_.getPoint(i);
        double currentTemp = focal_point.getTemperature();
        double totalHeatTransfer = 0.0;
        
        // Use nanoflann k-d tree to find neighbors within 1cm
        std::vector<size_t> neighborIndices = pointCloud_.findNeighborsInRadius(i, 0.01);
        
        // Debug: Print neighbor count for first few points
        if (i < 5) {
            std::cout << "Point " << i << " has " << neighborIndices.size() << " neighbors" << std::endl;
        }
        
        // Process each neighbor
        for (size_t neighborIdx : neighborIndices) {
            auto neighbor = pointCloud_.getPoint(neighborIdx);
            Position currentPos = focal_point.getPosition();
            Position neighborPos = neighbor.getPosition();
            
            // Calculate distance
            double dx = neighborPos.x - currentPos.x;
            double dy = neighborPos.y - currentPos.y;
            double dz = neighborPos.z - currentPos.z;
            double distance = std::sqrt(dx*dx + dy*dy + dz*dz);
            
            if (distance < 1e-10) continue; // Avoid division by zero
            
            // Calculate heat transfer rate between the two points
            double tempDiff = neighbor.getTemperature() - currentTemp;
            double k_eff = calculate_K(focal_point.getMaterial(), 
                                      neighbor.getMaterial());
                                      
            // Simple heat transfer: Q = k * A * dT/dx
            // using constant area and volume
            double area = 1e-6; // 1mm² contact area
            double heatTransferRate = k_eff * area * tempDiff / distance;
            totalHeatTransfer += heatTransferRate;

            // Debug output for first point only
            if (i == 0 && neighborIndices.size() > 0) {
                std::cout << "  Neighbor " << neighborIdx << ": distance=" << distance 
                         << ", k_eff=" << k_eff << ", tempDiff=" << tempDiff << std::endl;
            }
        }
        
        // Calculate temperature change: dT = Q * dt / (rho * c * V)
        MaterialType material = focal_point.getMaterial();
        const Material& mat = materials_[static_cast<int>(material)];
        double rho = mat.getDensity();
        double c = mat.getSpecificHeat();
        double V = 1e-9; // 1mm³ volume per point

        double tempChange = totalHeatTransfer * timeStep_ / (rho * c * V);
        newTemperatures[i] = currentTemp + tempChange;
        
        // Debug: Print temperature change for first few points
        if (i < 3) {
            std::cout << "Point " << i << " temp change: " << tempChange << "K (from " 
                     << currentTemp << "K to " << newTemperatures[i] << "K)" << std::endl;
        }
    }
    
    // Apply all temperature changes at once
    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        auto point = pointCloud_.getPoint(i);
        point.setTemperature(newTemperatures[i]);
    }
    
    currentTime_ += timeStep_;
    
    std::cout << "Step completed, time: " << currentTime_ << "s" << std::endl;
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