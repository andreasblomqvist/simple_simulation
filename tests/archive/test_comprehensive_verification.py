#!/usr/bin/env python3
"""
Comprehensive verification test for SimpleSim calculations
Validates mathematical accuracy of all core calculations
"""

import requests
import json
import math

def test_health_check():
    """Test if backend is running and healthy"""
    print("🏥 Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend healthy - {data.get('total_offices', 0)} offices, {data.get('total_fte', 0)} FTE")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_offices_endpoint():
    """Test if offices data loads correctly"""
    print("\n🏢 Testing offices endpoint...")
    try:
        response = requests.get("http://localhost:8000/offices", timeout=10)
        if response.status_code == 200:
            offices = response.json()
            print(f"✅ Loaded {len(offices)} offices successfully")
            
            # Verify we have expected offices
            office_names = [office['name'] for office in offices]
            expected_offices = ['Stockholm', 'Oslo', 'Copenhagen', 'Helsinki', 'Berlin', 'Hamburg', 'Munich', 'Zurich', 'Frankfurt', 'Amsterdam', 'Cologne', 'Toronto']
            
            missing_offices = set(expected_offices) - set(office_names)
            if missing_offices:
                print(f"⚠️ Missing offices: {missing_offices}")
            else:
                print("✅ All expected offices present")
            
            return True
        else:
            print(f"❌ Offices endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Offices endpoint error: {e}")
        return False

def test_basic_simulation():
    """Test basic simulation with realistic parameters"""
    print("\n🎯 Testing basic simulation...")
    
    params = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2025,
        "end_month": 12,
        "price_increase": 0.02,  # 2% yearly
        "salary_increase": 0.02,  # 2% yearly
        "hy_working_hours": 166.4,
        "unplanned_absence": 0.05,
        "other_expense": 20000000,  # 20M SEK monthly
        "office_overrides": {}
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=params,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Basic simulation completed")
            
            # Check for reasonable financial values
            if 'kpis' in results and 'financial' in results['kpis']:
                financial = results['kpis']['financial']
                net_sales = financial.get('current_net_sales', 0)
                ebitda = financial.get('current_ebitda', 0)
                margin = financial.get('current_margin', 0)
                
                print(f"   💰 Net Sales: {net_sales/1e9:.2f}B SEK")
                print(f"   💰 EBITDA: {ebitda/1e9:.2f}B SEK")
                print(f"   💰 Margin: {margin:.1f}%")
                
                # Reasonable bounds check
                if 1e9 <= net_sales <= 10e9 and 0.5e9 <= ebitda <= 5e9 and 20 <= margin <= 70:
                    print("   ✅ Financial values within reasonable bounds")
                    return True
                else:
                    print("   ❌ Financial values outside reasonable bounds")
                    return False
            else:
                print("   ❌ No financial KPIs found")
                return False
        else:
            print(f"❌ Basic simulation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic simulation error: {e}")
        return False

