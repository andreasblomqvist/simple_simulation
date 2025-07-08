#!/usr/bin/env python3
"""
Test script to verify KPI calculations have reasonable non-zero values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import config_service
from backend.src.services.scenario_models import ScenarioRequest, ScenarioDefinition
import json

def test_kpi_verification():
    """Test that KPIs have reasonable non-zero values."""
    
    print("🔍 Testing KPI Verification...")
    
    # Initialize services
    scenario_service = ScenarioService(config_service)
    
    # Consultant recruitment values from screenshot (2025)
    consultant_recruitment = {
        "A": {"202501": 20, "202502": 20, "202503": 10, "202504": 15, "202505": 10, "202506": 10, "202507": 5, "202508": 20, "202509": 90, "202510": 20, "202511": 15, "202512": 10},
        "AC": {"202501": 8, "202502": 8, "202503": 8, "202504": 8, "202505": 8, "202506": 8, "202507": 8, "202508": 8, "202509": 8, "202510": 8, "202511": 8, "202512": 8},
        "C": {"202501": 4, "202502": 4, "202503": 4, "202504": 4, "202505": 4, "202506": 4, "202507": 4, "202508": 4, "202509": 4, "202510": 4, "202511": 4, "202512": 4},
        "SrC": {"202501": 1, "202502": 1, "202503": 1, "202504": 1, "202505": 1, "202506": 1, "202507": 1, "202508": 1, "202509": 1, "202510": 1, "202511": 1, "202512": 1},
        "AM": {"202501": 1, "202502": 1, "202503": 1, "202504": 1, "202505": 1, "202506": 1, "202507": 1, "202508": 1, "202509": 1, "202510": 1, "202511": 1, "202512": 1}
    }
    # Consultant churn values from screenshot (2025)
    consultant_churn = {
        "A": {"202501": 2, "202502": 2, "202503": 2, "202504": 2, "202505": 2, "202506": 2, "202507": 4, "202508": 2, "202509": 2, "202510": 2, "202511": 4, "202512": 2},
        "AC": {"202501": 4, "202502": 4, "202503": 4, "202504": 4, "202505": 4, "202506": 4, "202507": 4, "202508": 4, "202509": 4, "202510": 4, "202511": 4, "202512": 4},
        "C": {"202501": 7, "202502": 7, "202503": 7, "202504": 7, "202505": 7, "202506": 7, "202507": 7, "202508": 7, "202509": 7, "202510": 7, "202511": 7, "202512": 7},
        "SrC": {"202501": 7, "202502": 7, "202503": 7, "202504": 7, "202505": 7, "202506": 7, "202507": 7, "202508": 7, "202509": 7, "202510": 7, "202511": 7, "202512": 7},
        "AM": {"202501": 9, "202502": 9, "202503": 9, "202504": 9, "202505": 9, "202506": 9, "202507": 9, "202508": 9, "202509": 9, "202510": 9, "202511": 9, "202512": 9},
        "M": {"202501": 1, "202502": 1, "202503": 1, "202504": 1, "202505": 1, "202506": 1, "202507": 2, "202508": 1, "202509": 1, "202510": 1, "202511": 2, "202512": 1},
        "SrM": {"202501": 0, "202502": 1, "202503": 0, "202504": 0, "202505": 0, "202506": 0, "202507": 0, "202508": 0, "202509": 2, "202510": 1, "202511": 1, "202512": 1},
        "PiP": {"202501": 0, "202502": 0, "202503": 1, "202504": 0, "202505": 0, "202506": 0, "202507": 0, "202508": 0, "202509": 0, "202510": 0, "202511": 0, "202512": 0}
    }

    # All months in 2025
    months = [f"2025{m:02d}" for m in range(1, 13)]
    # All Consultant levels from screenshots
    consultant_levels = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"]
    # All roles (from config, but for this test, use a typical set)
    all_roles = ["Consultant", "Sales", "Recruitment", "Operations"]

    # Build zeroed recruitment/churn for non-Consultant roles
    zeroed_levels = {lvl: {month: 0 for month in months} for lvl in consultant_levels}
    zeroed_roles = {role: zeroed_levels for role in all_roles if role != "Consultant"}

    # Build baseline_input
    baseline_input = {
        "global": {
            "recruitment": {"Consultant": consultant_recruitment, **zeroed_roles},
            "churn": {"Consultant": consultant_churn, **zeroed_roles}
        }
    }

    # Create a test scenario with absolute numbers for Consultant, others zero
    test_scenario = ScenarioDefinition(
        name="KPI Test Scenario",
        description="Test scenario to verify KPI calculations with absolute Consultant values (others zero)",
        time_range={
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12
        },
        office_scope=["Stockholm", "Munich", "Amsterdam"],
        levers={},  # No price or economic levers
        baseline_input=baseline_input
    )
    
    # Create scenario request
    request = ScenarioRequest(
        scenario_definition=test_scenario
    )
    
    print("📊 Running test scenario...")
    
    # Run the scenario
    response = scenario_service.run_scenario(request)
    
    if response.status != "success":
        print(f"❌ Scenario failed: {response.error_message}")
        return False
    
    print(f"✅ Scenario completed successfully in {response.execution_time:.2f} seconds")
    
    # Extract results
    results = response.results
    
    print("\n📈 KPI Verification Results:")
    print("=" * 50)
    
    # Check if results have the expected structure
    if not isinstance(results, dict):
        print("❌ Results is not a dictionary")
        return False
    
    # Verify financial KPIs
    print("\n💰 Financial KPIs:")
    financial_checks = [
        ("baseline_total_fte", "Baseline Total FTE"),
        ("current_total_fte", "Current Total FTE"),
        ("baseline_total_sales", "Baseline Total Sales"),
        ("current_total_sales", "Current Total Sales"),
        ("baseline_total_ebitda", "Baseline Total EBITDA"),
        ("current_total_ebitda", "Current Total EBITDA"),
        ("baseline_ebitda_margin", "Baseline EBITDA Margin"),
        ("current_ebitda_margin", "Current EBITDA Margin"),
        ("avg_hourly_rate_baseline", "Baseline Avg Hourly Rate"),
        ("avg_hourly_rate", "Current Avg Hourly Rate")
    ]
    
    financial_passed = 0
    for key, name in financial_checks:
        value = results.get(key, 0)
        if isinstance(value, (int, float)) and value > 0:
            print(f"  ✅ {name}: {value:,.2f}")
            financial_passed += 1
        else:
            print(f"  ❌ {name}: {value} (should be > 0)")
    
    # Verify growth KPIs
    print("\n📈 Growth KPIs:")
    growth_checks = [
        ("total_growth_absolute", "Total Growth (Absolute)"),
        ("total_growth_percentage", "Total Growth (%)"),
        ("fte_growth_absolute", "FTE Growth (Absolute)"),
        ("fte_growth_percentage", "FTE Growth (%)"),
        ("sales_growth_absolute", "Sales Growth (Absolute)"),
        ("sales_growth_percentage", "Sales Growth (%)"),
        ("ebitda_growth_absolute", "EBITDA Growth (Absolute)"),
        ("ebitda_growth_percentage", "EBITDA Growth (%)")
    ]
    
    growth_passed = 0
    for key, name in growth_checks:
        value = results.get(key, 0)
        if isinstance(value, (int, float)):
            print(f"  ✅ {name}: {value:,.2f}")
            growth_passed += 1
        else:
            print(f"  ❌ {name}: {value} (should be numeric)")
    
    # Verify journey KPIs
    print("\n🎯 Journey KPIs:")
    journey_checks = [
        ("journey_1_fte", "Journey 1 FTE"),
        ("journey_2_fte", "Journey 2 FTE"),
        ("journey_3_fte", "Journey 3 FTE"),
        ("journey_4_fte", "Journey 4 FTE"),
        ("journey_1_percentage", "Journey 1 (%)"),
        ("journey_2_percentage", "Journey 2 (%)"),
        ("journey_3_percentage", "Journey 3 (%)"),
        ("journey_4_percentage", "Journey 4 (%)")
    ]
    
    journey_passed = 0
    for key, name in journey_checks:
        value = results.get(key, 0)
        if isinstance(value, (int, float)) and value >= 0:
            print(f"  ✅ {name}: {value:,.2f}")
            journey_passed += 1
        else:
            print(f"  ❌ {name}: {value} (should be >= 0)")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"  Financial KPIs: {financial_passed}/{len(financial_checks)} passed")
    print(f"  Growth KPIs: {growth_passed}/{len(growth_checks)} passed")
    print(f"  Journey KPIs: {journey_passed}/{len(journey_checks)} passed")
    
    total_passed = financial_passed + growth_passed + journey_passed
    total_checks = len(financial_checks) + len(growth_checks) + len(journey_checks)
    
    print(f"\n  Overall: {total_passed}/{total_checks} KPIs passed")
    
    if total_passed == total_checks:
        print("🎉 All KPIs verified successfully!")
        return True
    else:
        print("⚠️  Some KPIs need attention")
        return False

if __name__ == "__main__":
    success = test_kpi_verification()
    sys.exit(0 if success else 1) 