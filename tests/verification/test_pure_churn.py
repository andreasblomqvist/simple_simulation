"""
Pure Churn Verification Test

This test isolates churn functionality by setting:
- Churn = 2% (monthly)
- Recruitment = 0% (no new hires)
- Progression = 0% (no internal movement)

This verifies that churn works correctly in isolation.
"""

import pytest
from typing import Dict, Any

class TestPureChurn:
    """Test churn functionality in isolation"""

    def test_pure_churn_2_percent_annual(self, api_client, ensure_server_running, test_helper, logger):
        """Test that 2% monthly churn works correctly over 1 year with no recruitment/progression"""
        
        logger("🧪 PURE CHURN TEST - 2% Monthly for 1 Year")
        logger("=" * 60)
        
        # Step 1: Get baseline config and FTEs
        logger("📊 Step 1: Getting baseline configuration")
        response = api_client.get("/offices/config")
        assert response.status_code == 200
        offices = response.json()
        total_baseline = 0
        office_baseline = {}
        for office in offices:
            office_name = office['name']
            total_fte = 0
            for role_name, role_data in office['roles'].items():
                if isinstance(role_data, dict):
                    for level_name, level_data in role_data.items():
                        total_fte += level_data.get('fte', 0)
                else:
                    total_fte += role_data.get('fte', 0)
            office_baseline[office_name] = total_fte
            total_baseline += total_fte
            logger(f"   {office_name}: {total_fte} FTE")
        logger(f"   TOTAL BASELINE: {total_baseline} FTE")
        
        # Step 2: Set pure churn rates (2% churn, 0% recruitment, 0% progression)
        logger("📊 Step 2: Setting pure churn rates")
        config_update = {}
        for office in offices:
            office_name = office['name']
            for role_name, role_data in office['roles'].items():
                if isinstance(role_data, dict):
                    for level_name, level_data in role_data.items():
                        for month in range(1, 13):
                            config_update[f'{office_name}.{role_name}.{level_name}.recruitment_{month}'] = 0.0
                            config_update[f'{office_name}.{role_name}.{level_name}.churn_{month}'] = 0.02
                            config_update[f'{office_name}.{role_name}.{level_name}.progression_{month}'] = 0.0
                else:
                    for month in range(1, 13):
                        config_update[f'{office_name}.{role_name}.recruitment_{month}'] = 0.0
                        config_update[f'{office_name}.{role_name}.churn_{month}'] = 0.02
                        config_update[f'{office_name}.{role_name}.progression_{month}'] = 0.0
        response = api_client.post("/offices/config/update", json_data=config_update)
        if response.status_code != 200:
            logger(f"   ❌ Config update failed: {response.status_code}")
            logger(f"   Response: {response.text}")
        assert response.status_code == 200
        logger("   ✅ Set all levels to 2% churn, 0% recruitment, 0% progression")
        
        # Step 3: Run simulation for 1 year
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
        expected_growth_factor = (1 - 0.02) ** 12
        expected_total = round(total_baseline * expected_growth_factor)
        expected_decline = total_baseline - expected_total
        logger(f"   Expected decline factor: {expected_growth_factor:.4f}")
        logger(f"   Expected total after 1 year: {expected_total} FTE")
        logger(f"   Expected decline: {expected_decline} FTE ({(expected_decline/total_baseline)*100:.1f}%)")
        
        # Step 5: Extract actual results
        logger("📊 Step 5: Extracting actual results")
        
        # Get final year results
        year_2025 = results['years']['2025']
        
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
            logger(f"   {office_name}: {office_total} FTE (was {office_baseline[office_name]}, decline: {office_baseline[office_name] - office_total})")
        
        logger(f"   ACTUAL TOTAL: {actual_total} FTE")
        logger(f"   ACTUAL DECLINE: {total_baseline - actual_total} FTE ({((total_baseline - actual_total) / total_baseline * 100):.1f}%)")
        
        # Step 6: Verification
        logger("📊 Step 6: Verification")
        
        # Check if churn happened
        assert actual_total < total_baseline, f"No decline detected: {actual_total} >= {total_baseline}"
        logger("   ✅ Decline detected - churn is working")
        
        # Check if decline is reasonable (within 15% tolerance of expected)
        tolerance = max(100, expected_total * 0.15)  # 15% tolerance or minimum 100 FTE
        decline_difference = abs(actual_total - expected_total)
        
        logger(f"   Expected: {expected_total}, Actual: {actual_total}, Difference: {decline_difference}")
        logger(f"   Tolerance: {tolerance}")
        
        # Calculate actual decline rate to understand what's happening
        actual_decline_factor = actual_total / total_baseline
        logger(f"   Expected decline factor: {expected_growth_factor:.4f}")
        logger(f"   Actual decline factor: {actual_decline_factor:.4f}")
        
        # Calculate what the monthly rate would be to achieve this decline
        import math
        implied_monthly_rate = 1 - (actual_decline_factor ** (1/12))
        logger(f"   Implied monthly churn rate: {implied_monthly_rate:.3%}")
        
        assert decline_difference <= tolerance, \
            f"Decline not as expected: got {actual_total}, expected {expected_total} (difference: {decline_difference}, tolerance: {tolerance})"
        
        # Check that each office declined (churn should affect all offices)
        offices_with_decline = 0
        for office_name in office_baseline:
            if actual_totals[office_name] < office_baseline[office_name]:
                offices_with_decline += 1
        
        # At least 80% of offices should show decline
        min_offices_with_decline = max(1, int(len(office_baseline) * 0.8))
        assert offices_with_decline >= min_offices_with_decline, \
            f"Too few offices showing decline: {offices_with_decline}/{len(office_baseline)} (expected at least {min_offices_with_decline})"
        
        logger(f"   ✅ {offices_with_decline}/{len(office_baseline)} offices showed decline")
        logger("   ✅ Pure churn functionality verified!")
        
        return {
            'baseline_total': total_baseline,
            'actual_total': actual_total,
            'expected_total': expected_total,
            'decline_factor': actual_total / total_baseline,
            'expected_decline_factor': expected_growth_factor
        } 