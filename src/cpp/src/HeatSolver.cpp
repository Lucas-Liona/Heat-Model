#include "HeatSolver.hpp"
#include <algorithm>

HeatSolver::HeatSolver(PointCloud& pointCloud, const std::vector<Material>& materials, double timeStep)
    : pointCloud_(pointCloud), materials_(materials), timeStep_(timeStep), currentTime_(0.0) {}

void HeatSolver::step() {
    // Simple forward Euler integration for now
    std::vector<double> newTemperatures;
    newTemperatures.reserve(pointCloud_.size());
    
    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        const Point& point = pointCloud_.getPoint(i);
        double temp = point.getTemperature();
        
        // Simple cooling to ambient (placeholder implementation)
        const Material& material = materials_[static_cast<int>(point.getMaterial())];
        double ambient = material.getAmbientTemperature();
        double coolingRate = 0.001; // Simple cooling coefficient
        
        double newTemp = temp - coolingRate * (temp - ambient) * timeStep_;
        newTemperatures.push_back(newTemp);
    }
    
    // Update temperatures
    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        pointCloud_.getPoint(i).setTemperature(newTemperatures[i]);
    }
    
    currentTime_ += timeStep_;
}

void HeatSolver::run(double duration) {
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
        const Point& point = pointCloud_.getPoint(i);
        if (point.getMaterial() == material) {
            sum += point.getTemperature();
            ++count;
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
    
    double minTemp = pointCloud_.getPoint(0).getTemperature();
    for (size_t i = 1; i < pointCloud_.size(); ++i) {
        minTemp = std::min(minTemp, pointCloud_.getPoint(i).getTemperature());
    }
    return minTemp;
}
