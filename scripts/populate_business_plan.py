#!/usr/bin/env python3
"""
Business Plan Population Script

This script populates the business plan database with realistic test data
based on the office configuration and our previous test scenarios.
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, Any, List

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Configuration
API_BASE_URL = "http://localhost:8000"
CURRENT_YEAR = 2025
MONTHS = list(range(1, 13))  # January to December

# Role configuration based on our office types
ROLE_CONFIG = {
    "Consultant": {
        "has_levels": True,
        "levels": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
        "has_price": True,
        "has_utr": True,
        "base_recruitment_rate": 0.08,  # 8% monthly recruitment
        "base_churn_rate": 0.03,       # 3% monthly churn
    },
    "Sales": {
        "has_levels": True,
        "levels": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
        "has_price": False,
        "has_utr": False,
        "base_recruitment_rate": 0.05,  # 5% monthly recruitment
        "base_churn_rate": 0.04,       # 4% monthly churn
    },
    "Recruitment": {
        "has_levels": True,
        "levels": ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
        "has_price": False,
        "has_utr": False,
        "base_recruitment_rate": 0.06,  # 6% monthly recruitment
        "base_churn_rate": 0.04,       # 4% monthly churn
    },
    "Operations": {
        "has_levels": False,
        "levels": ["General"],
        "has_price": False,
        "has_utr": False,
        "base_recruitment_rate": 0.02,  # 2% monthly recruitment
        "base_churn_rate": 0.02,       # 2% monthly churn
    }
}

# Office journey-based multipliers
JOURNEY_MULTIPLIERS = {
    "Emerging Office": {
        "recruitment_multiplier": 1.5,  # Higher growth
        "churn_multiplier": 1.3,        # Higher churn
        "salary_base": 40000
    },
    "Established Office": {
        "recruitment_multiplier": 1.0,  # Standard growth
        "churn_multiplier": 1.0,        # Standard churn
        "salary_base": 45000
    },
    "Mature Office": {
        "recruitment_multiplier": 0.7,  # Lower growth
        "churn_multiplier": 0.8,        # Lower churn
        "salary_base": 50000
    }
}

def load_office_config() -> Dict[str, Any]:
    """Load office configuration from JSON file"""
    config_path = os.path.join(backend_dir, "config", "office_configuration.json")
    with open(config_path, 'r') as f:
        return json.load(f)

def get_offices_from_api() -> List[Dict[str, Any]]:
    """Get list of offices from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/offices")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get offices: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Error connecting to API: {e}")
        return []

def calculate_realistic_values(office_config: Dict[str, Any], role: str, level: str, month: int) -> Dict[str, float]:
    """Calculate realistic business plan values for a role/level/month"""
    role_config = ROLE_CONFIG[role]
    journey = office_config.get("journey", "Established Office")
    journey_multiplier = JOURNEY_MULTIPLIERS.get(journey, JOURNEY_MULTIPLIERS["Established Office"])
    
    # Base values from role configuration
    base_recruitment = role_config["base_recruitment_rate"]
    base_churn = role_config["base_churn_rate"]
    
    # Calculate target headcount based on role percentage of office total
    office_total_fte = office_config.get("total_fte", 200)
    
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
    
    # Add seasonal variation (higher recruitment in Jan, Mar, Sep)
    seasonal_boost = 1.2 if month in [1, 3, 9] else 1.0
    
    # Convert percentage rates to actual people counts
    recruitment = max(0, round(
        base_recruitment * 
        base_headcount * 
        journey_multiplier["recruitment_multiplier"] * 
        seasonal_boost
    ))
    
    churn = max(0, round(
        base_churn * 
        base_headcount * 
        journey_multiplier["churn_multiplier"] * 
        (seasonal_boost * 0.8)  # Reduce churn seasonal impact
    ))
    
    # Base salary calculation
    salary_base = journey_multiplier["salary_base"]
    
    # Level-based salary scaling
    level_multipliers = {
        "A": 1.0, "AC": 1.2, "C": 1.4, "SrC": 1.7,
        "AM": 2.0, "M": 2.5, "SrM": 3.0, "PiP": 3.8,
        "General": 1.1
    }
    salary = salary_base * level_multipliers.get(level, 1.0)
    
    # Price and UTR for billable roles
    price = 0
    utr = 0
    if role_config["has_price"]:
        # Base price from office config if available
        if role in office_config.get("roles", {}) and level in office_config["roles"][role]:
            level_config = office_config["roles"][role][level]
            price = level_config.get("price_1", 100)  # Default to first month price
            utr = level_config.get("utr_1", 0.75)    # Default to first month UTR
        else:
            # Fallback calculation
            base_price = 80 + (level_multipliers.get(level, 1.0) * 30)
            price = base_price
            utr = 0.70 + (level_multipliers.get(level, 1.0) * 0.02)  # 70-85% UTR range
    
    return {
        "recruitment": round(recruitment, 2),
        "churn": round(churn, 2),
        "salary": round(salary),
        "price": round(price),
        "utr": round(utr, 2)
    }

