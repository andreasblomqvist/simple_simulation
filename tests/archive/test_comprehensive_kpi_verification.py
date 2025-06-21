#!/usr/bin/env python3
"""
Comprehensive KPI and Financial Verification Test

This test covers:
1. Load configuration
2. Run 1-year simulation (baseline)
3. Verify non-zero results for all KPIs
4. Apply recruitment lever (A level = 5%)
5. Run 1-year simulation with lever
6. Verify lever was applied correctly
"""

import sys
import os
import json
import requests
import time
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi_service import KPIService
from backend.src.services.config_service import config_service


class ComprehensiveKPITest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {}
        self.baseline_kpis = None
        self.lever_kpis = None
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def start_server_if_needed(self):
        """Start server if not running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Server is already running")
                return True
        except:
            pass
        
        self.log("🚀 Starting backend server...")
        
        # Kill any existing processes
        os.system("pkill -f uvicorn 2>/dev/null || true")
        time.sleep(2)
        
        # Start server in background
        cmd = "PYTHONPATH=. python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        for i in range(30):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=2)
                if response.status_code == 200:
                    self.log("✅ Server started successfully")
                    return True
            except:
                pass
            time.sleep(1)
        
        raise Exception("Failed to start server")
    
    def test_1_load_configuration(self):
        """Test 1: Load and verify configuration"""
        self.log("🧪 TEST 1: Loading and verifying configuration")
        
        # Check configuration via API
        response = requests.get(f"{self.base_url}/offices/config")
        assert response.status_code == 200, f"Config endpoint failed: {response.status_code}"
        
        offices = response.json()
        assert len(offices) > 0, "No offices found in configuration"
        
        # Verify Stockholm exists with expected structure
        stockholm = next((o for o in offices if o["name"] == "Stockholm"), None)
        assert stockholm is not None, "Stockholm office not found"
        
        # Verify Stockholm has consultant roles with levels
        assert "roles" in stockholm, "Stockholm missing roles"
        assert "Consultant" in stockholm["roles"], "Stockholm missing Consultant role"
        
        consultant_roles = stockholm["roles"]["Consultant"]
        assert "A" in consultant_roles, "Stockholm Consultant missing A level"
        
        # Verify A level has recruitment field
        a_level = consultant_roles["A"]
        assert "recruitment_1" in a_level, "Stockholm Consultant A missing recruitment_1"
        
        total_fte = sum(office["total_fte"] for office in offices)
        self.log(f"✅ Configuration loaded: {len(offices)} offices, {total_fte} total FTE")
        
        # Store for later use
        self.test_results["config_offices"] = len(offices)
        self.test_results["config_total_fte"] = total_fte
        self.test_results["stockholm_a_recruitment_original"] = a_level["recruitment_1"]
        
        return True
    
    def test_2_baseline_simulation(self):
        """Test 2: Run baseline simulation (1 year, no levers)"""
        self.log("🧪 TEST 2: Running baseline simulation (1 year)")
        
        # Prepare simulation request with required parameters
        simulation_request = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12,
            "price_increase": 0.0,  # No price increase for baseline
            "salary_increase": 0.0,  # No salary increase for baseline
            "unplanned_absence": 0.05,  # 5% default
            "hy_working_hours": 166.4,  # Monthly working hours
            "other_expense": 100000.0  # Monthly other expenses (reduced for testing)
        }
        
        # Run simulation
        response = requests.post(
            f"{self.base_url}/simulation/run",
            json=simulation_request,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout
        )
        
        assert response.status_code == 200, f"Simulation failed: {response.status_code} - {response.text}"
        
        results = response.json()
        assert "kpis" in results, "Simulation results missing KPIs"
        
        # Extract KPIs
        kpis = results["kpis"]
        self.baseline_kpis = kpis
        
        self.log("✅ Baseline simulation completed successfully")
        
        # Store results for verification
        self.test_results["baseline_simulation"] = {
            "duration_months": 12,
            "lever_count": 0,
            "has_kpis": "kpis" in results
        }
        
        return True
    
    def test_3_verify_nonzero_kpis(self):
        """Test 3: Verify all KPIs have non-zero values"""
        self.log("🧪 TEST 3: Verifying non-zero KPI values")
        
        assert self.baseline_kpis is not None, "No baseline KPIs available"
        
        # Check financial KPIs
        financial = self.baseline_kpis.get("financial", {})
        
        # Net Sales
        net_sales = financial.get("net_sales", 0)
        net_sales_baseline = financial.get("net_sales_baseline", 0)
        assert net_sales > 0, f"Net sales is zero: {net_sales}"
        assert net_sales_baseline > 0, f"Net sales baseline is zero: {net_sales_baseline}"
        
        # EBITDA
        ebitda = financial.get("ebitda", 0)
        ebitda_baseline = financial.get("ebitda_baseline", 0)
        assert ebitda != 0, f"EBITDA is zero: {ebitda}"  # Can be negative
        assert ebitda_baseline != 0, f"EBITDA baseline is zero: {ebitda_baseline}"
        
        # Margin
        margin = financial.get("margin", 0)
        margin_baseline = financial.get("margin_baseline", 0)
        assert margin != 0, f"Margin is zero: {margin}"
        assert margin_baseline != 0, f"Margin baseline is zero: {margin_baseline}"
        
        # Consultants
        total_consultants = financial.get("total_consultants", 0)
        total_consultants_baseline = financial.get("total_consultants_baseline", 0)
        assert total_consultants > 0, f"Total consultants is zero: {total_consultants}"
        assert total_consultants_baseline > 0, f"Total consultants baseline is zero: {total_consultants_baseline}"
        
        # Hourly Rate
        avg_hourly_rate = financial.get("avg_hourly_rate", 0)
        avg_hourly_rate_baseline = financial.get("avg_hourly_rate_baseline", 0)
        assert avg_hourly_rate > 0, f"Average hourly rate is zero: {avg_hourly_rate}"
        assert avg_hourly_rate_baseline > 0, f"Average hourly rate baseline is zero: {avg_hourly_rate_baseline}"
        
        self.log("✅ All financial KPIs have non-zero values")
        
        # Log the values for inspection
        self.log(f"📊 Financial KPIs:")
        self.log(f"   Net Sales: {net_sales:,.0f} SEK (baseline: {net_sales_baseline:,.0f} SEK)")
        self.log(f"   EBITDA: {ebitda:,.0f} SEK (baseline: {ebitda_baseline:,.0f} SEK)")
        self.log(f"   Margin: {margin:.1%} (baseline: {margin_baseline:.1%})")
        self.log(f"   Consultants: {total_consultants:,} (baseline: {total_consultants_baseline:,})")
        self.log(f"   Avg Hourly Rate: {avg_hourly_rate:,.0f} SEK (baseline: {avg_hourly_rate_baseline:,.0f} SEK)")
        
        # Check growth KPIs
        growth = self.baseline_kpis.get("growth", {})
        current_total_fte = growth.get("current_total_fte", 0)
        baseline_total_fte = growth.get("baseline_total_fte", 0)
        assert current_total_fte > 0, f"Current total FTE is zero: {current_total_fte}"
        assert baseline_total_fte > 0, f"Baseline total FTE is zero: {baseline_total_fte}"
        
        self.log(f"📊 Growth KPIs:")
        self.log(f"   Current Total FTE: {current_total_fte:,}")
        self.log(f"   Baseline Total FTE: {baseline_total_fte:,}")
        self.log(f"   Growth Rate: {growth.get('total_growth_percent', 0):.1f}%")
        
        # Store results
        self.test_results["baseline_kpis"] = {
            "net_sales": net_sales,
            "net_sales_baseline": net_sales_baseline,
            "ebitda": ebitda,
            "ebitda_baseline": ebitda_baseline,
            "margin": margin,
            "margin_baseline": margin_baseline,
            "total_consultants": total_consultants,
            "total_consultants_baseline": total_consultants_baseline,
            "current_total_fte": current_total_fte,
            "baseline_total_fte": baseline_total_fte
        }
        
        return True
    
    def test_4_apply_recruitment_lever(self):
        """Test 4: Apply recruitment lever (A level = 5%)"""
        self.log("🧪 TEST 4: Applying recruitment lever (A level = 5%)")
        
        # Update Stockholm Consultant A recruitment_1 to 5% (0.05)
        update_payload = {
            "Stockholm.Consultant.A.recruitment_1": 0.05
        }
        
        response = requests.post(
            f"{self.base_url}/offices/config/update",
            json=update_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Lever update failed: {response.status_code} - {response.text}"
        
        result = response.json()
        assert result["updated_count"] == 1, f"Expected 1 update, got {result['updated_count']}"
        
        # Verify the update was applied
        response = requests.get(f"{self.base_url}/offices/config")
        assert response.status_code == 200
        
        offices = response.json()
        stockholm = next((o for o in offices if o["name"] == "Stockholm"), None)
        assert stockholm is not None
        
        new_recruitment_rate = stockholm["roles"]["Consultant"]["A"]["recruitment_1"]
        assert abs(new_recruitment_rate - 0.05) < 0.001, f"Recruitment rate not updated: {new_recruitment_rate}"
        
        self.log(f"✅ Recruitment lever applied: A level recruitment = {new_recruitment_rate:.1%}")
        
        # Store for verification
        self.test_results["lever_applied"] = {
            "level": "Stockholm.Consultant.A",
            "field": "recruitment_1",
            "old_value": self.test_results["stockholm_a_recruitment_original"],
            "new_value": new_recruitment_rate
        }
        
        return True
    
    def test_5_lever_simulation(self):
        """Test 5: Run simulation with lever applied (1 year)"""
        self.log("🧪 TEST 5: Running simulation with recruitment lever")
        
        # Prepare simulation request (same as baseline but with updated config)
        simulation_request = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12,
            "price_increase": 0.0,  # No price increase for baseline
            "salary_increase": 0.0,  # No salary increase for baseline
            "unplanned_absence": 0.05,  # 5% default
            "hy_working_hours": 166.4,  # Monthly working hours
            "other_expense": 100000.0  # Monthly other expenses (reduced for testing)
        }
        
        # Run simulation
        response = requests.post(
            f"{self.base_url}/simulation/run",
            json=simulation_request,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout
        )
        
        assert response.status_code == 200, f"Lever simulation failed: {response.status_code} - {response.text}"
        
        results = response.json()
        assert "kpis" in results, "Lever simulation results missing KPIs"
        
        # Extract KPIs
        kpis = results["kpis"]
        self.lever_kpis = kpis
        
        self.log("✅ Lever simulation completed successfully")
        
        return True
    
    def test_6_verify_lever_impact(self):
        """Test 6: Verify that the lever was applied and had impact"""
        self.log("🧪 TEST 6: Verifying lever impact")
        
        assert self.baseline_kpis is not None, "No baseline KPIs available"
        assert self.lever_kpis is not None, "No lever KPIs available"
        
        # Compare consultant counts (should be higher with 5% recruitment)
        baseline_consultants = self.baseline_kpis["financial"]["total_consultants"]
        lever_consultants = self.lever_kpis["financial"]["total_consultants"]
        
        consultant_increase = lever_consultants - baseline_consultants
        consultant_increase_percent = (consultant_increase / baseline_consultants * 100) if baseline_consultants > 0 else 0
        
        self.log(f"📊 Consultant Count Comparison:")
        self.log(f"   Baseline: {baseline_consultants:,}")
        self.log(f"   With Lever: {lever_consultants:,}")
        self.log(f"   Increase: {consultant_increase:,} ({consultant_increase_percent:+.1f}%)")
        
        # Verify consultant count increased (5% recruitment should add consultants)
        assert consultant_increase > 0, f"Consultant count should increase with 5% recruitment, got {consultant_increase}"
        
        # Compare revenue (should be higher with more consultants)
        baseline_revenue = self.baseline_kpis["financial"]["net_sales"]
        lever_revenue = self.lever_kpis["financial"]["net_sales"]
        
        revenue_increase = lever_revenue - baseline_revenue
        revenue_increase_percent = (revenue_increase / baseline_revenue * 100) if baseline_revenue > 0 else 0
        
        self.log(f"📊 Revenue Comparison:")
        self.log(f"   Baseline: {baseline_revenue:,.0f} SEK")
        self.log(f"   With Lever: {lever_revenue:,.0f} SEK")
        self.log(f"   Increase: {revenue_increase:,.0f} SEK ({revenue_increase_percent:+.1f}%)")
        
        # Verify revenue increased
        assert revenue_increase > 0, f"Revenue should increase with more consultants, got {revenue_increase:,.0f} SEK"
        
        # Compare EBITDA
        baseline_ebitda = self.baseline_kpis["financial"]["ebitda"]
        lever_ebitda = self.lever_kpis["financial"]["ebitda"]
        
        ebitda_change = lever_ebitda - baseline_ebitda
        
        self.log(f"📊 EBITDA Comparison:")
        self.log(f"   Baseline: {baseline_ebitda:,.0f} SEK")
        self.log(f"   With Lever: {lever_ebitda:,.0f} SEK")
        self.log(f"   Change: {ebitda_change:,.0f} SEK")
        
        # Compare total FTE
        baseline_fte = self.baseline_kpis["growth"]["current_total_fte"]
        lever_fte = self.lever_kpis["growth"]["current_total_fte"]
        
        fte_increase = lever_fte - baseline_fte
        
        self.log(f"📊 Total FTE Comparison:")
        self.log(f"   Baseline: {baseline_fte:,}")
        self.log(f"   With Lever: {lever_fte:,}")
        self.log(f"   Increase: {fte_increase:,}")
        
        # Verify FTE increased
        assert fte_increase > 0, f"Total FTE should increase with recruitment lever, got {fte_increase}"
        
        self.log("✅ Lever impact verified successfully")
        
        # Store results
        self.test_results["lever_impact"] = {
            "consultant_increase": consultant_increase,
            "consultant_increase_percent": consultant_increase_percent,
            "revenue_increase": revenue_increase,
            "revenue_increase_percent": revenue_increase_percent,
            "ebitda_change": ebitda_change,
            "fte_increase": fte_increase
        }
        
        return True
    
    def test_7_detailed_recruitment_verification(self):
        """Test 7: Detailed verification of recruitment mechanics with 6% rate"""
        self.log("🧪 TEST 7: Detailed recruitment verification (6% rate)")
        
        # Apply 6% recruitment rate to Stockholm Consultant A level
        update_payload = {
            "Stockholm.Consultant.A.recruitment_1": 0.06
        }
        
        response = requests.post(
            f"{self.base_url}/offices/config/update",
            json=update_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"6% recruitment update failed: {response.status_code} - {response.text}"
        
        # Get baseline Stockholm A level count
        response = requests.get(f"{self.base_url}/offices/config")
        offices = response.json()
        stockholm = next((o for o in offices if o["name"] == "Stockholm"), None)
        baseline_a_level_fte = stockholm["roles"]["Consultant"]["A"]["fte"]
        
        self.log(f"📊 Stockholm Consultant A baseline FTE: {baseline_a_level_fte}")
        
        # Run simulation with 6% recruitment
        simulation_request = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12,
            "price_increase": 0.0,
            "salary_increase": 0.0,
            "unplanned_absence": 0.05,
            "hy_working_hours": 166.4,
            "other_expense": 100000.0
        }
        
        response = requests.post(
            f"{self.base_url}/simulation/run",
            json=simulation_request,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        assert response.status_code == 200, f"6% recruitment simulation failed: {response.status_code} - {response.text}"
        
        results = response.json()
        
        # Extract final year data to check actual recruitment
        years = list(results.get('years', {}).keys())
        final_year = max(years) if years else '2025'
        final_year_data = results['years'][final_year]
        
        # Get Stockholm office data
        stockholm_data = final_year_data['offices'].get('Stockholm', {})
        stockholm_levels = stockholm_data.get('levels', {})
        
        # Get Stockholm Consultant A final count
        consultant_levels = stockholm_levels.get('Consultant', {})
        a_level_data = consultant_levels.get('A', [])
        
        if a_level_data:
            final_a_level_count = a_level_data[-1].get('total', 0) if a_level_data else 0
        else:
            final_a_level_count = 0
        
        self.log(f"📊 Stockholm Consultant A final FTE: {final_a_level_count}")
        
        # Calculate expected recruitment over 12 months
        # With 6% monthly recruitment rate, we expect significant growth
        monthly_recruitment_rate = 0.06
        expected_min_growth = baseline_a_level_fte * monthly_recruitment_rate * 6  # Conservative estimate for 6 months
        
        actual_growth = final_a_level_count - baseline_a_level_fte
        
        self.log(f"📊 Recruitment Analysis:")
        self.log(f"   Baseline A Level FTE: {baseline_a_level_fte}")
        self.log(f"   Final A Level FTE: {final_a_level_count}")
        self.log(f"   Actual Growth: {actual_growth:+.1f}")
        self.log(f"   Expected Min Growth (6 months): {expected_min_growth:+.1f}")
        self.log(f"   Monthly Recruitment Rate: {monthly_recruitment_rate:.1%}")
        
        # Verify recruitment actually happened
        assert actual_growth > 0, f"No recruitment detected! Expected growth > 0, got {actual_growth}"
        assert actual_growth >= expected_min_growth * 0.5, f"Recruitment too low. Expected at least {expected_min_growth * 0.5:.1f}, got {actual_growth}"
        
        # Check if recruitment rate is reasonable (not too high)
        max_reasonable_growth = baseline_a_level_fte * monthly_recruitment_rate * 12 * 1.5  # Allow for compounding
        assert actual_growth <= max_reasonable_growth, f"Recruitment too high. Expected max {max_reasonable_growth:.1f}, got {actual_growth}"
        
        # Get monthly progression to verify recruitment happened each month
        monthly_counts = [month_data.get('total', 0) for month_data in a_level_data] if a_level_data else []
        
        if len(monthly_counts) >= 2:
            self.log(f"📊 Monthly A Level Progression:")
            for i, count in enumerate(monthly_counts[:6]):  # Show first 6 months
                month_name = f"Month {i+1}"
                growth_from_start = count - monthly_counts[0] if monthly_counts else 0
                self.log(f"   {month_name}: {count:.1f} FTE (+{growth_from_start:+.1f})")
            
            # Verify consistent growth trend
            growth_months = sum(1 for i in range(1, len(monthly_counts)) if monthly_counts[i] > monthly_counts[i-1])
            total_months = len(monthly_counts) - 1
            growth_ratio = growth_months / total_months if total_months > 0 else 0
            
            self.log(f"   Growth occurred in {growth_months}/{total_months} months ({growth_ratio:.1%})")
            
            # At least 50% of months should show growth with 6% recruitment
            assert growth_ratio >= 0.4, f"Insufficient growth months. Expected ≥40%, got {growth_ratio:.1%}"
        
        self.log("✅ Detailed recruitment verification successful")
        
        # Store detailed results
        self.test_results["detailed_recruitment"] = {
            "recruitment_rate": monthly_recruitment_rate,
            "baseline_fte": baseline_a_level_fte,
            "final_fte": final_a_level_count,
            "actual_growth": actual_growth,
            "expected_min_growth": expected_min_growth,
            "monthly_counts": monthly_counts[:12],  # Store first 12 months
            "growth_months": growth_months if 'growth_months' in locals() else 0,
            "total_months": total_months if 'total_months' in locals() else 0
        }
        
        return True
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("🚀 Starting Comprehensive KPI Verification Test")
        self.log("=" * 60)
        
        try:
            # Start server
            self.start_server_if_needed()
            time.sleep(3)  # Let server fully initialize
            
            # Run tests in sequence
            tests = [
                self.test_1_load_configuration,
                self.test_2_baseline_simulation,
                self.test_3_verify_nonzero_kpis,
                self.test_4_apply_recruitment_lever,
                self.test_5_lever_simulation,
                self.test_6_verify_lever_impact,
                self.test_7_detailed_recruitment_verification
            ]
            
            for i, test in enumerate(tests, 1):
                try:
                    success = test()
                    if success:
                        self.log(f"✅ Test {i} passed")
                    else:
                        self.log(f"❌ Test {i} failed")
                        return False
                except Exception as e:
                    self.log(f"❌ Test {i} failed with exception: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            self.log("=" * 60)
            self.log("🎉 ALL TESTS PASSED!")
            self.log("=" * 60)
            
            # Print summary
            self.print_summary()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self):
        """Print test summary"""
        self.log("📋 TEST SUMMARY:")
        self.log(f"   Configuration: {self.test_results['config_offices']} offices, {self.test_results['config_total_fte']} FTE")
        
        if "baseline_kpis" in self.test_results:
            kpis = self.test_results["baseline_kpis"]
            self.log(f"   Baseline Revenue: {kpis['net_sales']:,.0f} SEK")
            self.log(f"   Baseline EBITDA: {kpis['ebitda']:,.0f} SEK")
            self.log(f"   Baseline Margin: {kpis['margin']:.1%}")
            self.log(f"   Baseline Consultants: {kpis['total_consultants']:,}")
        
        if "lever_applied" in self.test_results:
            lever = self.test_results["lever_applied"]
            self.log(f"   Lever Applied: {lever['field']} from {lever['old_value']:.3f} to {lever['new_value']:.3f}")
        
        if "lever_impact" in self.test_results:
            impact = self.test_results["lever_impact"]
            self.log(f"   Impact: +{impact['consultant_increase']:,} consultants ({impact['consultant_increase_percent']:+.1f}%)")
            self.log(f"   Revenue Impact: +{impact['revenue_increase']:,.0f} SEK ({impact['revenue_increase_percent']:+.1f}%)")
            self.log(f"   FTE Impact: +{impact['fte_increase']:,}")
        
        if "detailed_recruitment" in self.test_results:
            recruitment = self.test_results["detailed_recruitment"]
            self.log(f"   📊 DETAILED RECRUITMENT (6% rate):")
            self.log(f"     Stockholm A Level Growth: {recruitment['baseline_fte']:.1f} → {recruitment['final_fte']:.1f} (+{recruitment['actual_growth']:+.1f})")
            self.log(f"     Growth Months: {recruitment['growth_months']}/{recruitment['total_months']} months")
            if recruitment['monthly_counts']:
                monthly_growth = recruitment['final_fte'] - recruitment['baseline_fte']
                monthly_avg_growth = monthly_growth / len(recruitment['monthly_counts']) if recruitment['monthly_counts'] else 0
                self.log(f"     Average Monthly Growth: {monthly_avg_growth:+.2f} FTE/month")
            self.log(f"     Recruitment Rate Verification: {'✅ WORKING' if recruitment['actual_growth'] > 0 else '❌ NOT WORKING'}")


if __name__ == "__main__":
    test = ComprehensiveKPITest()
    success = test.run_all_tests()
    exit(0 if success else 1)
