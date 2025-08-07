"""
Load Test Script for SimpleSim Engine V2

This script performs comprehensive load testing on the V2 engine:
- Multiple concurrent simulations
- Large workforce testing  
- Multi-year simulation stress tests
- Memory usage monitoring
- Performance regression detection
"""

import asyncio
import aiohttp
import time
import psutil
import threading
import json
from datetime import datetime, date
from typing import List, Dict, Any
import statistics
from dataclasses import dataclass
import argparse
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from backend.src.services.simulation_engine_v2 import (
    SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
    Person, PopulationSnapshot, WorkforceEntry
)


@dataclass
class LoadTestConfig:
    """Load test configuration"""
    concurrent_simulations: int = 5
    large_workforce_size: int = 1000
    multi_year_duration: int = 36  # months
    max_memory_mb: float = 500.0
    max_execution_time_seconds: float = 300.0
    api_base_url: str = "http://localhost:8000"


@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    success: bool
    execution_time: float
    memory_usage_mb: float
    error_message: str = None
    additional_metrics: Dict[str, Any] = None


@dataclass
class LoadTestResults:
    """Complete load test results"""
    config: LoadTestConfig
    test_results: List[TestResult]
    overall_success: bool
    total_execution_time: float
    peak_memory_usage: float
    
    def get_success_rate(self) -> float:
        """Get test success rate"""
        if not self.test_results:
            return 0.0
        successful = sum(1 for r in self.test_results if r.success)
        return successful / len(self.test_results) * 100
    
    def get_average_execution_time(self) -> float:
        """Get average execution time"""
        if not self.test_results:
            return 0.0
        times = [r.execution_time for r in self.test_results if r.success]
        return statistics.mean(times) if times else 0.0


class MemoryMonitor:
    """Monitor memory usage during tests"""
    
    def __init__(self):
        self.monitoring = False
        self.peak_memory = 0.0
        self.memory_samples = []
    
    def start_monitoring(self):
        """Start memory monitoring"""
        self.monitoring = True
        self.peak_memory = 0.0
        self.memory_samples = []
        
        def monitor():
            while self.monitoring:
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                self.memory_samples.append(memory_mb)
                self.peak_memory = max(self.peak_memory, memory_mb)
                time.sleep(0.5)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def stop_monitoring(self) -> float:
        """Stop monitoring and return peak memory"""
        self.monitoring = False
        return self.peak_memory


