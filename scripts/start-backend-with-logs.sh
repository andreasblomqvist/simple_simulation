#!/bin/bash

# SimpleSim Backend Server with Logging
# Starts the backend server and logs to a file for tailing

echo "🚀 Starting SimpleSim Backend Server with Logging"
echo "================================================="

# Create logs directory if it doesn't exist
mkdir -p backend/logs

# Generate timestamp for log file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="backend/logs/backend_${TIMESTAMP}.log"

echo "📝 Log file: $LOG_FILE"
echo "🔍 To tail logs: tail -f $LOG_FILE"
echo ""

# Start backend server and redirect output to log file
echo "Starting backend server..."
PYTHONPATH=. python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 2>&1 | tee "$LOG_FILE" 