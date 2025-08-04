#!/bin/bash

# Project and Quality Manager Agent Activation Script
# This script activates the PM/QM agent and provides initial project assessment

echo "🚀 Activating Project and Quality Manager Agent..."
echo "=================================================="

# Function to check if servers are running
check_servers() {
    echo "📊 Checking server status..."
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend server: RUNNING (port 8000)"
        BACKEND_STATUS="running"
    else
        echo "❌ Backend server: NOT RUNNING"
        BACKEND_STATUS="stopped"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend server: RUNNING (port 3000)"
        FRONTEND_STATUS="running"
    elif curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo "✅ Frontend server: RUNNING (port 3001)"
        FRONTEND_STATUS="running"
    elif curl -s http://localhost:3002 > /dev/null 2>&1; then
        echo "✅ Frontend server: RUNNING (port 3002)"
        FRONTEND_STATUS="running"
    else
        echo "❌ Frontend server: NOT RUNNING"
        FRONTEND_STATUS="stopped"
    fi
}

# Function to check recent git activity
check_git_status() {
    echo ""
    echo "📈 Checking recent project activity..."
    
    # Get recent commits
    RECENT_COMMITS=$(git log --oneline -5 2>/dev/null | wc -l)
    if [ "$RECENT_COMMITS" -gt 0 ]; then
        echo "✅ Recent git activity detected ($RECENT_COMMITS commits in last 5)"
        echo "📝 Latest commits:"
        git log --oneline -3 2>/dev/null || echo "   No recent commits"
    else
        echo "⚠️  No recent git activity detected"
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        echo "⚠️  Uncommitted changes detected"
        echo "   Files with changes:"
        git status --porcelain 2>/dev/null | head -5 | sed 's/^/   /'
    else
        echo "✅ No uncommitted changes"
    fi
}

# Function to check task files
check_task_files() {
    echo ""
    echo "📋 Checking task management files..."
    
    TASK_FILES=$(find . -name "tasks-*.md" -o -name "prd-*.md" 2>/dev/null | head -5)
    if [ -n "$TASK_FILES" ]; then
        echo "✅ Task files found:"
        echo "$TASK_FILES" | sed 's/^/   /'
        
        # Count completed vs pending tasks
        echo "📊 Task files found, checking completion status..."
        echo "   (Task counting temporarily disabled due to script optimization)"
    else
        echo "⚠️  No task files found"
    fi
}

# Function to check system health
check_system_health() {
    echo ""
    echo "🏥 Checking system health..."
    
    # Check disk space
    DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        echo "⚠️  High disk usage: ${DISK_USAGE}%"
    else
        echo "✅ Disk usage: ${DISK_USAGE}%"
    fi
    
    # Check memory usage
    if command -v free >/dev/null 2>&1; then
        MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
        echo "✅ Memory usage: ${MEMORY_USAGE}%"
    fi
    
    # Check for Python cache files
    CACHE_SIZE=$(find . -name "__pycache__" -type d 2>/dev/null | wc -l)
    if [ "$CACHE_SIZE" -gt 10 ]; then
        echo "⚠️  Large number of Python cache directories: $CACHE_SIZE"
    else
        echo "✅ Python cache: Clean"
    fi
}

# Function to provide PM/QM recommendations
provide_recommendations() {
    echo ""
    echo "💡 Project Manager Recommendations:"
    echo "==================================="
    
    if [ "$BACKEND_STATUS" = "stopped" ] || [ "$FRONTEND_STATUS" = "stopped" ]; then
        echo "🔧 IMMEDIATE ACTION REQUIRED:"
        echo "   - Start development servers"
        echo "   - Run: ./scripts/restart-servers.sh"
        echo ""
    fi
    
    echo "📋 RECOMMENDED NEXT STEPS:"
    echo "   1. Review current task status"
    echo "   2. Check for any blocking issues"
    echo "   3. Update task completion status"
    echo "   4. Plan next development session"
    echo ""
    
    echo "🔍 QUALITY ASSURANCE CHECKLIST:"
    echo "   - [ ] Code follows architecture patterns"
    echo "   - [ ] Tests are passing"
    echo "   - [ ] Documentation is up to date"
    echo "   - [ ] Performance is acceptable"
    echo "   - [ ] No security vulnerabilities"
    echo ""
}

# Main execution
main() {
    check_servers
    check_git_status
    check_task_files
    check_system_health
    provide_recommendations
    
    echo "🎯 Project and Quality Manager Agent is now active!"
    echo ""
    echo "Available commands:"
    echo "  - Check status: ./scripts/activate-project-manager.sh"
    echo "  - Restart servers: ./scripts/restart-servers.sh"
    echo "  - View tasks: find . -name 'tasks-*.md' -exec cat {} \\;"
    echo "  - Check logs: tail -f backend/logs/backend.log"
    echo ""
    echo "Ready to manage your project! 🚀"
}

# Run main function
main 