#include "CupGenerator.hpp"
#include <cmath>

CupGenerator::CupGenerator() = default;

PointCloud CupGenerator::generate(const Parameters& params) {
    PointCloud cloud;
    
    auto spacing = double{params.pointSpacing};
    auto boxHeight = double{.15};
    auto boxWidth = double{.3};

    //coffee cup will be .08 meters so a little less than half the 

    //so if you think about it, you slice it at the z and check if the x and y are in a circle with a set radius, the radius correlating to Z will be given by a formula

    // im choosing r = ln (z * 50 + 1)/50 + .07
    
    // I think we should generate points in batches or by cube, and assign them based on their location with mathematical formulas

    for (auto z = double{0.0}; z <= boxHeight; z += spacing) //go layer by later creating points
    {
        for (auto x = double{-boxWidth/2}; x <= boxWidth/2; x += spacing) 
        {
            for (auto y = double{-boxWidth/2}; y <= boxWidth/2; y += spacing)
            {
                auto max_radius = double{log(z*50.0 + 1.0)/50.0 + .05};
                auto min_radius = double{log(z*50.0 + 1.0)/50.0 + .04};

                auto radius = double{sqrt(pow(x, 2) + pow(y, 2))};

                //in later runs maybe we can add slight nonhomogeny with temperature or  xyz with normal distribution engines
                if ((radius <= max_radius && radius >= min_radius && z <= params.coffeeHeight) || (radius <= max_radius && z <= 0.01)) {
                    cloud.addPoint(Point(x, y, z, params.cupTemp, MaterialType::CUP_MATERIAL));
                } else if (radius <= min_radius && z <= params.coffeeHeight - .01 && z >= 0.01) {
                    cloud.addPoint(Point(x, y, z, params.coffeeTemp, MaterialType::COFFEE));
                } else {
                    cloud.addPoint(Point(x, y, z, params.airTemp, MaterialType::AIR));
                }
            }
        }
    }
    
    // one error might be overlapping particles, make one inclusive and the other exclusive

    return cloud;
}
