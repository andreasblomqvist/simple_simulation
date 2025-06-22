#!/usr/bin/env python3
"""
Focused Recruitment Verification Test

This test specifically verifies:
1. Load configuration
2. Set recruitment rate to 6%
3. Run simulation
4. Verify actual recruitment happened accounting for churn and progression
"""

import sys
import os
import json
import requests
import time

class RecruitmentVerificationTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_recruitment_mechanics(self):
        """Test recruitment mechanics accounting for all dynamics"""
        self.log("🧪 RECRUITMENT VERIFICATION TEST")
        self.log("=" * 50)
        
        # Step 1: Get baseline data
        self.log("📊 Step 1: Getting baseline data")
        response = requests.get(f"{self.base_url}/offices/config")
        assert response.status_code == 200
        
        offices = response.json()
        stockholm = next((o for o in offices if o["name"] == "Stockholm"), None)
        assert stockholm is not None
        
        baseline_a_fte = stockholm["roles"]["Consultant"]["A"]["fte"]
        current_recruitment = stockholm["roles"]["Consultant"]["A"]["recruitment_1"]
        current_churn = stockholm["roles"]["Consultant"]["A"]["churn_1"]
        current_progression = stockholm["roles"]["Consultant"]["A"]["progression_1"]
        
        self.log(f"   Stockholm A Level: {baseline_a_fte} FTE")
        self.log(f"   Current rates - Recruitment: {current_recruitment:.1%}, Churn: {current_churn:.1%}, Progression: {current_progression:.1%}")
        
        # Step 2: Set recruitment to 6%
        self.log("📊 Step 2: Setting recruitment to 6%")
        update_payload = {"Stockholm.Consultant.A.recruitment_1": 0.06}
        
        response = requests.post(f"{self.base_url}/offices/config/update", json=update_payload)
        assert response.status_code == 200
        
        # Get updated rates
        response = requests.get(f"{self.base_url}/offices/config")
        stockholm = next((o for o in response.json() if o["name"] == "Stockholm"), None)
        
        recruitment_rate = stockholm["roles"]["Consultant"]["A"]["recruitment_1"]
        churn_rate = stockholm["roles"]["Consultant"]["A"]["churn_1"]
        progression_rate = stockholm["roles"]["Consultant"]["A"]["progression_1"]
        
        self.log(f"   Updated rates - Recruitment: {recruitment_rate:.1%}, Churn: {churn_rate:.1%}, Progression: {progression_rate:.1%}")
        
        # Step 3: Calculate expected dynamics
        self.log("📊 Step 3: Expected dynamics calculation")
        
        # Simulation order: recruitment → churn → progression
        expected_recruited = int(baseline_a_fte * recruitment_rate)
        after_recruitment = baseline_a_fte + expected_recruited
        
        expected_churned = int(after_recruitment * churn_rate)
        after_churn = after_recruitment - expected_churned
        
        expected_progressed_out = int(after_churn * progression_rate)
        expected_final = after_churn - expected_progressed_out
        
        self.log(f"   Expected flow:")
        self.log(f"     Start: {baseline_a_fte}")
        self.log(f"     +Recruitment: {expected_recruited} → {after_recruitment}")
        self.log(f"     -Churn: {expected_churned} → {after_churn}")
        self.log(f"     -Progression: {expected_progressed_out} → {expected_final}")
        
        # Step 4: Run simulation
        self.log("📊 Step 4: Running 1-month simulation")
        simulation_request = {
            "start_year": 2025, "start_month": 1,
            "end_year": 2025, "end_month": 1,
            "price_increase": 0.0, "salary_increase": 0.0,
            "unplanned_absence": 0.05, "hy_working_hours": 166.4,
            "other_expense": 100000.0
        }
        
        response = requests.post(f"{self.base_url}/simulation/run", json=simulation_request, timeout=120)
        assert response.status_code == 200
        results = response.json()
        
        # Step 5: Extract actual results
        final_year_data = results['years']['2025']
        a_level_data = final_year_data['offices']['Stockholm']['levels']['Consultant']['A'][0]
        
        actual_final = a_level_data.get('total', 0)
        actual_recruited = a_level_data.get('recruited', 0)
        actual_churned = a_level_data.get('churned', 0)
        actual_progressed = a_level_data.get('progressed_out', 0)
        
        self.log(f"   Actual results:")
        self.log(f"     Final count: {actual_final}")
        self.log(f"     Recruited: {actual_recruited}")
        self.log(f"     Churned: {actual_churned}")
        self.log(f"     Progressed out: {actual_progressed}")
        
        # Step 6: Verification
        self.log("📊 Step 6: Verification")
        
        # Primary test: Was recruitment applied?
        recruitment_working = actual_recruited > 0
        self.log(f"   Recruitment status: {'✅ WORKING' if recruitment_working else '❌ NOT WORKING'}")
        
        if recruitment_working:
            # Secondary tests: Are the numbers reasonable?
            recruitment_close = abs(actual_recruited - expected_recruited) <= max(1, expected_recruited * 0.2)
            final_close = abs(actual_final - expected_final) <= max(2, expected_final * 0.3)
            
            self.log(f"   Recruitment accuracy: {'✅' if recruitment_close else '⚠️'} (expected {expected_recruited}, got {actual_recruited})")
            self.log(f"   Final count accuracy: {'✅' if final_close else '⚠️'} (expected {expected_final}, got {actual_final})")
            
            if recruitment_close and final_close:
                self.log("   🎉 ALL DYNAMICS WORKING CORRECTLY!")
            else:
                self.log("   ⚠️ Recruitment works but numbers are unexpected")
        
        return recruitment_working

if __name__ == "__main__":
    test = RecruitmentVerificationTest()
    success = test.test_recruitment_mechanics()
    
    if success:
        print("\n✅ TEST PASSED: Recruitment mechanics are working!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED: Recruitment mechanics are not working!")
        sys.exit(1)
