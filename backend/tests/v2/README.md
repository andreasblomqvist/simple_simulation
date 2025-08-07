# SimpleSim Engine V2 Test Suite

Comprehensive test suite for SimpleSim Engine V2 with full coverage of all components and workflows.

## Overview

This test suite provides thorough testing for the SimpleSim Engine V2 architecture including:

- **Unit Tests**: Individual component testing with mocking and isolation
- **Integration Tests**: Full workflow testing with component interactions  
- **Performance Tests**: Load testing, benchmarking, and scalability analysis
- **API Tests**: FastAPI endpoint testing and validation

## Test Structure

```
backend/tests/v2/
├── conftest.py                 # Shared fixtures and test utilities
├── unit/                      # Unit tests for each component
│   ├── test_simulation_engine_v2.py
│   ├── test_workforce_manager_v2.py
│   ├── test_business_plan_processor_v2.py
│   ├── test_growth_model_manager_v2.py
│   ├── test_snapshot_loader_v2.py
│   └── test_kpi_calculator_v2.py
├── integration/               # Integration and workflow tests
│   ├── test_simulation_workflows_v2.py
│   └── test_simulation_api_v2.py
├── performance/               # Performance and load tests
│   └── test_performance_benchmarks_v2.py
├── pytest.ini               # pytest configuration
├── run_tests.py             # Test runner script
└── README.md               # This file
```

## Quick Start

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-cov pytest-timeout pytest-mock
```

### Running Tests

#### Using the Test Runner (Recommended)

```bash
# Run all unit tests
python backend/tests/v2/run_tests.py unit

# Run all integration tests
python backend/tests/v2/run_tests.py integration

# Run complete test suite with coverage
python backend/tests/v2/run_tests.py full

# Run tests for specific component
python backend/tests/v2/run_tests.py component --component workforce

# Generate detailed coverage analysis
python backend/tests/v2/run_tests.py coverage

# Run performance tests (takes longer)
python backend/tests/v2/run_tests.py performance
```

#### Direct pytest Commands

```bash
# From project root directory

# Run all V2 tests
pytest backend/tests/v2/ -v

# Run unit tests only
pytest backend/tests/v2/unit/ -v

# Run with coverage
pytest backend/tests/v2/ --cov=backend/src/services --cov-report=html

# Run specific test file
pytest backend/tests/v2/unit/test_simulation_engine_v2.py -v
```

## Test Categories

### Unit Tests

Test individual components in isolation with comprehensive mocking:

- **SimulationEngineV2**: Core engine functionality, initialization, validation
- **WorkforceManagerV2**: Individual tracking, CAT progression, churn/recruitment
- **BusinessPlanProcessorV2**: Growth rates, financial calculations, lever application
- **GrowthModelManagerV2**: Multi-year modeling, compound growth, extrapolation
- **SnapshotLoaderV2**: Population loading, validation, Person conversion
- **KPICalculatorV2**: All KPI calculations, comparative analysis, executive summaries

### Integration Tests

Test complete workflows and component interactions:

- End-to-end scenario execution
- Multi-office simulation workflows
- Business plan integration 
- Data flow between components
- Error handling and recovery
- API endpoint functionality

### Performance Tests

Benchmark and load testing:

- Large workforce simulation (1000+ persons)
- Multi-year simulation performance
- Memory usage monitoring
- Concurrent simulation execution
- Component performance profiling
- Scalability limit testing

## Test Data and Fixtures

The test suite includes comprehensive fixtures for:

### Mock Data
- **Population Snapshots**: Realistic workforce datasets with various sizes
- **Business Plans**: Multi-year plans with seasonal variations
- **CAT Matrices**: Progression probability matrices
- **Economic Parameters**: Office-specific parameters
- **Scenarios**: Base, growth, and multi-office scenarios

### Utilities
- **Person Factory**: Generate test Person objects with realistic data
- **Event Validator**: Validate PersonEvent objects
- **Memory Profiler**: Monitor memory usage during tests
- **Performance Benchmarking**: Time and resource measurement

## Coverage Requirements

The test suite maintains **90%+ code coverage** across all components:

- Line coverage: >90%
- Branch coverage: >85%
- Function coverage: >95%

Coverage reports are generated in multiple formats:
- HTML: `backend/tests/v2/htmlcov/index.html`
- XML: `backend/tests/v2/coverage.xml`
- JSON: `backend/tests/v2/coverage.json`

## Performance Benchmarks

### Target Performance Metrics

- **Large Workforce (1000+ persons)**: <60 seconds execution
- **Multi-year Simulation (3 years)**: <180 seconds execution
- **Memory Usage**: <200MB peak for large simulations
- **Concurrent Simulations**: Support 3+ parallel executions

### Performance Test Categories

1. **Load Testing**: Large datasets, extended time ranges
2. **Stress Testing**: Maximum workforce size, duration limits
3. **Memory Profiling**: Memory leak detection, usage optimization
4. **Concurrent Testing**: Multi-threading and parallel execution

## Test Configuration

### pytest.ini Settings

- Test discovery patterns
- Coverage configuration (90% minimum)
- Timeout settings (5 minutes default)
- Logging configuration
- Warning filters
- Custom markers for test categorization

### Markers

Use pytest markers to run specific test categories:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration

# Run only performance tests
pytest -m performance

# Skip slow tests
pytest -m "not slow"

# Run only API tests
pytest -m api
```

