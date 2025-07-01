# Scripts Directory Organization

This directory contains Python scripts organized by their purpose and functionality.

## Directory Structure

### `/analysis/` - Data Analysis Scripts
Scripts for analyzing simulation results, logs, and data patterns.

**Scripts:**
- `analyze_debug_log_by_year.py` - Analyze debug simulation logs by year to identify growth issues
- `analyze_debug_log_detailed.py` - Detailed analysis of debug logs with comprehensive metrics
- `analyze_debug_log_simple.py` - Simple analysis of debug logs for basic insights
- `analyze_event_log.py` - Analyze event logs for recruitment, churn, and progression patterns
- `analyze_simulation_rec_churn_table_enhanced.py` - Enhanced analysis of recruitment and churn data
- `analyze_simulation_rec_churn_table.py` - Basic analysis of recruitment and churn data
- `analyze_simulation_json.py` - Analyze simulation JSON results
- `analyze_simulation_json_yearly.py` - Analyze yearly simulation JSON results
- `analyze_growth_issue.py` - Analyze growth issues in simulation results
- `analyze_recruitment_rates.py` - Analyze recruitment rates and patterns
- `analyze_tenure_distribution.py` - Analyze tenure distribution patterns
- `analyze_progression.py` - Analyze progression patterns
- `analyze_stockholm_margins.py` - Analyze Stockholm office margins
- `analyze_initial_tenure.py` - Analyze initial tenure distribution
- `verify_simulation_rates_vs_growth.py` - Verify simulation rates against growth
- `verify_simulation_results.py` - Verify simulation results accuracy

### `/debug/` - Debugging Scripts
Scripts for debugging simulation issues, data discrepancies, and engine problems.

**Scripts:**
- `debug_fte_discrepancy.py` - Debug FTE discrepancies between event logs and simulation results
- `debug_progression_issue.py` - Debug progression logic and issues
- `debug_promotion_analysis.py` - Analyze promotion patterns and issues
- `debug_simulation.py` - General simulation debugging
- `debug_recruitment_issue.py` - Debug recruitment-related issues
- `debug_monthly_metrics.py` - Debug monthly metric calculations
- `debug_negative_financials.py` - Debug negative financial results
- `debug_kpi_simple.py` - Simple KPI debugging
- `debug_financial_issue.py` - Debug financial calculation issues
- `debug_kpi_calculation.py` - Debug KPI calculation logic
- `debug_event_logs.py` - Debug event logging functionality
- `debug_actual_financials.py` - Debug actual financial data
- `debug_ac_am_progression.py` - Debug AC/AM progression logic

### `/test/` - Testing Scripts
Scripts for testing various components, functionality, and edge cases.

**Scripts:**
- `test_download_functionality.py` - Test download and export functionality
- `test_verification.py` - Test verification processes
- `test_json_export.py` - Test JSON export functionality
- `test_ui_simulation.py` - Test UI simulation integration
- `test_tenure_debug.py` - Test tenure-related functionality
- `test_single_vs_multi_year.py` - Test single vs multi-year simulation
- `test_realistic_simulation.py` - Test realistic simulation scenarios
- `test_refactored_engine.py` - Test refactored simulation engine
- `test_realistic_initialization.py` - Test realistic initialization
- `test_kpi_display.py` - Test KPI display functionality
- `test_fixed_progression.py` - Test fixed progression logic
- `test_formatting.py` - Test formatting functionality
- `test_excel_export_results.py` - Test Excel export results
- `test_event_logging_extended.py` - Extended event logging tests
- `test_event_logging.py` - Basic event logging tests
- `test_edge_cases_event_logs.py` - Test edge cases in event logging
- `test_engine_debug.py` - Test engine debugging functionality
- `test_ebitda_debug.py` - Test EBITDA debugging
- `test_csv_logging.py` - Test CSV logging functionality
- `test_3year_simulation.py` - Test 3-year simulation scenarios

### `/fixes/` - Configuration and Data Fixes
Scripts for fixing configuration issues, data problems, and applying patches.

**Scripts:**
- `fix_operations.py` - Fix operations-related configuration issues
- `fix_simulation_rates.py` - Fix simulation rates based on debugging analysis
- `patch_office_config.py` - Patch office configuration files
- `patch_utr.py` - Patch UTR (Utilization, Tenure, Revenue) data
- `set_consultant_recruitment_churn.py` - Set consultant recruitment and churn rates
- `set_non_consultant_prices_to_zero.py` - Set non-consultant prices to zero

### `/utilities/` - Utility Scripts
General utility scripts for data retrieval, running processes, and checking systems.

**Scripts:**
- `get_recruitment_churn_totals.py` - Get recruitment and churn totals
- `run_debug_simulation.py` - Run debug simulations
- `check_ui_discrepancy.py` - Check UI discrepancies
- `run_and_verify_simulation.py` - Run and verify simulation results
- `generate_monthly_excel.py` - Generate monthly Excel reports
- `generate_office_config.py` - Generate office configuration files
- `generate_office_config_cat_progression.py` - Generate office config with progression data

## Usage Guidelines

1. **Analysis Scripts**: Use these to understand simulation results, identify patterns, and generate insights
2. **Debug Scripts**: Use these when investigating issues or discrepancies in the simulation engine
3. **Test Scripts**: Use these to verify functionality, test edge cases, and ensure system reliability
4. **Fix Scripts**: Use these to apply configuration fixes and data corrections
5. **Utility Scripts**: Use these for general data retrieval and system checks

## Running Scripts

Most scripts can be run directly from their respective directories:

```bash
# Example: Run an analysis script
python scripts/analysis/analyze_debug_log_by_year.py

# Example: Run a debug script
python scripts/debug/debug_fte_discrepancy.py

# Example: Run a test script
python scripts/test/test_json_export.py
```

## Notes

- All scripts are designed to work with the SimpleSim project structure
- Most scripts include proper error handling and logging
- Scripts in the `/test/` directory are particularly useful for regression testing
- Scripts in the `/fixes/` directory should be run carefully as they modify configuration data

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