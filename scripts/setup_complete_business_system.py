#!/usr/bin/env python3
"""
Complete Business System Setup Script

This script creates a complete business planning system with:
1. Office entities with proper configurations
2. Comprehensive business plan data for each office
3. Test data for aggregation functionality
4. Realistic variations for testing different scenarios
"""

import os
import sys
import json
import requests
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Configuration
API_BASE_URL = "http://localhost:8000"
CURRENT_YEAR = 2025
MONTHS = list(range(1, 13))  # January to December

# Office configurations with comprehensive test data
OFFICE_CONFIGS = [
    {
        "id": "stockholm",
        "name": "Stockholm",
        "journey": "mature",
        "timezone": "Europe/Stockholm",
        "economic_parameters": {
            "cost_of_living": 1.2,
            "market_multiplier": 1.15,
            "tax_rate": 0.32
        },
        "total_fte": 679,
        "description": "Mature office with large scale operations"
    },
    {
        "id": "gothenburg", 
        "name": "Gothenburg",
        "journey": "established",
        "timezone": "Europe/Stockholm",
        "economic_parameters": {
            "cost_of_living": 1.0,
            "market_multiplier": 1.0,
            "tax_rate": 0.30
        },
        "total_fte": 234,
        "description": "Established office with steady growth"
    },
    {
        "id": "malmo",
        "name": "Malmö",
        "journey": "emerging",
        "timezone": "Europe/Stockholm", 
        "economic_parameters": {
            "cost_of_living": 0.95,
            "market_multiplier": 0.9,
            "tax_rate": 0.28
        },
        "total_fte": 87,
        "description": "Emerging office with high growth potential"
    },
    {
        "id": "oslo",
        "name": "Oslo",
        "journey": "established",
        "timezone": "Europe/Oslo",
        "economic_parameters": {
            "cost_of_living": 1.3,
            "market_multiplier": 1.2,
            "tax_rate": 0.35
        },
        "total_fte": 156,
        "description": "Established Nordic office"
    },
    {
        "id": "copenhagen",
        "name": "Copenhagen", 
        "journey": "mature",
        "timezone": "Europe/Copenhagen",
        "economic_parameters": {
            "cost_of_living": 1.25,
            "market_multiplier": 1.1,
            "tax_rate": 0.38
        },
        "total_fte": 198,
        "description": "Mature office with premium market positioning"
    }
]

# Role configuration with detailed parameters
ROLE_CONFIGURATIONS = {
    "Consultant": {
        "has_levels": True,
        "levels": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
        "has_price": True,
        "has_utr": True,
        "billing_role": True,
        "level_data": {
            "A": {"salary_base": 42000, "price_base": 95, "utr_base": 0.75, "recruitment": 0.08, "churn": 0.03},
            "AC": {"salary_base": 48000, "price_base": 110, "utr_base": 0.77, "recruitment": 0.06, "churn": 0.025},
            "C": {"salary_base": 55000, "price_base": 125, "utr_base": 0.79, "recruitment": 0.05, "churn": 0.02},
            "SrC": {"salary_base": 65000, "price_base": 145, "utr_base": 0.81, "recruitment": 0.04, "churn": 0.015},
            "AM": {"salary_base": 75000, "price_base": 165, "utr_base": 0.83, "recruitment": 0.03, "churn": 0.01},
            "M": {"salary_base": 90000, "price_base": 190, "utr_base": 0.85, "recruitment": 0.025, "churn": 0.008},
            "SrM": {"salary_base": 110000, "price_base": 220, "utr_base": 0.87, "recruitment": 0.02, "churn": 0.005},
            "PiP": {"salary_base": 135000, "price_base": 260, "utr_base": 0.89, "recruitment": 0.015, "churn": 0.003}
        }
    },
    "Sales": {
        "has_levels": True,
        "levels": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
        "has_price": False,
        "has_utr": False,
        "billing_role": False,
        "level_data": {
            "A": {"salary_base": 40000, "recruitment": 0.05, "churn": 0.04},
            "AC": {"salary_base": 45000, "recruitment": 0.04, "churn": 0.035},
            "C": {"salary_base": 52000, "recruitment": 0.035, "churn": 0.03},
            "SrC": {"salary_base": 62000, "recruitment": 0.03, "churn": 0.025},
            "AM": {"salary_base": 72000, "recruitment": 0.025, "churn": 0.02},
            "M": {"salary_base": 85000, "recruitment": 0.02, "churn": 0.015},
            "SrM": {"salary_base": 105000, "recruitment": 0.015, "churn": 0.01},
            "PiP": {"salary_base": 130000, "recruitment": 0.01, "churn": 0.005}
        }
    },
    "Recruitment": {
        "has_levels": True,
        "levels": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
        "has_price": False,
        "has_utr": False,
        "billing_role": False,
        "level_data": {
            "A": {"salary_base": 38000, "recruitment": 0.06, "churn": 0.04},
            "AC": {"salary_base": 43000, "recruitment": 0.05, "churn": 0.035},
            "C": {"salary_base": 50000, "recruitment": 0.04, "churn": 0.03},
            "SrC": {"salary_base": 60000, "recruitment": 0.035, "churn": 0.025},
            "AM": {"salary_base": 70000, "recruitment": 0.03, "churn": 0.02},
            "M": {"salary_base": 82000, "recruitment": 0.025, "churn": 0.015},
            "SrM": {"salary_base": 100000, "recruitment": 0.02, "churn": 0.01},
            "PiP": {"salary_base": 125000, "recruitment": 0.015, "churn": 0.005}
        }
    },
    "Operations": {
        "has_levels": False,
        "levels": ["General"],
        "has_price": False,
        "has_utr": False,
        "billing_role": False,
        "level_data": {
            "General": {"salary_base": 50000, "recruitment": 0.02, "churn": 0.02}
        }
    }
}

