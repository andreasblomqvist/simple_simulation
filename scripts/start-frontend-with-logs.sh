#!/bin/bash

# SimpleSim Frontend Server with Logging
# Starts the frontend server and logs to a file for tailing

echo "🌐 Starting SimpleSim Frontend Server with Logging"
echo "=================================================="

# Create logs directory if it doesn't exist
mkdir -p frontend/logs

# Generate timestamp for log file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="frontend/logs/frontend_${TIMESTAMP}.log"

echo "📝 Log file: $LOG_FILE"
echo "🔍 To tail logs: tail -f $LOG_FILE"
echo ""

# Change to frontend directory
cd frontend

# Start frontend server and redirect output to log file
echo "Starting frontend server..."
npm run dev 2>&1 | tee "../$LOG_FILE" 