#!/bin/bash

# SimpleSim Servers with Logging
# Starts both backend and frontend servers with logging to files

echo "🚀 SimpleSim Servers with Logging"
echo "=================================="

# Create log directories
mkdir -p backend/logs frontend/logs

# Generate timestamp for log files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKEND_LOG="backend/logs/backend_${TIMESTAMP}.log"
FRONTEND_LOG="frontend/logs/frontend_${TIMESTAMP}.log"

echo "📝 Backend log: $BACKEND_LOG"
echo "📝 Frontend log: $FRONTEND_LOG"
echo ""
echo "🔍 To tail backend logs: tail -f $BACKEND_LOG"
echo "🔍 To tail frontend logs: tail -f $FRONTEND_LOG"
echo "🔍 To tail both logs: tail -f $BACKEND_LOG $FRONTEND_LOG"
echo ""

# Kill any existing servers
echo "🚫 Killing existing servers..."
pkill -f uvicorn 2>/dev/null || true
pkill -f vite 2>/dev/null || true
sleep 2

# Start backend server in background
echo "🚀 Starting backend server..."
PYTHONPATH=. python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server in background
echo "🌐 Starting frontend server..."
cd frontend
npm run dev > "../$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for servers to start
echo "⏳ Waiting for servers to start..."
sleep 5

# Check if servers are running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend server is running on http://localhost:8000"
else
    echo "❌ Backend server failed to start"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend server is running on http://localhost:3000"
else
    echo "❌ Frontend server failed to start"
fi

echo ""
echo "🎉 Servers started with logging!"
echo "📝 Backend PID: $BACKEND_PID"
echo "📝 Frontend PID: $FRONTEND_PID"
echo ""
echo "📋 Log Commands:"
echo "   Backend logs:  tail -f $BACKEND_LOG"
echo "   Frontend logs: tail -f $FRONTEND_LOG"
echo "   Both logs:     tail -f $BACKEND_LOG $FRONTEND_LOG"
echo ""
echo "💡 To stop servers:"
echo "   pkill -f uvicorn && pkill -f vite" 