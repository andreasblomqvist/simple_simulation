"""
Shared fixtures and test utilities for SimpleSim Engine V2 tests

Provides comprehensive test data including:
- Mock scenarios and business plans
- Population snapshots with realistic workforce data
- CAT matrices and economic parameters
- Mock external dependencies
- Test utilities and helpers
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, List, Any
from datetime import datetime, date
import json
import uuid
import random

# Import V2 engine components
from backend.src.services.simulation_engine_v2 import (
    Person, PersonEvent, EventType, CATMatrix, PopulationSnapshot,
    WorkforceEntry, BusinessPlan, MonthlyPlan, EconomicParameters,
    GrowthRates, Levers, TimeRange, ScenarioRequest, MonthlyTargets,
    SimulationResults, SimulationEngineV2Factory
)

from backend.src.services.workforce_manager_v2 import (
    WorkforceManagerV2, ChurnConfiguration, ProgressionConfiguration,
    RecruitmentConfiguration
)

from backend.src.services.business_plan_processor_v2 import BusinessPlanProcessorV2
from backend.src.services.growth_model_manager_v2 import GrowthModelManagerV2
from backend.src.services.snapshot_loader_v2 import SnapshotLoaderV2
from backend.src.services.kpi_calculator_v2 import KPICalculatorV2


# ============================================================================
# Test Configuration
# ============================================================================

@pytest.fixture(scope="session")
def test_seed():
    """Fixed seed for deterministic testing"""
    return 42


@pytest.fixture(scope="session")
def test_offices():
    """Standard test offices"""
    return ["Stockholm", "Munich", "London"]


@pytest.fixture(scope="session")
def test_roles():
    """Standard test roles and levels"""
    return {
        "Consultant": ["A", "AC", "C", "SC", "P", "SP"],
        "Operations": ["Junior", "Senior"],
        "Marketing": ["Specialist", "Manager"]
    }


# ============================================================================
# Mock External Dependencies
# ============================================================================

@pytest.fixture
def mock_config_service():
    """Mock configuration service with realistic office data"""
    mock = Mock()
    mock.get_config.return_value = {
        "Stockholm": {
            "name": "Stockholm",
            "total_fte": 850.0,
            "journey": "Mature Office",
            "economic_parameters": {
                "base_salary_multiplier": 1.0,
                "price_multiplier": 1.1,
                "cost_of_living_adjustment": 1.15,
                "tax_rate": 0.32
            },
            "roles": {
                "Consultant": {
                    "A": {"fte": 120.0, "recruitment_1": 8.0, "churn_1": 4.0, "price_1": 1200.0, "salary_1": 45000.0},
                    "AC": {"fte": 100.0, "recruitment_1": 6.0, "churn_1": 3.0, "price_1": 1400.0, "salary_1": 55000.0},
                    "C": {"fte": 80.0, "recruitment_1": 4.0, "churn_1": 2.0, "price_1": 1600.0, "salary_1": 65000.0},
                    "SC": {"fte": 60.0, "recruitment_1": 2.0, "churn_1": 1.0, "price_1": 1800.0, "salary_1": 75000.0},
                    "P": {"fte": 40.0, "recruitment_1": 1.0, "churn_1": 0.5, "price_1": 2000.0, "salary_1": 85000.0},
                    "SP": {"fte": 20.0, "recruitment_1": 0.5, "churn_1": 0.2, "price_1": 2200.0, "salary_1": 95000.0}
                },
                "Operations": {
                    "Junior": {"fte": 15.0, "recruitment_1": 2.0, "churn_1": 1.5, "price_1": 800.0, "salary_1": 35000.0},
                    "Senior": {"fte": 10.0, "recruitment_1": 1.0, "churn_1": 0.5, "price_1": 1000.0, "salary_1": 45000.0}
                }
            }
        },
        "Munich": {
            "name": "Munich", 
            "total_fte": 450.0,
            "journey": "Growth Office",
            "economic_parameters": {
                "base_salary_multiplier": 0.95,
                "price_multiplier": 1.05,
                "cost_of_living_adjustment": 1.08,
                "tax_rate": 0.35
            },
            "roles": {
                "Consultant": {
                    "A": {"fte": 80.0, "recruitment_1": 6.0, "churn_1": 3.0, "price_1": 1100.0, "salary_1": 42000.0},
                    "AC": {"fte": 60.0, "recruitment_1": 4.0, "churn_1": 2.0, "price_1": 1300.0, "salary_1": 52000.0},
                    "C": {"fte": 40.0, "recruitment_1": 2.0, "churn_1": 1.0, "price_1": 1500.0, "salary_1": 62000.0}
                },
                "Operations": {
                    "Junior": {"fte": 8.0, "recruitment_1": 1.5, "churn_1": 1.0, "price_1": 750.0, "salary_1": 33000.0},
                    "Senior": {"fte": 5.0, "recruitment_1": 0.5, "churn_1": 0.3, "price_1": 950.0, "salary_1": 43000.0}
                }
            }
        }
    }
    return mock


@pytest.fixture
def mock_database():
    """Mock database with realistic stored data"""
    mock = Mock()
    
    # Mock snapshot data
    mock.get_snapshots.return_value = [
        {
            "id": "snapshot-1",
            "office_id": "Stockholm",
            "snapshot_date": "2025-01",
            "name": "Stockholm Baseline 2025",
            "workforce": []  # Will be populated by other fixtures
        }
    ]
    
    # Mock business plan data  
    mock.get_business_plans.return_value = [
        {
            "id": "plan-1",
            "office_id": "Stockholm", 
            "name": "Stockholm Growth Plan 2025-2027",
            "monthly_plans": {}  # Will be populated by other fixtures
        }
    ]
    
    return mock


# ============================================================================
# Population Snapshot Fixtures
# ============================================================================

@pytest.fixture
def sample_workforce_entries():
    """Generate realistic workforce entries for testing"""
    entries = []
    
    # Stockholm Consultants
    consultant_levels = ["A", "AC", "C", "SC", "P", "SP"]
    consultant_counts = [120, 100, 80, 60, 40, 20]
    
    for level, count in zip(consultant_levels, consultant_counts):
        for i in range(count):
            hire_year = random.randint(2020, 2024)
            hire_month = random.randint(1, 12)
            level_start_year = random.randint(hire_year, 2024)
            level_start_month = random.randint(1, 12)
            
            entries.append(WorkforceEntry(
                id=f"consultant-{level}-{i+1}",
                role="Consultant",
                level=level,
                hire_date=f"{hire_year:04d}-{hire_month:02d}",
                level_start_date=f"{level_start_year:04d}-{level_start_month:02d}",
                office="Stockholm"
            ))
    
    # Stockholm Operations
    for level, count in [("Junior", 15), ("Senior", 10)]:
        for i in range(count):
            hire_year = random.randint(2021, 2024)
            hire_month = random.randint(1, 12)
            
            entries.append(WorkforceEntry(
                id=f"operations-{level.lower()}-{i+1}",
                role="Operations",
                level=level,
                hire_date=f"{hire_year:04d}-{hire_month:02d}",
                level_start_date=f"{hire_year:04d}-{hire_month:02d}",
                office="Stockholm"
            ))
    
    return entries


@pytest.fixture
def population_snapshot(sample_workforce_entries):
    """Complete population snapshot for testing"""
    return PopulationSnapshot(
        id="test-snapshot-stockholm-2025-01",
        office_id="Stockholm",
        snapshot_date="2025-01",
        name="Stockholm Test Snapshot",
        workforce=sample_workforce_entries
    )


# ============================================================================
# Business Plan Fixtures
# ============================================================================

@pytest.fixture
def sample_monthly_plans():
    """Generate realistic monthly business plans"""
    plans = {}
    
    # Generate plans for 2025-2027
    for year in range(2025, 2028):
        for month in range(1, 13):
            key = f"{year:04d}-{month:02d}"
            
            # Base targets with seasonal variation
            seasonal_factor = 1.0 + 0.1 * (month - 6.5) / 6.5  # Higher in Q4, lower in Q1
            
            plans[key] = MonthlyPlan(
                year=year,
                month=month,
                recruitment={
                    "Consultant": {
                        "A": 8.0 * seasonal_factor,
                        "AC": 6.0 * seasonal_factor,
                        "C": 4.0 * seasonal_factor,
                        "SC": 2.0 * seasonal_factor,
                        "P": 1.0 * seasonal_factor,
                        "SP": 0.5 * seasonal_factor
                    },
                    "Operations": {
                        "Junior": 2.0 * seasonal_factor,
                        "Senior": 1.0 * seasonal_factor
                    }
                },
                churn={
                    "Consultant": {
                        "A": 4.0,
                        "AC": 3.0,
                        "C": 2.0,
                        "SC": 1.0,
                        "P": 0.5,
                        "SP": 0.2
                    },
                    "Operations": {
                        "Junior": 1.5,
                        "Senior": 0.5
                    }
                },
                revenue=850000.0 + (year - 2025) * 50000,  # Growing revenue
                costs=650000.0 + (year - 2025) * 30000,    # Growing costs
                price_per_role={
                    "Consultant": {
                        "A": 1200.0 * (1.03 ** (year - 2025)),
                        "AC": 1400.0 * (1.03 ** (year - 2025)),
                        "C": 1600.0 * (1.03 ** (year - 2025)),
                        "SC": 1800.0 * (1.03 ** (year - 2025)),
                        "P": 2000.0 * (1.03 ** (year - 2025)),
                        "SP": 2200.0 * (1.03 ** (year - 2025))
                    }
                },
                salary_per_role={
                    "Consultant": {
                        "A": 45000.0 * (1.025 ** (year - 2025)),
                        "AC": 55000.0 * (1.025 ** (year - 2025)),
                        "C": 65000.0 * (1.025 ** (year - 2025)),
                        "SC": 75000.0 * (1.025 ** (year - 2025)),
                        "P": 85000.0 * (1.025 ** (year - 2025)),
                        "SP": 95000.0 * (1.025 ** (year - 2025))
                    }
                },
                utr_per_role={
                    "Consultant": {
                        "A": 0.75,
                        "AC": 0.80,
                        "C": 0.85,
                        "SC": 0.90,
                        "P": 0.90,
                        "SP": 0.85
                    }
                }
            )
    
    return plans


@pytest.fixture
def business_plan(sample_monthly_plans):
    """Complete business plan for testing"""
    return BusinessPlan(
        office_id="Stockholm",
        name="Stockholm Test Business Plan 2025-2027",
        monthly_plans=sample_monthly_plans
    )


# ============================================================================
# CAT Matrix Fixtures
# ============================================================================

@pytest.fixture
def cat_matrix():
    """Realistic CAT matrix with progression probabilities"""
    return CATMatrix(
        progression_probabilities={
            "A": {"High": 0.8, "Medium": 0.4, "Low": 0.1},
            "AC": {"High": 0.7, "Medium": 0.35, "Low": 0.08},
            "C": {"High": 0.6, "Medium": 0.3, "Low": 0.06},
            "SC": {"High": 0.5, "Medium": 0.25, "Low": 0.05},
            "P": {"High": 0.4, "Medium": 0.2, "Low": 0.04},
            "SP": {"High": 0.0, "Medium": 0.0, "Low": 0.0}  # No progression from top level
        }
    )


# ============================================================================
# Economic Parameter Fixtures
# ============================================================================

@pytest.fixture
def economic_parameters():
    """Standard economic parameters for testing"""
    return EconomicParameters(
        base_salary_multiplier=1.0,
        price_multiplier=1.1,
        cost_of_living_adjustment=1.15,
        tax_rate=0.32
    )


@pytest.fixture
def growth_rates():
    """Standard growth rates for multi-year testing"""
    return GrowthRates(
        recruitment_growth_rate=0.05,  # 5% per year
        price_growth_rate=0.03,        # 3% per year
        salary_growth_rate=0.025,      # 2.5% per year
        cost_growth_rate=0.02          # 2% per year
    )


# ============================================================================
# Scenario Fixtures
# ============================================================================

@pytest.fixture
def base_scenario():
    """Basic scenario request for testing"""
    return ScenarioRequest(
        name="Test Scenario - Base Case",
        description="Standard test scenario with baseline parameters",
        time_range=TimeRange(
            start_year=2025,
            start_month=1,
            end_year=2027,
            end_month=12
        ),
        office_scope=["Stockholm"],
        levers=Levers(),  # Default levers (all 1.0)
        use_snapshot=True,
        snapshot_id="test-snapshot-stockholm-2025-01",
        use_business_plan=True,
        business_plan_id="test-business-plan-stockholm"
    )


@pytest.fixture
def growth_scenario():
    """Growth scenario with increased recruitment"""
    return ScenarioRequest(
        name="Test Scenario - Growth",
        description="Growth scenario with 20% increased recruitment",
        time_range=TimeRange(
            start_year=2025,
            start_month=1,
            end_year=2027,
            end_month=12
        ),
        office_scope=["Stockholm"],
        levers=Levers(
            recruitment_multiplier=1.2,
            price_multiplier=1.05
        ),
        use_snapshot=True,
        snapshot_id="test-snapshot-stockholm-2025-01",
        use_business_plan=True,
        business_plan_id="test-business-plan-stockholm"
    )


@pytest.fixture
def multi_office_scenario():
    """Multi-office scenario for integration testing"""
    return ScenarioRequest(
        name="Test Scenario - Multi-Office",
        description="Multi-office scenario covering Stockholm and Munich",
        time_range=TimeRange(
            start_year=2025,
            start_month=1,
            end_year=2026,
            end_month=12
        ),
        office_scope=["Stockholm", "Munich"],
        levers=Levers(
            recruitment_multiplier=1.1,
            churn_multiplier=0.9
        ),
        use_snapshot=True,
        use_business_plan=True
    )


# ============================================================================
# Component Configuration Fixtures
# ============================================================================

@pytest.fixture
def churn_config():
    """Standard churn configuration for testing"""
    return ChurnConfiguration(
        method="random",
        tenure_bias=0.1,
        preserve_top_performers=True
    )


@pytest.fixture
def progression_config():
    """Standard progression configuration for testing"""
    return ProgressionConfiguration(
        progression_months=[1, 7],  # January and July
        minimum_tenure_months=6,
        use_cat_probabilities=True
    )


@pytest.fixture
def recruitment_config():
    """Standard recruitment configuration for testing"""
    return RecruitmentConfiguration(
        default_hire_level="A",
        distribution_strategy="entry_level"
    )


# ============================================================================
# Mock Engine Components
# ============================================================================

@pytest.fixture
def mock_workforce_manager():
    """Mock workforce manager for integration testing"""
    mock = Mock(spec=WorkforceManagerV2)
    
    # Mock return values for common operations
    mock.process_month.return_value = ([], [])  # (events, updated_persons)
    mock.process_recruitment.return_value = []
    mock.process_churn.return_value = []
    mock.process_progression.return_value = []
    mock.get_workforce_counts.return_value = {"Consultant": {"A": 120}}
    
    return mock


@pytest.fixture  
def mock_business_plan_processor():
    """Mock business plan processor for testing"""
    mock = Mock(spec=BusinessPlanProcessorV2)
    
    # Mock monthly targets
    mock.get_monthly_targets.return_value = MonthlyTargets(
        recruitment_targets={"Consultant": {"A": 8.0}},
        churn_targets={"Consultant": {"A": 4.0}},
        revenue_target=850000.0,
        cost_target=650000.0,
        salary_budget=45000000.0
    )
    
    return mock


@pytest.fixture
def mock_kpi_calculator():
    """Mock KPI calculator for testing"""
    mock = Mock(spec=KPICalculatorV2)
    
    # Mock KPI calculations
    mock.calculate_monthly_kpis.return_value = {
        "total_fte": 850.0,
        "total_recruitment": 24.5,
        "total_churn": 12.2,
        "net_recruitment": 12.3,
        "revenue": 850000.0,
        "costs": 650000.0,
        "profit": 200000.0
    }
    
    return mock


# ============================================================================
# Test Utilities
# ============================================================================

@pytest.fixture
def test_person_factory():
    """Factory for creating test persons"""
    def create_person(
        role: str = "Consultant",
        level: str = "A",
        office: str = "Stockholm",
        hire_date: str = "2024-01",
        **kwargs
    ) -> Person:
        return Person(
            id=str(uuid.uuid4()),
            role=role,
            level=level,
            office=office,
            hire_date=hire_date,
            level_start_date=hire_date,
            cat_rating="Medium",
            salary=45000.0,
            events=[],
            **kwargs
        )
    return create_person


@pytest.fixture
def event_validator():
    """Utility for validating person events"""
    def validate_event(event: PersonEvent, expected_type: EventType):
        assert event.event_type == expected_type
        assert event.date is not None
        assert event.simulation_month >= 0
        assert event.details is not None
        return True
    return validate_event


@pytest.fixture
def results_validator():
    """Utility for validating simulation results"""
    def validate_results(results: SimulationResults):
        assert results.scenario_id is not None
        assert len(results.monthly_results) > 0
        assert results.execution_metadata is not None
        assert results.execution_metadata.get("execution_time_seconds", 0) > 0
        return True
    return validate_results


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def large_workforce_entries():
    """Generate large workforce dataset for performance testing"""
    entries = []
    
    # Generate 1000+ persons across different roles and offices
    for office in ["Stockholm", "Munich", "London"]:
        for role in ["Consultant", "Operations", "Marketing"]:
            levels = ["A", "AC", "C"] if role == "Consultant" else ["Junior", "Senior"]
            
            for level in levels:
                count = 100 if role == "Consultant" else 50
                for i in range(count):
                    hire_year = random.randint(2020, 2024)
                    hire_month = random.randint(1, 12)
                    
                    entries.append(WorkforceEntry(
                        id=f"{office.lower()}-{role.lower()}-{level.lower()}-{i+1}",
                        role=role,
                        level=level,
                        hire_date=f"{hire_year:04d}-{hire_month:02d}",
                        level_start_date=f"{hire_year:04d}-{hire_month:02d}",
                        office=office
                    ))
    
    return entries


@pytest.fixture
def performance_snapshot(large_workforce_entries):
    """Large population snapshot for performance testing"""
    return PopulationSnapshot(
        id="performance-test-snapshot",
        office_id="Multi-Office",
        snapshot_date="2025-01",
        name="Performance Test Snapshot - 1000+ Persons",
        workforce=large_workforce_entries
    )


@pytest.fixture
def memory_profiler():
    """Memory usage profiling utility"""
    def profile_memory(func, *args, **kwargs):
        import tracemalloc
        import gc
        
        # Start memory tracing
        tracemalloc.start()
        gc.collect()
        
        # Take initial snapshot
        initial_memory = tracemalloc.take_snapshot()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Take final snapshot
        final_memory = tracemalloc.take_snapshot()
        
        # Calculate memory usage
        top_stats = final_memory.compare_to(initial_memory, 'lineno')
        total_memory = sum(stat.size_diff for stat in top_stats)
        
        tracemalloc.stop()
        
        return result, total_memory
    
    return profile_memory