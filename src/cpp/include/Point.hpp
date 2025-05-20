#pragma once

#include <vector>   // For std::vector
#include <cstddef>  // For size_t
#include <cmath>    // For std::sqrt

enum class MaterialType {
    COFFEE = 0,
    CUP_MATERIAL = 1,
    AIR = 2
};

struct Position {
    double x, y, z;
    Position() = default;
    Position(double x, double y, double z) : x(x), y(y), z(z) {}
    
    double distanceTo(const Position& other) const {
        double dx = x - other.x;
        double dy = y - other.y;
        double dz = z - other.z;
        return std::sqrt(dx*dx + dy*dy + dz*dz);
    }
};

// Forward declaration needed for Point reference class
class PointCloud;

class Point {
public:
    // Constructors for both modes
    
    // Legacy constructor for old code - creates a new point
    Point(double x, double y, double z, double temp, MaterialType material, size_t index = 0);
    
    // New reference constructor (used internally by PointCloud)
    Point(PointCloud* cloud, size_t index);
    
    // Interface matches original Point class
    Position getPosition() const;
    double getTemperature() const;
    void setTemperature(double temp);
    MaterialType getMaterial() const;
    void setMaterial(MaterialType material);
    size_t getIndex() const;
    
    // Neighbor methods
    void addNeighbor(size_t neighborIdx, double distance);
    const std::vector<size_t>& getNeighborIndices() const;
    void finalizeNeighbors();
    bool hasNeighbors() const;
    
private:
    // One of two modes: either standalone or reference
    bool isStandalone_;  // True if this is a standalone point, false if it's a reference
    
    // Reference mode (points into PointCloud arrays)
    PointCloud* cloud_;
    size_t index_;
    
    // Standalone mode (for compatibility with old code)
    Position position_;
    double temperature_;
    MaterialType material_;
    std::vector<size_t> neighborIndices_;
    bool neighborsFinalized_;
};