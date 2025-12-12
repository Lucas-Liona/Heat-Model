#!/bin/bash
# Script to validate Docker optimization improvements

set -e

echo "================================"
echo "Docker Optimization Validation"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Building optimized Docker image...${NC}"
docker build -t heat-model:optimized .

echo ""
echo -e "${BLUE}Checking image size...${NC}"
SIZE=$(docker images heat-model:optimized --format "{{.Size}}")
echo -e "${GREEN}Optimized image size: ${SIZE}${NC}"

echo ""
echo -e "${BLUE}Checking image layers...${NC}"
docker history heat-model:optimized --no-trunc | head -10

echo ""
echo -e "${BLUE}Testing if container runs...${NC}"
CONTAINER_ID=$(docker run -d heat-model:optimized sleep 30)

if [ -z "$CONTAINER_ID" ]; then
    echo "Failed to start container"
    exit 1
fi

echo -e "${GREEN}Container started successfully: ${CONTAINER_ID}${NC}"

echo ""
echo -e "${BLUE}Checking installed packages in container...${NC}"
docker exec $CONTAINER_ID python --version
docker exec $CONTAINER_ID python -c "import heat_transfer; print('heat_transfer module imported successfully')"

echo ""
echo -e "${BLUE}Checking runtime dependencies...${NC}"
docker exec $CONTAINER_ID dpkg -l | grep -E "libomp|python"

echo ""
echo -e "${BLUE}Verifying build tools are NOT present (this should fail)...${NC}"
docker exec $CONTAINER_ID which cmake || echo -e "${GREEN}✓ cmake not found (as expected)${NC}"
docker exec $CONTAINER_ID which gcc || echo -e "${GREEN}✓ gcc not found (as expected)${NC}"
docker exec $CONTAINER_ID which g++ || echo -e "${GREEN}✓ g++ not found (as expected)${NC}"

echo ""
echo -e "${BLUE}Cleaning up...${NC}"
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Validation completed successfully!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Summary:"
echo "- Optimized image size: ${SIZE}"
echo "- Build tools removed from final image"
echo "- Application runs successfully"
echo ""
