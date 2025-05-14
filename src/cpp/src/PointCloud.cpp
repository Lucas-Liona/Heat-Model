#include "PointCloud.hpp"
#include <fstream>

PointCloud::PointCloud() = default;

void PointCloud::addPoint(const Point& point) {
    points_.push_back(point);
}

const Point& PointCloud::getPoint(size_t index) const {
    return points_.at(index);
}

Point& PointCloud::getPoint(size_t index) {
    return points_.at(index);
}

size_t PointCloud::size() const {
    return points_.size();
}

void PointCloud::clear() {
    points_.clear();
}

void PointCloud::saveToVTK(const std::string& filename) const {
    std::ofstream file(filename);
    file << "# vtk DataFile Version 3.0\n";
    file << "Heat Transfer Simulation\n";
    file << "ASCII\n";
    file << "DATASET UNSTRUCTURED_GRID\n";
    file << "POINTS " << points_.size() << " double\n";
    
    for (const auto& point : points_) {
        auto pos = point.getPosition();
        file << pos.x << " " << pos.y << " " << pos.z << "\n";
    }
    
    file << "POINT_DATA " << points_.size() << "\n";
    file << "SCALARS temperature double\n";
    file << "LOOKUP_TABLE default\n";
    
    for (const auto& point : points_) {
        file << point.getTemperature() << "\n";
    }
}