def test_fte_movement_calculations():
    """Test that FTE movements (recruitment, churn, progression) are calculated correctly"""
    print("\n👥 Testing FTE movement calculations...")
    
    # Get baseline data first
    try:
        baseline_response = requests.get("http://localhost:8000/offices/config", timeout=10)
        if baseline_response.status_code != 200:
            print("❌ Failed to get baseline data")
            return False
        
        baseline_offices = baseline_response.json()
        
        # Calculate expected movements for Stockholm office as example
        stockholm = next((office for office in baseline_offices if office['name'] == 'Stockholm'), None)
        if not stockholm:
            print("❌ Stockholm office not found")
            return False
        
        print(f"📊 Analyzing Stockholm office movements...")
        
        # Get Stockholm's baseline FTE by role using the actual data structure
        baseline_fte = {}
        total_baseline_fte = 0
        
        for role_name, role_data in stockholm['roles'].items():
            if isinstance(role_data, dict):
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict) and 'total' in level_data:
                        key = f"{role_name}_{level_name}"
                        fte = level_data.get('total', 0)
                        baseline_fte[key] = fte
                        total_baseline_fte += fte
                        if fte > 0:  # Only show non-zero levels
                            print(f"   Baseline {key}: {fte} FTE")
        
        print(f"   Total Baseline FTE: {total_baseline_fte}")
        
        # Run 1-month simulation to verify movements
        params = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1,  # Just 1 month
            "price_increase": 0.0,
            "salary_increase": 0.0,
            "hy_working_hours": 166.4,
            "unplanned_absence": 0.0,
            "other_expense": 0,
            "office_overrides": {}
        }
        
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=params,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Simulation failed: {response.status_code}")
            return False
        
        results = response.json()
        
        # Get final FTE after 1 month - using correct structure
        if 'years' not in results or '2025' not in results['years']:
            print("❌ No 2025 results found")
            return False
        
        offices_dict = results['years']['2025']['offices']
        if 'Stockholm' not in offices_dict:
            print("❌ Stockholm final data not found")
            return False
        
        stockholm_final = offices_dict['Stockholm']
        
        # Calculate actual final FTE using the correct simulation results structure
        final_fte = {}
        total_final_fte = 0
        
        if 'levels' in stockholm_final:
            for role_name, role_data in stockholm_final['levels'].items():
                if isinstance(role_data, dict):
                    for level_name, level_list in role_data.items():
                        if isinstance(level_list, list) and len(level_list) > 0:
                            level_data = level_list[0]  # Get first (and only) element
                            key = f"{role_name}_{level_name}"
                            fte = level_data.get('total', 0)
                            final_fte[key] = fte
                            total_final_fte += fte
        
        print(f"   Total Final FTE: {total_final_fte}")
        print(f"   Net Change: {total_final_fte - total_baseline_fte:+.1f} FTE")
        
        # Verify movement calculations for key levels
        verification_passed = True
        
        # Check Consultant A (should have recruitment)
        if 'Consultant_A' in baseline_fte and 'Consultant_A' in final_fte:
            baseline_a = baseline_fte['Consultant_A']
            final_a = final_fte['Consultant_A']
            
            # Get recruitment and churn rates from config
            consultant_a_config = stockholm['roles']['Consultant']['A']
            recruitment_rate = consultant_a_config.get('recruitment_1', 0)  # First month rate
            churn_rate = consultant_a_config.get('churn_1', 0)  # First month rate
            
            expected_recruitment = baseline_a * recruitment_rate
            expected_churn = baseline_a * churn_rate
            expected_net_change = expected_recruitment - expected_churn
            
            actual_change = final_a - baseline_a
            
            # Get actual movement data from simulation
            if 'levels' in stockholm_final and 'Consultant' in stockholm_final['levels'] and 'A' in stockholm_final['levels']['Consultant']:
                movement_data = stockholm_final['levels']['Consultant']['A'][0]
                actual_recruited = movement_data.get('recruited', 0)
                actual_churned = movement_data.get('churned', 0)
                actual_progressed_out = movement_data.get('progressed_out', 0)
                actual_progressed_in = movement_data.get('progressed_in', 0)
                
                print(f"   Consultant A: {baseline_a} → {final_a} (change: {actual_change:+.1f})")
                print(f"   Config rates - Recruitment: {recruitment_rate*100:.1f}%, Churn: {churn_rate*100:.1f}%")
                print(f"   Expected recruitment: {expected_recruitment:.1f}, churn: {expected_churn:.1f}")
                print(f"   Actual movements - Recruited: {actual_recruited}, Churned: {actual_churned}, Prog Out: {actual_progressed_out}, Prog In: {actual_progressed_in}")
                
                # Verify the math: final = baseline + recruited - churned - progressed_out + progressed_in
                expected_final = baseline_a + actual_recruited - actual_churned - actual_progressed_out + actual_progressed_in
                if abs(final_a - expected_final) <= 1:
                    print("   ✅ Consultant A movement math correct")
                else:
                    print(f"   ❌ Consultant A movement math incorrect: expected {expected_final}, got {final_a}")
                    verification_passed = False
        
        # Verify total FTE growth is reasonable
        if total_baseline_fte > 0:
            growth_rate = (total_final_fte - total_baseline_fte) / total_baseline_fte * 100
            print(f"   Monthly Growth Rate: {growth_rate:.2f}%")
            
            # Should be positive but reasonable (less than 10% per month)
            if -2 <= growth_rate <= 10:
                print("   ✅ Overall growth rate reasonable")
            else:
                print("   ⚠️ Overall growth rate seems unreasonable")
                verification_passed = False
        else:
            print("   ⚠️ No baseline FTE found")
            verification_passed = False
        
        return verification_passed
        
    except Exception as e:
        print(f"❌ FTE movement calculation error: {e}")
        return False

