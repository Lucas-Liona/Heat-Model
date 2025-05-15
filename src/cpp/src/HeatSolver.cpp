#include "HeatSolver.hpp"
#include <algorithm>

HeatSolver::HeatSolver(PointCloud& pointCloud, const std::vector<Material>& materials, double timeStep)
    : pointCloud_(pointCloud), materials_(materials), timeStep_(timeStep), currentTime_(0.0) {}


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

    std::vector<double> newTemperatures;
    newTemperatures.reserve(pointCloud_.size());
    
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

    class Point {
    static constexpr double POINT_VOLUME = 1.25e-7;  // m³
    static constexpr double CONTACT_AREA = 2.5e-5;   // m²
    };

    // In heat transfer calculation:
    double heat_flux = k_eff * CONTACT_AREA * temp_diff / distance;
    double temp_change = heat_flux * dt / (density * specific_heat * POINT_VOLUME);
    */
    
    for (auto i = size_t{0}; i < pointCloud_.size(); ++i) {
        //newTemperatures[i] = pointCloud_.getPoint(i).getNeighbors().getTemperature();

        Point focal_point = pointCloud_.getPoint(i);
        std::cout << focal_point.index();
        //std::vector<Point> neighbors = focal_point.getNeighbors();

        //for (Point neighbor : neighbors) {
            
        //}
        
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
