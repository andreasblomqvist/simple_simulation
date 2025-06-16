#!/bin/bash

# Local development setup for SimpleSim
# Usage: ./scripts/setup-local.sh

set -e

echo "Setting up SimpleSim for local development..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Build and start the application
echo "Building and starting containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check if backend is responding
echo "Checking backend health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health &>/dev/null; then
        echo "✓ Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ Backend failed to start"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
done

# Check if frontend is responding
echo "Checking frontend health..."
for i in {1..30}; do
    if curl -f http://localhost:3000/health &>/dev/null; then
        echo "✓ Frontend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ Frontend failed to start"
        docker-compose logs frontend
        exit 1
    fi
    sleep 2
done

echo ""
echo "🎉 SimpleSim is now running locally!"
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the application:"
echo "  docker-compose down" 