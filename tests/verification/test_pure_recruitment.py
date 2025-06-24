"""
Pure Recruitment Verification Test

This test isolates recruitment functionality by setting:
- Churn = 0% (no one leaves)
- Progression = 0% (no internal movement)
- Recruitment = 2% (only growth mechanism)

This verifies that recruitment works correctly in isolation.
"""

import pytest
from typing import Dict, Any


class TestPureRecruitment:
    """Test recruitment functionality in isolation"""

    def test_pure_recruitment_2_percent_annual(self, api_client, ensure_server_running, test_helper, logger):
        """Test that 2% monthly recruitment works correctly over 1 year with no churn/progression"""
        
        logger("🧪 PURE RECRUITMENT TEST - 2% Monthly for 1 Year")
        logger("=" * 60)
        
        # Step 1: Get baseline configuration
        logger("📊 Step 1: Getting baseline configuration")
        response = api_client.get("/offices/config")
        assert response.status_code == 200
        
        offices = response.json()
        baseline_totals = {}
        
        for office in offices:
            office_name = office['name']
            total_fte = 0
            
            # Count total FTE for this office
            for role_name, role_data in office['roles'].items():
                if isinstance(role_data, dict):  # Roles with levels (Consultant, Sales, Recruitment)
                    for level_name, level_data in role_data.items():
                        # Skip non-dict values (like duplicate top-level fields in flat roles)
                        if isinstance(level_data, dict):
                            total_fte += level_data.get('fte', 0)
                else:  # Flat roles (Operations)
                    if isinstance(role_data, dict):
                        total_fte += role_data.get('fte', 0)
            
            baseline_totals[office_name] = total_fte
            logger(f"   {office_name}: {total_fte} FTE")
        
        total_baseline = sum(baseline_totals.values())
        
        logger(f"   TOTAL BASELINE: {total_baseline} FTE")
        
        # Step 2: Set pure recruitment rates (2% recruitment, 0% churn, 0% progression)
        logger("📊 Step 2: Setting pure recruitment rates")
        
        config_update = {}
        
        for office in offices:
            office_name = office['name']
            
            for role_name, role_data in office['roles'].items():
                if isinstance(role_data, dict):  # Roles with levels
                    for level_name, level_data in role_data.items():
                        # Skip non-dict values (like duplicate top-level fields in flat roles)
                        if isinstance(level_data, dict):
                            # Set recruitment to 2% for all months
                            for month in range(1, 13):
                                config_update[f'{office_name}.{role_name}.{level_name}.recruitment_{month}'] = 0.02
                                config_update[f'{office_name}.{role_name}.{level_name}.churn_{month}'] = 0.0
                                config_update[f'{office_name}.{role_name}.{level_name}.progression_{month}'] = 0.0
                else:  # Flat roles (Operations)
                    if isinstance(role_data, dict):
                        # Set recruitment to 2% for all months
                        for month in range(1, 13):
                            config_update[f'{office_name}.{role_name}.recruitment_{month}'] = 0.02
                            config_update[f'{office_name}.{role_name}.churn_{month}'] = 0.0
        
        response = api_client.post("/offices/config/update", json_data=config_update)
        if response.status_code != 200:
            logger(f"   ❌ Config update failed: {response.status_code}")
            logger(f"   Response: {response.text}")
        assert response.status_code == 200
        logger("   ✅ Set all levels to 2% recruitment, 0% churn, 0% progression")
        
        # Step 3: Run 1-year simulation
        logger("📊 Step 3: Running 1-year simulation")
        simulation_config = {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12,
            "price_increase": 0.0,
            "salary_increase": 0.0
        }
        
        response = api_client.post("/simulation/run", json_data=simulation_config, timeout=180)
        assert response.status_code == 200
        results = response.json()
        
        # Step 4: Calculate expected results
        logger("📊 Step 4: Calculating expected results")
        
        # With 2% monthly recruitment and no churn/progression:
        # Each month: new_total = old_total * (1 + 0.02)
        # After 12 months: final_total = baseline * (1.02)^12
        expected_growth_factor = (1.02) ** 12
        expected_total = int(total_baseline * expected_growth_factor)
        
        logger(f"   Expected growth factor: {expected_growth_factor:.4f}")
        logger(f"   Expected total after 1 year: {expected_total} FTE")
        logger(f"   Expected growth: {expected_total - total_baseline} FTE ({((expected_total - total_baseline) / total_baseline * 100):.1f}%)")
        
        # Step 5: Extract actual results
        logger("📊 Step 5: Extracting actual results")
        
        # Get final year results
        year_2025 = results['years']['2025']
        final_month_data = None
        
        # Find the last month with data
        for office_name, office_data in year_2025['offices'].items():
            if office_data['levels']:
                # Get the length of data arrays to find last month
                first_role = list(office_data['levels'].keys())[0]
                if isinstance(office_data['levels'][first_role], dict):
                    first_level = list(office_data['levels'][first_role].keys())[0]
                    data_length = len(office_data['levels'][first_role][first_level])
                else:
                    data_length = len(office_data['levels'][first_role])
                break
        
        # Calculate actual totals from final month
        actual_totals = {}
        actual_total = 0
        
        for office_name, office_data in year_2025['offices'].items():
            office_total = 0
            
            for role_name, role_data in office_data['levels'].items():
                if isinstance(role_data, dict):  # Roles with levels
                    for level_name, level_data in role_data.items():
                        if level_data:  # If there's data
                            office_total += level_data[-1]['total']  # Last month's total
                else:  # Flat roles
                    if role_data:  # If there's data
                        office_total += role_data[-1]['total']  # Last month's total
            
            # Add operations if it exists
            if office_data.get('operations') and office_data['operations'][-1]:
                office_total += office_data['operations'][-1]['total']
            
            actual_totals[office_name] = office_total
            actual_total += office_total
            logger(f"   {office_name}: {office_total} FTE (was {baseline_totals[office_name]}, growth: {office_total - baseline_totals[office_name]})")
        
        logger(f"   ACTUAL TOTAL: {actual_total} FTE")
        logger(f"   ACTUAL GROWTH: {actual_total - total_baseline} FTE ({((actual_total - total_baseline) / total_baseline * 100):.1f}%)")
        
        # Step 6: Verification
        logger("📊 Step 6: Verification")
        
        # Check if recruitment happened
        assert actual_total > total_baseline, f"No growth detected: {actual_total} <= {total_baseline}"
        logger("   ✅ Growth detected - recruitment is working")
        
        # Check if growth is reasonable (within 15% tolerance of expected)
        tolerance = max(100, expected_total * 0.15)  # 15% tolerance or minimum 100 FTE
        growth_difference = abs(actual_total - expected_total)
        
        logger(f"   Expected: {expected_total}, Actual: {actual_total}, Difference: {growth_difference}")
        logger(f"   Tolerance: {tolerance}")
        
        # Calculate actual growth rate to understand what's happening
        actual_growth_factor = actual_total / total_baseline
        logger(f"   Expected growth factor: {expected_growth_factor:.4f}")
        logger(f"   Actual growth factor: {actual_growth_factor:.4f}")
        
        # Calculate what the monthly rate would be to achieve this growth
        import math
        implied_monthly_rate = (actual_growth_factor ** (1/12)) - 1
        logger(f"   Implied monthly recruitment rate: {implied_monthly_rate:.3%}")
        
        assert growth_difference <= tolerance, \
            f"Growth not as expected: got {actual_total}, expected {expected_total} (difference: {growth_difference}, tolerance: {tolerance})"
        
        # Check that each office grew (recruitment should affect all offices)
        offices_with_growth = 0
        for office_name in baseline_totals:
            if actual_totals[office_name] > baseline_totals[office_name]:
                offices_with_growth += 1
        
        # At least 60% of offices should show growth (accounting for very small offices)
        min_offices_with_growth = max(1, int(len(baseline_totals) * 0.6))
        assert offices_with_growth >= min_offices_with_growth, \
            f"Too few offices showing growth: {offices_with_growth}/{len(baseline_totals)} (expected at least {min_offices_with_growth})"
        
        logger(f"   ✅ {offices_with_growth}/{len(baseline_totals)} offices showed growth")
        logger("   ✅ Pure recruitment functionality verified!")

    def test_recruitment_scales_with_rate(self, api_client, ensure_server_running, test_helper, logger):
        """Test that recruitment scales correctly with different rates"""
        
        logger("🧪 RECRUITMENT SCALING TEST")
        logger("=" * 40)
        
        test_rates = [0.01, 0.03, 0.05]  # 1%, 3%, 5% monthly
        results = {}
        
        # Get baseline
        response = api_client.get("/offices/config")
        offices = response.json()
        baseline_total = 0
        for office in offices:
            for role_name, role_data in office['roles'].items():
                if isinstance(role_data, dict):
                    for level_name, level_data in role_data.items():
                        # Skip non-dict values (like duplicate top-level fields in flat roles)
                        if isinstance(level_data, dict):
                            baseline_total += level_data.get('fte', 0)
                else:
                    if isinstance(role_data, dict):
                        baseline_total += role_data.get('fte', 0)
        
        for rate in test_rates:
            logger(f"   Testing {rate:.1%} monthly recruitment...")
            
            # Set recruitment rate
            config_update = {}
            for office in offices:
                office_name = office['name']
                for role_name, role_data in office['roles'].items():
                    if isinstance(role_data, dict):
                        for level_name, level_data in role_data.items():
                            # Skip non-dict values (like duplicate top-level fields in flat roles)
                            if isinstance(level_data, dict):
                                for month in range(1, 13):
                                    config_update[f'{office_name}.{role_name}.{level_name}.recruitment_{month}'] = rate
                                    config_update[f'{office_name}.{role_name}.{level_name}.churn_{month}'] = 0.0
                                    config_update[f'{office_name}.{role_name}.{level_name}.progression_{month}'] = 0.0
                    else:
                        if isinstance(role_data, dict):
                            for month in range(1, 13):
                                config_update[f'{office_name}.{role_name}.recruitment_{month}'] = rate
                                config_update[f'{office_name}.{role_name}.churn_{month}'] = 0.0
            
            response = api_client.post("/offices/config/update", json_data=config_update)
            if response.status_code != 200:
                logger(f"   ❌ Config update failed: {response.status_code}")
                logger(f"   Response: {response.text}")
            assert response.status_code == 200
            
            # Run 6-month simulation (shorter for scaling test)
            simulation_config = {
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2025,
                "end_month": 6,
                "price_increase": 0.0,
                "salary_increase": 0.0
            }
            
            response = api_client.post("/simulation/run", json_data=simulation_config, timeout=120)
            assert response.status_code == 200
            sim_results = response.json()
            
            # Extract final total
            year_data = sim_results['years']['2025']
            actual_total = 0
            for office_name, office_data in year_data['offices'].items():
                for role_name, role_data in office_data['levels'].items():
                    if isinstance(role_data, dict):
                        for level_name, level_data in role_data.items():
                            if level_data:
                                actual_total += level_data[-1]['total']
                    else:
                        if role_data:
                            actual_total += role_data[-1]['total']
                if office_data.get('operations') and office_data['operations'][-1]:
                    actual_total += office_data['operations'][-1]['total']
            
            growth_factor = actual_total / baseline_total
            expected_factor = (1 + rate) ** 6
            
            results[rate] = {
                'actual_total': actual_total,
                'growth_factor': growth_factor,
                'expected_factor': expected_factor
            }
            
            logger(f"     {rate:.1%}: {baseline_total} → {actual_total} (factor: {growth_factor:.3f}, expected: {expected_factor:.3f})")
        
        # Verify scaling relationship
        growth_factors = [results[rate]['growth_factor'] for rate in test_rates]
        
        # Growth factors should increase with recruitment rate
        for i in range(1, len(test_rates)):
            assert growth_factors[i] > growth_factors[i-1], \
                f"Growth factor didn't increase with rate: {test_rates[i-1]:.1%}={growth_factors[i-1]:.3f}, {test_rates[i]:.1%}={growth_factors[i]:.3f}"
        
        logger("   ✅ Recruitment scales correctly with rate!") 