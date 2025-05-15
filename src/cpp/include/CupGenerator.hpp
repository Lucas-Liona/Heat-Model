#pragma once
#include "PointCloud.hpp"

class CupGenerator {
public:
    struct Parameters {
        double innerRadius = 0.035;     // 3.5 cm
        double wallThickness = 0.003;   // 3 mm
        double height = 0.09;          // 9 cm
        double coffeeHeight = 0.12;     // 8 cm (coffee level)
        double pointSpacing = 0.005;   // 5 mm
        double coffeeTemp = 363.15;    // 90°C in Kelvin
        double cupTemp = 330.15;       // 20°C in Kelvin
        double airTemp = 293.15;       // 20°C in Kelvin
    };
    
    CupGenerator();
    
    PointCloud generate(const Parameters& params);
};