"""
Comprehensive Test Runner for SimpleSim Engine V2

This script runs all V2 tests including unit, integration, performance, and API tests.
Provides detailed reporting, coverage analysis, and CI/CD integration.
"""

import subprocess
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

class TestCategory:
    """Test category definitions"""
    UNIT = "unit"
    INTEGRATION = "integration" 
    PERFORMANCE = "performance"
    API = "api"
    ALL = "all"


class TestResult:
    """Test execution result"""
    def __init__(self, category: str, passed: bool, duration: float, 
                 details: Dict[str, Any] = None):
        self.category = category
        self.passed = passed
        self.duration = duration
        self.details = details or {}
        self.timestamp = datetime.now()


class V2TestRunner:
    """Comprehensive test runner for Engine V2"""
    
    def __init__(self):
        self.test_root = Path(__file__).parent
        self.backend_root = self.test_root.parent.parent
        self.results: List[TestResult] = []
        self.start_time: Optional[datetime] = None
        self.coverage_report: Optional[Dict[str, Any]] = None
    
    def run_tests(self, categories: List[str], verbose: bool = True, 
                  coverage: bool = False, parallel: bool = True) -> bool:
        """
        Run specified test categories
        
        Args:
            categories: List of test categories to run
            verbose: Enable verbose output
            coverage: Generate coverage reports
            parallel: Run tests in parallel where possible
            
        Returns:
            True if all tests passed
        """
        print("🚀 SimpleSim Engine V2 - Comprehensive Test Suite")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # Validate environment
        if not self._validate_environment():
            return False
        
        overall_success = True
        
        for category in categories:
            print(f"\n📋 Running {category.upper()} tests...")
            
            success = self._run_category_tests(
                category, verbose=verbose, coverage=coverage, parallel=parallel
            )
            
            if not success:
                overall_success = False
                if not verbose:
                    print(f"❌ {category.upper()} tests failed")
        
        # Generate coverage report if requested
        if coverage and overall_success:
            self._generate_coverage_report()
        
        # Print summary
        self._print_summary(overall_success)
        
        return overall_success
    
    def _validate_environment(self) -> bool:
        """Validate test environment"""
        print("🔧 Validating test environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        
        # Check if backend directory exists
        if not self.backend_root.exists():
            print(f"❌ Backend directory not found: {self.backend_root}")
            return False
        
        # Check required packages
        required_packages = [
            "pytest", "pytest-cov", "pytest-asyncio", "pytest-xdist",
            "fastapi", "aiohttp", "psutil"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            return False
        
        print("✅ Environment validation passed")
        return True
    
    def _run_category_tests(self, category: str, verbose: bool, 
                           coverage: bool, parallel: bool) -> bool:
        """Run tests for specific category"""
        start_time = time.time()
        
        try:
            if category == TestCategory.UNIT:
                success = self._run_unit_tests(verbose, coverage, parallel)
            elif category == TestCategory.INTEGRATION:
                success = self._run_integration_tests(verbose, coverage)
            elif category == TestCategory.PERFORMANCE:
                success = self._run_performance_tests(verbose)
            elif category == TestCategory.API:
                success = self._run_api_tests(verbose)
            elif category == TestCategory.ALL:
                success = (
                    self._run_unit_tests(verbose, coverage, parallel) and
                    self._run_integration_tests(verbose, coverage) and
                    self._run_performance_tests(verbose) and
                    self._run_api_tests(verbose)
                )
            else:
                print(f"❌ Unknown test category: {category}")
                return False
            
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                category=category,
                passed=success,
                duration=duration
            ))
            
            return success
            
        except Exception as e:
            print(f"❌ Error running {category} tests: {str(e)}")
            duration = time.time() - start_time
            self.results.append(TestResult(
                category=category,
                passed=False,
                duration=duration,
                details={"error": str(e)}
            ))
            return False
    
    def _run_unit_tests(self, verbose: bool, coverage: bool, parallel: bool) -> bool:
        """Run unit tests"""
        print("  🧪 Running unit tests...")
        
        cmd = ["python", "-m", "pytest"]
        cmd.extend([str(self.test_root / "unit")])
        cmd.extend(["-v"] if verbose else ["-q"])
        
        if coverage:
            cmd.extend([
                "--cov=backend.src.services",
                "--cov-report=html:backend/tests/v2/coverage_html",
                "--cov-report=xml:backend/tests/v2/coverage.xml",
                "--cov-report=term"
            ])
        
        if parallel:
            cmd.extend(["-n", "auto"])  # pytest-xdist parallel execution
        
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "--disable-warnings"
        ])
        
        result = subprocess.run(cmd, cwd=self.backend_root, capture_output=not verbose)
        
        if result.returncode == 0:
            print("  ✅ Unit tests passed")
            return True
        else:
            print("  ❌ Unit tests failed")
            if not verbose:
                print(f"     Exit code: {result.returncode}")
            return False
    
    def _run_integration_tests(self, verbose: bool, coverage: bool) -> bool:
        """Run integration tests"""
        print("  🔗 Running integration tests...")
        
        cmd = ["python", "-m", "pytest"]
        cmd.extend([str(self.test_root / "integration")])
        cmd.extend(["-v"] if verbose else ["-q"])
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "-s"  # Don't capture output for integration tests
        ])
        
        result = subprocess.run(cmd, cwd=self.backend_root, capture_output=not verbose)
        
        if result.returncode == 0:
            print("  ✅ Integration tests passed")
            return True
        else:
            print("  ❌ Integration tests failed")
            if not verbose:
                print(f"     Exit code: {result.returncode}")
            return False
    
    def _run_performance_tests(self, verbose: bool) -> bool:
        """Run performance tests"""
        print("  ⚡ Running performance tests...")
        
        cmd = ["python", "-m", "pytest"]
        cmd.extend([str(self.test_root / "performance")])
        cmd.extend(["-v"] if verbose else ["-q"])
        cmd.extend([
            "--tb=short",
            "--strict-markers", 
            "--disable-warnings",
            "-s",  # Don't capture output
            "--timeout=600"  # 10 minute timeout for performance tests
        ])
        
        result = subprocess.run(cmd, cwd=self.backend_root, capture_output=not verbose)
        
        if result.returncode == 0:
            print("  ✅ Performance tests passed")
            return True
        else:
            print("  ❌ Performance tests failed")
            if not verbose:
                print(f"     Exit code: {result.returncode}")
            return False
    
    def _run_api_tests(self, verbose: bool) -> bool:
        """Run API validation tests"""
        print("  🌐 Running API validation tests...")
        
        # First check if server is running
        if not self._check_server_running():
            print("  ⚠️  API server not running - starting test server...")
            if not self._start_test_server():
                print("  ❌ Could not start test server")
                return False
        
        cmd = ["python", "-m", "pytest"]
        cmd.extend([str(self.test_root / "test_api_validation.py")])
        cmd.extend(["-v"] if verbose else ["-q"])
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "-s"
        ])
        
        result = subprocess.run(cmd, cwd=self.backend_root, capture_output=not verbose)
        
        if result.returncode == 0:
            print("  ✅ API tests passed")
            return True
        else:
            print("  ❌ API tests failed")
            if not verbose:
                print(f"     Exit code: {result.returncode}")
            return False
    
    def _check_server_running(self) -> bool:
        """Check if API server is running"""
        try:
            import requests
            response = requests.get("http://localhost:8000/api/v2/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _start_test_server(self) -> bool:
        """Start test server for API tests"""
        print("  🚀 Starting test server...")
        # This would start the FastAPI server in the background
        # For now, we'll just indicate that manual start is needed
        print("  ℹ️  Please start the server manually: uvicorn backend.main:app --reload")
        return False
    
    def _generate_coverage_report(self):
        """Generate detailed coverage report"""
        print("\n📊 Generating coverage report...")
        
        coverage_file = self.test_root / "coverage.xml"
        if coverage_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                
                coverage_pct = float(root.attrib.get('line-rate', 0)) * 100
                
                print(f"  📈 Overall Coverage: {coverage_pct:.1f}%")
                
                # Find individual package coverage
                packages = root.findall('.//package')
                for package in packages:
                    name = package.attrib.get('name', 'unknown')
                    line_rate = float(package.attrib.get('line-rate', 0)) * 100
                    if 'simulation' in name or 'workforce' in name or 'business' in name:
                        print(f"     {name}: {line_rate:.1f}%")
                
                self.coverage_report = {
                    "overall": coverage_pct,
                    "packages": {p.attrib.get('name'): float(p.attrib.get('line-rate', 0)) * 100 
                               for p in packages}
                }
                
                html_report = self.test_root / "coverage_html" / "index.html"
                if html_report.exists():
                    print(f"  📄 HTML Report: {html_report}")
                
            except Exception as e:
                print(f"  ⚠️  Could not parse coverage report: {str(e)}")
    
    def _print_summary(self, overall_success: bool):
        """Print test execution summary"""
        print("\n" + "=" * 60)
        print("📋 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        if self.start_time:
            total_duration = (datetime.now() - self.start_time).total_seconds()
            print(f"⏱️  Total Execution Time: {total_duration:.2f} seconds")
        
        status = "✅ PASSED" if overall_success else "❌ FAILED"
        print(f"🎯 Overall Status: {status}")
        
        # Individual category results
        print("\n📊 Category Results:")
        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(f"   {status} {result.category.upper()}: {result.duration:.2f}s")
            
            if result.details and result.details.get("error"):
                print(f"      Error: {result.details['error']}")
        
        # Coverage summary
        if self.coverage_report:
            print(f"\n📈 Coverage Summary:")
            print(f"   Overall: {self.coverage_report['overall']:.1f}%")
            
            if self.coverage_report['overall'] >= 90:
                print("   🎉 Excellent coverage!")
            elif self.coverage_report['overall'] >= 80:
                print("   👍 Good coverage")
            elif self.coverage_report['overall'] >= 70:
                print("   ⚠️  Coverage could be better")
            else:
                print("   ❌ Low coverage - needs improvement")
        
        # Success metrics
        passed_tests = sum(1 for r in self.results if r.passed)
        total_tests = len(self.results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if overall_success:
            print("\n🎉 All tests passed! Engine V2 is ready for deployment.")
        else:
            print("\n⚠️  Some tests failed. Review the results and fix issues before deployment.")
        
        print("=" * 60)


def main():
    """Main test runner execution"""
    parser = argparse.ArgumentParser(description="SimpleSim Engine V2 Test Runner")
    parser.add_argument(
        "categories", 
        nargs="*",
        default=["all"],
        choices=[TestCategory.UNIT, TestCategory.INTEGRATION, 
                TestCategory.PERFORMANCE, TestCategory.API, TestCategory.ALL],
        help="Test categories to run"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage reports")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick test mode (unit tests only)")
    
    args = parser.parse_args()
    
    # Handle special modes
    if args.quick:
        categories = [TestCategory.UNIT]
    else:
        categories = args.categories
    
    # Run tests
    runner = V2TestRunner()
    success = runner.run_tests(
        categories=categories,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=not args.no_parallel
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()