def test_revenue_calculations():
    """Test that revenue calculations are mathematically correct"""
    print("\n💰 Testing revenue calculations...")
    
    try:
        # Run simple simulation with known parameters
        params = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1,  # Just 1 month
            "price_increase": 0.0,  # No price increase
            "salary_increase": 0.0,  # No salary increase
            "hy_working_hours": 166.4,  # Standard working hours
            "unplanned_absence": 0.0,  # No absence for simplicity
            "other_expense": 0,  # No other expenses
            "office_overrides": {}
        }
        
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=params,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Revenue test simulation failed: {response.status_code}")
            return False
        
        results = response.json()
        
        # Get baseline data for manual calculation
        baseline_response = requests.get("http://localhost:8000/offices/config", timeout=10)
        if baseline_response.status_code != 200:
            print("❌ Failed to get baseline data")
            return False
        
        baseline_offices = baseline_response.json()
        
        # Calculate expected revenue manually for Stockholm
        stockholm = next((office for office in baseline_offices if office['name'] == 'Stockholm'), None)
        if not stockholm:
            print("❌ Stockholm office not found")
            return False
        
        print("📊 Manual revenue calculation for Stockholm:")
        
        expected_revenue = 0
        utr = 0.85  # 85% utilization rate
        working_hours = 166.4
        
        for role_name, role_data in stockholm['roles'].items():
            if isinstance(role_data, dict):
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict) and 'total' in level_data:
                        fte = level_data.get('total', 0)
                        price = level_data.get('price_1', 0)  # First month price
                        
                        if fte > 0 and price > 0:
                            level_revenue = fte * price * working_hours * utr
                            expected_revenue += level_revenue
                            print(f"   {role_name} {level_name}: {fte} FTE × {price:.2f} SEK/hr × {working_hours} hrs × {utr} UTR = {level_revenue:,.0f} SEK")
        
        print(f"   Expected Stockholm Revenue: {expected_revenue:,.0f} SEK")
        
        # Get actual revenue from simulation using correct structure
        offices_dict = results['years']['2025']['offices']
        if 'Stockholm' in offices_dict and 'metrics' in offices_dict['Stockholm'] and len(offices_dict['Stockholm']['metrics']) > 0:
            actual_revenue = offices_dict['Stockholm']['metrics'][0]['revenue']
            print(f"   Actual Stockholm Revenue: {actual_revenue:,.0f} SEK")
            
            # Check if they match (within 5% tolerance for rounding and simulation effects)
            if expected_revenue > 0 and abs(actual_revenue - expected_revenue) / expected_revenue <= 0.05:
                print("   ✅ Stockholm revenue calculation correct")
            else:
                print(f"   ❌ Stockholm revenue mismatch: {abs(actual_revenue - expected_revenue):,.0f} SEK difference")
                if expected_revenue > 0:
                    print(f"   Difference: {abs(actual_revenue - expected_revenue) / expected_revenue * 100:.1f}%")
                return False
        else:
            print("   ❌ Stockholm actual revenue not found")
            return False
        
        # Verify total revenue calculation
        total_expected = 0
        for office in baseline_offices:
            office_revenue = 0
            for role_name, role_data in office['roles'].items():
                if isinstance(role_data, dict):
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict) and 'total' in level_data:
                            fte = level_data.get('total', 0)
                            price = level_data.get('price_1', 0)
                            if fte > 0 and price > 0:
                                office_revenue += fte * price * working_hours * utr
            total_expected += office_revenue
        
        # Get actual total from KPIs
        if 'kpis' in results and 'financial' in results['kpis']:
            actual_total = results['kpis']['financial'].get('current_net_sales', 0)
            print(f"📊 Total Revenue - Expected: {total_expected:,.0f} SEK, Actual: {actual_total:,.0f} SEK")
            
            if total_expected > 0 and abs(actual_total - total_expected) / total_expected <= 0.05:
                print("✅ Total revenue calculation correct")
                return True
            else:
                print(f"❌ Total revenue mismatch: {abs(actual_total - total_expected):,.0f} SEK difference")
                if total_expected > 0:
                    print(f"   Difference: {abs(actual_total - total_expected) / total_expected * 100:.1f}%")
                return False
        else:
            print("❌ Total revenue KPI not found")
            return False
        
    except Exception as e:
        print(f"❌ Revenue calculation error: {e}")
        return False