class V2EngineLoadTester:
    """Load tester for SimpleSim Engine V2"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.memory_monitor = MemoryMonitor()
        self.results: List[TestResult] = []
    
    def run_all_tests(self) -> LoadTestResults:
        """Run all load tests"""
        print("🚀 Starting SimpleSim Engine V2 Load Tests")
        print(f"Config: {self.config.concurrent_simulations} concurrent, {self.config.large_workforce_size} workforce")
        print("=" * 60)
        
        start_time = time.time()
        self.memory_monitor.start_monitoring()
        
        try:
            # Test 1: Basic engine performance
            self._test_basic_engine_performance()
            
            # Test 2: Concurrent simulations
            self._test_concurrent_simulations()
            
            # Test 3: Large workforce simulation
            self._test_large_workforce_simulation()
            
            # Test 4: Multi-year simulation
            self._test_multi_year_simulation()
            
            # Test 5: Memory stress test
            self._test_memory_stress()
            
            # Test 6: API load testing
            asyncio.run(self._test_api_load())
            
        except Exception as e:
            print(f"❌ Load test suite failed: {str(e)}")
            self.results.append(TestResult(
                test_name="load_test_suite",
                success=False,
                execution_time=time.time() - start_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                error_message=str(e)
            ))
        
        total_time = time.time() - start_time
        peak_memory = self.memory_monitor.stop_monitoring()
        
        overall_success = all(r.success for r in self.results)
        
        return LoadTestResults(
            config=self.config,
            test_results=self.results,
            overall_success=overall_success,
            total_execution_time=total_time,
            peak_memory_usage=peak_memory
        )
    
    def _test_basic_engine_performance(self):
        """Test basic engine creation and simple simulation"""
        print("🔧 Testing basic engine performance...")
        
        start_time = time.time()
        try:
            # Create engine
            engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
            
            # Create simple scenario
            scenario = ScenarioRequest(
                scenario_id="basic_perf_test",
                name="Basic Performance Test",
                time_range=TimeRange(2024, 1, 2024, 6),
                office_ids=["test_office"],
                levers=Levers()
            )
            
            # Run simulation
            results = engine.run_simulation(scenario)
            
            execution_time = time.time() - start_time
            
            # Validate results
            assert len(results.all_events) >= 0
            assert len(results.monthly_results) == 6
            
            self.results.append(TestResult(
                test_name="basic_engine_performance",
                success=True,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                additional_metrics={
                    "events_count": len(results.all_events),
                    "months_simulated": len(results.monthly_results)
                }
            ))
            
            print(f"✅ Basic performance test passed in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_name="basic_engine_performance",
                success=False,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                error_message=str(e)
            ))
            print(f"❌ Basic performance test failed: {str(e)}")
    
    def _test_concurrent_simulations(self):
        """Test concurrent simulations"""
        print(f"⚡ Testing {self.config.concurrent_simulations} concurrent simulations...")
        
        start_time = time.time()
        results = {}
        
        def run_simulation(sim_id):
            try:
                engine = SimulationEngineV2Factory.create_test_engine(random_seed=sim_id + 100)
                scenario = ScenarioRequest(
                    scenario_id=f"concurrent_test_{sim_id}",
                    name=f"Concurrent Test {sim_id}",
                    time_range=TimeRange(2024, 1, 2024, 12),
                    office_ids=[f"office_{sim_id}"],
                    levers=Levers(recruitment_multiplier=1.0 + sim_id * 0.1)
                )
                
                sim_results = engine.run_simulation(scenario)
                results[sim_id] = {
                    "success": True,
                    "events": len(sim_results.all_events),
                    "months": len(sim_results.monthly_results)
                }
                
            except Exception as e:
                results[sim_id] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Run concurrent simulations
        threads = []
        for i in range(self.config.concurrent_simulations):
            thread = threading.Thread(target=run_simulation, args=[i])
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        execution_time = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results.values() if r.get("success", False))
        success_rate = successful / len(results) * 100
        
        test_success = success_rate >= 80.0  # Allow 20% failure rate
        
        self.results.append(TestResult(
            test_name="concurrent_simulations",
            success=test_success,
            execution_time=execution_time,
            memory_usage_mb=self.memory_monitor.peak_memory,
            additional_metrics={
                "concurrent_count": self.config.concurrent_simulations,
                "success_rate": success_rate,
                "successful_sims": successful,
                "total_events": sum(r.get("events", 0) for r in results.values() if r.get("success"))
            }
        ))
        
        status = "✅" if test_success else "❌"
        print(f"{status} Concurrent test: {successful}/{len(results)} succeeded ({success_rate:.1f}%)")
    
    def _test_large_workforce_simulation(self):
        """Test simulation with large workforce"""
        print(f"👥 Testing large workforce simulation ({self.config.large_workforce_size} people)...")
        
        start_time = time.time()
        try:
            # Create large population snapshot
            large_snapshot = self._create_large_population_snapshot(self.config.large_workforce_size)
            
            engine = SimulationEngineV2Factory.create_test_engine(random_seed=1000)
            
            # Mock the snapshot loader to return our large population
            with self._mock_snapshot_loader(large_snapshot):
                scenario = ScenarioRequest(
                    scenario_id="large_workforce_test",
                    name="Large Workforce Test",
                    time_range=TimeRange(2024, 1, 2024, 12),
                    office_ids=["large_office"],
                    levers=Levers()
                )
                
                results = engine.run_simulation(scenario)
            
            execution_time = time.time() - start_time
            
            # Validate results
            final_workforce = sum(office.get_total_workforce() for office in results.final_workforce.values())
            
            # Check performance constraints
            performance_ok = (
                execution_time <= self.config.max_execution_time_seconds and
                self.memory_monitor.peak_memory <= self.config.max_memory_mb and
                len(results.all_events) > 0
            )
            
            self.results.append(TestResult(
                test_name="large_workforce_simulation",
                success=performance_ok,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                additional_metrics={
                    "initial_workforce": self.config.large_workforce_size,
                    "final_workforce": final_workforce,
                    "total_events": len(results.all_events),
                    "performance_within_limits": performance_ok
                }
            ))
            
            status = "✅" if performance_ok else "❌"
            print(f"{status} Large workforce test: {final_workforce} final FTE in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_name="large_workforce_simulation",
                success=False,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                error_message=str(e)
            ))
            print(f"❌ Large workforce test failed: {str(e)}")
    
    def _test_multi_year_simulation(self):
        """Test multi-year simulation"""
        print(f"📅 Testing multi-year simulation ({self.config.multi_year_duration} months)...")
        
        start_time = time.time()
        try:
            engine = SimulationEngineV2Factory.create_test_engine(random_seed=2000)
            
            # Calculate years and months
            start_year = 2024
            start_month = 1
            end_year = start_year + (self.config.multi_year_duration // 12)
            end_month = start_month + (self.config.multi_year_duration % 12)
            
            if end_month > 12:
                end_year += 1
                end_month -= 12
            
            scenario = ScenarioRequest(
                scenario_id="multi_year_test",
                name="Multi-Year Test",
                time_range=TimeRange(start_year, start_month, end_year, end_month),
                office_ids=["multi_year_office"],
                levers=Levers(recruitment_multiplier=1.05)  # 5% annual growth
            )
            
            results = engine.run_simulation(scenario)
            
            execution_time = time.time() - start_time
            
            # Validate results
            expected_months = self.config.multi_year_duration
            actual_months = len(results.monthly_results)
            
            months_correct = abs(actual_months - expected_months) <= 1  # Allow 1 month tolerance
            performance_ok = execution_time <= self.config.max_execution_time_seconds * 2  # Allow 2x time for long sims
            
            test_success = months_correct and performance_ok
            
            self.results.append(TestResult(
                test_name="multi_year_simulation",
                success=test_success,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                additional_metrics={
                    "expected_months": expected_months,
                    "actual_months": actual_months,
                    "total_events": len(results.all_events),
                    "performance_within_limits": performance_ok
                }
            ))
            
            status = "✅" if test_success else "❌"
            print(f"{status} Multi-year test: {actual_months}/{expected_months} months in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_name="multi_year_simulation",
                success=False,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                error_message=str(e)
            ))
            print(f"❌ Multi-year test failed: {str(e)}")
    
    def _test_memory_stress(self):
        """Test memory usage under stress"""
        print("🧠 Testing memory usage under stress...")
        
        start_time = time.time()
        try:
            # Run multiple overlapping simulations to stress memory
            engines = []
            scenarios = []
            
            for i in range(3):  # 3 engines for memory stress
                engine = SimulationEngineV2Factory.create_test_engine(random_seed=3000 + i)
                engines.append(engine)
                
                scenario = ScenarioRequest(
                    scenario_id=f"memory_stress_{i}",
                    name=f"Memory Stress Test {i}",
                    time_range=TimeRange(2024, 1, 2024, 24),  # 2 years
                    office_ids=[f"stress_office_{i}"],
                    levers=Levers()
                )
                scenarios.append(scenario)
            
            # Run all scenarios (this should stress memory)
            all_results = []
            for engine, scenario in zip(engines, scenarios):
                results = engine.run_simulation(scenario)
                all_results.append(results)
            
            execution_time = time.time() - start_time
            
            # Check memory usage
            memory_ok = self.memory_monitor.peak_memory <= self.config.max_memory_mb
            
            total_events = sum(len(r.all_events) for r in all_results)
            
            self.results.append(TestResult(
                test_name="memory_stress_test",
                success=memory_ok,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                additional_metrics={
                    "simultaneous_engines": len(engines),
                    "total_events_processed": total_events,
                    "memory_limit_mb": self.config.max_memory_mb,
                    "memory_within_limit": memory_ok
                }
            ))
            
            status = "✅" if memory_ok else "❌"
            print(f"{status} Memory stress test: {self.memory_monitor.peak_memory:.1f}MB peak ({total_events} events)")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_name="memory_stress_test",
                success=False,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                error_message=str(e)
            ))
            print(f"❌ Memory stress test failed: {str(e)}")
    
    async def _test_api_load(self):
        """Test API under load"""
        print("🌐 Testing API under load...")
        
        start_time = time.time()
        
        async def submit_scenario(session, scenario_id):
            scenario_data = {
                "scenario_id": f"api_load_{scenario_id}",
                "name": f"API Load Test {scenario_id}",
                "time_range": {
                    "start_year": 2024,
                    "start_month": 1,
                    "end_year": 2024,
                    "end_month": 6
                },
                "office_ids": [f"api_office_{scenario_id}"]
            }
            
            try:
                async with session.post(
                    f"{self.config.api_base_url}/api/v2/scenarios/run",
                    json=scenario_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return {"success": True, "scenario_id": scenario_id}
                    else:
                        text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {text}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        try:
            # Check if API is available
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.api_base_url}/api/v2/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"API health check failed: {response.status}")
            
            # Submit multiple scenarios concurrently via API
            async with aiohttp.ClientSession() as session:
                tasks = [
                    submit_scenario(session, i) 
                    for i in range(self.config.concurrent_simulations)
                ]
                
                api_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            execution_time = time.time() - start_time
            
            # Analyze API results
            successful_api_calls = sum(
                1 for r in api_results 
                if isinstance(r, dict) and r.get("success", False)
            )
            
            api_success_rate = successful_api_calls / len(api_results) * 100
            api_test_success = api_success_rate >= 80.0
            
            self.results.append(TestResult(
                test_name="api_load_test",
                success=api_test_success,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                additional_metrics={
                    "api_calls_made": len(api_results),
                    "successful_calls": successful_api_calls,
                    "api_success_rate": api_success_rate,
                    "api_endpoint": self.config.api_base_url
                }
            ))
            
            status = "✅" if api_test_success else "❌"
            print(f"{status} API load test: {successful_api_calls}/{len(api_results)} calls succeeded ({api_success_rate:.1f}%)")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_name="api_load_test",
                success=False,
                execution_time=execution_time,
                memory_usage_mb=self.memory_monitor.peak_memory,
                error_message=f"API test failed: {str(e)}"
            ))
            print(f"❌ API load test failed: {str(e)}")
            print("   (Make sure the server is running at http://localhost:8000)")
    
    def _create_large_population_snapshot(self, size: int) -> PopulationSnapshot:
        """Create a large population snapshot for testing"""
        workforce_entries = []
        
        roles = ["Consultant", "Sales", "Recruitment", "Operations"]
        levels = {
            "Consultant": ["A", "AC", "C", "SrC", "M"],
            "Sales": ["A", "AC", "C", "SrC"],
            "Recruitment": ["A", "AC", "C"],
            "Operations": ["Operations"]
        }
        
        for i in range(size):
            role = roles[i % len(roles)]
            level = levels[role][i % len(levels[role])]
            
            # Random hire date in the past
            months_ago = (i % 60) + 1  # 1-60 months ago
            hire_date = date(2024, 1, 1).replace(month=max(1, 1 - (months_ago % 12)))
            
            entry = WorkforceEntry(
                id=f"person_{i:06d}",
                role=role,
                level=level,
                hire_date=hire_date.strftime("%Y-%m"),
                level_start_date=hire_date.strftime("%Y-%m"),
                office="large_office"
            )
            workforce_entries.append(entry)
        
        return PopulationSnapshot(
            id="large_test_snapshot",
            office_id="large_office",
            snapshot_date="2024-01",
            name=f"Large Test Snapshot ({size} people)",
            workforce=workforce_entries
        )
    
    def _mock_snapshot_loader(self, snapshot: PopulationSnapshot):
        """Mock snapshot loader to return test data"""
        from unittest.mock import patch
        
        def mock_load_office_snapshot(office_id, snapshot_id):
            from backend.src.services.snapshot_loader_v2 import SnapshotLoaderV2
            loader = SnapshotLoaderV2()
            return loader.create_initial_people(snapshot.workforce)
        
        return patch(
            'backend.src.services.simulation_engine_v2.SimulationEngineV2._load_office_configuration',
            return_value={
                'name': 'Test Office',
                'current_snapshot_id': 'test_snapshot',
                'business_plan': None,
                'cat_matrix': None,
                'economic_parameters': None
            }
        )


def generate_load_test_report(results: LoadTestResults) -> str:
    """Generate a comprehensive load test report"""
    report = []
    report.append("=" * 80)
    report.append("SIMPLESIM ENGINE V2 - LOAD TEST REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Test configuration
    report.append("📋 TEST CONFIGURATION")
    report.append(f"   Concurrent Simulations: {results.config.concurrent_simulations}")
    report.append(f"   Large Workforce Size: {results.config.large_workforce_size}")
    report.append(f"   Multi-Year Duration: {results.config.multi_year_duration} months")
    report.append(f"   Max Memory Limit: {results.config.max_memory_mb} MB")
    report.append(f"   Max Execution Time: {results.config.max_execution_time_seconds} seconds")
    report.append("")
    
    # Overall results
    status_emoji = "✅" if results.overall_success else "❌"
    report.append("📊 OVERALL RESULTS")
    report.append(f"   Status: {status_emoji} {'PASSED' if results.overall_success else 'FAILED'}")
    report.append(f"   Success Rate: {results.get_success_rate():.1f}%")
    report.append(f"   Total Execution Time: {results.total_execution_time:.2f} seconds")
    report.append(f"   Peak Memory Usage: {results.peak_memory_usage:.1f} MB")
    report.append(f"   Average Test Time: {results.get_average_execution_time():.2f} seconds")
    report.append("")
    
    # Individual test results
    report.append("📝 DETAILED TEST RESULTS")
    for i, test in enumerate(results.test_results, 1):
        status = "✅ PASS" if test.success else "❌ FAIL"
        report.append(f"   {i}. {test.test_name}")
        report.append(f"      Status: {status}")
        report.append(f"      Execution Time: {test.execution_time:.2f}s")
        report.append(f"      Memory Usage: {test.memory_usage_mb:.1f}MB")
        
        if test.error_message:
            report.append(f"      Error: {test.error_message}")
        
        if test.additional_metrics:
            report.append("      Metrics:")
            for key, value in test.additional_metrics.items():
                report.append(f"        - {key}: {value}")
        report.append("")
    
    # Performance analysis
    report.append("📈 PERFORMANCE ANALYSIS")
    successful_tests = [t for t in results.test_results if t.success]
    if successful_tests:
        exec_times = [t.execution_time for t in successful_tests]
        memory_usage = [t.memory_usage_mb for t in successful_tests]
        
        report.append(f"   Execution Time Stats:")
        report.append(f"     - Min: {min(exec_times):.2f}s")
        report.append(f"     - Max: {max(exec_times):.2f}s")
        report.append(f"     - Average: {statistics.mean(exec_times):.2f}s")
        report.append(f"     - Median: {statistics.median(exec_times):.2f}s")
        report.append("")
        
        report.append(f"   Memory Usage Stats:")
        report.append(f"     - Min: {min(memory_usage):.1f}MB")
        report.append(f"     - Max: {max(memory_usage):.1f}MB")
        report.append(f"     - Average: {statistics.mean(memory_usage):.1f}MB")
        report.append(f"     - Peak Overall: {results.peak_memory_usage:.1f}MB")
        report.append("")
    
    # Recommendations
    report.append("💡 RECOMMENDATIONS")
    failed_tests = [t for t in results.test_results if not t.success]
    
    if not failed_tests:
        report.append("   🎉 All tests passed! Engine V2 is performing excellently.")
    else:
        report.append("   ⚠️ Some tests failed. Consider the following actions:")
        for test in failed_tests:
            report.append(f"     - {test.test_name}: {test.error_message or 'Review performance constraints'}")
    
    if results.peak_memory_usage > results.config.max_memory_mb * 0.8:
        report.append("   📊 Memory usage is high - consider optimization")
    
    if results.get_average_execution_time() > results.config.max_execution_time_seconds * 0.5:
        report.append("   ⏱️ Execution times are high - consider performance tuning")
    
    report.append("")
    report.append("=" * 80)
    report.append(f"Report generated at: {datetime.now().isoformat()}")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main load test execution"""
    parser = argparse.ArgumentParser(description="SimpleSim Engine V2 Load Tester")
    parser.add_argument("--concurrent", type=int, default=5, help="Number of concurrent simulations")
    parser.add_argument("--workforce", type=int, default=1000, help="Large workforce size")
    parser.add_argument("--months", type=int, default=36, help="Multi-year simulation duration in months")
    parser.add_argument("--memory-limit", type=float, default=500.0, help="Memory limit in MB")
    parser.add_argument("--time-limit", type=float, default=300.0, help="Time limit in seconds")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--report-file", help="Save report to file")
    
    args = parser.parse_args()
    
    config = LoadTestConfig(
        concurrent_simulations=args.concurrent,
        large_workforce_size=args.workforce,
        multi_year_duration=args.months,
        max_memory_mb=args.memory_limit,
        max_execution_time_seconds=args.time_limit,
        api_base_url=args.api_url
    )
    
    # Run load tests
    tester = V2EngineLoadTester(config)
    results = tester.run_all_tests()
    
    # Generate report
    report = generate_load_test_report(results)
    
    # Print report
    print("\n" + report)
    
    # Save report if requested
    if args.report_file:
        with open(args.report_file, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results.overall_success else 1)


if __name__ == "__main__":
    main()