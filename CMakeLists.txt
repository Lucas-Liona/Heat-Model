cmake_minimum_required(VERSION 3.16)
project(heat_transfer_sim VERSION 1.0.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

# Find required packages
find_package(Python COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(OpenMP)

# Enable OpenMP if found
if(OpenMP_CXX_FOUND)
    target_link_libraries(heat_transfer_core PUBLIC OpenMP::OpenMP_CXX)
    add_definitions(-DWITH_OPENMP)
endif()

# Include directories
include_directories(src/cpp/include)
include_directories(${EIGEN3_INCLUDE_DIR})

# Create core library
set(CORE_SOURCES
    src/cpp/src/Point.cpp
    src/cpp/src/PointCloud.cpp
    src/cpp/src/HeatSolver.cpp
    src/cpp/src/Material.cpp
    src/cpp/src/CupGenerator.cpp
)

add_library(heat_transfer_core STATIC ${CORE_SOURCES})
target_link_libraries(heat_transfer_core ${EIGEN3_LIBRARIES})

# Python module
pybind11_add_module(heat_transfer src/cpp/pybind/bindings.cpp)
target_link_libraries(heat_transfer PRIVATE heat_transfer_core)

# Compiler flags for optimization
target_compile_options(heat_transfer_core PRIVATE -O3 -march=native)
target_compile_options(heat_transfer PRIVATE -O3 -march=native)

# Install targets
install(TARGETS heat_transfer
    COMPONENT python
    LIBRARY DESTINATION .)

# Add tests
enable_testing()
if(BUILD_TESTING)
    add_subdirectory(tests/cpp)
endif()