#!/bin/bash

# Business Plan Data Setup Script
# This script helps populate business plan data for testing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Business Plan Data Setup"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="

echo "📁 Project root: $PROJECT_ROOT"
echo "📁 Script directory: $SCRIPT_DIR"

# Function to check if backend is running
check_backend() {
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start backend if not running
start_backend() {
    echo "🔄 Starting backend server..."
    cd "$PROJECT_ROOT"
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f ".venv/installed" ]; then
        echo "📦 Installing Python dependencies..."
        cd backend
        pip install -r requirements.txt
        cd ..
        touch .venv/installed
    fi
    
    # Start backend in background
    echo "🚀 Starting FastAPI server..."
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    echo "⏳ Waiting for backend to start..."
    for i in {1..30}; do
        if check_backend; then
            echo "✅ Backend is running"
            return 0
        fi
        sleep 2
    done
    
    echo "❌ Backend failed to start"
    return 1
}

# Function to generate test data files
generate_test_data() {
    echo ""
    echo "📊 Generating test data files..."
    cd "$SCRIPT_DIR"
    python3 generate_test_business_plan_data.py
    echo "✅ Test data files generated"
}

# Function to populate via API
populate_via_api() {
    echo ""
    echo "🌐 Populating business plan via API..."
    
    if ! check_backend; then
        echo "⚠️  Backend not running, starting it first..."
        if ! start_backend; then
            echo "❌ Cannot populate via API without backend"
            return 1
        fi
    else
        echo "✅ Backend is already running"
    fi
    
    cd "$SCRIPT_DIR"
    python3 populate_business_plan.py
    echo "✅ API population complete"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  generate    Generate test data JSON files only"
    echo "  populate    Populate business plan via API (starts backend if needed)"
    echo "  both        Generate files AND populate via API (default)"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Generate files and populate via API"
    echo "  $0 generate          # Only generate JSON test files"
    echo "  $0 populate          # Only populate via API"
    echo "  $0 both              # Do both operations"
}

# Main execution
case "${1:-both}" in
    "generate")
        generate_test_data
        ;;
    "populate")
        populate_via_api
        ;;
    "both")
        generate_test_data
        populate_via_api
        ;;
    "--help"|"-h")
        show_usage
        exit 0
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_usage
        exit 1
        ;;
esac

echo ""
echo "🎉 Business plan data setup complete!"
echo ""
echo "📋 What was created:"
echo "  • Test data JSON files in scripts/test_data/"
echo "  • Business plan entries in database (if populate was run)"
echo ""
echo "🚀 Next steps:"
echo "  • Start the frontend: cd frontend && npm run dev"
echo "  • Navigate to Business Planning section"
echo "  • Select an office to see populated data"