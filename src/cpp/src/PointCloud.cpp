#include "PointCloud.hpp"
#include <fstream>

PointCloud::PointCloud() = default;

// Add point from existing Point object (compatibility method)
void PointCloud::addPoint(const Point& point) {
    Position pos = point.getPosition();
    x_.push_back(pos.x);
    y_.push_back(pos.y);
    z_.push_back(pos.z);
    temperatures_.push_back(point.getTemperature());
    materials_.push_back(point.getMaterial());
    neighbors_.emplace_back();  // Empty neighbor list
}

// Clear all data
void PointCloud::clear() {
    x_.clear();
    y_.clear();
    z_.clear();
    temperatures_.clear();
    materials_.clear();
    neighbors_.clear();
}

// Save to VTK format
void PointCloud::saveToVTK(const std::string& filename) const {
    std::ofstream file(filename);
    file << "# vtk DataFile Version 3.0\n";
    file << "Heat Transfer Simulation\n";
    file << "ASCII\n";
    file << "DATASET UNSTRUCTURED_GRID\n";
    file << "POINTS " << size() << " double\n";
    
    // Write all points
    for (size_t i = 0; i < size(); ++i) {
        file << x_[i] << " " << y_[i] << " " << z_[i] << "\n";
    }
    
    file << "POINT_DATA " << size() << "\n";
    file << "SCALARS temperature double\n";
    file << "LOOKUP_TABLE default\n";
    
    // Write all temperatures
    for (size_t i = 0; i < size(); ++i) {
        file << temperatures_[i] << "\n";
    }
    
    // Add material as a second scalar
    file << "SCALARS material int\n";
    file << "LOOKUP_TABLE default\n";
    
    // Write all materials as integers
    for (size_t i = 0; i < size(); ++i) {
        file << static_cast<int>(materials_[i]) << "\n";
    }
}