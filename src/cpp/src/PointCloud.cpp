#include "PointCloud.hpp"
#include <fstream>
#include <iostream>

PointCloud::PointCloud() : kdTreeBuilt_(false) {}

// Add point from existing Point object (compatibility method)
void PointCloud::addPoint(const Point& point) {
    Position pos = point.getPosition();
    x_.push_back(pos.x);
    y_.push_back(pos.y);
    z_.push_back(pos.z);
    temperatures_.push_back(point.getTemperature());
    materials_.push_back(point.getMaterial());
    neighbors_.emplace_back();  // Empty neighbor list
    kdTreeBuilt_ = false;  // Mark tree as needing rebuild
}

// Clear all data
void PointCloud::clear() {
    x_.clear();
    y_.clear();
    z_.clear();
    temperatures_.clear();
    materials_.clear();
    neighbors_.clear();
    kdTree_.reset();  // Clear the k-d tree
    kdTreeBuilt_ = false;
}

// Build the k-d tree
void PointCloud::buildKDTree() {
    if (x_.empty()) {
        std::cout << "Warning: Cannot build k-d tree with no points" << std::endl;
        return;
    }
    
    std::cout << "Building k-d tree with " << size() << " points..." << std::endl;
    
    // Create the k-d tree
    kdTree_ = std::make_unique<PointCloudKDTree>(
        3,  // dimensionality
        *this,  // dataset adaptor
        nanoflann::KDTreeSingleIndexAdaptorParams(10)  // max leaf size
    );
    
    // Build the index
    kdTree_->buildIndex();
    kdTreeBuilt_ = true;
    
    std::cout << "K-d tree built successfully!" << std::endl;
}

// Find neighbors within radius using k-d tree
std::vector<size_t> PointCloud::findNeighborsInRadius(size_t pointIndex, double radius) const {
    if (!kdTreeBuilt_ || !kdTree_) {
        std::cout << "Warning: K-d tree not built. Call buildKDTree() first." << std::endl;
        return {};
    }
    
    if (pointIndex >= size()) {
        std::cout << "Warning: Invalid point index " << pointIndex << std::endl;
        return {};
    }
    
    // Query point coordinates
    double query_pt[3] = {x_[pointIndex], y_[pointIndex], z_[pointIndex]};
    
    // Search parameters
    nanoflann::SearchParams params;
    params.sorted = false;  // We don't need sorted results
    
    // Perform radius search - Use the correct type for matches
    std::vector<std::pair<size_t, double>> matches;
    size_t numMatches = kdTree_->radiusSearch(query_pt, radius * radius, matches, params);
    
    // Extract just the indices (not the squared distances)
    std::vector<size_t> neighborIndices;
    neighborIndices.reserve(numMatches);
    
    for (const auto& match : matches) {
        // Skip self-match
        if (match.first != pointIndex) {
            neighborIndices.push_back(match.first);
        }
    }
    
    return neighborIndices;
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