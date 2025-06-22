#!/bin/bash

# Create logs directory
mkdir -p logs

echo "🔄 Starting servers with persistent logging..."

# Kill existing servers
echo "🚫 Killing existing servers..."
pkill -f uvicorn 2>/dev/null || true
pkill -f vite 2>/dev/null || true
sleep 2

# Clear old logs
rm -f logs/backend.log logs/frontend.log

# Start backend with logging
echo "🚀 Starting backend server (logs: logs/backend.log)..."
PYTHONPATH=. python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Start frontend with logging
echo "🌐 Starting frontend server (logs: logs/frontend.log)..."
cd frontend && npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "✅ Servers started!"
echo "📝 Backend PID: $BACKEND_PID (logs/backend.log)"
echo "📝 Frontend PID: $FRONTEND_PID (logs/frontend.log)"
echo ""
echo "💡 To view logs:"
echo "   Backend: tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo "   Both: tail -f logs/*.log"
echo ""
echo "🛑 To stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   Or: pkill -f uvicorn && pkill -f vite" 