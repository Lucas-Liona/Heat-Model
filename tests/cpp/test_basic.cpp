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
