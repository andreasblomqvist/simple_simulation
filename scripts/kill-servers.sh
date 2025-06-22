#!/bin/bash

# Kill SimpleSim Servers Script
# Stops all running SimpleSim server processes

echo "🛑 Killing SimpleSim servers..."

# Kill by process name
pkill -f uvicorn 2>/dev/null || true
pkill -f vite 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true

# Kill by port
for port in 3000 3001 3002 3003 8000 8001; do
    pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "📍 Killing processes on port $port: $pids"
        echo $pids | xargs kill -9 2>/dev/null || true
    fi
done

# Clean up Python cache
echo "🧹 Clearing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "✅ All servers stopped and cache cleared" 