# Journey-based multipliers for realistic variations
JOURNEY_MULTIPLIERS = {
    "emerging": {
        "recruitment": 1.8,   # High growth
        "churn": 1.4,         # Higher churn
        "salary": 0.85,       # Lower salaries
        "price": 0.9,         # Competitive pricing
        "market_factor": 1.2  # Aggressive market approach
    },
    "established": {
        "recruitment": 1.0,   # Standard growth
        "churn": 1.0,         # Standard churn
        "salary": 1.0,        # Market salaries
        "price": 1.0,         # Market pricing
        "market_factor": 1.0  # Standard market approach
    },
    "mature": {
        "recruitment": 0.6,   # Slower growth
        "churn": 0.7,         # Lower churn
        "salary": 1.15,       # Premium salaries
        "price": 1.1,         # Premium pricing
        "market_factor": 0.8  # Conservative market approach
    }
}

def check_backend_health() -> bool:
    """Check if backend is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_existing_offices() -> List[Dict[str, Any]]:
    """Get list of existing offices from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/offices")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Failed to get offices: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"⚠️  Error getting offices: {e}")
        return []

def create_office_entity(office_config: Dict[str, Any]) -> bool:
    """Create office entity via API (if endpoint exists)"""
    # Note: The current API only reads from config, doesn't create new offices
    # This is a placeholder for when office creation is implemented
    print(f"📋 Office '{office_config['name']}' managed via configuration")
    return True

def calculate_business_plan_entry(
    office_config: Dict[str, Any], 
    role: str, 
    level: str, 
    month: int
) -> Dict[str, Any]:
    """Calculate realistic business plan entry values"""
    role_config = ROLE_CONFIGURATIONS[role]
    level_data = role_config["level_data"][level]
    journey_mult = JOURNEY_MULTIPLIERS[office_config["journey"]]
    
    # Seasonal variations
    seasonal_factors = {
        1: 1.3,   # January - Strong Q1
        2: 1.2,   # February - Good Q1
        3: 1.1,   # March - End Q1
        4: 0.9,   # April - Slower Q2
        5: 0.8,   # May - Vacation season
        6: 0.9,   # June - End Q2
        7: 0.7,   # July - Summer vacation
        8: 0.8,   # August - Post vacation
        9: 1.4,   # September - Strong Q3 start
        10: 1.2,  # October - Good Q3
        11: 1.0,  # November - Standard
        12: 0.9   # December - Holiday season
    }
    
    seasonal_factor = seasonal_factors.get(month, 1.0)
    
    # Market size factor based on office total_fte
    fte_factor = min(1.5, max(0.7, office_config["total_fte"] / 200))
    
    # Calculate target headcount based on role percentage of office total
    office_total_fte = office_config["total_fte"]
    
    # Role distribution targets
    role_fte_targets = {
        "Consultant": 0.75,    # 75% of office (billable consultants)
        "Sales": 0.06,         # 6% of office 
        "Recruitment": 0.04,   # 4% of office
        "Operations": 0.15     # 15% of office (support functions)
    }
    
    role_target_fte = office_total_fte * role_fte_targets[role]
    
    # Level distribution within role (pyramid structure)
    level_distribution = {
        "A": 0.35, "AC": 0.25, "C": 0.20, "SrC": 0.10, 
        "AM": 0.06, "M": 0.03, "SrM": 0.015, "PiP": 0.005,
        "General": 1.0
    }
    
    level_target_fte = role_target_fte * level_distribution.get(level, 0.1)
    base_headcount = max(1, round(level_target_fte))
    
    # Convert percentage rates to actual people counts
    # Use level target headcount as baseline for recruitment/churn calculations
    recruitment = max(0, round(
        level_data["recruitment"] * 
        base_headcount * 
        journey_mult["recruitment"] * 
        seasonal_factor
    ))
    
    churn = max(0, round(
        level_data["churn"] * 
        base_headcount * 
        journey_mult["churn"] * 
        (seasonal_factor * 0.8)  # Reduce churn seasonal impact
    ))
    
    # Cost of living adjustment
    cost_factor = office_config["economic_parameters"]["cost_of_living"]
    salary = round(level_data["salary_base"] * journey_mult["salary"] * cost_factor)
    
    entry = {
        "role": role,
        "level": level,
        "recruitment": recruitment,
        "churn": churn,
        "salary": salary
    }
    
    # Add price and UTR for billable roles
    if role_config["has_price"]:
        market_mult = office_config["economic_parameters"]["market_multiplier"]
        price = round(level_data["price_base"] * journey_mult["price"] * market_mult)
        utr = round(level_data["utr_base"], 2)
        entry.update({
            "price": price,
            "utr": utr
        })
    else:
        entry.update({
            "price": 0,
            "utr": 0
        })
    
    return entry

