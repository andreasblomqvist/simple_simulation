#!/bin/bash

# SimpleSim Frontend Server Restart Script
# Kills any existing dev server processes and starts fresh

echo "🔄 Restarting SimpleSim Frontend Development Server..."

# Kill any existing vite dev server processes
echo "🛑 Stopping existing dev servers..."
pkill -f "vite" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

# Wait a moment for processes to clean up
sleep 2

# Check if ports are still occupied and kill processes using them
for port in 3000 3001 3002; do
  if lsof -ti :$port >/dev/null 2>&1; then
    echo "🛑 Killing process on port $port..."
    lsof -ti :$port | xargs kill -9 2>/dev/null || true
  fi
done

# Wait another moment
sleep 1

echo "✅ All existing servers stopped"
echo "🚀 Starting fresh development server..."

# Start the development server
npm run dev