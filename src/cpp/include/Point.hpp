#pragma once
#include <cstddef>  // For size_t
#include <vector>   // For std::vector

enum class MaterialType {
    COFFEE = 0,
    CUP_MATERIAL = 1,
    AIR = 2
};

struct Position {
    double x, y, z;
    Position() = default;
    Position(double x, double y, double z) : x(x), y(y), z(z) {}
};

class Point {
public:
    Point(double x, double y, double z, double temp, MaterialType material, size_t index);
    
    Position getPosition() const;
    double getTemperature() const;
    void setTemperature(double temp);
    MaterialType getMaterial() const;
    void setMaterial(MaterialType material);

    size_t getIndex() const;
    std::vector<Point> getNeighbors(); 
    std::vector<size_t> getNeighborsIndex();
    void setNeighbors();

private:
    Position position_;
    double temperature_;
    MaterialType material_;

    size_t index_;
    std::vector<size_t> neighbors_;
};