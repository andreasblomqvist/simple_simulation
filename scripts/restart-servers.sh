#!/bin/bash

# SimpleSim Server Restart Script
# Automatically kills old instances and restarts servers cleanly

echo "🔄 SimpleSim Server Restart Script"
echo "=================================="

# Function to kill processes by port
kill_by_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "📍 Killing processes on port $port: $pids"
        echo $pids | xargs kill -9 2>/dev/null || true
    fi
}

# Function to kill processes by name
kill_by_name() {
    local name=$1
    echo "📍 Killing all $name processes..."
    pkill -f $name 2>/dev/null || true
}

# Step 1: Kill existing server processes
echo "🚫 Killing existing server processes..."
kill_by_name "uvicorn"
kill_by_name "vite"
kill_by_name "npm.*dev"

# Kill by specific ports
for port in 3000 3001 3002 3003 8000 8001; do
    kill_by_port $port
done

# Step 2: Clear Python cache
echo "🧹 Clearing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Step 3: Wait for processes to fully terminate
echo "⏳ Waiting for processes to terminate..."
sleep 3

# Step 4: Start backend server
echo "🚀 Starting backend server..."
cd "$(dirname "$0")/.." # Go to project root
PYTHONPATH=. python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Step 5: Start frontend server
echo "🌐 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Step 6: Wait and verify servers are running
echo "⏳ Waiting for servers to start..."
sleep 5

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend server is running on http://localhost:8000"
else
    echo "❌ Backend server failed to start"
fi

# Check if frontend is running (try common ports)
for port in 3000 3001 3002 3003; do
    if curl -s http://localhost:$port > /dev/null; then
        echo "✅ Frontend server is running on http://localhost:$port"
        break
    fi
done

echo ""
echo "🎉 Server restart complete!"
echo "📝 Backend PID: $BACKEND_PID"
echo "📝 Frontend PID: $FRONTEND_PID"
echo ""
echo "💡 To stop servers manually:"
echo "   Backend: kill $BACKEND_PID"
echo "   Frontend: kill $FRONTEND_PID"
echo "   Or run: pkill -f uvicorn && pkill -f vite" 