def test_salary_cost_calculations():
    """Test that salary cost calculations are mathematically correct"""
    print("\n💸 Testing salary cost calculations...")
    
    try:
        # Run simple simulation
        params = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1,  # Just 1 month
            "price_increase": 0.0,
            "salary_increase": 0.0,
            "hy_working_hours": 166.4,
            "unplanned_absence": 0.0,
            "other_expense": 0,
            "office_overrides": {}
        }
        
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=params,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Salary test simulation failed: {response.status_code}")
            return False
        
        results = response.json()
        
        # Get baseline data
        baseline_response = requests.get("http://localhost:8000/offices/config", timeout=10)
        if baseline_response.status_code != 200:
            print("❌ Failed to get baseline data")
            return False
        
        baseline_offices = baseline_response.json()
        
        # Calculate expected salary costs manually
        print("📊 Manual salary cost calculation:")
        
        total_expected_salary = 0
        
        for office in baseline_offices:
            office_salary = 0
            print(f"   {office['name']}:")
            
            for role_name, role_data in office['roles'].items():
                if isinstance(role_data, dict):
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict) and 'total' in level_data:
                            fte = level_data.get('total', 0)
                            salary = level_data.get('salary_1', 0)  # First month salary
                            
                            if fte > 0 and salary > 0:
                                level_salary_cost = fte * salary
                                office_salary += level_salary_cost
                                if fte >= 5:  # Only show significant levels
                                    print(f"      {role_name} {level_name}: {fte} FTE × {salary:,.0f} SEK/month = {level_salary_cost:,.0f} SEK")
            
            total_expected_salary += office_salary
            if office_salary > 0:
                print(f"      Office Total: {office_salary:,.0f} SEK")
        
        print(f"   Expected Total Salary Cost: {total_expected_salary:,.0f} SEK")
        
        # Get actual salary costs from simulation using correct structure
        total_actual_salary = 0
        offices_dict = results['years']['2025']['offices']
        
        for office_name, office_data in offices_dict.items():
            if 'metrics' in office_data and len(office_data['metrics']) > 0:
                office_costs = office_data['metrics'][0]['costs']
                total_actual_salary += office_costs
                if office_costs > 1000000:  # Show offices with significant costs
                    print(f"      {office_name} actual costs: {office_costs:,.0f} SEK")
        
        print(f"   Actual Total Salary Cost: {total_actual_salary:,.0f} SEK")
        
        # Check if they match (within 5% tolerance)
        if total_expected_salary > 0 and abs(total_actual_salary - total_expected_salary) / total_expected_salary <= 0.05:
            print("✅ Salary cost calculation correct")
            return True
        else:
            print(f"❌ Salary cost mismatch: {abs(total_actual_salary - total_expected_salary):,.0f} SEK difference")
            if total_expected_salary > 0:
                print(f"   Difference: {abs(total_actual_salary - total_expected_salary) / total_expected_salary * 100:.1f}%")
            return False
        
    except Exception as e:
        print(f"❌ Salary cost calculation error: {e}")
        return False

def test_ebitda_calculations():
    """Test that EBITDA calculations are mathematically correct"""
    print("\n📊 Testing EBITDA calculations...")
    
    try:
        # Run simulation with other expenses
        params = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1,  # Just 1 month
            "price_increase": 0.0,
            "salary_increase": 0.0,
            "hy_working_hours": 166.4,
            "unplanned_absence": 0.0,
            "other_expense": 20000000,  # 20M SEK monthly
            "office_overrides": {}
        }
        
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=params,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ EBITDA test simulation failed: {response.status_code}")
            return False
        
        results = response.json()
        
        if 'kpis' not in results or 'financial' not in results['kpis']:
            print("❌ Financial KPIs not found")
            return False
        
        financial = results['kpis']['financial']
        
        # Get components
        revenue = financial.get('current_net_sales', 0)
        salary_costs = 0
        other_expenses = 20000000  # We set this
        
        # Calculate total salary costs using correct structure
        offices_dict = results['years']['2025']['offices']
        for office_name, office_data in offices_dict.items():
            if 'metrics' in office_data and len(office_data['metrics']) > 0:
                salary_costs += office_data['metrics'][0]['costs']
        
        # Calculate expected EBITDA
        expected_ebitda = revenue - salary_costs - other_expenses
        actual_ebitda = financial.get('current_ebitda', 0)
        
        print(f"📊 EBITDA Calculation:")
        print(f"   Revenue: {revenue:,.0f} SEK")
        print(f"   Salary Costs: {salary_costs:,.0f} SEK")
        print(f"   Other Expenses: {other_expenses:,.0f} SEK")
        print(f"   Expected EBITDA: {expected_ebitda:,.0f} SEK")
        print(f"   Actual EBITDA: {actual_ebitda:,.0f} SEK")
        
        # Check if they match (within 1% tolerance)
        if abs(actual_ebitda - expected_ebitda) / abs(expected_ebitda) <= 0.01:
            print("✅ EBITDA calculation correct")
            
            # Also verify margin calculation
            expected_margin = (expected_ebitda / revenue) * 100
            actual_margin = financial.get('current_margin', 0)
            
            print(f"   Expected Margin: {expected_margin:.2f}%")
            print(f"   Actual Margin: {actual_margin:.2f}%")
            
            if abs(actual_margin - expected_margin) <= 0.1:
                print("✅ Margin calculation correct")
                return True
            else:
                print("❌ Margin calculation incorrect")
                return False
        else:
            print(f"❌ EBITDA mismatch: {abs(actual_ebitda - expected_ebitda):,.0f} SEK difference")
            return False
        
    except Exception as e:
        print(f"❌ EBITDA calculation error: {e}")
        return False

