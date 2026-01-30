#!/bin/bash
# Docker Quick Start for NetOps Command Center

set -e

echo "=========================================="
echo "NetOps Command Center - Docker Startup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker found: $(docker --version)"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "Please install Docker Compose"
    exit 1
fi

echo "✓ Docker Compose found: $(docker-compose --version)"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running"
    echo "Please start Docker Desktop or Docker service"
    exit 1
fi

echo "✓ Docker daemon is running"
echo ""

# Check if port 5000 is available
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Warning: Port 5000 is already in use"
    echo "The container might fail to start."
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Check if required files exist
echo "Checking required files..."
REQUIRED_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "network_device_manager.py"
    "api_server.py"
    "requirements.txt"
    "static/index.html"
)

ALL_FOUND=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ] && [ ! -d "$file" ]; then
        echo "❌ Missing: $file"
        ALL_FOUND=false
    else
        echo "✓ Found: $file"
    fi
done

if [ "$ALL_FOUND" = false ]; then
    echo ""
    echo "❌ Some required files are missing!"
    echo "Please ensure all files are in the current directory."
    exit 1
fi

echo ""
echo "=========================================="
echo "Building and starting container..."
echo "=========================================="
echo ""

# Build and start with docker-compose
docker-compose up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Container started successfully!"
    echo "=========================================="
    echo ""
    echo "Access the application:"
    echo "  🌐 http://localhost:5000"
    echo ""
    echo "Useful commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop:         docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo "  Status:       docker-compose ps"
    echo ""
    echo "Testing API endpoint..."
    sleep 3
    
    if curl -s http://localhost:5000/api/health > /dev/null; then
        echo "✓ API is responding!"
    else
        echo "⚠️  API not responding yet (may need a few more seconds)"
    fi
    
    echo ""
    echo "=========================================="
else
    echo ""
    echo "❌ Failed to start container"
    echo "Check the errors above or run:"
    echo "  docker-compose logs"
    exit 1
fi
