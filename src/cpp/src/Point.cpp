#include "Point.hpp"
#include "PointCloud.hpp"
#include <cmath>

// Legacy constructor for old code
Point::Point(double x, double y, double z, double temp, MaterialType material, size_t index)
    : isStandalone_(true), cloud_(nullptr), index_(index),
      position_(x, y, z), temperature_(temp), material_(material),
      neighborsFinalized_(false) {}

// New reference constructor
Point::Point(PointCloud* cloud, size_t index)
    : isStandalone_(false), cloud_(cloud), index_(index),
      position_(), temperature_(0), material_(MaterialType::AIR),
      neighborsFinalized_(false) {}

Position Point::getPosition() const {
    if (isStandalone_) {
        return position_;
    } else {
        return Position{
            cloud_->getX(index_),
            cloud_->getY(index_),
            cloud_->getZ(index_)
        };
    }
}

double Point::getTemperature() const {
    if (isStandalone_) {
        return temperature_;
    } else {
        return cloud_->getTemperature(index_);
    }
}

void Point::setTemperature(double temp) {
    if (isStandalone_) {
        temperature_ = temp;
    } else {
        cloud_->setTemperature(index_, temp);
    }
}

MaterialType Point::getMaterial() const {
    if (isStandalone_) {
        return material_;
    } else {
        return cloud_->getMaterial(index_);
    }
}

void Point::setMaterial(MaterialType material) {
    if (isStandalone_) {
        material_ = material;
    } else {
        // Assuming PointCloud has a setMaterial method
        // cloud_->setMaterial(index_, material);
    }
}

size_t Point::getIndex() const {
    return index_;
}

void Point::addNeighbor(size_t neighborIdx, double distance) {
    if (isStandalone_) {
        neighborIndices_.push_back(neighborIdx);
    } else {
        // Forward to PointCloud's addNeighbor method
        // cloud_->addNeighbor(index_, neighborIdx, distance);
    }
}

const std::vector<size_t>& Point::getNeighborIndices() const {
    if (isStandalone_) {
        return neighborIndices_;
    } else {
        // Assuming PointCloud::getPoint(index_) returns a PointRef with getNeighborIndices
        return cloud_->getPoint(index_).getNeighborIndices();
    }
}

void Point::finalizeNeighbors() {
    if (isStandalone_) {
        neighborsFinalized_ = true;
    } else {
        // Forward to PointCloud
        // cloud_->finalizeNeighbors(index_);
    }
}

bool Point::hasNeighbors() const {
    if (isStandalone_) {
        return neighborsFinalized_;
    } else {
        // Forward to PointCloud
        // return cloud_->hasNeighbors(index_);
        return !getNeighborIndices().empty();
    }
}