def test_price_increase_logic():
    """Test that price increases are applied correctly (yearly, not monthly)"""
    print("\n📈 Testing price increase logic...")
    
    # Test with 10% yearly price increase over 2 years
    params = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2026,
        "end_month": 12,
        "price_increase": 0.10,  # 10% yearly
        "salary_increase": 0.0,  # No salary increase
        "hy_working_hours": 166.4,
        "unplanned_absence": 0.0,
        "other_expense": 0,
        "office_overrides": {}
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/simulation/run",
            json=params,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Price increase simulation completed")
            
            # Check year-over-year revenue growth
            if 'years' in results:
                years = results['years']
                if '2025' in years and '2026' in years:
                    
                    # Get KPIs for each year
                    kpis_2025 = years['2025'].get('kpis', {}).get('financial', {})
                    kpis_2026 = years['2026'].get('kpis', {}).get('financial', {})
                    
                    revenue_2025 = kpis_2025.get('net_sales', 0)
                    revenue_2026 = kpis_2026.get('net_sales', 0)
                    
                    if revenue_2025 > 0 and revenue_2026 > 0:
                        # Calculate actual growth
                        actual_growth = (revenue_2026 / revenue_2025 - 1) * 100
                        
                        # Expected growth: 10% price increase compounded over 2 years
                        # But we need to account for FTE changes too
                        # For price increase effect only, it should be close to (1.1)^2 - 1 = 21%
                        # But with recruitment, it will be higher
                        
                        print(f"   💰 Revenue 2025: {revenue_2025/1e9:.2f}B SEK")
                        print(f"   💰 Revenue 2026: {revenue_2026/1e9:.2f}B SEK")
                        print(f"   📈 Actual Growth: {actual_growth:.1f}%")
                        
                        # Price increases should contribute significantly to growth
                        # With 10% yearly increases over 2 years, we expect at least 20% growth from prices alone
                        if actual_growth >= 20:
                            print("   ✅ Price increase effect detected (>20% growth)")
                            return True
                        else:
                            print("   ❌ Price increase effect too small (<20% growth)")
                            return False
                    else:
                        print("   ❌ Revenue data missing")
                        return False
                else:
                    print("   ❌ Year data missing")
                    return False
            else:
                print("   ❌ No years data found")
                return False
        else:
            print(f"❌ Price increase simulation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Price increase test error: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🔍 COMPREHENSIVE CALCULATION VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Offices Loading", test_offices_endpoint),
        ("Basic Simulation", test_basic_simulation),
        ("FTE Movement Calculations", test_fte_movement_calculations),
        ("Revenue Calculations", test_revenue_calculations),
        ("Salary Cost Calculations", test_salary_cost_calculations),
        ("EBITDA Calculations", test_ebitda_calculations),
        ("Price Increase Logic", test_price_increase_logic),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
    
    print(f"\n{'='*50}")
    print(f"🎯 FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CALCULATIONS VERIFIED CORRECT!")
        return True
    else:
        print("⚠️ SOME CALCULATIONS NEED REVIEW")
        return False

if __name__ == "__main__":
    main()
