"""
Unit tests for simulation mechanisms via ScenarioService.

These tests focus on one mechanism at a time with deterministic results
and absolute number assertions to verify the simulation engine works correctly.
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock

from src.services.scenario_service import ScenarioService
from src.services.scenario_storage import ScenarioStorageService
from src.services.scenario_models import (
    ScenarioRequest, ScenarioDefinition, ScenarioListResponse, ScenarioComparisonRequest
)
from src.services.kpi.kpi_models import EconomicParameters


class TestSimulationMechanisms:
    """Test individual simulation mechanisms with deterministic results."""
    
    @pytest.fixture
    def mock_config_service(self):
        """Create a mock config service for the minimal config."""
        mock = Mock()
        # We'll set the return_value in each test
        return mock

    @pytest.fixture
    def scenario_service(self, mock_config_service):
        """Create a ScenarioService instance with mock config service."""
        storage_service = ScenarioStorageService()
        return ScenarioService(mock_config_service)
    
    @pytest.fixture
    def base_economic_params(self):
        """Base economic parameters for testing."""
        return {
            'unplanned_absence': 0.05,
            'other_expense': 19000000.0,
            'employment_cost_rate': 0.40,
            'working_hours_per_month': 166.4,
            'utilization': 0.85
        }
    
    def create_minimal_config(self, office_name: str = "TestOffice") -> Dict[str, Any]:
        """Create a minimal office configuration for testing."""
        return {
            office_name: {
                "name": office_name,
                "total_fte": 100,
                "journey": "New Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 100.0,
                            "price_1": 1200.0,
                            "price_2": 1300.0,
                            "price_3": 1400.0,
                            "salary": 80000.0,
                            "recruitment_rate": 0.0,  # Will be overridden in tests
                            "churn_rate": 0.0,        # Will be overridden in tests
                            "progression_rates": {}   # Will be overridden in tests
                        }
                    }
                }
            }
        }
    
    def test_recruitment_mechanism(self, scenario_service, base_economic_params, mock_config_service):
        """
        Test recruitment mechanism in isolation.
        
        Setup: 1 office, 1 role, 1 level, FTE=100, recruitment=5%, no churn, no progression
        Expected: After 1 month, FTE should be 105
        """
        # Create minimal config with 5% recruitment rate
        config = self.create_minimal_config()
        config["TestOffice"]["roles"]["Consultant"]["A"]["recruitment_rate"] = 0.05
        mock_config_service.get_config.return_value = config
        
        # Create scenario definition
        scenario_def = ScenarioDefinition(
            name="Recruitment Test",
            description="Test recruitment mechanism in isolation",
            time_range={
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2025,
                "end_month": 2  # 2 months to see the effect
            },
            office_scope=["TestOffice"],
            levers={},  # No levers
            economic_params=base_economic_params,
            baseline_input=config
        )
        
        # Run scenario
        request = ScenarioRequest(scenario_definition=scenario_def)
        response = scenario_service.run_scenario(request)
        
        # Extract results
        results = response.results
        print('RESULTS:', results)
        year_2025 = results["years"]["2025"]
        
        # Check initial FTE (month 1)
        month_1_fte = year_2025["offices"]["TestOffice"]["total_fte"]
        assert month_1_fte == 100, f"Initial FTE should be 100, got {month_1_fte}"
        
        # Check FTE after recruitment (month 2)
        year_2026 = results["years"]["2026"]
        month_2_fte = year_2026["offices"]["TestOffice"]["total_fte"]
        expected_fte = 100 * (1 + 0.05)  # 100 + 5% = 105
        assert month_2_fte == expected_fte, f"FTE after recruitment should be {expected_fte}, got {month_2_fte}"
        
        # Check financial KPIs are calculated
        office_financial = year_2026["offices"]["TestOffice"]["financial"]
        assert office_financial["total_revenue"] > 0, "Revenue should be positive"
        assert office_financial["total_salary_costs"] > 0, "Salary costs should be positive"
        assert office_financial["ebitda"] != 0, "EBITDA should be calculated"
    
    def test_churn_mechanism(self, scenario_service, base_economic_params, mock_config_service):
        """
        Test churn mechanism in isolation.
        
        Setup: 1 office, 1 role, 1 level, FTE=100, no recruitment, churn=10%, no progression
        Expected: After 1 month, FTE should be 90
        """
        # Create minimal config with 10% churn rate
        config = self.create_minimal_config()
        config["TestOffice"]["roles"]["Consultant"]["A"]["churn_rate"] = 0.10
        mock_config_service.get_config.return_value = config
        
        # Create scenario definition
        scenario_def = ScenarioDefinition(
            name="Churn Test",
            description="Test churn mechanism in isolation",
            time_range={
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2025,
                "end_month": 2
            },
            office_scope=["TestOffice"],
            levers={},
            economic_params=base_economic_params,
            baseline_input=config
        )
        
        # Run scenario
        request = ScenarioRequest(scenario_definition=scenario_def)
        response = scenario_service.run_scenario(request)
        
        # Extract results
        results = response.results
        print('RESULTS:', results)
        year_2025 = results["years"]["2025"]
        year_2026 = results["years"]["2026"]
        
        # Check initial FTE
        month_1_fte = year_2025["offices"]["TestOffice"]["total_fte"]
        assert month_1_fte == 100, f"Initial FTE should be 100, got {month_1_fte}"
        
        # Check FTE after churn
        month_2_fte = year_2026["offices"]["TestOffice"]["total_fte"]
        expected_fte = 100 * (1 - 0.10)  # 100 - 10% = 90
        assert month_2_fte == expected_fte, f"FTE after churn should be {expected_fte}, got {month_2_fte}"
    
    def test_progression_mechanism(self, scenario_service, base_economic_params, mock_config_service):
        """
        Test progression mechanism in isolation.
        
        Setup: 1 office, 1 role, 2 levels (A, B), FTE=100 at A, progression A→B=10%, no recruitment, no churn
        Expected: After 1 month, A=90, B=10
        """
        # Create config with 2 levels and progression
        config = {
            "TestOffice": {
                "name": "TestOffice",
                "total_fte": 100,
                "journey": "New Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 100.0,
                            "price_1": 1200.0,
                            "price_2": 1300.0,
                            "price_3": 1400.0,
                            "salary": 80000.0,
                            "recruitment_rate": 0.0,
                            "churn_rate": 0.0,
                            "progression_rates": {"B": 0.10}  # 10% progression to B
                        },
                        "B": {
                            "fte": 0.0,  # Start with 0 FTE
                            "price_1": 1400.0,
                            "price_2": 1500.0,
                            "price_3": 1600.0,
                            "salary": 100000.0,
                            "recruitment_rate": 0.0,
                            "churn_rate": 0.0,
                            "progression_rates": {}
                        }
                    }
                }
            }
        }
        mock_config_service.get_config.return_value = config
        
        # Create scenario definition
        scenario_def = ScenarioDefinition(
            name="Progression Test",
            description="Test progression mechanism in isolation",
            time_range={
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2025,
                "end_month": 2
            },
            office_scope=["TestOffice"],
            levers={},
            economic_params=base_economic_params,
            baseline_input=config
        )
        
        # Run scenario
        request = ScenarioRequest(scenario_definition=scenario_def)
        response = scenario_service.run_scenario(request)
        
        # Extract results
        results = response.results
        print('RESULTS:', results)
        year_2025 = results["years"]["2025"]
        year_2026 = results["years"]["2026"]
        
        # Check initial FTE distribution
        month_1_levels = year_2025["offices"]["TestOffice"]["levels"]
        level_a_fte_1 = month_1_levels["Consultant"]["A"]["fte"]
        level_b_fte_1 = month_1_levels["Consultant"]["B"]["fte"]
        assert level_a_fte_1 == 100, f"Initial A level FTE should be 100, got {level_a_fte_1}"
        assert level_b_fte_1 == 0, f"Initial B level FTE should be 0, got {level_b_fte_1}"
        
        # Check FTE distribution after progression
        month_2_levels = year_2026["offices"]["TestOffice"]["levels"]
        level_a_fte_2 = month_2_levels["Consultant"]["A"]["fte"]
        level_b_fte_2 = month_2_levels["Consultant"]["B"]["fte"]
        expected_a_fte = 100 * (1 - 0.10)  # 100 - 10% = 90
        expected_b_fte = 100 * 0.10        # 100 * 10% = 10
        
        assert level_a_fte_2 == expected_a_fte, f"A level FTE after progression should be {expected_a_fte}, got {level_a_fte_2}"
        assert level_b_fte_2 == expected_b_fte, f"B level FTE after progression should be {expected_b_fte}, got {level_b_fte_2}"
        
        # Check total FTE remains the same
        total_fte_2 = year_2026["offices"]["TestOffice"]["total_fte"]
        assert total_fte_2 == 100, f"Total FTE should remain 100, got {total_fte_2}"
    
    def test_combined_mechanisms(self, scenario_service, base_economic_params, mock_config_service):
        """
        Test combined mechanisms with realistic values.
        
        Setup: 1 office, 1 role, 1 level, FTE=100, recruitment=5%, churn=2%, no progression
        Expected: After 1 month, FTE should be 100 * (1 + 0.05 - 0.02) = 103
        """
        # Create config with both recruitment and churn
        config = self.create_minimal_config()
        config["TestOffice"]["roles"]["Consultant"]["A"]["recruitment_rate"] = 0.05
        config["TestOffice"]["roles"]["Consultant"]["A"]["churn_rate"] = 0.02
        mock_config_service.get_config.return_value = config
        
        # Create scenario definition
        scenario_def = ScenarioDefinition(
            name="Combined Mechanisms Test",
            description="Test recruitment and churn together",
            time_range={
                "start_year": 2025,
                "start_month": 1,
                "end_year": 2025,
                "end_month": 2
            },
            office_scope=["TestOffice"],
            levers={},
            economic_params=base_economic_params,
            baseline_input=config
        )
        
        # Run scenario
        request = ScenarioRequest(scenario_definition=scenario_def)
        response = scenario_service.run_scenario(request)
        
        # Extract results
        results = response.results
        print('RESULTS:', results)
        year_2026 = results["years"]["2026"]
        
        # Check FTE after combined effects
        month_2_fte = year_2026["offices"]["TestOffice"]["total_fte"]
        expected_fte = 100 * (1 + 0.05 - 0.02)  # 100 + 5% - 2% = 103
        assert month_2_fte == expected_fte, f"FTE after combined mechanisms should be {expected_fte}, got {month_2_fte}"
        
        # Check that financial KPIs are calculated and reasonable
        office_financial = year_2026["offices"]["TestOffice"]["financial"]
        assert office_financial["total_revenue"] > 0, "Revenue should be positive"
        assert office_financial["total_salary_costs"] > 0, "Salary costs should be positive"
        assert office_financial["ebitda"] != 0, "EBITDA should be calculated"
        
        # Check that growth KPIs are calculated
        office_growth = year_2026["offices"]["TestOffice"]["growth"]
        assert "fte_growth_rate" in office_growth, "FTE growth rate should be calculated"
        assert office_growth["fte_growth_rate"] > 0, "FTE growth rate should be positive with net recruitment" 