def create_monthly_business_plan(
    office_config: Dict[str, Any], 
    year: int, 
    month: int
) -> Dict[str, Any]:
    """Create a complete monthly business plan for an office"""
    entries = []
    
    for role_name, role_config in ROLE_CONFIGURATIONS.items():
        for level in role_config["levels"]:
            entry = calculate_business_plan_entry(office_config, role_name, level, month)
            entries.append(entry)
    
    plan_id = str(uuid.uuid4())
    
    return {
        "id": plan_id,
        "office_id": office_config["id"],
        "year": year,
        "month": month,
        "entries": entries,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def populate_office_business_plans(office_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create complete business plans for an office (all months)"""
    plans = []
    
    print(f"📊 Generating business plans for {office_config['name']}...")
    
    for month in MONTHS:
        plan = create_monthly_business_plan(office_config, CURRENT_YEAR, month)
        plans.append(plan)
        
        # Send to API (will be mock for now)
        try:
            response = requests.post(f"{API_BASE_URL}/business-plans", json=plan)
            if response.status_code in [200, 201]:
                print(f"  ✅ Month {month:02d} created")
            else:
                print(f"  ⚠️  Month {month:02d} API returned {response.status_code}")
        except requests.RequestException as e:
            print(f"  ⚠️  Month {month:02d} API error: {e}")
    
    return plans

def generate_aggregation_test_scenarios(all_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate aggregation test scenarios"""
    scenarios = {
        "single_office": {
            "description": "Single office analysis (Stockholm)",
            "offices": ["stockholm"],
            "months": list(range(1, 13)),
            "expected_totals": {}
        },
        "multi_office": {
            "description": "Multi-office aggregation (Stockholm + Gothenburg)",
            "offices": ["stockholm", "gothenburg"],
            "months": list(range(1, 13)),
            "expected_totals": {}
        },
        "journey_comparison": {
            "description": "Journey-based comparison (Emerging vs Mature)",
            "emerging": ["malmo"],
            "mature": ["stockholm", "copenhagen"],
            "months": list(range(1, 13))
        },
        "seasonal_analysis": {
            "description": "Seasonal pattern analysis",
            "offices": ["stockholm", "gothenburg", "malmo"],
            "peak_months": [1, 9],  # January and September
            "low_months": [5, 7],   # May and July
        },
        "quarterly_aggregation": {
            "description": "Quarterly business planning",
            "q1": {"months": [1, 2, 3], "offices": ["stockholm", "gothenburg"]},
            "q2": {"months": [4, 5, 6], "offices": ["stockholm", "gothenburg"]},
            "q3": {"months": [7, 8, 9], "offices": ["stockholm", "gothenburg"]},
            "q4": {"months": [10, 11, 12], "offices": ["stockholm", "gothenburg"]}
        }
    }
    
    # Calculate expected totals for validation
    for office_plans in all_plans:
        office_id = office_plans["office"]["id"]
        for plan in office_plans["monthly_plans"]:
            month = plan["month"]
            
            # Single office totals
            if office_id == "stockholm":
                if "stockholm_monthly" not in scenarios["single_office"]["expected_totals"]:
                    scenarios["single_office"]["expected_totals"]["stockholm_monthly"] = {}
                
                month_totals = {
                    "recruitment": sum(e["recruitment"] for e in plan["entries"]),
                    "churn": sum(e["churn"] for e in plan["entries"]),
                    "salary_cost": sum(e["salary"] for e in plan["entries"]),
                    "revenue_potential": sum(
                        e["price"] * e["utr"] * 166.4 for e in plan["entries"] 
                        if e["price"] > 0 and e["utr"] > 0
                    )
                }
                scenarios["single_office"]["expected_totals"]["stockholm_monthly"][month] = month_totals
    
    return scenarios

def save_comprehensive_test_data(all_plans: List[Dict[str, Any]], scenarios: Dict[str, Any]):
    """Save comprehensive test data for frontend testing"""
    output_dir = os.path.join(os.path.dirname(__file__), "test_data")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save complete dataset
    complete_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "description": "Comprehensive business planning test data with aggregation scenarios",
            "year": CURRENT_YEAR,
            "offices_count": len(OFFICE_CONFIGS),
            "total_plans": sum(len(op["monthly_plans"]) for op in all_plans),
            "total_entries": sum(
                len(plan["entries"]) 
                for office_plans in all_plans 
                for plan in office_plans["monthly_plans"]
            )
        },
        "offices": OFFICE_CONFIGS,
        "business_plans": all_plans,
        "aggregation_scenarios": scenarios,
        "role_configurations": ROLE_CONFIGURATIONS
    }
    
    with open(os.path.join(output_dir, "comprehensive_business_data.json"), "w") as f:
        json.dump(complete_data, f, indent=2, ensure_ascii=False)
    
    # Save aggregation test cases
    with open(os.path.join(output_dir, "aggregation_test_scenarios.json"), "w") as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)
    
    # Save individual office plans for targeted testing
    for office_plans in all_plans:
        office_id = office_plans["office"]["id"]
        filename = f"office_complete_{office_id}.json"
        with open(os.path.join(output_dir, filename), "w") as f:
            json.dump(office_plans, f, indent=2, ensure_ascii=False)

