#!/usr/bin/env python3
"""
Test Runner for SimpleSim Engine V2 Test Suite

Comprehensive test execution script with multiple run configurations:
- Unit tests only
- Integration tests only
- Performance tests (with warnings)
- Full test suite
- Coverage analysis
- Test reporting
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path
import time

def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False, text=True)
    end_time = time.time()
    
    print(f"\nCompleted in {end_time - start_time:.2f} seconds")
    print(f"Exit code: {result.returncode}")
    
    return result.returncode == 0

def run_unit_tests():
    """Run unit tests only"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/v2/unit/",
        "-v",
        "--cov=backend/src/services",
        "--cov-report=term-missing",
        "--cov-report=html:tests/v2/htmlcov/unit",
        "-m", "not slow"
    ]
    return run_command(cmd, "Unit Tests")

def run_integration_tests():
    """Run integration tests only"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/v2/integration/",
        "-v",
        "--cov=backend/src/services",
        "--cov-report=term-missing",
        "--cov-report=html:tests/v2/htmlcov/integration",
        "-m", "not slow"
    ]
    return run_command(cmd, "Integration Tests")

def run_performance_tests():
    """Run performance tests with warnings"""
    print("\n" + "="*60)
    print("WARNING: Performance tests may take significant time!")
    print("These tests include:")
    print("- Large dataset processing (1000+ persons)")
    print("- Multi-year simulations")
    print("- Memory and CPU monitoring")
    print("- Concurrent execution tests")
    print("="*60)
    
    response = input("Continue with performance tests? [y/N]: ")
    if response.lower() != 'y':
        print("Performance tests skipped.")
        return True
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/v2/performance/",
        "-v",
        "--timeout=600",  # 10 minute timeout
        "-s"  # Don't capture output for performance monitoring
    ]
    return run_command(cmd, "Performance Tests")

def run_api_tests():
    """Run API endpoint tests"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/v2/integration/test_simulation_api_v2.py",
        "-v",
        "--cov=backend/routers",
        "--cov-report=term-missing"
    ]
    return run_command(cmd, "API Endpoint Tests")

def run_full_test_suite():
    """Run the complete test suite"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/v2/",
        "-v",
        "--cov=backend/src/services",
        "--cov=backend/routers/simulation_v2.py",
        "--cov-report=html:tests/v2/htmlcov/full",
        "--cov-report=xml:tests/v2/coverage.xml",
        "--cov-report=term-missing",
        "--cov-fail-under=90",
        "-m", "not slow",  # Exclude slow performance tests by default
        "--junit-xml=tests/v2/junit-report.xml"
    ]
    return run_command(cmd, "Full Test Suite (excluding performance tests)")

def run_coverage_analysis():
    """Generate detailed coverage analysis"""
    print("\n" + "="*60)
    print("Generating Coverage Analysis")
    print("="*60)
    
    # Run tests with coverage
    cmd = [
        "python", "-m", "pytest", 
        "tests/v2/unit/",
        "tests/v2/integration/",
        "--cov=backend/src/services",
        "--cov-branch",
        "--cov-report=html:tests/v2/htmlcov/analysis",
        "--cov-report=term-missing:skip-covered",
        "--cov-report=json:tests/v2/coverage.json",
        "--quiet"
    ]
    
    success = run_command(cmd, "Coverage Analysis")
    
    if success:
        print(f"\nCoverage reports generated:")
        print(f"- HTML: {Path('tests/v2/htmlcov/analysis/index.html').absolute()}")
        print(f"- JSON: {Path('tests/v2/coverage.json').absolute()}")
    
    return success

def run_component_tests(component):
    """Run tests for a specific component"""
    component_file_map = {
        "engine": "test_simulation_engine_v2.py",
        "workforce": "test_workforce_manager_v2.py", 
        "business": "test_business_plan_processor_v2.py",
        "growth": "test_growth_model_manager_v2.py",
        "snapshot": "test_snapshot_loader_v2.py",
        "kpi": "test_kpi_calculator_v2.py"
    }
    
    if component not in component_file_map:
        print(f"Unknown component: {component}")
        print(f"Available components: {', '.join(component_file_map.keys())}")
        return False
    
    test_file = f"tests/v2/unit/{component_file_map[component]}"
    
    cmd = [
        "python", "-m", "pytest", 
        test_file,
        "-v",
        "--cov=backend/src/services",
        "--cov-report=term-missing"
    ]
    
    return run_command(cmd, f"Component Tests: {component}")

def setup_test_environment():
    """Set up the test environment"""
    print("Setting up test environment...")
    
    # Ensure test directories exist
    test_dirs = [
        "tests/v2/htmlcov",
        "tests/v2/htmlcov/unit",
        "tests/v2/htmlcov/integration", 
        "tests/v2/htmlcov/full",
        "tests/v2/htmlcov/analysis"
    ]
    
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Check required dependencies
    try:
        import pytest
        import pytest_cov
        import pytest_timeout
        print("✓ All required test dependencies available")
        return True
    except ImportError as e:
        print(f"✗ Missing test dependency: {e}")
        print("Please install test dependencies:")
        print("pip install pytest pytest-cov pytest-timeout pytest-mock")
        return False

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="SimpleSim Engine V2 Test Runner")
    parser.add_argument(
        "test_type", 
        choices=[
            "unit", "integration", "performance", "api", 
            "full", "coverage", "component"
        ],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--component", 
        choices=[
            "engine", "workforce", "business", 
            "growth", "snapshot", "kpi"
        ],
        help="Specific component to test (only with component test_type)"
    )
    parser.add_argument(
        "--no-setup", 
        action="store_true",
        help="Skip environment setup"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Extra verbose output"
    )
    
    args = parser.parse_args()
    
    # Setup environment unless skipped
    if not args.no_setup:
        if not setup_test_environment():
            return 1
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    print(f"\nRunning tests from: {os.getcwd()}")
    print(f"Test type: {args.test_type}")
    
    # Run appropriate tests
    success = False
    
    if args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "performance":
        success = run_performance_tests()
    elif args.test_type == "api":
        success = run_api_tests()
    elif args.test_type == "full":
        success = run_full_test_suite()
    elif args.test_type == "coverage":
        success = run_coverage_analysis()
    elif args.test_type == "component":
        if not args.component:
            print("Component must be specified with --component option")
            return 1
        success = run_component_tests(args.component)
    
    # Summary
    print("\n" + "="*60)
    if success:
        print("✓ TEST EXECUTION COMPLETED SUCCESSFULLY")
    else:
        print("✗ TEST EXECUTION FAILED")
    print("="*60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())