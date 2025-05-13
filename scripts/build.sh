#!/bin/bash

set -e

echo "Building Heat Transfer Simulation..."

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake .. -DCMAKE_BUILD_TYPE=Release \
         -DPYTHON_EXECUTABLE=$(which python) \
         -DBUILD_TESTING=ON

# Build
make -j$(nproc)

# Install Python package
make install

# Install in development mode
cd ..
pip install -e .

echo "Build complete!"