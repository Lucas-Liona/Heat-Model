#pragma once
#include "Point.hpp"
#include <vector>
#include <string>
#include <cstddef>  // For size_t
#include <memory>

// nanoflann includes
#include <nanoflann.hpp>

// Forward declaration for nanoflann compatibility
class PointCloud;

// Define the KD-tree type for nanoflann
typedef nanoflann::KDTreeSingleIndexAdaptor<
    nanoflann::L2_Simple_Adaptor<double, PointCloud>,
    PointCloud,
    3 // 3D points
> PointCloudKDTree;

class PointCloud {
private:
    // SoA storage
    std::vector<double> x_;
    std::vector<double> y_;
    std::vector<double> z_;
    std::vector<double> temperatures_;
    std::vector<MaterialType> materials_;
    
    // For neighbor storage (will be added later)
    std::vector<std::vector<size_t>> neighbors_;
    
    // nanoflann k-d tree
    std::unique_ptr<PointCloudKDTree> kdTree_;
    bool kdTreeBuilt_;
    
public:
    PointCloud();
    
    // Point-like reference class for backward compatibility
    class PointRef {
    private:
        PointCloud* cloud_;
        size_t index_;
        
    public:
        PointRef(PointCloud* cloud, size_t i) : cloud_(cloud), index_(i) {}
        
        // Maintain Point interface
        Position getPosition() const {
            return Position{cloud_->x_[index_], cloud_->y_[index_], cloud_->z_[index_]};
        }
        
        double getTemperature() const { 
            return cloud_->temperatures_[index_]; 
        }
        
        void setTemperature(double temp) { 
            cloud_->temperatures_[index_] = temp; 
        }
        
        MaterialType getMaterial() const { 
            return cloud_->materials_[index_]; 
        }
        
        void setMaterial(MaterialType material) { 
            cloud_->materials_[index_] = material; 
        }
        
        // For neighbor support (to be added)
        void addNeighbor(size_t neighborIdx, double distance) {
            // Will implement with neighbors_ array
            cloud_->neighbors_[index_].push_back(neighborIdx);
        }
        
        const std::vector<size_t>& getNeighborIndices() const {
            return cloud_->neighbors_[index_];
        }
        
        size_t getIndex() const { return index_; }
    };
    
    // Maintain existing interface
    void addPoint(const Point& point);
    PointRef getPoint(size_t index) { return PointRef(this, index); }
    const PointRef getPoint(size_t index) const { 
        return PointRef(const_cast<PointCloud*>(this), index); 
    }
    size_t size() const { return x_.size(); }
    void clear();
    
    // New interface for adding points directly (more efficient)
    size_t addPoint(double x, double y, double z, double temp, MaterialType mat) {
        size_t index = x_.size();
        x_.push_back(x);
        y_.push_back(y);
        z_.push_back(z);
        temperatures_.push_back(temp);
        materials_.push_back(mat);
        neighbors_.emplace_back();  // Empty neighbor list
        kdTreeBuilt_ = false;  // Mark tree as needing rebuild
        return index;
    }
    
    // Direct array access methods for performance
    double getX(size_t i) const { return x_[i]; }
    double getY(size_t i) const { return y_[i]; }
    double getZ(size_t i) const { return z_[i]; }
    double getTemperature(size_t i) const { return temperatures_[i]; }
    void setTemperature(size_t i, double temp) { temperatures_[i] = temp; }
    MaterialType getMaterial(size_t i) const { return materials_[i]; }
    
    // VTK export (update implementation needed)
    void saveToVTK(const std::string& filename) const;
    
    // K-d tree methods
    void buildKDTree();
    std::vector<size_t> findNeighborsInRadius(size_t pointIndex, double radius) const;
    bool isKDTreeBuilt() const { return kdTreeBuilt_; }
    
    // nanoflann interface - REQUIRED by nanoflann
    inline size_t kdtree_get_point_count() const { return x_.size(); }
    
    inline double kdtree_get_pt(const size_t idx, const int dim) const {
        return (dim == 0) ? x_[idx] : (dim == 1) ? y_[idx] : z_[idx];
    }
    
    template <class BBOX> bool kdtree_get_bbox(BBOX&) const { return false; }
};