#!/bin/bash

# Check if logs directory exists
if [ ! -d "logs" ]; then
    echo "❌ No logs directory found. Run ./scripts/start-servers-with-logs.sh first"
    exit 1
fi

echo "📋 SimpleSim Server Logs Viewer"
echo "==============================="
echo ""
echo "Available commands:"
echo "  1) Backend logs only"
echo "  2) Frontend logs only"
echo "  3) Both logs (split screen)"
echo "  4) Both logs (combined)"
echo "  q) Quit"
echo ""

while true; do
    read -p "Choose option (1-4, q): " choice
    case $choice in
        1)
            echo "📊 Viewing backend logs (Ctrl+C to stop)..."
            tail -f logs/backend.log
            ;;
        2)
            echo "🌐 Viewing frontend logs (Ctrl+C to stop)..."
            tail -f logs/frontend.log
            ;;
        3)
            echo "📊🌐 Viewing both logs in split screen (Ctrl+C to stop)..."
            # Use tmux if available, otherwise fallback
            if command -v tmux &> /dev/null; then
                tmux new-session -d -s logs 'tail -f logs/backend.log' \; split-window -h 'tail -f logs/frontend.log' \; attach
            else
                echo "⚠️  tmux not available, showing combined logs instead..."
                tail -f logs/*.log
            fi
            ;;
        4)
            echo "📊🌐 Viewing combined logs (Ctrl+C to stop)..."
            tail -f logs/*.log
            ;;
        q|Q)
            echo "👋 Goodbye!"
            break
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-4 or q."
            ;;
    esac
    echo ""
    echo "📋 Back to menu..."
done 