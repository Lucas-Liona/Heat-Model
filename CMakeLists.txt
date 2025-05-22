cmake_minimum_required(VERSION 3.16)
project(heat_transfer_sim VERSION 1.0.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

# Find required packages
find_package(Python COMPONENTS Interpreter Development)

# Try to find pybind11
find_package(pybind11 QUIET)
if(NOT pybind11_FOUND)
    # If not found, try to use pip installed version
    execute_process(
        COMMAND ${Python_EXECUTABLE} -m pybind11 --cmakedir
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    find_package(pybind11 REQUIRED PATHS ${pybind11_DIR})
endif()

# Find Eigen3
find_package(Eigen3 QUIET)
if(NOT Eigen3_FOUND)
    # Try to find it in standard locations
    find_path(EIGEN3_INCLUDE_DIR 
        NAMES Eigen/Dense
        PATHS /usr/include/eigen3 /usr/local/include/eigen3
    )
    if(EIGEN3_INCLUDE_DIR)
        set(EIGEN3_FOUND TRUE)
        message(STATUS "Found Eigen3: ${EIGEN3_INCLUDE_DIR}")
    else()
        message(FATAL_ERROR "Eigen3 not found. Please install with: sudo apt install libeigen3-dev")
    endif()
endif()

# Find OpenMP
find_package(OpenMP)

# Find nanoflann (header-only library)
find_path(NANOFLANN_INCLUDE_DIR 
    NAMES nanoflann.hpp
    PATHS /usr/include /usr/local/include
    PATH_SUFFIXES nanoflann
)

if(NOT NANOFLANN_INCLUDE_DIR)
    message(STATUS "nanoflann not found, downloading...")
    # Download nanoflann header if not found
    file(DOWNLOAD 
        https://raw.githubusercontent.com/jlblancoc/nanoflann/master/include/nanoflann.hpp
        ${CMAKE_CURRENT_SOURCE_DIR}/external/nanoflann.hpp
    )
    set(NANOFLANN_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/external)
    file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/external)
endif()

message(STATUS "Using nanoflann from: ${NANOFLANN_INCLUDE_DIR}")

# Add nanoflann include directory
include_directories(${NANOFLANN_INCLUDE_DIR})

# Include directories
include_directories(src/cpp/include)
if(EIGEN3_INCLUDE_DIR)
    include_directories(${EIGEN3_INCLUDE_DIR})
endif()

# Create core library
set(CORE_SOURCES
    src/cpp/src/Point.cpp
    src/cpp/src/PointCloud.cpp
    src/cpp/src/HeatSolver.cpp
    src/cpp/src/Material.cpp
    src/cpp/src/CupGenerator.cpp
)

add_library(heat_transfer_core STATIC ${CORE_SOURCES})

# Set position independent code for the static library
set_property(TARGET heat_transfer_core PROPERTY POSITION_INDEPENDENT_CODE ON)

# Enable OpenMP if found (using keyword signature)
if(OpenMP_CXX_FOUND)
    target_link_libraries(heat_transfer_core PUBLIC OpenMP::OpenMP_CXX)
    add_definitions(-DWITH_OPENMP)
endif()

# Link Eigen3 if found (using keyword signature)
if(TARGET Eigen3::Eigen)
    target_link_libraries(heat_transfer_core PUBLIC Eigen3::Eigen)
endif()

# Python module
pybind11_add_module(heat_transfer src/cpp/pybind/bindings.cpp)
target_link_libraries(heat_transfer PRIVATE heat_transfer_core)

# Compiler flags for optimization
target_compile_options(heat_transfer_core PRIVATE -O3)
target_compile_options(heat_transfer PRIVATE -O3)

# Install targets
install(TARGETS heat_transfer
    COMPONENT python
    LIBRARY DESTINATION .)

# Add tests
enable_testing()
if(BUILD_TESTING)
    # Try to find Google Test
    find_package(GTest QUIET)
    if(NOT GTest_FOUND)
        message(STATUS "Google Test not found. Tests will be skipped.")
        message(STATUS "Install with: sudo apt-get install libgtest-dev")
    else()
        add_subdirectory(tests/cpp)
    endif()
endif()