#pragma once
#include "Point.hpp"
#include <vector>
#include <string>

class PointCloud {
public:
    PointCloud();
    
    void addPoint(const Point& point);
    const Point& getPoint(size_t index) const;
    Point& getPoint(size_t index);
    size_t size() const;
    void clear();
    
    void saveToVTK(const std::string& filename) const;

private:
    std::vector<Point> points_;
};