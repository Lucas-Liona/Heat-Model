#pragma once

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
    Point(double x, double y, double z, double temp, MaterialType material);
    
    Position getPosition() const;
    double getTemperature() const;
    void setTemperature(double temp);
    MaterialType getMaterial() const;
    void setMaterial(MaterialType material);

private:
    Position position_;
    double temperature_;
    MaterialType material_;
};