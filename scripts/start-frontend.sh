#!/bin/bash

# Start SimpleSim Frontend Script
# Kills existing frontend processes and starts fresh

echo "🌐 Starting SimpleSim Frontend..."

# Kill existing vite/npm processes
pkill -f vite 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true

# Kill processes on frontend ports
for port in 3000 3001 3002 3003; do
    pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "📍 Killing processes on port $port: $pids"
        echo $pids | xargs kill -9 2>/dev/null || true
    fi
done

# Wait for processes to terminate
sleep 2

# Start frontend server
echo "🌐 Starting frontend server..."
cd "$(dirname "$0")/../frontend" # Go to frontend directory
npm run dev 