"""
Simple Test Data Generator for V2 Engine - No Unicode
"""

import json
import random
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def create_simple_test_data():
    """Create simple but comprehensive test data"""
    print("Creating V2 Engine Test Data...")
    print("=" * 50)
    
    random.seed(2024)  # Deterministic
    
    # Create test data directory
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    # 1. Create population snapshot for London office
    print("Creating population snapshot...")
    
    workforce_data = []
    person_id = 1
    
    # Create 50 people with realistic distribution
    roles_count = {"Consultant": 30, "Sales": 15, "Recruitment": 3, "Operations": 2}
    
    for role, count in roles_count.items():
        if role == "Operations":
            levels = ["Operations"]
        elif role == "Consultant":
            levels = ["A", "AC", "C", "SrC", "M"]
        elif role == "Sales":
            levels = ["A", "AC", "C"]
        else:  # Recruitment
            levels = ["A", "AC", "C"]
        
        for i in range(count):
            # Distribute across levels
            if role == "Operations":
                level = "Operations"
            else:
                level_weights = [0.4, 0.3, 0.2, 0.1] if len(levels) >= 4 else [0.5, 0.3, 0.2]
                level = random.choices(levels[:len(level_weights)], weights=level_weights)[0]
            
            # Random hire date (6 months to 3 years ago)
            months_ago = random.randint(6, 36)
            hire_date = date(2024, 1, 1) - timedelta(days=months_ago * 30)
            
            workforce_data.append({
                "id": f"london_person_{person_id:04d}",
                "role": role,
                "level": level,
                "hire_date": hire_date.strftime("%Y-%m"),
                "level_start_date": hire_date.strftime("%Y-%m"),
                "office": "london"
            })
            person_id += 1
    
    # Save population snapshot
    population_snapshot = {
        "london": {
            "id": "london_baseline_2024",
            "office_id": "london",
            "snapshot_date": "2024-01",
            "name": "London Office Baseline - January 2024",
            "workforce": workforce_data
        }
    }
    
    with open(test_data_dir / "population_snapshots.json", 'w') as f:
        json.dump(population_snapshot, f, indent=2)
    
    print(f"  Created population snapshot: {len(workforce_data)} people")
    
    # 2. Create business plan with realistic recruitment targets
    print("Creating business plan...")
    
    monthly_plans = {}
    for month in range(1, 25):  # 24 months
        year = 2024 if month <= 12 else 2025
        month_num = month if month <= 12 else month - 12
        month_key = f"{year}-{month_num:02d}"
        
        monthly_plans[month_key] = {
            "month": month_key,
            "revenue": 500000 + random.randint(-50000, 100000),
            "costs": 400000 + random.randint(-30000, 50000),
            "recruitment": {
                "Consultant": {"A": 2, "AC": 1, "C": 0 if month % 3 != 0 else 1},
                "Sales": {"A": 1, "AC": 0 if month % 2 != 0 else 1},
                "Recruitment": {"A": 1 if month % 6 == 0 else 0},
                "Operations": {"Operations": 1 if month % 12 == 0 else 0}
            },
            "churn": {
                "Consultant": {"A": 1, "AC": 0 if month % 2 != 0 else 1, "C": 0, "SrC": 0, "M": 0},
                "Sales": {"A": 0 if month % 3 != 0 else 1, "AC": 0, "C": 0},
                "Recruitment": {"A": 0, "AC": 0, "C": 0},
                "Operations": {"Operations": 0}
            },
            "targets": {
                "revenue_target": 600000,
                "headcount_target": 50 + (month * 2),  # Growth target
                "utilization_target": 0.85,
                "client_satisfaction": 0.92
            }
        }
    
    business_plan = {
        "london": {
            "office_id": "london",
            "plan_id": "london_growth_2024_2025",
            "name": "London Office Growth Plan 2024-2025",
            "monthly_plans": monthly_plans
        }
    }
    
    with open(test_data_dir / "business_plans.json", 'w') as f:
        json.dump(business_plan, f, indent=2)
    
    print(f"  Created business plan: {len(monthly_plans)} monthly plans")
    
    # 3. Create CAT matrix for career progression
    print("Creating CAT matrices...")
    
    cat_matrices = {
        "Consultant": {
            "role": "Consultant",
            "progression_probabilities": {
                "A": {"AC": 0.15, "C": 0.02},
                "AC": {"C": 0.12, "SrC": 0.01},
                "C": {"SrC": 0.08, "M": 0.005},
                "SrC": {"M": 0.06}
            }
        },
        "Sales": {
            "role": "Sales",
            "progression_probabilities": {
                "A": {"AC": 0.18, "C": 0.03},
                "AC": {"C": 0.15}
            }
        },
        "Recruitment": {
            "role": "Recruitment",
            "progression_probabilities": {
                "A": {"AC": 0.20, "C": 0.04},
                "AC": {"C": 0.18}
            }
        }
    }
    
    with open(test_data_dir / "cat_matrices.json", 'w') as f:
        json.dump(cat_matrices, f, indent=2)
    
    print(f"  Created CAT matrices: {len(cat_matrices)} roles")
    
    # 4. Create office configuration
    print("Creating office configuration...")
    
    office_config = {
        "london": {
            "name": "London Office",
            "current_snapshot_id": "london_baseline_2024",
            "business_plan_id": "london_growth_2024_2025",
            "economic_parameters": {
                "base_salary_ranges": {
                    "Consultant": {
                        "A": {"min": 45000, "max": 55000},
                        "AC": {"min": 55000, "max": 70000},
                        "C": {"min": 70000, "max": 90000},
                        "SrC": {"min": 90000, "max": 120000},
                        "M": {"min": 120000, "max": 150000}
                    },
                    "Sales": {
                        "A": {"min": 35000, "max": 45000},
                        "AC": {"min": 45000, "max": 60000},
                        "C": {"min": 60000, "max": 80000}
                    },
                    "Recruitment": {
                        "A": {"min": 30000, "max": 40000},
                        "AC": {"min": 40000, "max": 50000},
                        "C": {"min": 50000, "max": 65000}
                    },
                    "Operations": {
                        "Operations": {"min": 35000, "max": 55000}
                    }
                },
                "churn_rates": {
                    "Consultant": {"A": 0.08, "AC": 0.06, "C": 0.04, "SrC": 0.02, "M": 0.01},
                    "Sales": {"A": 0.10, "AC": 0.07, "C": 0.05},
                    "Recruitment": {"A": 0.12, "AC": 0.08, "C": 0.05},
                    "Operations": {"Operations": 0.06}
                },
                "recruitment_capacity": {
                    "monthly_max": 10,
                    "role_priorities": ["Consultant", "Sales", "Recruitment", "Operations"]
                }
            }
        }
    }
    
    with open(test_data_dir / "office_configurations.json", 'w') as f:
        json.dump(office_config, f, indent=2)
    
    print("  Created office configuration")
    
    # 5. Create test scenarios
    print("Creating test scenarios...")
    
    test_scenarios = [
        {
            "scenario_id": "growth_10pct_london",
            "name": "London 10% Growth - 2 Years",
            "description": "Target 10% workforce growth in London over 24 months",
            "time_range": {"start_year": 2024, "start_month": 1, "end_year": 2025, "end_month": 12},
            "office_ids": ["london"],
            "levers": {
                "recruitment_multiplier": 1.2,
                "churn_multiplier": 0.9,
                "price_multiplier": 1.03,
                "salary_multiplier": 1.02
            },
            "expected_outcomes": {
                "workforce_growth_pct": 10.0,
                "events_expected": ["hired", "churned", "promoted"],
                "minimum_events": 30
            }
        }
    ]
    
    with open(test_data_dir / "test_scenarios.json", 'w') as f:
        json.dump(test_scenarios, f, indent=2)
    
    print(f"  Created test scenarios: {len(test_scenarios)}")
    
    print()
    print("TEST DATA SUMMARY")
    print("=" * 20)
    print(f"Population: {len(workforce_data)} people")
    print(f"Business Plan: {len(monthly_plans)} months")
    print(f"CAT Matrices: {len(cat_matrices)} roles") 
    print(f"Test Scenarios: {len(test_scenarios)}")
    print(f"Data saved to: {test_data_dir}")
    
    return test_data_dir

if __name__ == "__main__":
    create_simple_test_data()