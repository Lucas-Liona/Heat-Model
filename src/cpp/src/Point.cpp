#include "Point.hpp"

Point::Point(double x, double y, double z, double temp, MaterialType material)
    : position_{x, y, z}, temperature_(temp), material_(material) {}

Position Point::getPosition() const {
    return position_;
}

double Point::getTemperature() const {
    return temperature_;
}

void Point::setTemperature(double temp) {
    temperature_ = temp;
}

MaterialType Point::getMaterial() const {
    return material_;
}

void Point::setMaterial(MaterialType material) {
    material_ = material;
}
