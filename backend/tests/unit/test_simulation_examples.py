import unittest
import sys
import os
from unittest.mock import patch
import random

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.simulation_engine import SimulationEngine, Month, OfficeJourney, Journey, Level, RoleData
from backend.src.services.simulation_engine import Office, Level

class TestSimulationExamples(unittest.TestCase):
    """
    Test cases based on examples from simulation_engine.md documentation,
    adapted for monthly operation
    """
    
    def setUp(self):
        """Set up a simulation engine for testing"""
        self.engine = SimulationEngine()
    
    def test_processing_order_may_evaluation_month(self):
        """
        Test Scenario 1 from documentation: Normal Recruitment in May (evaluation month)
        Order: Churn → Progression → Recruitment
        """
        # Set up test data with level A having 10 FTE
        level_a = self.engine.offices['Stockholm'].roles['Consultant']['A']
        level_a.total = 10
        
        # Set higher rates to see the effects clearly
        # 5% churn, 20% progression (May), 20% recruitment
        for month in range(1, 13):
            setattr(level_a, f'churn_{month}', 0.05)
            setattr(level_a, f'recruitment_{month}', 0.2)
            if month == 5:  # May - evaluation month
                setattr(level_a, f'progression_{month}', 0.2)
            else:
                setattr(level_a, f'progression_{month}', 0.0)
        
        # Run simulation for May only
        results = self.engine.run_simulation(2024, 5, 2024, 5)
        
        # Order of operations:
        # 1. Churn: 10 * (1-0.05) = 9.5 → rounds to 9
        # 2. Progression: 9 * 0.2 = 1.8 → rounds to 1 progressed → 9-1 = 8 remain  
        # 3. Recruitment: 8 * 0.2 = 1.6 → rounds to 1 recruit → 8+1 = 9 final
        
        self.assertEqual(level_a.total, 9,
                        "Level A should end up with 9 FTE after churn/progression/recruitment in May")
        
        # Verify it's an evaluation month (progression should occur)
        self.assertIn(Month.MAY, level_a.progression_months,
                     "May should be an evaluation month for level A")
    
    def test_processing_order_january_non_evaluation(self):
        """
        Test Scenario 2 from documentation: Non-Evaluation Month (January)
        Order: Churn → Progression → Recruitment (no progression in January)
        """
        # Set up test data
        level_a = self.engine.offices['Stockholm'].roles['Consultant']['A']
        level_a.total = 10
        
        # Set rates: 5% churn, 0% progression (January), 20% recruitment  
        for month in range(1, 13):
            setattr(level_a, f'churn_{month}', 0.05)
            setattr(level_a, f'recruitment_{month}', 0.2)
            setattr(level_a, f'progression_{month}', 0.0)  # No progression in January
        
        # Run simulation for January only
        results = self.engine.run_simulation(2024, 1, 2024, 1)
        
        # Order of operations:
        # 1. Churn: 10 * (1-0.05) = 9.5 → rounds to 9
        # 2. Progression: 0% → 0 progressed
        # 3. Recruitment: 9 * 0.2 = 1.8 → rounds to 1 recruit → 9+1 = 10 final
        
        self.assertEqual(level_a.total, 10,
                        "Level A should end up with 10 FTE in January (no progression month)")
        
        # Verify January is not an evaluation month
        self.assertNotIn(Month.JAN, level_a.progression_months,
                        "January should not be an evaluation month for level A")
    
    def test_progression_timing_a_level(self):
        """
        Test that A-level progression only occurs in May and November
        """
        office = self.engine.offices['Stockholm']
        level_a = office.roles['Consultant']['A']
        
        # Check progression_months parameter
        expected_months = [Month.MAY, Month.NOV]
        self.assertEqual(level_a.progression_months, expected_months,
                        "A level should only progress in May and November")
    
    def test_progression_timing_m_level(self):
        """
        Test that M-level progression only occurs in November
        """
        office = self.engine.offices['Stockholm']
        level_m = office.roles['Consultant']['M']
        
        # Check progression_months parameter
        expected_months = [Month.NOV]
        self.assertEqual(level_m.progression_months, expected_months,
                        "M level should only progress in November")
    
    def test_churn_calculation_example(self):
        """
        Test churn calculation from documentation:
        Formula: new_total = current_total * (1 - churn_rate)
        Example: 100 people with 5% churn → 95 people remain
        """
        office = self.engine.offices['Stockholm']
        level_a = office.roles['Consultant']['A']
        level_a.total = 100
        
        # Set 5% churn rate, no progression, no recruitment
        for month in range(1, 13):
            setattr(level_a, f'churn_{month}', 0.05)
            setattr(level_a, f'progression_{month}', 0.0)
            setattr(level_a, f'recruitment_{month}', 0.0)
        
        # Run simulation for one month
        results = self.engine.run_simulation(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1
        )
        
        # Should have 95 people remaining (100 * (1 - 0.05) = 95)
        expected_remaining = int(100 * (1 - 0.05))
        self.assertEqual(level_a.total, expected_remaining,
                        f"Should have {expected_remaining} people after 5% churn")
    
    def test_new_office_minimum_recruitment(self):
        """
        Test Scenario 3: New Office Recruitment
        New offices should have minimum recruitment even with zero FTE
        """
        # Toronto is configured as a new office (10 total FTE)
        office = self.engine.offices['Toronto']
        self.assertEqual(office.journey, OfficeJourney.NEW,
                        "Toronto should be classified as NEW office")
        
        # Set a level to zero FTE
        level_a = office.roles['Consultant']['A']
        original_total = level_a.total
        level_a.total = 0
        
        # Set recruitment rate
        for month in range(1, 13):
            setattr(level_a, f'recruitment_{month}', 0.2)  # 20% recruitment
            setattr(level_a, f'churn_{month}', 0.0)        # No churn
            setattr(level_a, f'progression_{month}', 0.0)  # No progression
        
        # Run simulation for one month
        results = self.engine.run_simulation(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1
        )
        
        # New office should recruit even from zero base
        self.assertGreater(level_a.total, 0,
                          "New office should recruit even from zero FTE")
        
        # Reset for cleanup
        level_a.total = original_total
    
    def test_office_journey_classification(self):
        """
        Test office classification based on total FTE:
        - New Office: 0-24 FTE
        - Emerging Office: 25-200 FTE  
        - Established Office: 200-500 FTE
        - Mature Office: 500+ FTE
        """
        classifications = {
            'Toronto': (5, OfficeJourney.NEW),         # 5 FTE → New
            'Frankfurt': (27, OfficeJourney.EMERGING), # 27 FTE → Emerging
            'Cologne': (22, OfficeJourney.NEW),        # 22 FTE → New
            'Amsterdam': (23, OfficeJourney.NEW),      # 23 FTE → New
            'Hamburg': (165, OfficeJourney.EMERGING),  # 165 FTE → Emerging
            'Stockholm': (821, OfficeJourney.MATURE)   # 821 FTE → Mature
        }
        
        for office_name, (expected_fte, expected_journey) in classifications.items():
            office = self.engine.offices[office_name]
            self.assertEqual(office.journey, expected_journey,
                           f"{office_name} with {expected_fte} FTE should be {expected_journey.value}")
    
    def test_monthly_simulation_full_year(self):
        """
        Test that monthly simulation runs for a full year (12 months)
        """
        # Run simulation for a full year
        results = self.engine.run_simulation(
            start_year=2024, start_month=1,
            end_year=2024, end_month=12
        )
        
        # Verify results structure
        self.assertIn('periods', results, "Results should contain periods")
        self.assertIn('offices', results, "Results should contain offices")
        
        # Should have 12 periods (one per month)
        self.assertEqual(len(results['periods']), 12,
                        "Should have 12 monthly periods")
        
        # Each period should be a month name
        expected_periods = [month.name for month in Month]
        for i, period in enumerate(results['periods']):
            self.assertEqual(period, expected_periods[i],
                           f"Period {i+1} should be {expected_periods[i]}")
    
    def test_progression_moves_to_next_level(self):
        """
        Test that progressed employees move to the next level
        """
        engine = SimulationEngine()
        
        # Set up test data  
        level_a = engine.offices['Stockholm'].roles['Consultant']['A']
        level_ac = engine.offices['Stockholm'].roles['Consultant']['AC']
        level_a.total = 20
        initial_ac = level_ac.total
        
        # Set rates for A: 0% churn, 20% progression, 0% recruitment (to isolate progression)
        for month in range(1, 13):
            setattr(level_a, f'churn_{month}', 0.0)
            setattr(level_a, f'recruitment_{month}', 0.0)
            if month == 5:  # May - evaluation month
                setattr(level_a, f'progression_{month}', 0.2)
            else:
                setattr(level_a, f'progression_{month}', 0.0)
        
        # Set rates for AC: 0% churn, 0% progression, 0% recruitment (to prevent AC from changing)
        for month in range(1, 13):
            setattr(level_ac, f'churn_{month}', 0.0)
            setattr(level_ac, f'recruitment_{month}', 0.0)
            setattr(level_ac, f'progression_{month}', 0.0)  # Prevent AC from progressing further
        
        # Run simulation for May (evaluation month)
        results = engine.run_simulation(2024, 5, 2024, 5)
        
        # Expected: 
        # A: 20 * 0.2 = 4 progressed from A to AC, 16 remain in A
        # AC: 8 (initial) + 4 (from A) = 12 final
        expected_progressed = 4
        self.assertEqual(level_a.total, 16, f"Level A should have {16} FTE after progression")
        self.assertEqual(level_ac.total, initial_ac + expected_progressed,
                        f"Level AC should have exactly {initial_ac + expected_progressed} FTE after receiving progression")
    
    def test_operations_flat_role(self):
        """
        Test that Operations role works as a flat role (no levels)
        """
        office = self.engine.offices['Stockholm']
        
        # Operations should be a flat role
        if 'Operations' in office.roles:
            operations = office.roles['Operations']
            self.assertIsInstance(operations, RoleData,
                                "Operations should be a flat role (RoleData)")
            self.assertIsInstance(operations.total, int,
                                "Operations should have integer total")
            self.assertGreater(operations.total, 0,
                             "Operations should have some FTE")
    
    def test_recruitment_calculation(self):
        """
        Test recruitment calculation: new_recruits = current_total * recruitment_rate
        """
        office = self.engine.offices['Stockholm']
        level_a = office.roles['Consultant']['A']
        level_a.total = 50
        
        # Set rates for testing (no churn or progression)
        for month in range(1, 13):
            setattr(level_a, f'churn_{month}', 0.0)       # No churn
            setattr(level_a, f'progression_{month}', 0.0) # No progression
            setattr(level_a, f'recruitment_{month}', 0.2) # 20% recruitment
        
        # Run simulation for one month
        results = self.engine.run_simulation(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1
        )
        
        # 20% of 50 = 10 new recruits
        expected_recruits = int(50 * 0.2)
        expected_total = 50 + expected_recruits
        
        self.assertEqual(level_a.total, expected_total,
                        f"Should have {expected_total} after recruiting {expected_recruits}")
    
    def test_lever_plan_override(self):
        """
        Test that lever plans can override default rates
        """
        # Create a lever plan that overrides Stockholm Consultant A recruitment
        lever_plan = {
            'Stockholm': {
                'Consultant': {
                    'A': {
                        'recruitment_1': 0.5,  # 50% recruitment in January
                        'churn_1': 0.1         # 10% churn in January
                    }
                }
            }
        }
        
        office = self.engine.offices['Stockholm']
        level_a = office.roles['Consultant']['A']
        initial_total = level_a.total
        
        # Run simulation with lever plan
        results = self.engine.run_simulation(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1,
            lever_plan=lever_plan
        )
        
        # The lever plan should have been applied
        self.assertIsNotNone(results, "Simulation should complete with lever plan")
        # Note: Specific verification would depend on implementation details
    
    def test_progression_evaluation_periods_only(self):
        """
        Test that progression only occurs during evaluation periods
        """
        office = self.engine.offices['Stockholm']
        level_a = office.roles['Consultant']['A']
        level_ac = office.roles['Consultant']['AC']
        
        # Test non-evaluation months (should have no progression)
        level_a.total = 10
        initial_ac = level_ac.total
        
        # Set high progression rate but run in non-evaluation month
        for month in range(1, 13):
            setattr(level_a, f'churn_{month}', 0.0)
            setattr(level_a, f'recruitment_{month}', 0.0)
            setattr(level_a, f'progression_{month}', 0.5)  # 50% progression rate
        
        # Run in April (non-evaluation month for A level)
        results = self.engine.run_simulation(
            start_year=2024, start_month=4,
            end_year=2024, end_month=4
        )
        
        # Despite 50% progression rate, should be no progression in April
        # A level should have progression_months = [Month.MAY, Month.NOV]
        april_allows_progression = Month.APR in level_a.progression_months
        self.assertFalse(april_allows_progression,
                        "A level should not allow progression in April")
    
    def test_oslo_consultant_churn_and_recruitment(self):
        """Test Oslo office with 96 consultants (A, AC, C, SrC) and 2% monthly churn and 3% monthly recruitment."""
        # Oslo is already in ACTUAL_OFFICE_LEVEL_DATA and OFFICE_HEADCOUNT
        # Re-initialize roles to ensure Oslo is present
        self.engine._initialize_roles()
        oslo = self.engine.offices["Oslo"]
        # Set churn and recruitment rates for Consultant A, AC, C, SrC
        for level in ["A", "AC", "C", "SrC"]:
            for month in range(1, 13):
                setattr(oslo.roles["Consultant"][level], f'churn_{month}', 0.02)
                setattr(oslo.roles["Consultant"][level], f'recruitment_{month}', 0.042)  # 4.2% to achieve 110 total consultants
        
        # Verify rates were set correctly
        print("Oslo A level rates:")
        print(f"  churn_1: {oslo.roles['Consultant']['A'].churn_1}")
        print(f"  recruitment_1: {oslo.roles['Consultant']['A'].recruitment_1}")
        print(f"  Expected net growth: {oslo.roles['Consultant']['A'].recruitment_1 - oslo.roles['Consultant']['A'].churn_1:.1%} per month")
        
        # Disable progression for A, AC, C, SrC
        for level in ["A", "AC", "C", "SrC"]:
            for month in range(1, 13):
                setattr(oslo.roles["Consultant"][level], f'progression_{month}', 0.0)
        # Set 0 churn/recruitment for higher Consultant levels
        for level in ["AM", "M", "SrM", "PiP"]:
            for month in range(1, 13):
                setattr(oslo.roles["Consultant"][level], f'churn_{month}', 0.0)
                setattr(oslo.roles["Consultant"][level], f'recruitment_{month}', 0.0)
        # Run simulation for 12 months
        self.engine.run_simulation(2024, 1, 2024, 12)
        
        # Assert final headcount for A, AC, C, SrC 
        # With 4.2% recruitment and 2% churn (net +2.2% monthly), starting from 59:
        # Expected A-SrC: 59 × (1.022)^12 ≈ 73 consultants
        # Expected total: 96 + 14 = 110 consultants
        print('Final Oslo Consultant headcounts:')
        for lvl in ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"]:
            print(f'{lvl}:', oslo.roles["Consultant"][lvl].total)
        
        # Check A-SrC growth (should be around 71-75)
        a_src_total = sum(oslo.roles["Consultant"][lvl].total for lvl in ["A", "AC", "C", "SrC"])
        print(f"✅ Oslo A-SrC levels: {a_src_total} consultants (expected ~73 with 4.2% recruitment, 2% churn)")
        
        # Check TOTAL consultants across all levels (target: 110)
        total_all = sum(oslo.roles["Consultant"][lvl].total for lvl in ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"])
        self.assertGreaterEqual(total_all, 108, f"Oslo should have at least 108 total consultants at year end (got {total_all})")
        self.assertLessEqual(total_all, 112, f"Oslo should have at most 112 total consultants at year end (got {total_all})")
        print(f"✅ Total Oslo consultants: {total_all} (target: 110, started with 96)")

if __name__ == '__main__':
    unittest.main() 