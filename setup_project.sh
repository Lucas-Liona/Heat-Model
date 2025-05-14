#!/bin/bash

# Setup script to get the heat transfer simulation to a working state

set -e

echo "Setting up heat transfer simulation project..."

# Create missing C++ source directories
mkdir -p src/cpp/src
mkdir -p tests/cpp

# Create minimal C++ implementation files to get the project compiling
echo "Creating minimal C++ implementation files..."

# Create Point.cpp
cat > src/cpp/src/Point.cpp << 'EOF'
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
EOF

# Create PointCloud.cpp
cat > src/cpp/src/PointCloud.cpp << 'EOF'
#include "PointCloud.hpp"
#include <fstream>

PointCloud::PointCloud() = default;

void PointCloud::addPoint(const Point& point) {
    points_.push_back(point);
}

const Point& PointCloud::getPoint(size_t index) const {
    return points_.at(index);
}

Point& PointCloud::getPoint(size_t index) {
    return points_.at(index);
}

size_t PointCloud::size() const {
    return points_.size();
}

void PointCloud::clear() {
    points_.clear();
}

void PointCloud::saveToVTK(const std::string& filename) const {
    std::ofstream file(filename);
    file << "# vtk DataFile Version 3.0\n";
    file << "Heat Transfer Simulation\n";
    file << "ASCII\n";
    file << "DATASET UNSTRUCTURED_GRID\n";
    file << "POINTS " << points_.size() << " double\n";
    
    for (const auto& point : points_) {
        auto pos = point.getPosition();
        file << pos.x << " " << pos.y << " " << pos.z << "\n";
    }
    
    file << "POINT_DATA " << points_.size() << "\n";
    file << "SCALARS temperature double\n";
    file << "LOOKUP_TABLE default\n";
    
    for (const auto& point : points_) {
        file << point.getTemperature() << "\n";
    }
}
EOF

# Create Material.cpp
cat > src/cpp/src/Material.cpp << 'EOF'
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
EOF

# Create HeatSolver.cpp
cat > src/cpp/src/HeatSolver.cpp << 'EOF'
#include "HeatSolver.hpp"
#include <algorithm>

HeatSolver::HeatSolver(PointCloud& pointCloud, const std::vector<Material>& materials, double timeStep)
    : pointCloud_(pointCloud), materials_(materials), timeStep_(timeStep), currentTime_(0.0) {}

void HeatSolver::step() {
    // Simple forward Euler integration for now
    std::vector<double> newTemperatures;
    newTemperatures.reserve(pointCloud_.size());
    
    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        const Point& point = pointCloud_.getPoint(i);
        double temp = point.getTemperature();
        
        // Simple cooling to ambient (placeholder implementation)
        const Material& material = materials_[static_cast<int>(point.getMaterial())];
        double ambient = material.getAmbientTemperature();
        double coolingRate = 0.001; // Simple cooling coefficient
        
        double newTemp = temp - coolingRate * (temp - ambient) * timeStep_;
        newTemperatures.push_back(newTemp);
    }
    
    // Update temperatures
    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        pointCloud_.getPoint(i).setTemperature(newTemperatures[i]);
    }
    
    currentTime_ += timeStep_;
}

void HeatSolver::run(double duration) {
    double endTime = currentTime_ + duration;
    while (currentTime_ < endTime) {
        step();
    }
}

double HeatSolver::getCurrentTime() const {
    return currentTime_;
}

double HeatSolver::getAverageTemperature(MaterialType material) const {
    double sum = 0.0;
    size_t count = 0;
    
    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        const Point& point = pointCloud_.getPoint(i);
        if (point.getMaterial() == material) {
            sum += point.getTemperature();
            ++count;
        }
    }
    
    return count > 0 ? sum / count : 0.0;
}

double HeatSolver::getMaxTemperature() const {
    double maxTemp = 0.0;
    for (size_t i = 0; i < pointCloud_.size(); ++i) {
        maxTemp = std::max(maxTemp, pointCloud_.getPoint(i).getTemperature());
    }
    return maxTemp;
}

double HeatSolver::getMinTemperature() const {
    if (pointCloud_.size() == 0) return 0.0;
    
    double minTemp = pointCloud_.getPoint(0).getTemperature();
    for (size_t i = 1; i < pointCloud_.size(); ++i) {
        minTemp = std::min(minTemp, pointCloud_.getPoint(i).getTemperature());
    }
    return minTemp;
}
EOF