def create_monthly_plan(office_id: str, year: int, month: int, entries: List[Dict[str, Any]]) -> bool:
    """Create a monthly business plan via API"""
    plan_data = {
        "office_id": office_id,
        "year": year,
        "month": month,
        "entries": entries
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/business-plans", json=plan_data)
        if response.status_code in [200, 201]:
            print(f"✅ Created plan for {office_id} {year}-{month:02d}")
            return True
        else:
            print(f"❌ Failed to create plan for {office_id} {year}-{month:02d}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error creating plan for {office_id} {year}-{month:02d}: {e}")
        return False

def populate_office_business_plan(office: Dict[str, Any], office_config: Dict[str, Any]):
    """Populate business plan for a single office"""
    office_id = office["id"]
    office_name = office["name"]
    
    print(f"\n🏢 Populating business plan for {office_name} ({office_id})")
    
    # Get office config if available
    config = office_config.get(office_name, {})
    
    for month in MONTHS:
        entries = []
        
        for role_name, role_config in ROLE_CONFIG.items():
            if role_config["has_levels"]:
                # Leveled roles (Consultant, Sales, Recruitment)
                for level in role_config["levels"]:
                    values = calculate_realistic_values(config, role_name, level, month)
                    
                    entry = {
                        "role": role_name,
                        "level": level,
                        "recruitment": values["recruitment"],
                        "churn": values["churn"],
                        "salary": values["salary"],
                        "price": values["price"],
                        "utr": values["utr"]
                    }
                    entries.append(entry)
            else:
                # Flat roles (Operations)
                values = calculate_realistic_values(config, role_name, "General", month)
                
                entry = {
                    "role": role_name,
                    "level": "General",
                    "recruitment": values["recruitment"],
                    "churn": values["churn"],
                    "salary": values["salary"],
                    "price": values["price"],
                    "utr": values["utr"]
                }
                entries.append(entry)
        
        # Create the monthly plan
        success = create_monthly_plan(office_id, CURRENT_YEAR, month, entries)
        if not success:
            print(f"⚠️  Skipping remaining months for {office_name} due to error")
            break

def main():
    """Main function to populate business plans"""
    print("🚀 Business Plan Population Script")
    print("=" * 50)
    
    # Load office configuration
    print("📋 Loading office configuration...")
    try:
        office_config = load_office_config()
        print(f"✅ Loaded configuration for {len(office_config)} offices")
    except Exception as e:
        print(f"❌ Failed to load office configuration: {e}")
        return
    
    # Get offices from API
    print("🌐 Fetching offices from API...")
    offices = get_offices_from_api()
    if not offices:
        print("❌ No offices found or API unavailable")
        return
    
    print(f"✅ Found {len(offices)} offices")
    
    # Populate business plans for each office
    success_count = 0
    total_count = len(offices)
    
    for office in offices:
        try:
            populate_office_business_plan(office, office_config)
            success_count += 1
        except Exception as e:
            print(f"❌ Error populating {office.get('name', 'Unknown')}: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Population Summary")
    print(f"✅ Successfully populated: {success_count}/{total_count} offices")
    print(f"📅 Year: {CURRENT_YEAR}")
    print(f"📆 Months: {len(MONTHS)} months (Jan-Dec)")
    print(f"👥 Roles: {len(ROLE_CONFIG)} roles")
    print(f"📈 Total entries per office: ~{sum(len(config['levels']) if config['has_levels'] else 1 for config in ROLE_CONFIG.values())} per month")
    
    if success_count == total_count:
        print("\n🎉 All business plans populated successfully!")
    else:
        print(f"\n⚠️  {total_count - success_count} offices had errors")

if __name__ == "__main__":
    main()