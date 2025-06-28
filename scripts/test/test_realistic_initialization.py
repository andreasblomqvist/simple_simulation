#!/usr/bin/env python3
"""
Test script to verify realistic initialization of people in the simulation engine.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from backend.src.services.simulation.office_manager import OfficeManager
from backend.src.services.config_service import ConfigService

def test_realistic_initialization():
    """Test realistic initialization with actual office configuration"""
    
    # Initialize services
    config_service = ConfigService()
    office_manager = OfficeManager(config_service)
    
    # Initialize offices with realistic people
    offices = office_manager.initialize_offices_from_config()
    
    print("=== REALISTIC INITIALIZATION TEST ===")
    print(f"Total offices: {len(offices)}")
    
    for office_name, office in offices.items():
        print(f"\n{office_name} (Total FTE: {office.total_fte}):")
        
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles
                for level_name, level in role_data.items():
                    print(f"  {role_name} {level_name}: {level.total} FTE")
                    
                    if level.total > 0:
                        # Calculate average time on level
                        avg_tenure = sum(p.get_level_tenure_months('2025-01') for p in level.people) / level.total
                        avg_career = sum(p.get_career_tenure_months('2025-01') for p in level.people) / level.total
                        
                        print(f"    Avg time on level: {avg_tenure:.1f} months")
                        print(f"    Avg career tenure: {avg_career:.1f} months")
                        
                        # Show some sample people
                        if level.total <= 5:  # Show all if small group
                            for i, person in enumerate(level.people[:3]):
                                level_tenure = person.get_level_tenure_months('2025-01')
                                career_tenure = person.get_career_tenure_months('2025-01')
                                print(f"      Person {i+1}: Level tenure {level_tenure}m, Career {career_tenure}m")
                        else:
                            # Show sample
                            for i, person in enumerate(level.people[:2]):
                                level_tenure = person.get_level_tenure_months('2025-01')
                                career_tenure = person.get_career_tenure_months('2025-01')
                                print(f"      Sample {i+1}: Level tenure {level_tenure}m, Career {career_tenure}m")
            else:  # Flat roles (Operations)
                print(f"  {role_name}: {role_data.total} FTE")
                
                if role_data.total > 0:
                    avg_career = sum(p.get_career_tenure_months('2025-01') for p in role_data.people) / role_data.total
                    print(f"    Avg career tenure: {avg_career:.1f} months")
    
    print("\n=== INITIALIZATION COMPLETE ===")

if __name__ == "__main__":
    test_realistic_initialization() 