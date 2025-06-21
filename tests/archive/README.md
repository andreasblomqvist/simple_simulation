# Archived Tests

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
