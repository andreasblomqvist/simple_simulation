# SimpleSim Server Management Scripts

This directory contains scripts to manage the SimpleSim application servers.

## Available Scripts

### 🔄 Server Management
- **`restart-servers.sh`** - Complete restart of both backend and frontend servers (recommended)
- **`start-backend.sh`** - Start only the backend server
- **`start-frontend.sh`** - Start only the frontend server  
- **`kill-servers.sh`** - Emergency stop all servers

### 📊 Logging & Monitoring
- **`start-servers-with-logs.sh`** - Start servers with persistent logging to files
- **`view-logs.sh`** - Interactive log viewer for server output

## Quick Start

### Standard Server Restart
```bash
./scripts/restart-servers.sh
```

### Server Restart with Persistent Logs (for Cursor Terminal issues)
```bash
# Start servers with logging
./scripts/start-servers-with-logs.sh

# In another terminal tab, view logs
./scripts/view-logs.sh
```

### Manual Commands
```bash
# Emergency stop everything
./scripts/kill-servers.sh

# Start individual servers
./scripts/start-backend.sh
./scripts/start-frontend.sh
```

## Cursor Terminal Issues

If you're losing server logs in Cursor due to terminal restarts, use the logging solution:

1. **Start with logging**: `./scripts/start-servers-with-logs.sh`
2. **View logs persistently**: `./scripts/view-logs.sh`
3. **Log files location**: `logs/backend.log` and `logs/frontend.log`

You can also view logs directly:
```bash
# Backend logs only
tail -f logs/backend.log

# Frontend logs only  
tail -f logs/frontend.log

# Both logs combined
tail -f logs/*.log
```

## Ports Managed

- **Backend**: 8000, 8001
- **Frontend**: 3000, 3001, 3002, 3003

## Health Checks

All scripts include health checks to verify servers are running properly.

## Error Handling

Scripts handle common issues:
- Port conflicts ("Address already in use")
- Stale Python cache (`__pycache__` cleanup)
- Process termination delays
- Module import errors (PYTHONPATH setup)

## Common Issues Solved

### ❌ "Address already in use" Error
**Problem:** `ERROR: [Errno 48] Address already in use`

**Solution:** Run the restart script
```bash
./scripts/restart-servers.sh
```

### ❌ Python Module Import Errors
**Problem:** `ModuleNotFoundError: No module named 'backend'`

**Solution:** The scripts automatically set PYTHONPATH and clear cache
```bash
./scripts/start-backend.sh
```

### ❌ Stale Server Processes
**Problem:** Old servers keep running after crashes

**Solution:** Kill all processes first
```bash
./scripts/kill-servers.sh
./scripts/restart-servers.sh
```

## Manual Commands

If scripts are not available, use these manual commands:

### Kill All Servers
```bash
pkill -f uvicorn
pkill -f vite
lsof -ti:3000,3001,3002,3003,8000,8001 | xargs kill -9
```

### Start Backend Manually
```bash
PYTHONPATH=. python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend Manually
```bash
cd frontend && npm run dev
```

### Check What's Running
```bash
lsof -i:8000,3000,3001,3002,3003
ps aux | grep -E "(uvicorn|vite|npm.*dev)"
```

## Port Usage

| Service  | Primary Port | Fallback Ports |
|----------|-------------|----------------|
| Backend  | 8000        | 8001           |
| Frontend | 3000        | 3001, 3002, 3003 |

## Health Checks

After starting servers, verify they're working:

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend check (adjust port as needed)
curl http://localhost:3000

# Configuration validation
curl http://localhost:8000/simulation/config/validation
```

## Troubleshooting

### Script Permission Denied
```bash
chmod +x scripts/*.sh
```

### Python Path Issues
Make sure you're in the project root and set PYTHONPATH:
```bash
cd /path/to/simple_simulation
PYTHONPATH=. python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Cache Issues
Clear all Python cache:
```bash
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## Integration with .cursorrules

These scripts implement the **Server Port Management** rule defined in `.cursorrules`. The rule states:

> **Always kill old instances and restart on port conflicts**

This ensures clean development environment and prevents common server startup issues. 