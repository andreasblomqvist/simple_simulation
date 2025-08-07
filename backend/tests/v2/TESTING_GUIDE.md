# SimpleSim Engine V2 - Comprehensive Testing Guide

## 🎯 Overview

This guide provides complete instructions for testing SimpleSim Engine V2, including unit tests, integration tests, performance benchmarks, and API validation. The test suite ensures Engine V2 meets quality, performance, and reliability standards before production deployment.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)  
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Performance Testing](#performance-testing)
6. [API Testing](#api-testing)
7. [Coverage Requirements](#coverage-requirements)
8. [CI/CD Integration](#cicd-integration)
9. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio pytest-xdist pytest-timeout
pip install aiohttp psutil requests
```

### Run All Tests
```bash
cd backend/tests/v2/
python run_all_tests.py
```

### Run Quick Unit Tests Only
```bash
python run_all_tests.py --quick
```

### Demo Engine V2
```bash
python demo_v2_engine.py
```

## 📁 Test Structure

```
backend/tests/v2/
├── conftest.py                          # Shared fixtures and utilities
├── unit/                               # Unit tests (90%+ coverage target)
│   ├── test_simulation_engine_v2.py    # Core engine tests
│   ├── test_workforce_manager_v2.py    # Individual tracking tests  
│   ├── test_business_plan_processor_v2.py # Business logic tests
│   ├── test_growth_model_manager_v2.py # Growth modeling tests
│   ├── test_snapshot_loader_v2.py      # Population loading tests
│   └── test_kpi_calculator_v2.py       # KPI calculation tests
├── integration/                        # Integration tests
│   ├── test_simulation_workflows_v2.py # End-to-end workflows
│   └── test_simulation_api_v2.py       # API integration
├── performance/                        # Performance tests
│   └── test_performance_benchmarks_v2.py # Load and stress tests
├── test_api_validation.py             # API validation tests
├── load_test.py                        # Comprehensive load testing
├── demo_v2_engine.py                   # Interactive demo
├── run_all_tests.py                    # Test runner
└── TESTING_GUIDE.md                    # This guide
```

## 🔧 Running Tests

### Test Runner Options

#### 1. Comprehensive Test Suite
```bash
# Run all test categories
python run_all_tests.py all --verbose --coverage

# Run specific categories  
python run_all_tests.py unit integration --verbose
python run_all_tests.py performance --verbose
python run_all_tests.py api --verbose
```

#### 2. Direct pytest Usage
```bash
# Unit tests with coverage
pytest unit/ -v --cov=backend.src.services --cov-report=html

# Integration tests
pytest integration/ -v -s

# Performance tests (long running)
pytest performance/ -v -s --timeout=600

# API tests (requires running server)
pytest test_api_validation.py -v -s
```

#### 3. Parallel Execution
```bash
# Run unit tests in parallel
pytest unit/ -n auto -v

# Run with custom worker count
pytest unit/ -n 4 -v
```

### Load Testing
```bash
# Basic load test
python load_test.py

# Custom load test parameters
python load_test.py --concurrent 10 --workforce 2000 --months 48
python load_test.py --memory-limit 1000 --time-limit 600
python load_test.py --report-file load_test_report.txt
```

## 📊 Test Categories

### 1. Unit Tests (`unit/`)
**Purpose**: Test individual components in isolation  
**Coverage Target**: 90%+  
**Execution Time**: < 30 seconds  

**What's Tested**:
- Component initialization and configuration
- Core business logic and algorithms
- Error handling and edge cases
- Data validation and transformation
- Individual method functionality

**Key Test Files**:
- `test_simulation_engine_v2.py`: Core engine, factory, validation
- `test_workforce_manager_v2.py`: Individual tracking, CAT progression
- `test_business_plan_processor_v2.py`: Growth rates, financial calculations
- `test_growth_model_manager_v2.py`: Multi-year modeling, extrapolation
- `test_snapshot_loader_v2.py`: Population loading, validation
- `test_kpi_calculator_v2.py`: Comprehensive metrics calculation

### 2. Integration Tests (`integration/`)
**Purpose**: Test component interactions and workflows  
**Coverage Target**: 85%+  
**Execution Time**: < 2 minutes  

**What's Tested**:
- End-to-end simulation workflows
- Component data flow validation
- Service integration points
- Error propagation and recovery
- Multi-component scenarios

**Key Test Files**:
- `test_simulation_workflows_v2.py`: Complete simulation workflows
- `test_simulation_api_v2.py`: API endpoint integration

### 3. Performance Tests (`performance/`)
**Purpose**: Validate performance and scalability  
**Coverage Target**: Key scenarios  
**Execution Time**: < 10 minutes  

**What's Tested**:
- Large workforce simulations (1000+ people)
- Multi-year scenarios (24-60 months)
- Memory usage under load
- Execution time benchmarks
- Concurrent simulation handling

**Performance Targets**:
- Large workforce (1000 people): < 60 seconds
- Multi-year (3 years): < 180 seconds
- Memory usage: < 500MB peak
- Concurrent simulations: 5+ parallel

### 4. API Tests (`test_api_validation.py`)
**Purpose**: Validate REST API endpoints  
**Coverage Target**: All endpoints  
**Execution Time**: < 1 minute  

**What's Tested**:
- Request/response validation
- Error handling and status codes
- Authentication and authorization
- Rate limiting and timeouts
- Concurrent API requests

## ⚡ Performance Testing

### Load Test Configuration
```python
LoadTestConfig(
    concurrent_simulations=5,      # Parallel simulations
    large_workforce_size=1000,     # Max people per simulation
    multi_year_duration=36,        # Max months to simulate
    max_memory_mb=500.0,          # Memory limit
    max_execution_time_seconds=300.0  # Time limit
)
```

### Performance Benchmarks

#### Expected Performance
| Test Scenario | Target Time | Target Memory | Success Rate |
|---------------|-------------|---------------|--------------|
| Basic simulation (6 months, 1 office) | < 5 seconds | < 100MB | 100% |
| Large workforce (1000 people) | < 60 seconds | < 500MB | 100% |
| Multi-year (36 months) | < 180 seconds | < 400MB | 100% |
| Concurrent (5 simulations) | < 300 seconds | < 600MB | 80%+ |
| API load (10 requests) | < 30 seconds | < 200MB | 80%+ |

#### Running Performance Tests
```bash
# Quick performance test
python -m pytest performance/ -v --timeout=600

# Comprehensive load test
python load_test.py --concurrent 5 --workforce 1000 --months 36

# Memory stress test
python load_test.py --memory-limit 1000 --concurrent 8

# API performance test (requires server)
python load_test.py --api-url http://localhost:8000
```

### Performance Monitoring
The load test script includes:
- Memory usage tracking
- Execution time measurement
- Success rate calculation
- Performance regression detection
- Comprehensive reporting

## 🌐 API Testing

### Starting Test Server
```bash
# Start FastAPI server for API tests
cd backend/
uvicorn main:app --reload --port 8000

# Check server health
curl http://localhost:8000/api/v2/health
```

### API Test Categories

#### 1. Endpoint Validation
- Health check endpoints
- Scenario submission and tracking
- Result retrieval and formatting
- Error handling and status codes

#### 2. Request Validation  
- Input parameter validation
- Required field checking
- Data type validation
- Range and constraint checking

#### 3. Response Validation
- Correct response structure
- Data completeness and accuracy
- Error message clarity
- Status code appropriateness

#### 4. Load Testing
- Concurrent request handling
- Response time under load
- Memory usage during API calls
- Error rate under stress

### Running API Tests
```bash
# Ensure server is running first
uvicorn backend.main:app --reload &

# Run API tests
pytest test_api_validation.py -v -s

# Run API load test
python load_test.py --api-url http://localhost:8000
```

## 📈 Coverage Requirements

### Coverage Targets
- **Overall Coverage**: 90%+
- **Unit Test Coverage**: 95%+
- **Integration Coverage**: 85%+
- **Critical Path Coverage**: 100%

### Generating Coverage Reports
```bash
# HTML coverage report
pytest unit/ --cov=backend.src.services --cov-report=html
# Open: backend/tests/v2/coverage_html/index.html

# Terminal coverage report
pytest unit/ --cov=backend.src.services --cov-report=term

# XML coverage report (for CI)
pytest unit/ --cov=backend.src.services --cov-report=xml
```

### Coverage Analysis
```bash
# Detailed coverage by file
python run_all_tests.py unit --coverage --verbose

# Coverage with missing lines
pytest unit/ --cov=backend.src.services --cov-report=term-missing
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: SimpleSim V2 Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio pytest-xdist
    
    - name: Run unit tests
      run: |
        cd backend/tests/v2/
        python run_all_tests.py unit --coverage
    
    - name: Run integration tests
      run: |
        cd backend/tests/v2/
        python run_all_tests.py integration
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v2
      with:
        file: backend/tests/v2/coverage.xml
```

### Test Environment Setup
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r test-requirements.txt

# Run tests
cd backend/tests/v2/
python run_all_tests.py
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```
ImportError: No module named 'backend.src.services'
```
**Solution**: Ensure PYTHONPATH includes backend directory
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
# Or run from backend/tests/v2/ directory
```

#### 2. Test Failures Due to Dependencies
```
ModuleNotFoundError: No module named 'pytest_asyncio'
```
**Solution**: Install test dependencies
```bash
pip install pytest pytest-cov pytest-asyncio pytest-xdist pytest-timeout aiohttp psutil
```

#### 3. API Tests Failing
```
Connection refused to localhost:8000
```
**Solution**: Start the FastAPI server
```bash
cd backend/
uvicorn main:app --reload --port 8000
```

#### 4. Performance Test Timeouts
```
TimeoutError: Test exceeded 300 seconds
```
**Solution**: Increase timeout or run on faster hardware
```bash
pytest performance/ --timeout=600
```

#### 5. Coverage Not Generated
```
coverage: No data to report
```
**Solution**: Run tests with coverage flag
```bash
pytest unit/ --cov=backend.src.services --cov-report=term
```

### Debug Mode
```bash
# Run tests with detailed output
pytest -vvv -s --tb=long unit/test_simulation_engine_v2.py

# Run single test method
pytest -v unit/test_simulation_engine_v2.py::TestSimulationEngineV2::test_engine_initialization

# Debug with pdb
pytest --pdb unit/test_simulation_engine_v2.py
```

### Test Data Issues
```bash
# Clear test cache
rm -rf __pycache__/ .pytest_cache/

# Reset test database/files
rm -rf test_data/
```

## 📚 Additional Resources

### Test Development Guidelines
- Follow Arrange-Act-Assert pattern
- Use descriptive test names
- Create focused, single-purpose tests
- Mock external dependencies
- Use fixtures for common setup
- Test both happy path and error cases

### Performance Optimization Tips
- Use deterministic random seeds for consistency
- Mock expensive operations in unit tests
- Use parallel execution for independent tests
- Monitor memory usage in long-running tests
- Profile slow tests to identify bottlenecks

### Best Practices
- Keep tests fast and reliable
- Maintain test independence
- Use meaningful assertions
- Document complex test scenarios
- Regular test maintenance and updates

---

**📧 Questions or Issues?**
- Check the troubleshooting section above
- Review existing test examples
- Consult the Engine V2 documentation
- Run the demo script for reference examples

**🎯 Test Quality Standards**
- All tests must be deterministic
- Coverage targets must be met
- Performance benchmarks must pass
- API contracts must be validated
- Error handling must be comprehensive