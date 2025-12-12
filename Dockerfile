# Multi-stage build to reduce final image size
# Stage 1: Build environment
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libeigen3-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Install pybind11
RUN pip install --no-cache-dir --user pybind11[global]

# Copy source code
COPY setup.py CMakeLists.txt ./
COPY src ./src

# Build the C++ extension
RUN pip install --no-cache-dir --user -e .

# Stage 2: Runtime environment
FROM python:3.11-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libomp5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy built extension and source
COPY --from=builder /app /app

# Copy examples and other runtime files
COPY examples /app/examples
COPY scripts /app/scripts

# Set working directory
WORKDIR /app

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create necessary directories
RUN mkdir -p results

# Expose port for dashboard
EXPOSE 8050

# Default command - use the correct existing file
CMD ["python", "examples/simple_test.py"]