# Create CupGenerator.cpp
cat > src/cpp/src/CupGenerator.cpp << 'EOF'
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
EOF

# Create a simple test file
cat > tests/cpp/test_basic.cpp << 'EOF'
#include <gtest/gtest.h>
#include "Point.hpp"
#include "PointCloud.hpp"
#include "HeatSolver.hpp"
#include "CupGenerator.hpp"

TEST(BasicTest, PointCreation) {
    Point p(1.0, 2.0, 3.0, 300.0, MaterialType::COFFEE);
    auto pos = p.getPosition();
    
    EXPECT_DOUBLE_EQ(pos.x, 1.0);
    EXPECT_DOUBLE_EQ(pos.y, 2.0);
    EXPECT_DOUBLE_EQ(pos.z, 3.0);
    EXPECT_DOUBLE_EQ(p.getTemperature(), 300.0);
    EXPECT_EQ(p.getMaterial(), MaterialType::COFFEE);
}

TEST(BasicTest, PointCloudOperations) {
    PointCloud cloud;
    cloud.addPoint(Point(0, 0, 0, 300, MaterialType::COFFEE));
    cloud.addPoint(Point(1, 1, 1, 350, MaterialType::CUP_MATERIAL));
    
    EXPECT_EQ(cloud.size(), 2);
    EXPECT_DOUBLE_EQ(cloud.getPoint(0).getTemperature(), 300.0);
    EXPECT_DOUBLE_EQ(cloud.getPoint(1).getTemperature(), 350.0);
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
EOF

# Update CMakeLists.txt to handle tests properly
cat > tests/cpp/CMakeLists.txt << 'EOF'
find_package(GTest REQUIRED)

add_executable(tests
    test_basic.cpp
)

target_link_libraries(tests
    heat_transfer_core
    GTest::GTest
    GTest::Main
)

add_test(NAME heat_transfer_tests COMMAND tests)
EOF

# Create a simple Python test to verify the bindings work
cat > src/python/test_bindings.py << 'EOF'
#!/usr/bin/env python3
"""Simple test to verify Python bindings work"""

try:
    import heat_transfer
    print("SUCCESS: heat_transfer module imported successfully!")
    
    # Test basic functionality
    generator = heat_transfer.CupGenerator()
    params = heat_transfer.CupParameters()
    print("SUCCESS: CupGenerator and CupParameters created!")
    
    # Generate a small test geometry
    params.point_spacing = 0.02  # Large spacing for quick test
    params.inner_radius = 0.03
    params.height = 0.05
    
    point_cloud = generator.generate(params)
    print(f"SUCCESS: Generated {point_cloud.size()} points!")
    
    # Test Materials
    materials = [
        heat_transfer.Material.coffee(),
        heat_transfer.Material.ceramic(),
        heat_transfer.Material.air()
    ]
    print("SUCCESS: Materials created!")
    
    # Test HeatSolver
    solver = heat_transfer.HeatSolver(point_cloud, materials, 0.1)
    print("SUCCESS: HeatSolver created!")
    
    # Run a few simulation steps
    for _ in range(5):
        solver.step()
    
    print(f"SUCCESS: Simulation ran, current time: {solver.get_current_time():.2f}s")
    print(f"Coffee temperature: {solver.get_average_temperature(0):.1f}K")
    
    print("\n✅ All tests passed! Your C++ core with Python bindings is working!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure to build the project first with ./scripts/build.sh")
except Exception as e:
    print(f"❌ Error: {e}")
    print("There might be an issue with the implementation")
EOF

chmod +x src/python/test_bindings.py

# Make build script executable
chmod +x scripts/build.sh

echo "✅ Project setup complete!"
echo ""
echo "To get started:"
echo "1. Build the project: ./scripts/build.sh"
echo "2. Test Python bindings: python src/python/test_bindings.py"
echo "3. Run the basic simulation example: python examples/simulation.py"
echo ""
echo "You can now implement your own C++ algorithms in the generated files:"
echo "- src/cpp/src/Point.cpp"
echo "- src/cpp/src/PointCloud.cpp"
echo "- src/cpp/src/HeatSolver.cpp"
echo "- src/cpp/src/Material.cpp"
echo "- src/cpp/src/CupGenerator.cpp"