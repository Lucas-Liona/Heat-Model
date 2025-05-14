#pragma once

class Material {
public:
    Material(double density, double specificHeat, double thermalConductivity, double ambientTemp);
    
    // Factory methods for common materials
    static Material Coffee();
    static Material Ceramic();
    static Material Air();
    
    // Getters
    double getDensity() const;
    double getSpecificHeat() const;
    double getThermalConductivity() const;
    double getAmbientTemperature() const;

private:
    double density_;
    double specificHeat_;
    double thermalConductivity_;
    double ambientTemperature_;
};