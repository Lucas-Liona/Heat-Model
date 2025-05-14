#include "CupGenerator.hpp"
#include <cmath>

CupGenerator::CupGenerator() = default;

PointCloud CupGenerator::generate(const Parameters& params) {
    PointCloud cloud;
    
    // Generate points for a simple cylindrical cup
    double spacing = params.pointSpacing;
    double innerR = params.innerRadius;
    double outerR = innerR + params.wallThickness;
    
    // Generate coffee points (inside cylinder)
    for (double z = 0; z < params.coffeeHeight; z += spacing) {
        for (double r = 0; r < innerR; r += spacing) {
            for (double theta = 0; theta < 2 * M_PI; theta += spacing / r) {
                double x = r * cos(theta);
                double y = r * sin(theta);
                cloud.addPoint(Point(x, y, z, params.coffeeTemp, MaterialType::COFFEE));
            }
        }
    }
    
    // Generate cup wall points
    for (double z = 0; z < params.height; z += spacing) {
        for (double r = innerR; r < outerR; r += spacing) {
            for (double theta = 0; theta < 2 * M_PI; theta += spacing / r) {
                double x = r * cos(theta);
                double y = r * sin(theta);
                cloud.addPoint(Point(x, y, z, params.cupTemp, MaterialType::CUP_MATERIAL));
            }
        }
    }
    
    // Generate air points (simplified)
    double airRadius = outerR + 0.02; // 2cm of air around cup
    for (double z = 0; z < params.height; z += spacing * 2) {
        for (double r = outerR; r < airRadius; r += spacing * 2) {
            for (double theta = 0; theta < 2 * M_PI; theta += spacing * 2 / r) {
                double x = r * cos(theta);
                double y = r * sin(theta);
                cloud.addPoint(Point(x, y, z, params.airTemp, MaterialType::AIR));
            }
        }
    }
    
    return cloud;
}