def main():
    """Main function to set up complete business system"""
    print("🚀 Complete Business System Setup")
    print("=" * 50)
    
    # Check backend health
    print("🔍 Checking backend health...")
    if not check_backend_health():
        print("❌ Backend is not running or unhealthy")
        print("   Please start the backend: cd backend && uvicorn main:app --reload")
        return
    
    print("✅ Backend is healthy")
    
    # Get existing offices
    print("\n📋 Checking existing offices...")
    existing_offices = get_existing_offices()
    print(f"Found {len(existing_offices)} existing offices")
    
    # Create/verify office entities
    print("\n🏢 Setting up office entities...")
    for office_config in OFFICE_CONFIGS:
        create_office_entity(office_config)
    
    # Generate business plans for all offices
    print(f"\n📊 Generating business plans for {len(OFFICE_CONFIGS)} offices...")
    all_plans = []
    
    for office_config in OFFICE_CONFIGS:
        print(f"\n🏢 Processing {office_config['name']}...")
        plans = populate_office_business_plans(office_config)
        
        office_data = {
            "office": office_config,
            "monthly_plans": plans,
            "metadata": {
                "total_months": len(plans),
                "total_entries": sum(len(plan["entries"]) for plan in plans),
                "journey": office_config["journey"],
                "fte": office_config["total_fte"]
            }
        }
        all_plans.append(office_data)
    
    # Generate aggregation test scenarios
    print("\n🧮 Generating aggregation test scenarios...")
    scenarios = generate_aggregation_test_scenarios(all_plans)
    
    # Save comprehensive test data
    print("\n💾 Saving comprehensive test data...")
    save_comprehensive_test_data(all_plans, scenarios)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Setup Complete - Summary")
    print("=" * 50)
    
    total_plans = sum(len(op["monthly_plans"]) for op in all_plans)
    total_entries = sum(
        len(plan["entries"]) 
        for office_plans in all_plans 
        for plan in office_plans["monthly_plans"]
    )
    
    print(f"🏢 Offices: {len(OFFICE_CONFIGS)}")
    print(f"📅 Monthly plans: {total_plans}")
    print(f"📋 Total entries: {total_entries}")
    print(f"🧮 Test scenarios: {len(scenarios)}")
    print(f"👥 Roles: {len(ROLE_CONFIGURATIONS)}")
    print(f"📈 Levels: {sum(len(role['levels']) for role in ROLE_CONFIGURATIONS.values())}")
    
    print(f"\n📁 Test Data Files Created:")
    print(f"• comprehensive_business_data.json - Complete dataset")
    print(f"• aggregation_test_scenarios.json - Test scenarios")
    for office_config in OFFICE_CONFIGS:
        print(f"• office_complete_{office_config['id']}.json - {office_config['name']} data")
    
    print(f"\n🧮 Aggregation Test Scenarios:")
    for scenario_name, scenario in scenarios.items():
        print(f"• {scenario_name}: {scenario['description']}")
    
    print(f"\n🚀 Next Steps:")
    print(f"1. Start frontend: cd frontend && npm run dev")
    print(f"2. Navigate to Business Planning section")
    print(f"3. Test office selection and data display")
    print(f"4. Test aggregation functionality")
    print(f"5. Verify monthly and yearly calculations")

if __name__ == "__main__":
    main()