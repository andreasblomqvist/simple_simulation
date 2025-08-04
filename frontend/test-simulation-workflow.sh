#!/bin/bash

# Test script for simulation workflow E2E tests
# This script runs only the new simulation workflow tests

echo "🧪 Running SimpleSim Simulation Workflow E2E Tests"
echo "=================================================="

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  Installing dependencies..."
    npm install
fi

# Start development server in background if not running
if ! curl -s http://localhost:5173 > /dev/null; then
    echo "🚀 Starting development server..."
    npm run dev &
    DEV_PID=$!
    
    # Wait for server to start
    echo "⏳ Waiting for server to start..."
    timeout=60
    while [ $timeout -gt 0 ] && ! curl -s http://localhost:5173 > /dev/null; do
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        echo "❌ Server failed to start within 60 seconds"
        exit 1
    fi
    
    echo "✅ Server started successfully"
else
    echo "✅ Development server already running"
    DEV_PID=""
fi

# Run the specific simulation workflow tests
echo "🏃 Running simulation workflow tests..."
npx playwright test e2e/simulation-workflow.spec.ts --headed --project=chromium

# Capture test exit code
TEST_EXIT_CODE=$?

# Cleanup: kill dev server if we started it
if [ ! -z "$DEV_PID" ]; then
    echo "🧹 Cleaning up development server..."
    kill $DEV_PID 2>/dev/null
fi

# Report results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All simulation workflow tests passed!"
else
    echo "❌ Some tests failed (exit code: $TEST_EXIT_CODE)"
fi

exit $TEST_EXIT_CODE