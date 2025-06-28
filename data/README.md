# Data Directory

This directory contains all data files, configurations, and exports for the SimpleSim project.

## Directory Structure

### `/exports/`
Excel files containing simulation results and exports.
- `*_export.xlsx` - Simulation result exports
- `*_results.xlsx` - Analysis results
- `final_*.xlsx` - Final processed exports
- `successful_*.xlsx` - Successful simulation exports
- `test_*.xlsx` - Test exports
- `working_*.xlsx` - Working draft exports

### `/imports/`
Files used for importing data into the system.
- Excel templates for data import
- Configuration import files

### `/configs/`
Configuration files and office setups.
- `*_config*.xlsx` - Office configuration files
- `*_progression*.xlsx` - Career progression configurations
- `office_config*.xlsx` - Office-specific configurations
- `LAF*.xlsx` - LAF progression files
- `balanced_strategy*.xlsx` - Balanced strategy configurations
- `conservative_strategy*.xlsx` - Conservative strategy configurations

### `/input_data/`
Original input data files.
- Historical data files
- Reference data for simulations

### `/default_data/`
Default data and templates.
- Default office configurations
- Template files
- Reference images and data

## File Types

- **Excel (.xlsx)** - Main data format for configurations and exports
- **CSV (.csv)** - Data exports and logs
- **JSON (.json)** - Configuration files
- **Images (.png, .jpeg)** - Reference images and charts

## Usage

### Importing Data
```bash
# Import office configuration
python scripts/utilities/import_config.py data/configs/office_config.xlsx
```

### Exporting Results
```bash
# Export simulation results
python scripts/export/export_simulation.py
```

## Notes

- Some Excel files may be locked if opened in Excel
- Configuration files should follow the established format
- Export files are timestamped for version control
- Backup important configurations before making changes 