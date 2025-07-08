.PHONY: install start-backend start-frontend start-all stop-all clean

# Install dependencies
install:
	pip install -e .
	cd frontend && npm install

# Start backend server
start-backend:
	cd backend && PYTHONPATH=. uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend server
start-frontend:
	cd frontend && npm run dev

# Start both servers
start-all:
	@echo "Starting both servers..."
	@make start-backend & make start-frontend

# Stop all servers
stop-all:
	pkill -f uvicorn || true
	pkill -f vite || true
	pkill -f node || true

# Clean up
clean:
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	cd frontend && rm -rf node_modules/.vite dist 2>/dev/null || true 