#include "HeatSolver.hpp"
#include <algorithm>

HeatSolver::HeatSolver(PointCloud& pointCloud, const std::vector<Material>& materials, double timeStep)
    : pointCloud_(pointCloud), materials_(materials), timeStep_(timeStep), currentTime_(0.0) {}

void HeatSolver::step() {

    std::vector<double> newTemperatures;
    newTemperatures.reserve(pointCloud_.size());
    
    for (auto i = size_t{0}; i < pointCloud_.size(); ++i) {

    }
    
    // set temperatures
    for (auto i = size_t{0}; i < pointCloud_.size(); ++i) {
        pointCloud_.getPoint(i).setTemperature(newTemperatures[i]);
    }
    
    currentTime_ += timeStep_;
}

void HeatSolver::run_for_time(double duration) {

}

double HeatSolver::getCurrentTime() const {
    return currentTime_;
}

double HeatSolver::getAverageTemperature(MaterialType material) const {
    double sum = 0.0;
    size_t count = 0;
    
    for (size_t i = 0; i < pointCloud_.size(); ++i) {

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