## Continuous Integration

The test suite is designed for CI/CD integration:

### GitHub Actions Example

```yaml
name: Test SimpleSim V2
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov pytest-timeout
      - name: Run unit tests
        run: python backend/tests/v2/run_tests.py unit
      - name: Run integration tests
        run: python backend/tests/v2/run_tests.py integration
      - name: Generate coverage report
        run: python backend/tests/v2/run_tests.py coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v1
        with:
          file: backend/tests/v2/coverage.xml
```

## Debugging and Development

### Running Individual Tests

```bash
# Run single test method
pytest backend/tests/v2/unit/test_simulation_engine_v2.py::TestSimulationEngineV2::test_engine_initialization -v

# Run with debugger
pytest backend/tests/v2/unit/test_workforce_manager_v2.py --pdb

# Run with output capture disabled
pytest backend/tests/v2/unit/test_kpi_calculator_v2.py -s
```

### Mock Usage

The test suite extensively uses mocking to isolate components:

```python
from unittest.mock import Mock, patch

# Mock external dependencies
@patch('backend.src.services.simulation_engine_v2.random.seed')
def test_random_seed_applied(self, mock_random_seed):
    # Test implementation
    pass

# Use fixtures for consistent test data
def test_with_fixtures(self, population_snapshot, business_plan):
    # Test using provided fixtures
    pass
```

### Custom Fixtures

Add custom fixtures in `conftest.py` for specialized test needs:

```python
@pytest.fixture
def custom_scenario():
    return ScenarioRequest(
        name="Custom Test Scenario",
        # ... configuration
    )
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH includes project root
2. **Fixture Not Found**: Check fixture names and scopes in conftest.py  
3. **Performance Test Timeouts**: Increase timeout or use `@pytest.mark.slow`
4. **Coverage Below Threshold**: Add tests for uncovered code paths

### Environment Setup

```bash
# From project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Install in development mode
pip install -e .

# Verify imports work
python -c "from backend.src.services.simulation_engine_v2 import SimulationEngineV2; print('OK')"
```

## Contributing

When adding new components or features:

1. **Add Unit Tests**: Comprehensive test coverage for new code
2. **Update Integration Tests**: Test interactions with existing components
3. **Add Performance Tests**: If performance-critical functionality
4. **Update Fixtures**: Add test data for new components
5. **Update Documentation**: Keep README and docstrings current

### Test Naming Conventions

- Test files: `test_[component_name]_v2.py`
- Test classes: `Test[ComponentName]V2[Category]`  
- Test methods: `test_[functionality]_[scenario]`

Example:
```python
class TestWorkforceManagerV2ChurnProcessing:
    def test_churn_processing_with_insufficient_people(self):
        pass
```

## Performance Monitoring

The test suite includes built-in performance monitoring:

- Execution time measurement
- Memory usage tracking  
- CPU usage monitoring
- Concurrent execution testing
- Scalability limit detection

Results are reported in test output and can be tracked over time to detect performance regressions.