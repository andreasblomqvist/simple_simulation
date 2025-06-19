#!/bin/bash

# Setup SimpleSim for local development
# Usage: ./scripts/setup-local.sh

set -e

echo "Setting up SimpleSim for local development..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# SimpleSim Environment Variables
PYTHONPATH=/app
LOG_LEVEL=INFO
REACT_APP_API_URL=http://localhost:8000
EOF
    echo "Created .env file"
fi

# Build Docker images
echo "Building Docker images..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check if backend is healthy
echo "Checking backend health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "Backend is healthy!"
        break
    fi
    echo "Waiting for backend to be ready... (attempt $i/30)"
    sleep 2
done

# Check if frontend is healthy
echo "Checking frontend health..."
for i in {1..30}; do
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "Frontend is healthy!"
        break
    fi
    echo "Waiting for frontend to be ready... (attempt $i/30)"
    sleep 2
done

echo ""
echo "SimpleSim is now running!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "To restart services:"
echo "  docker-compose restart" 