"""
Recruitment Mechanics Verification Test

This test verifies that recruitment mechanics work correctly
accounting for recruitment, churn, and progression dynamics.
"""

import pytest
from typing import Dict, Any


class TestRecruitmentMechanics:
    """Test recruitment mechanics with proper dynamics calculation"""

    def test_recruitment_with_6_percent_rate(self, api_client, ensure_server_running, test_config, 
                                           stockholm_consultant_a_config, test_helper, logger):
        """Test that 6% recruitment rate works correctly with churn and progression"""
        
        logger("🧪 RECRUITMENT VERIFICATION TEST")
        logger("=" * 50)
        
        # Step 1: Get baseline data
        logger("📊 Step 1: Getting baseline data")
        response = api_client.get("/offices/config")
        assert response.status_code == 200
        
        offices = response.json()
        baseline_data = test_helper.get_stockholm_a_level_data(offices)
        
        logger(f"   Stockholm A Level: {baseline_data['fte']} FTE")
        logger(f"   Current rates - Recruitment: {baseline_data['recruitment_1']:.1%}, "
               f"Churn: {baseline_data['churn_1']:.1%}, Progression: {baseline_data['progression_1']:.1%}")
        
        # Step 2: Set recruitment to 6%
        logger("📊 Step 2: Setting recruitment to 6%")
        config_update = stockholm_consultant_a_config(recruitment_rate=0.06)
        
        response = api_client.post("/offices/config/update", json_data=config_update)
        assert response.status_code == 200
        
        # Get updated rates
        response = api_client.get("/offices/config")
        assert response.status_code == 200
        
        offices = response.json()
        updated_data = test_helper.get_stockholm_a_level_data(offices)
        
        logger(f"   Updated rates - Recruitment: {updated_data['recruitment_1']:.1%}, "
               f"Churn: {updated_data['churn_1']:.1%}, Progression: {updated_data['progression_1']:.1%}")
        
        # Step 3: Calculate expected dynamics
        logger("📊 Step 3: Expected dynamics calculation")
        expected = test_helper.calculate_expected_dynamics(
            baseline_fte=baseline_data['fte'],
            recruitment_rate=updated_data['recruitment_1'],
            churn_rate=updated_data['churn_1'],
            progression_rate=updated_data['progression_1']
        )
        
        logger(f"   Expected flow:")
        logger(f"     Start: {baseline_data['fte']}")
        logger(f"     +Recruitment: {expected['recruited']} → {baseline_data['fte'] + expected['recruited']}")
        logger(f"     -Churn: {expected['churned']} → {baseline_data['fte'] + expected['recruited'] - expected['churned']}")
        logger(f"     -Progression: {expected['progressed_out']} → {expected['final']}")
        
        # Step 4: Run simulation
        logger("📊 Step 4: Running 1-month simulation")
        response = api_client.post("/simulation/run", json_data=test_config, timeout=120)
        assert response.status_code == 200
        results = response.json()
        
        # Step 5: Extract actual results
        actual = test_helper.extract_simulation_results(results)
        
        logger(f"   Actual results:")
        logger(f"     Final count: {actual['total']}")
        logger(f"     Recruited: {actual['recruited']}")
        logger(f"     Churned: {actual['churned']}")
        logger(f"     Progressed out: {actual['progressed_out']}")
        
        # Step 6: Verification
        logger("📊 Step 6: Verification")
        
        # Primary test: Was recruitment applied?
        assert actual['recruited'] > 0, "No recruitment detected despite 6% rate"
        logger(f"   Recruitment status: ✅ WORKING")
        
        # Secondary tests: Are the numbers reasonable?
        recruitment_tolerance = max(2, expected['recruited'] * 0.5)  # 50% tolerance for real-world data
        final_tolerance = max(5, expected['final'] * 0.4)  # 40% tolerance for complex dynamics
        
        recruitment_close = abs(actual['recruited'] - expected['recruited']) <= recruitment_tolerance
        final_close = abs(actual['total'] - expected['final']) <= final_tolerance
        
        logger(f"   Recruitment accuracy: {'✅' if recruitment_close else '⚠️'} "
               f"(expected {expected['recruited']}, got {actual['recruited']})")
        logger(f"   Final count accuracy: {'✅' if final_close else '⚠️'} "
               f"(expected {expected['final']}, got {actual['total']})")
        
        # Assert key requirements
        assert recruitment_close, f"Recruitment count not close to expected: got {actual['recruited']}, expected {expected['recruited']}"
        assert final_close, f"Final count not close to expected: got {actual['total']}, expected {expected['final']}"
        
        logger("   🎉 ALL DYNAMICS WORKING CORRECTLY!")

    def test_recruitment_with_different_rates(self, api_client, ensure_server_running, test_config, 
                                            stockholm_consultant_a_config, test_helper, logger):
        """Test recruitment with different rates to ensure scaling works"""
        
        test_rates = [0.02, 0.04, 0.08, 0.10]  # 2%, 4%, 8%, 10%
        
        for rate in test_rates:
            logger(f"🧪 Testing recruitment at {rate:.1%}")
            
            # Set recruitment rate
            config_update = stockholm_consultant_a_config(recruitment_rate=rate)
            response = api_client.post("/offices/config/update", json_data=config_update)
            assert response.status_code == 200
            
            # Get baseline
            response = api_client.get("/offices/config")
            offices = response.json()
            baseline_data = test_helper.get_stockholm_a_level_data(offices)
            
            # Run simulation
            response = api_client.post("/simulation/run", json_data=test_config, timeout=120)
            assert response.status_code == 200
            results = response.json()
            
            # Check results
            actual = test_helper.extract_simulation_results(results)
            expected_recruited = int(baseline_data['fte'] * rate)
            
            logger(f"   Rate {rate:.1%}: Expected {expected_recruited}, Got {actual['recruited']}")
            
            # Should have some recruitment at all rates > 0
            assert actual['recruited'] > 0, f"No recruitment at {rate:.1%} rate"
            
            # Should be roughly proportional (within 50% tolerance for small numbers)
            if expected_recruited > 0:
                tolerance = max(1, expected_recruited * 0.5)
                assert abs(actual['recruited'] - expected_recruited) <= tolerance, \
                    f"Recruitment not proportional at {rate:.1%}: got {actual['recruited']}, expected {expected_recruited}"
        
        logger("   ✅ Recruitment scales correctly with different rates!")
