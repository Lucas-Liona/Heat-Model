#include "Material.hpp"

Material::Material(double density, double specificHeat, double thermalConductivity, double ambientTemp)
    : density_(density), specificHeat_(specificHeat), 
      thermalConductivity_(thermalConductivity), ambientTemperature_(ambientTemp) {}

Material Material::Coffee() {
    return Material(1000.0, 4180.0, 0.6, 363.15); // ~90°C
}

Material Material::Ceramic() {
    return Material(2400.0, 800.0, 1.5, 293.15); // ~20°C
}

Material Material::Air() {
    return Material(1.2, 1005.0, 0.025, 293.15); // ~20°C
}

double Material::getDensity() const { return density_; }
double Material::getSpecificHeat() const { return specificHeat_; }
double Material::getThermalConductivity() const { return thermalConductivity_; }
double Material::getAmbientTemperature() const { return ambientTemperature_; }
