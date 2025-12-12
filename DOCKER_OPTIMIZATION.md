# Docker Container Size Optimization

## Summary of Changes

This document describes the optimizations made to reduce the Docker container size and improve build efficiency.

## Key Improvements

### 1. Multi-Stage Build
- **Before**: Single-stage build with all build tools in final image (~600-800 MB)
- **After**: Two-stage build that separates build and runtime environments
  - Stage 1 (builder): Contains all build tools and compiles the C++ extensions
  - Stage 2 (runtime): Contains only runtime dependencies and compiled artifacts
- **Impact**: Reduces final image size by ~300-400 MB by excluding build tools

### 2. Smaller Base Image
- **Before**: `ubuntu:22.04` (~77 MB compressed)
- **After**: `python:3.11-slim` (~48 MB compressed)
- **Impact**: ~29 MB savings on base image alone, plus better Python tooling integration

### 3. Removed Unnecessary Dependencies
**Build-only dependencies (not in final image):**
- `build-essential` - C/C++ compilers (only needed during build)
- `cmake` - Build system (only needed during build)
- `python3-dev` - Python headers (only needed during build)
- `git` - Version control (not needed in container)
- `libeigen3-dev` - Eigen headers (only needed during build)

**Runtime dependencies (kept in final image):**
- `libomp5` - OpenMP runtime library (needed for parallel execution)

### 4. Optimized Package Installation
- Added `--no-install-recommends` flag to apt-get to avoid installing suggested packages
- Added `--no-cache-dir` flag to pip to avoid caching packages
- Added `--user` flag to pip for better isolation

### 5. Fixed Dockerfile Issues
- **Fixed CMD**: Changed from non-existent `interactive_demo.py` to existing `simple_test.py`
- **Better layer caching**: Separated concerns for optimal Docker layer reuse

### 6. Enhanced .dockerignore
Added more exclusions to prevent unnecessary files from being copied into the build context:
- Test files and directories
- Documentation files (README.md, LICENSE)
- Docker files themselves
- IDE configuration files
- Temporary files and swap files
- Build artifacts

### 7. Simplified docker-compose.yml
- Removed redundant `pip install jupyter` command (already in requirements.txt)
- Cleaner service definitions

## Expected Results

### Size Comparison
- **Before**: ~600-800 MB
- **After**: ~300-400 MB
- **Reduction**: ~50% smaller

### Build Time
- Build time may slightly increase due to multi-stage build
- However, layer caching will make subsequent builds faster
- Docker layer reuse is now optimized

### Ease of Use
- Container is now more portable and faster to download/deploy
- Fewer dependencies mean less potential for conflicts
- Cleaner separation between build and runtime concerns

## How to Use

### Build the optimized image:
```bash
docker build -t heat-model .
```

### Run with docker-compose:
```bash
docker-compose up --build
```

### Verify the size:
```bash
docker images heat-model
```

## Technical Details

### Multi-Stage Build Flow
1. **Builder stage**: Install build tools → Install Python packages → Build C++ extensions
2. **Runtime stage**: Install minimal runtime libs → Copy Python packages → Copy compiled extensions → Copy application code
3. **Result**: Final image contains only what's needed to run the application

### Why This Works
- Build tools (gcc, cmake, etc.) are large but only needed during compilation
- Python packages are installed once and copied to final image
- C++ extensions are compiled once and copied to final image
- Runtime only needs the compiled binaries and runtime libraries

## Maintenance Notes

- Keep requirements.txt minimal - only include packages actually needed at runtime
- If adding new system dependencies, consider if they're build-time or runtime
- The .dockerignore file should be updated if new file types are added to the repo
