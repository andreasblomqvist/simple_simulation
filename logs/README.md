# Logs Directory

This directory contains organized log files and output from various simulation runs and analyses.

## Directory Structure

### `/test_logs/`
Log files from test runs and debugging sessions.
- Contains CSV files with detailed simulation results
- Includes financial metrics, monthly progression, and office summaries
- Organized by timestamp for easy tracking

### `/analysis_logs/`
Log files from analysis scripts and data processing.
- Output from analysis scripts in `/scripts/analysis/`
- Processed data and metrics

### `/debug_logs/`
Log files from debugging sessions.
- Output from debug scripts in `/scripts/debug/`
- Error logs and diagnostic information

## File Naming Convention

Log files follow this naming pattern:
- `{category}_{timestamp}.csv` - Main log files
- `simulation_run_{timestamp}/` - Directory containing all logs for a specific simulation run

## Usage

Logs are automatically generated when running:
- Simulation tests
- Analysis scripts
- Debug scripts
- Excel export operations

## Notes

- Log files may be large for long simulations
- CSV format for easy analysis in Excel or other tools
- Timestamps help track when simulations were run
- Some files may be locked if Excel is open 