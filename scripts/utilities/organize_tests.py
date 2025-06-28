#!/usr/bin/env python3
"""
Script to organize existing test files into the new structure
"""

import os
import shutil
from pathlib import Path

def organize_tests():
    """Move existing test files to appropriate directories"""
    
    # Create archive directory for old tests
    archive_dir = Path("tests/archive")
    archive_dir.mkdir(exist_ok=True)
    
    # Map of test files to their new locations
    test_mapping = {
        # Keep important verification tests
        "test_comprehensive_kpi_verification.py": "tests/archive/",
        "test_recruitment_verification.py": "tests/archive/",
        
        # Archive debugging and one-off tests
        "test_config_debug.py": "tests/archive/",
        "test_config_service_lifecycle.py": "tests/archive/",
        "test_config_service_simple.py": "tests/archive/",
        "test_startup_with_config.py": "tests/archive/",
        "test_debug_simulation.py": "tests/archive/",
        "test_progression_debug.py": "tests/archive/",
        
        # Archive financial verification tests (can be converted to pytest later)
        "test_financial_calculation.py": "tests/archive/",
        "test_updated_employment_costs.py": "tests/archive/",
        "test_comprehensive_verification.py": "tests/archive/",
        "test_correct_spreadsheet_logic.py": "tests/archive/",
        "test_price_increase_verification.py": "tests/archive/",
        "test_stockholm_direct.py": "tests/archive/",
        "test_exact_spreadsheet_calculation.py": "tests/archive/",
        "test_updated_utr.py": "tests/archive/",
        "test_ebitda_debug.py": "tests/archive/",
        
        # Archive Excel and simulation tests
        "test_excel_service.py": "tests/archive/",
        "test_engine_validation.py": "tests/archive/",
        "test_simulation_only.py": "tests/archive/",
        "test_excel_detailed.py": "tests/archive/",
        "test_excel_export_validation.py": "tests/archive/",
        "test_excel.py": "tests/archive/",
        "test_mcp_simple.py": "tests/archive/",
    }
    
    print("📁 Organizing test files...")
    
    moved_count = 0
    for test_file, destination in test_mapping.items():
        source_path = Path(test_file)
        if source_path.exists():
            dest_path = Path(destination) / test_file
            print(f"   Moving {test_file} → {destination}")
            shutil.move(str(source_path), str(dest_path))
            moved_count += 1
        else:
            print(f"   ⚠️  {test_file} not found")
    
    print(f"\n✅ Moved {moved_count} test files to archive")
    
    # Create a README in the archive
    archive_readme = archive_dir / "README.md"
    archive_readme.write_text("""# Archived Tests

This directory contains the original test files that were created during development.
These tests are archived for reference but are not part of the main test suite.

## Contents

- **Debugging tests**: Files used for debugging specific issues
- **One-off verification tests**: Tests created to verify specific functionality
- **Legacy tests**: Tests that predate the organized test structure

## Migration

To migrate any of these tests to the new structure:

1. Convert to pytest format using fixtures from `conftest.py`
2. Categorize as unit, integration, or verification test
3. Move to appropriate directory in `tests/`
4. Update imports and test structure

## Running Archived Tests

These tests can still be run individually:

```bash
python3 test_filename.py
```

Note: Some tests may require the backend server to be running.
""")
    
    print(f"📝 Created archive README")
    
    # Show final structure
    print("\n📊 Final test structure:")
    for root, dirs, files in os.walk("tests"):
        level = root.replace("tests", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            if file.endswith(".py"):
                print(f"{subindent}{file}")

if __name__ == "__main__":
    organize_tests()
