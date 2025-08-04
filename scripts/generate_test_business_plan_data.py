#!/usr/bin/env python3
"""
Generate Test Business Plan Data

This script generates realistic business plan test data in JSON format
that can be used for testing the business planning interface.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Office test data
OFFICES = [
    {
        "id": "stockholm-office",
        "name": "Stockholm",
        "journey": "Mature Office",
        "total_fte": 679
    },
    {
        "id": "gothenburg-office", 
        "name": "Gothenburg",
        "journey": "Established Office",
        "total_fte": 234
    },
    {
        "id": "malmo-office",
        "name": "Malmö", 
        "journey": "Emerging Office",
        "total_fte": 87
    }
]

# Role configuration
ROLES = {
    "Consultant": {
        "levels": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
        "has_price_utr": True
    },
    "Sales": {
        "levels": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
        "has_price_utr": False
    },
    "Recruitment": {
        "levels": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
        "has_price_utr": False
    },
    "Operations": {
        "levels": ["General"],
        "has_price_utr": False
    }
}

# Level-based multipliers
LEVEL_DATA = {
    "A": {"salary_base": 42000, "price_base": 95, "utr_base": 0.75, "recruitment": 0.08, "churn": 0.03},
    "AC": {"salary_base": 48000, "price_base": 110, "utr_base": 0.77, "recruitment": 0.06, "churn": 0.025},
    "C": {"salary_base": 55000, "price_base": 125, "utr_base": 0.79, "recruitment": 0.05, "churn": 0.02},
    "SrC": {"salary_base": 65000, "price_base": 145, "utr_base": 0.81, "recruitment": 0.04, "churn": 0.015},
    "AM": {"salary_base": 75000, "price_base": 165, "utr_base": 0.83, "recruitment": 0.03, "churn": 0.01},
    "M": {"salary_base": 90000, "price_base": 190, "utr_base": 0.85, "recruitment": 0.025, "churn": 0.008},
    "SrM": {"salary_base": 110000, "price_base": 220, "utr_base": 0.87, "recruitment": 0.02, "churn": 0.005},
    "PiP": {"salary_base": 135000, "price_base": 260, "utr_base": 0.89, "recruitment": 0.015, "churn": 0.003},
    "General": {"salary_base": 50000, "price_base": 0, "utr_base": 0, "recruitment": 0.02, "churn": 0.02}
}

# Journey-based multipliers
JOURNEY_MULTIPLIERS = {
    "Emerging Office": {"recruitment": 1.5, "churn": 1.3, "salary": 0.9, "price": 0.95},
    "Established Office": {"recruitment": 1.0, "churn": 1.0, "salary": 1.0, "price": 1.0},
    "Mature Office": {"recruitment": 0.7, "churn": 0.8, "salary": 1.1, "price": 1.05}
}

def generate_monthly_entry(role: str, level: str, office_journey: str, month: int) -> Dict[str, Any]:
    """Generate a monthly business plan entry"""
    level_data = LEVEL_DATA[level]
    journey_mult = JOURNEY_MULTIPLIERS[office_journey]
    role_config = ROLES[role]
    
    # Seasonal variation (higher activity in Q1, Q3)
    seasonal_factor = 1.2 if month in [1, 2, 3, 7, 8, 9] else 1.0
    
    # Calculate values
    recruitment = round(level_data["recruitment"] * journey_mult["recruitment"] * seasonal_factor, 3)
    churn = round(level_data["churn"] * journey_mult["churn"] * seasonal_factor, 3)
    salary = round(level_data["salary_base"] * journey_mult["salary"])
    
    entry = {
        "role": role,
        "level": level,
        "recruitment": recruitment,
        "churn": churn,
        "salary": salary
    }
    
    # Add price and UTR for billable roles
    if role_config["has_price_utr"]:
        price = round(level_data["price_base"] * journey_mult["price"])
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

def generate_office_business_plan(office: Dict[str, Any], year: int = 2025) -> List[Dict[str, Any]]:
    """Generate business plan for an office"""
    monthly_plans = []
    
    for month in range(1, 13):  # January to December
        entries = []
        
        for role_name, role_config in ROLES.items():
            for level in role_config["levels"]:
                entry = generate_monthly_entry(role_name, level, office["journey"], month)
                entries.append(entry)
        
        monthly_plan = {
            "id": f"{office['id']}-{year}-{month:02d}",
            "office_id": office["id"],
            "year": year,
            "month": month,
            "entries": entries,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        monthly_plans.append(monthly_plan)
    
    return monthly_plans

def generate_all_test_data() -> Dict[str, Any]:
    """Generate complete test data for all offices"""
    test_data = {
        "offices": OFFICES,
        "business_plans": [],
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "description": "Test business plan data for SimpleSim",
            "year": 2025,
            "roles": list(ROLES.keys()),
            "total_offices": len(OFFICES)
        }
    }
    
    for office in OFFICES:
        office_plans = generate_office_business_plan(office)
        test_data["business_plans"].extend(office_plans)
    
    return test_data

def save_test_data():
    """Save test data to JSON files"""
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "test_data")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate and save complete test data
    test_data = generate_all_test_data()
    
    # Save complete dataset
    with open(os.path.join(output_dir, "business_plan_test_data.json"), "w") as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    # Save individual office plans
    for office in OFFICES:
        office_plans = generate_office_business_plan(office)
        filename = f"business_plan_{office['id']}.json"
        with open(os.path.join(output_dir, filename), "w") as f:
            json.dump({
                "office": office,
                "monthly_plans": office_plans,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "office_name": office["name"],
                    "total_months": len(office_plans),
                    "total_entries": sum(len(plan["entries"]) for plan in office_plans)
                }
            }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Test data generated in {output_dir}/")
    print(f"📊 Generated data for {len(OFFICES)} offices")
    print(f"📅 12 months of data for 2025")
    print(f"👥 {len(ROLES)} roles with {sum(len(config['levels']) for config in ROLES.values())} total role-level combinations")
    print(f"📈 {len(test_data['business_plans'])} monthly plans total")
    
    # Print summary statistics
    total_entries = sum(len(plan["entries"]) for plan in test_data["business_plans"])
    print(f"📋 {total_entries} total entries across all plans")

def main():
    """Main function"""
    print("🚀 Generating Business Plan Test Data")
    print("=" * 40)
    save_test_data()
    print("\n🎉 Test data generation complete!")

if __name__ == "__main__":
    main()