FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3 \
    python3-dev \
    python3-pip \
    libeigen3-dev \
    libomp-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Python3 as default python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install pybind11
RUN pip install pybind11[global]

# Create working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Build the project (clean any existing build)
RUN rm -rf build && mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc)

# Install Python package in development mode
RUN cd build && make install
RUN pip install -e .

# Create necessary directories
RUN mkdir -p results examples

# Expose port for dashboard
EXPOSE 8050

# Default command
CMD ["python", "examples/interactive_demo.py"]