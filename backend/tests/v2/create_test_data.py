"""
Test Data Generator for SimpleSim Engine V2

Creates comprehensive test data to verify engine functionality:
- Realistic population snapshots with diverse workforce
- Business plans with recruitment and growth targets
- Office configurations with economic parameters
- CAT matrices for career progression
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

from src.services.simulation_engine_v2 import (
    PopulationSnapshot, WorkforceEntry, BusinessPlan, MonthlyPlan,
    CATMatrix, EconomicParameters, Person
)


class V2TestDataGenerator:
    """Generate comprehensive test data for V2 engine verification"""
    
    def __init__(self, random_seed: int = 2024):
        """Initialize with deterministic seed for reproducible test data"""
        random.seed(random_seed)
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
    
    def generate_all_test_data(self) -> Dict[str, Any]:
        """Generate complete test data suite"""
        print("🏗️ Generating comprehensive V2 test data...")
        print("=" * 50)
        
        test_data = {
            "population_snapshots": self.create_population_snapshots(),
            "business_plans": self.create_business_plans(), 
            "office_configurations": self.create_office_configurations(),
            "cat_matrices": self.create_cat_matrices(),
            "scenarios": self.create_test_scenarios()
        }
        
        # Save all test data
        self.save_test_data(test_data)
        
        print("\n✅ Test data generation complete!")
        return test_data
    
    def create_population_snapshots(self) -> Dict[str, PopulationSnapshot]:
        """Create realistic population snapshots for different offices"""
        print("👥 Creating population snapshots...")
        
        snapshots = {}
        
        # London office - Large, established office
        london_workforce = self._create_office_workforce(
            office_id="london",
            size=120,
            roles_distribution={
                "Consultant": 0.60,    # 72 people
                "Sales": 0.25,         # 30 people  
                "Recruitment": 0.10,   # 12 people
                "Operations": 0.05     # 6 people
            },
            seniority_distribution={
                "junior": 0.40,        # 40% junior (A, AC)
                "mid": 0.35,           # 35% mid-level (C)
                "senior": 0.20,        # 20% senior (SrC, M)
                "leadership": 0.05     # 5% leadership (SM, D)
            }
        )
        
        snapshots["london"] = PopulationSnapshot(
            id="london_baseline_2024",
            office_id="london",
            snapshot_date="2024-01",
            name="London Office Baseline - January 2024",
            workforce=london_workforce
        )
        
        # New York office - Medium growth office
        ny_workforce = self._create_office_workforce(
            office_id="new_york",
            size=80,
            roles_distribution={
                "Consultant": 0.65,    # 52 people
                "Sales": 0.30,         # 24 people
                "Recruitment": 0.05    # 4 people
            },
            seniority_distribution={
                "junior": 0.50,        # Higher junior ratio (growth office)
                "mid": 0.30,
                "senior": 0.15,
                "leadership": 0.05
            }
        )
        
        snapshots["new_york"] = PopulationSnapshot(
            id="ny_baseline_2024",
            office_id="new_york", 
            snapshot_date="2024-01",
            name="New York Office Baseline - January 2024",
            workforce=ny_workforce
        )
        
        # Singapore office - Small, new office
        sg_workforce = self._create_office_workforce(
            office_id="singapore",
            size=35,
            roles_distribution={
                "Consultant": 0.70,    # 25 people
                "Sales": 0.20,         # 7 people
                "Operations": 0.10     # 3 people
            },
            seniority_distribution={
                "junior": 0.60,        # Very junior (new office)
                "mid": 0.25,
                "senior": 0.10,
                "leadership": 0.05
            }
        )
        
        snapshots["singapore"] = PopulationSnapshot(
            id="sg_baseline_2024",
            office_id="singapore",
            snapshot_date="2024-01", 
            name="Singapore Office Baseline - January 2024",
            workforce=sg_workforce
        )
        
        print(f"  ✅ Created {len(snapshots)} population snapshots")
        for office, snapshot in snapshots.items():
            print(f"    - {office}: {len(snapshot.workforce)} people")
        
        return snapshots
    
    def _create_office_workforce(self, office_id: str, size: int, 
                                roles_distribution: Dict[str, float],
                                seniority_distribution: Dict[str, float]) -> List[WorkforceEntry]:
        """Create realistic workforce for an office"""
        workforce = []
        
        # Define role levels
        role_levels = {
            "Consultant": ["A", "AC", "C", "SrC", "M", "SM", "D"],
            "Sales": ["A", "AC", "C", "SrC"],
            "Recruitment": ["A", "AC", "C"],
            "Operations": ["Operations"]  # Flat role
        }
        
        # Map seniority to levels
        seniority_to_levels = {
            "junior": {"Consultant": ["A", "AC"], "Sales": ["A", "AC"], "Recruitment": ["A", "AC"], "Operations": ["Operations"]},
            "mid": {"Consultant": ["C"], "Sales": ["C"], "Recruitment": ["C"], "Operations": ["Operations"]},
            "senior": {"Consultant": ["SrC", "M"], "Sales": ["SrC"], "Recruitment": ["C"], "Operations": ["Operations"]},
            "leadership": {"Consultant": ["SM", "D"], "Sales": ["SrC"], "Recruitment": ["C"], "Operations": ["Operations"]}
        }
        
        person_id = 1
        
        for role, role_percentage in roles_distribution.items():
            role_size = int(size * role_percentage)
            
            for _ in range(role_size):
                # Determine seniority
                rand = random.random()
                cumulative = 0
                selected_seniority = "junior"
                
                for seniority, percentage in seniority_distribution.items():
                    cumulative += percentage
                    if rand <= cumulative:
                        selected_seniority = seniority
                        break
                
                # Select level based on seniority and role
                available_levels = seniority_to_levels[selected_seniority][role]
                level = random.choice(available_levels)
                
                # Generate hire date (6 months to 5 years ago)
                months_ago = random.randint(6, 60)
                hire_date = date(2024, 1, 1) - timedelta(days=months_ago * 30)
                
                # Level start date (hire date to 2 years after hire)
                level_months_after_hire = random.randint(0, min(24, months_ago))
                level_start_date = hire_date + timedelta(days=level_months_after_hire * 30)
                
                workforce.append(WorkforceEntry(
                    id=f"{office_id}_person_{person_id:04d}",
                    role=role,
                    level=level,
                    hire_date=hire_date.strftime("%Y-%m"),
                    level_start_date=level_start_date.strftime("%Y-%m"),
                    office=office_id
                ))
                
                person_id += 1
        
        return workforce
    
    def create_business_plans(self) -> Dict[str, BusinessPlan]:
        """Create realistic business plans with recruitment targets"""
        print("📊 Creating business plans...")
        
        business_plans = {}
        
        # London - Established office with steady growth
        london_monthly_plans = {}
        for month in range(1, 25):  # 24 months
            year = 2024 if month <= 12 else 2025
            month_num = month if month <= 12 else month - 12
            
            # Base values with seasonal variation
            seasonal_factor = 1.0 + 0.1 * random.random()  # ±10% variation
            
            london_monthly_plans[f"{year}-{month_num:02d}"] = MonthlyPlan(
                month=f"{year}-{month_num:02d}",
                revenue=850000 * seasonal_factor,
                costs=650000 * seasonal_factor,
                recruitment={
                    "Consultant": {"A": 3, "AC": 2, "C": 1},
                    "Sales": {"A": 2, "AC": 1},
                    "Recruitment": {"A": 1 if month % 3 == 0 else 0}  # Every 3 months
                },
                churn={
                    "Consultant": {"A": 1, "AC": 1, "C": 1, "SrC": 0, "M": 0},
                    "Sales": {"A": 1, "AC": 0, "C": 0},
                    "Recruitment": {"A": 0, "AC": 0, "C": 0},
                    "Operations": {"Operations": 0}
                },
                targets=MonthlyTargets(
                    revenue_target=900000,
                    headcount_target=125 + (month * 2),  # Grow by 2 per month
                    utilization_target=0.85,
                    client_satisfaction=0.92
                )
            )
        
        business_plans["london"] = BusinessPlan(
            office_id="london",
            plan_id="london_growth_2024_2025",
            name="London Office Growth Plan 2024-2025",
            monthly_plans=london_monthly_plans
        )
        
        # New York - Aggressive growth office
        ny_monthly_plans = {}
        for month in range(1, 25):
            year = 2024 if month <= 12 else 2025
            month_num = month if month <= 12 else month - 12
            
            seasonal_factor = 1.0 + 0.15 * random.random()  # Higher variation
            
            ny_monthly_plans[f"{year}-{month_num:02d}"] = MonthlyPlan(
                month=f"{year}-{month_num:02d}",
                revenue=600000 * seasonal_factor,
                costs=450000 * seasonal_factor,
                recruitment={
                    "Consultant": {"A": 4, "AC": 2, "C": 1},  # Higher recruitment
                    "Sales": {"A": 3, "AC": 1, "C": 1},
                    "Recruitment": {"A": 1 if month % 2 == 0 else 0}  # Every 2 months
                },
                churn={
                    "Consultant": {"A": 2, "AC": 1, "C": 0},  # Higher junior churn
                    "Sales": {"A": 1, "AC": 0, "C": 0},
                    "Recruitment": {"A": 0}
                },
                targets=MonthlyTargets(
                    revenue_target=700000,
                    headcount_target=85 + (month * 3),  # Aggressive growth
                    utilization_target=0.88,
                    client_satisfaction=0.90
                )
            )
        
        business_plans["new_york"] = BusinessPlan(
            office_id="new_york",
            plan_id="ny_expansion_2024_2025", 
            name="New York Office Expansion Plan 2024-2025",
            monthly_plans=ny_monthly_plans
        )
        
        # Singapore - Conservative growth
        sg_monthly_plans = {}
        for month in range(1, 25):
            year = 2024 if month <= 12 else 2025
            month_num = month if month <= 12 else month - 12
            
            seasonal_factor = 1.0 + 0.05 * random.random()  # Lower variation
            
            sg_monthly_plans[f"{year}-{month_num:02d}"] = MonthlyPlan(
                month=f"{year}-{month_num:02d}",
                revenue=200000 * seasonal_factor,
                costs=150000 * seasonal_factor,
                recruitment={
                    "Consultant": {"A": 2, "AC": 1},  # Conservative recruitment
                    "Sales": {"A": 1},
                    "Operations": {"Operations": 1 if month % 6 == 0 else 0}  # Every 6 months
                },
                churn={
                    "Consultant": {"A": 1, "AC": 0, "C": 0},
                    "Sales": {"A": 0, "AC": 0},
                    "Operations": {"Operations": 0}
                },
                targets=MonthlyTargets(
                    revenue_target=250000,
                    headcount_target=38 + month,  # Slow growth
                    utilization_target=0.82,
                    client_satisfaction=0.88
                )
            )
        
        business_plans["singapore"] = BusinessPlan(
            office_id="singapore",
            plan_id="sg_foundation_2024_2025",
            name="Singapore Office Foundation Plan 2024-2025", 
            monthly_plans=sg_monthly_plans
        )
        
        print(f"  ✅ Created {len(business_plans)} business plans")
        for office, plan in business_plans.items():
            print(f"    - {office}: {len(plan.monthly_plans)} monthly plans")
        
        return business_plans
    
    def create_cat_matrices(self) -> Dict[str, CATMatrix]:
        """Create Career Advancement Timeline matrices for progression"""
        print("📈 Creating CAT matrices...")
        
        cat_matrices = {}
        
        # Consultant progression matrix
        consultant_progression = {
            "A": {
                "AC": 0.15,    # 15% chance per month to AC (6.7 months avg)
                "C": 0.02      # 2% direct to C (rare fast track)
            },
            "AC": {
                "C": 0.12,     # 12% chance per month to C (8.3 months avg)
                "SrC": 0.01    # 1% direct to SrC (fast track)
            },
            "C": {
                "SrC": 0.08,   # 8% chance per month to SrC (12.5 months avg)
                "M": 0.005     # 0.5% direct to M (very rare)
            },
            "SrC": {
                "M": 0.06,     # 6% chance per month to M (16.7 months avg)
                "SM": 0.002    # 0.2% direct to SM (exceptional)
            },
            "M": {
                "SM": 0.04,    # 4% chance per month to SM (25 months avg)
                "D": 0.001     # 0.1% direct to D (extremely rare)
            },
            "SM": {
                "D": 0.02      # 2% chance per month to D (50 months avg)
            }
        }
        
        cat_matrices["Consultant"] = CATMatrix(
            role="Consultant",
            progression_probabilities=consultant_progression
        )
        
        # Sales progression matrix
        sales_progression = {
            "A": {
                "AC": 0.18,    # Faster progression in sales
                "C": 0.03
            },
            "AC": {
                "C": 0.15,
                "SrC": 0.02
            },
            "C": {
                "SrC": 0.10
            }
        }
        
        cat_matrices["Sales"] = CATMatrix(
            role="Sales",
            progression_probabilities=sales_progression
        )
        
        # Recruitment progression matrix
        recruitment_progression = {
            "A": {
                "AC": 0.20,    # Fast progression (specialized skill)
                "C": 0.04
            },
            "AC": {
                "C": 0.18
            }
        }
        
        cat_matrices["Recruitment"] = CATMatrix(
            role="Recruitment", 
            progression_probabilities=recruitment_progression
        )
        
        print(f"  ✅ Created {len(cat_matrices)} CAT matrices")
        for role, matrix in cat_matrices.items():
            total_paths = sum(len(paths) for paths in matrix.progression_probabilities.values())
            print(f"    - {role}: {total_paths} progression paths")
        
        return cat_matrices
    
    def create_office_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Create office configurations with economic parameters"""
        print("🏢 Creating office configurations...")
        
        configs = {
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
                            "M": {"min": 120000, "max": 150000},
                            "SM": {"min": 150000, "max": 200000},
                            "D": {"min": 200000, "max": 300000}
                        },
                        "Sales": {
                            "A": {"min": 35000, "max": 45000},
                            "AC": {"min": 45000, "max": 60000},
                            "C": {"min": 60000, "max": 80000},
                            "SrC": {"min": 80000, "max": 110000}
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
                        "Sales": {"A": 0.10, "AC": 0.07, "C": 0.05, "SrC": 0.03},
                        "Recruitment": {"A": 0.12, "AC": 0.08, "C": 0.05},
                        "Operations": {"Operations": 0.06}
                    },
                    "recruitment_capacity": {
                        "monthly_max": 15,
                        "role_priorities": ["Consultant", "Sales", "Recruitment", "Operations"]
                    }
                }
            },
            "new_york": {
                "name": "New York Office", 
                "current_snapshot_id": "ny_baseline_2024",
                "business_plan_id": "ny_expansion_2024_2025",
                "economic_parameters": {
                    "base_salary_ranges": {
                        "Consultant": {
                            "A": {"min": 60000, "max": 75000},    # Higher salaries (US market)
                            "AC": {"min": 75000, "max": 95000},
                            "C": {"min": 95000, "max": 120000},
                            "SrC": {"min": 120000, "max": 160000},
                            "M": {"min": 160000, "max": 200000}
                        },
                        "Sales": {
                            "A": {"min": 50000, "max": 65000},
                            "AC": {"min": 65000, "max": 85000},
                            "C": {"min": 85000, "max": 110000},
                            "SrC": {"min": 110000, "max": 150000}
                        },
                        "Recruitment": {
                            "A": {"min": 45000, "max": 60000},
                            "AC": {"min": 60000, "max": 75000},
                            "C": {"min": 75000, "max": 95000}
                        }
                    },
                    "churn_rates": {
                        "Consultant": {"A": 0.12, "AC": 0.09, "C": 0.06, "SrC": 0.03},  # Higher churn (competitive market)
                        "Sales": {"A": 0.15, "AC": 0.10, "C": 0.07, "SrC": 0.04},
                        "Recruitment": {"A": 0.18, "AC": 0.12, "C": 0.08}
                    },
                    "recruitment_capacity": {
                        "monthly_max": 20,  # Higher capacity (growth office)
                        "role_priorities": ["Sales", "Consultant", "Recruitment"]
                    }
                }
            },
            "singapore": {
                "name": "Singapore Office",
                "current_snapshot_id": "sg_baseline_2024", 
                "business_plan_id": "sg_foundation_2024_2025",
                "economic_parameters": {
                    "base_salary_ranges": {
                        "Consultant": {
                            "A": {"min": 35000, "max": 45000},    # Lower cost market
                            "AC": {"min": 45000, "max": 60000},
                            "C": {"min": 60000, "max": 80000},
                            "SrC": {"min": 80000, "max": 105000},
                            "M": {"min": 105000, "max": 135000}
                        },
                        "Sales": {
                            "A": {"min": 30000, "max": 40000},
                            "AC": {"min": 40000, "max": 55000},
                            "C": {"min": 55000, "max": 75000}
                        },
                        "Operations": {
                            "Operations": {"min": 25000, "max": 40000}
                        }
                    },
                    "churn_rates": {
                        "Consultant": {"A": 0.06, "AC": 0.04, "C": 0.03, "SrC": 0.02, "M": 0.01},  # Lower churn (stable market)
                        "Sales": {"A": 0.08, "AC": 0.05, "C": 0.03},
                        "Operations": {"Operations": 0.04}
                    },
                    "recruitment_capacity": {
                        "monthly_max": 8,   # Lower capacity (small office)
                        "role_priorities": ["Consultant", "Sales", "Operations"]
                    }
                }
            }
        }
        
        print(f"  ✅ Created {len(configs)} office configurations")
        for office, config in configs.items():
            print(f"    - {office}: {len(config['economic_parameters']['base_salary_ranges'])} role salary ranges")
        
        return configs
    
    def create_test_scenarios(self) -> List[Dict[str, Any]]:
        """Create test scenarios for different simulation types"""
        print("🎯 Creating test scenarios...")
        
        scenarios = [
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
                    "revenue_growth_pct": 15.0,
                    "events_expected": ["hired", "churned", "promoted"],
                    "minimum_events": 50
                }
            },
            {
                "scenario_id": "aggressive_expansion_ny",
                "name": "New York Aggressive Expansion",
                "description": "Rapid 25% growth in New York over 18 months",
                "time_range": {"start_year": 2024, "start_month": 1, "end_year": 2025, "end_month": 6},
                "office_ids": ["new_york"],
                "levers": {
                    "recruitment_multiplier": 1.5,
                    "churn_multiplier": 0.8,
                    "price_multiplier": 1.05,
                    "salary_multiplier": 1.04
                },
                "expected_outcomes": {
                    "workforce_growth_pct": 25.0,
                    "revenue_growth_pct": 30.0,
                    "events_expected": ["hired", "churned", "promoted"],
                    "minimum_events": 80
                }
            },
            {
                "scenario_id": "multi_office_expansion",
                "name": "Multi-Office Global Expansion",
                "description": "Coordinated growth across London, NY, and Singapore",
                "time_range": {"start_year": 2024, "start_month": 1, "end_year": 2025, "end_month": 12},
                "office_ids": ["london", "new_york", "singapore"],
                "levers": {
                    "recruitment_multiplier": 1.25,
                    "churn_multiplier": 0.85,
                    "price_multiplier": 1.04,
                    "salary_multiplier": 1.03
                },
                "expected_outcomes": {
                    "workforce_growth_pct": 15.0,
                    "revenue_growth_pct": 20.0,
                    "events_expected": ["hired", "churned", "promoted", "office_transfer"],
                    "minimum_events": 150
                }
            },
            {
                "scenario_id": "conservative_singapore",
                "name": "Singapore Conservative Growth",
                "description": "Steady 5% growth in Singapore over 2 years",
                "time_range": {"start_year": 2024, "start_month": 1, "end_year": 2025, "end_month": 12},
                "office_ids": ["singapore"],
                "levers": {
                    "recruitment_multiplier": 1.1,
                    "churn_multiplier": 0.95,
                    "price_multiplier": 1.02,
                    "salary_multiplier": 1.01
                },
                "expected_outcomes": {
                    "workforce_growth_pct": 5.0,
                    "revenue_growth_pct": 8.0,
                    "events_expected": ["hired", "churned", "promoted"],
                    "minimum_events": 20
                }
            }
        ]
        
        print(f"  ✅ Created {len(scenarios)} test scenarios")
        for scenario in scenarios:
            months = (scenario["time_range"]["end_year"] - scenario["time_range"]["start_year"]) * 12 + \
                    (scenario["time_range"]["end_month"] - scenario["time_range"]["start_month"])
            print(f"    - {scenario['name']}: {months} months, {len(scenario['office_ids'])} offices")
        
        return scenarios
    
    def save_test_data(self, test_data: Dict[str, Any]):
        """Save all test data to JSON files"""
        print("\n💾 Saving test data...")
        
        # Save population snapshots
        snapshots_file = self.test_data_dir / "population_snapshots.json"
        snapshots_data = {}
        for office, snapshot in test_data["population_snapshots"].items():
            snapshots_data[office] = {
                "id": snapshot.id,
                "office_id": snapshot.office_id,
                "snapshot_date": snapshot.snapshot_date,
                "name": snapshot.name,
                "workforce": [
                    {
                        "id": entry.id,
                        "role": entry.role,
                        "level": entry.level,
                        "hire_date": entry.hire_date,
                        "level_start_date": entry.level_start_date,
                        "office": entry.office
                    }
                    for entry in snapshot.workforce
                ]
            }
        
        with open(snapshots_file, 'w') as f:
            json.dump(snapshots_data, f, indent=2)
        print(f"  ✅ Population snapshots saved to {snapshots_file}")
        
        # Save business plans
        business_plans_file = self.test_data_dir / "business_plans.json"
        business_plans_data = {}
        for office, plan in test_data["business_plans"].items():
            business_plans_data[office] = {
                "office_id": plan.office_id,
                "plan_id": plan.plan_id,
                "name": plan.name,
                "monthly_plans": {}
            }
            
            for month, monthly_plan in plan.monthly_plans.items():
                business_plans_data[office]["monthly_plans"][month] = {
                    "month": monthly_plan.month,
                    "revenue": monthly_plan.revenue,
                    "costs": monthly_plan.costs,
                    "recruitment": monthly_plan.recruitment,
                    "churn": monthly_plan.churn,
                    "targets": {
                        "revenue_target": monthly_plan.targets.revenue_target,
                        "headcount_target": monthly_plan.targets.headcount_target,
                        "utilization_target": monthly_plan.targets.utilization_target,
                        "client_satisfaction": monthly_plan.targets.client_satisfaction
                    }
                }
        
        with open(business_plans_file, 'w') as f:
            json.dump(business_plans_data, f, indent=2)
        print(f"  ✅ Business plans saved to {business_plans_file}")
        
        # Save office configurations
        office_configs_file = self.test_data_dir / "office_configurations.json"
        with open(office_configs_file, 'w') as f:
            json.dump(test_data["office_configurations"], f, indent=2)
        print(f"  ✅ Office configurations saved to {office_configs_file}")
        
        # Save CAT matrices
        cat_matrices_file = self.test_data_dir / "cat_matrices.json"
        cat_data = {}
        for role, matrix in test_data["cat_matrices"].items():
            cat_data[role] = {
                "role": matrix.role,
                "progression_probabilities": matrix.progression_probabilities
            }
        
        with open(cat_matrices_file, 'w') as f:
            json.dump(cat_data, f, indent=2)
        print(f"  ✅ CAT matrices saved to {cat_matrices_file}")
        
        # Save test scenarios
        scenarios_file = self.test_data_dir / "test_scenarios.json"
        with open(scenarios_file, 'w') as f:
            json.dump(test_data["scenarios"], f, indent=2)
        print(f"  ✅ Test scenarios saved to {scenarios_file}")
        
        print(f"\n📁 All test data saved to: {self.test_data_dir}")


def main():
    """Generate all test data"""
    print("🚀 SimpleSim Engine V2 - Test Data Generator")
    print("=" * 60)
    
    generator = V2TestDataGenerator(random_seed=2024)
    test_data = generator.generate_all_test_data()
    
    print("\n📊 TEST DATA SUMMARY")
    print("=" * 30)
    print(f"Population Snapshots: {len(test_data['population_snapshots'])} offices")
    
    total_people = sum(len(snapshot.workforce) for snapshot in test_data['population_snapshots'].values())
    print(f"Total People: {total_people}")
    
    print(f"Business Plans: {len(test_data['business_plans'])} offices")
    total_months = sum(len(plan.monthly_plans) for plan in test_data['business_plans'].values())
    print(f"Total Monthly Plans: {total_months}")
    
    print(f"CAT Matrices: {len(test_data['cat_matrices'])} roles")
    print(f"Test Scenarios: {len(test_data['scenarios'])}")
    
    print("\n✅ Test data generation complete!")
    print("Ready to test V2 engine with realistic data!")


if __name__ == "__main__":
    main()