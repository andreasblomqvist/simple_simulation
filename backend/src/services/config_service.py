"""
Configuration Service - Manages configuration data separately from simulation engine
"""
import copy
import pandas as pd
from typing import Dict, Any
from backend.config.default_config import ACTUAL_OFFICE_LEVEL_DATA, BASE_PRICING, BASE_SALARIES, DEFAULT_RATES, OFFICE_HEADCOUNT

class ConfigurationService:
    """Service to manage configuration data independently of simulation engine"""
    
    def __init__(self):
        # Store the current configuration (starts with defaults, can be modified)
        self._config_data = None
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize configuration from default config files"""
        self._config_data = {}
        
        for office_name, office_data in ACTUAL_OFFICE_LEVEL_DATA.items():
            total_fte = OFFICE_HEADCOUNT.get(office_name, 0)
            
            # Determine office journey based on total FTE
            if total_fte >= 500:
                journey = "Mature Office"
            elif total_fte >= 200:
                journey = "Established Office"
            elif total_fte >= 25:
                journey = "Emerging Office"
            else:
                journey = "New Office"
            
            roles_data = {}
            
            # Process roles with levels (Consultant, Sales, Recruitment)
            for role_name in ["Consultant", "Sales", "Recruitment"]:
                if role_name in office_data:
                    role_levels = office_data[role_name]
                    roles_data[role_name] = {}
                    
                    for level_name, fte in role_levels.items():
                        if fte > 0:  # Only include levels with actual FTE
                            # Get pricing and salary
                            base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
                            base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
                            price = base_prices.get(level_name, 0.0)
                            salary = base_salaries.get(level_name, 0.0)
                            
                            # Get rates
                            if role_name in DEFAULT_RATES['recruitment'] and isinstance(DEFAULT_RATES['recruitment'][role_name], dict):
                                recruitment_rate = DEFAULT_RATES['recruitment'][role_name].get(level_name, 0.01)
                            else:
                                recruitment_rate = 0.01
                            
                            if role_name in DEFAULT_RATES['churn'] and isinstance(DEFAULT_RATES['churn'][role_name], dict):
                                churn_rate = DEFAULT_RATES['churn'][role_name].get(level_name, 0.014)
                            elif role_name in DEFAULT_RATES['churn']:
                                churn_rate = DEFAULT_RATES['churn'][role_name]
                            else:
                                churn_rate = 0.014
                            
                            # Set progression rate based on level
                            progression_map = {
                                'C': 0.26, 'SrC': 0.20, 'AM': 0.07, 'M': 0.12, 'SrM': 0.14,
                                'A': 0.15, 'AC': 0.12, 'PiP': 0.0
                            }
                            progression_rate = progression_map.get(level_name, 0.10)
                            
                            roles_data[role_name][level_name] = {
                                "total": fte,
                                **{f"price_{i}": price * (1 + 0.0025 * (i - 1)) for i in range(1, 13)},
                                **{f"salary_{i}": salary * (1 + 0.0025 * (i - 1)) for i in range(1, 13)},
                                **{f"recruitment_{i}": recruitment_rate for i in range(1, 13)},
                                **{f"churn_{i}": churn_rate for i in range(1, 13)},
                                **{f"progression_{i}": progression_rate if i in [1, 6] else 0.0 for i in range(1, 13)},
                                **{f"utr_{i}": DEFAULT_RATES['utr'] for i in range(1, 13)}
                            }
            
            # Process Operations (flat role)
            if "Operations" in office_data and office_data["Operations"] > 0:
                operations_fte = office_data["Operations"]
                base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
                base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
                op_price = base_prices.get('Operations', 80.0)
                op_salary = base_salaries.get('Operations', 40000.0)
                
                operations_recruitment = DEFAULT_RATES['recruitment'].get('Operations', 0.021)
                operations_churn = DEFAULT_RATES['churn'].get('Operations', 0.0149)
                
                roles_data["Operations"] = {
                    "total": operations_fte,
                    **{f"price_{i}": op_price * (1 + 0.0025 * (i - 1)) for i in range(1, 13)},
                    **{f"salary_{i}": op_salary * (1 + 0.0025 * (i - 1)) for i in range(1, 13)},
                    **{f"recruitment_{i}": operations_recruitment for i in range(1, 13)},
                    **{f"churn_{i}": operations_churn for i in range(1, 13)},
                    **{f"progression_{i}": 0.0 for i in range(1, 13)},  # Operations has no progression
                    **{f"utr_{i}": DEFAULT_RATES['utr'] for i in range(1, 13)}
                }
            
            self._config_data[office_name] = {
                "name": office_name,
                "total_fte": total_fte,
                "journey": journey,
                "roles": roles_data
            }
    
    def get_configuration(self) -> list:
        """Get current configuration as list of offices"""
        return list(self._config_data.values())
    
    def update_configuration(self, changes: Dict[str, Any]) -> int:
        """Update configuration with changes. Returns number of updates applied."""
        updated_count = 0
        
        print(f"[CONFIG_SERVICE] Applying {len(changes)} configuration changes...")
        
        for path, value in changes.items():
            try:
                # Parse the path: office.role.level.field or office.role.field
                path_parts = path.split('.')
                if len(path_parts) < 3:
                    print(f"[CONFIG_SERVICE] ⚠️ Skipping invalid path: {path}")
                    continue
                    
                office_name = path_parts[0]
                role_type = path_parts[1]
                
                # Find the office
                if office_name not in self._config_data:
                    print(f"[CONFIG_SERVICE] ⚠️ Office not found: {office_name}")
                    continue
                
                office_config = self._config_data[office_name]
                
                # Handle Operations (flat structure) vs other roles (level-based)
                if role_type == "Operations":
                    # Operations: office.role.field
                    if len(path_parts) != 3:
                        print(f"[CONFIG_SERVICE] ⚠️ Invalid Operations path: {path}")
                        continue
                        
                    field = path_parts[2]
                    if role_type in office_config["roles"] and field in office_config["roles"][role_type]:
                        office_config["roles"][role_type][field] = value
                        print(f"[CONFIG_SERVICE] ✓ Updated {path} = {value}")
                        updated_count += 1
                    else:
                        print(f"[CONFIG_SERVICE] ⚠️ Field not found: {field} in {role_type}")
                        
                else:
                    # Other roles: office.role.level.field
                    if len(path_parts) != 4:
                        print(f"[CONFIG_SERVICE] ⚠️ Invalid role path: {path}")
                        continue
                        
                    level = path_parts[2]
                    field = path_parts[3]
                    
                    # Check if role and level exist
                    if (role_type in office_config["roles"] and 
                        level in office_config["roles"][role_type] and
                        field in office_config["roles"][role_type][level]):
                        
                        office_config["roles"][role_type][level][field] = value
                        print(f"[CONFIG_SERVICE] ✓ Updated {path} = {value}")
                        updated_count += 1
                    else:
                        print(f"[CONFIG_SERVICE] ⚠️ Path not found: {path}")
                        
            except Exception as e:
                print(f"[CONFIG_SERVICE] ❌ Error updating {path}: {str(e)}")
        
        print(f"[CONFIG_SERVICE] ✅ Applied {updated_count} configuration changes")
        return updated_count
    
    def import_from_excel(self, df) -> int:
        """Import configuration changes from Excel DataFrame"""
        updated_count = 0
        
        print(f"[CONFIG_SERVICE] Processing {len(df)} rows from Excel file...")
        
        for _, row in df.iterrows():
            office_name = row.get("Office")
            role_type = row.get("Role")
            role_level = row.get("Level")
            
            if office_name and role_type and office_name in self._config_data:
                office_config = self._config_data[office_name]
                
                # Check if role exists
                if role_type in office_config["roles"]:
                    
                    # Handle Operations (flat) vs other roles (level-based)
                    if role_type == "Operations":
                        target_config = office_config["roles"][role_type]
                    else:
                        # Role with levels
                        if role_level in office_config["roles"][role_type]:
                            target_config = office_config["roles"][role_type][role_level]
                        else:
                            continue
                    
                    # Update monthly attributes
                    for i in range(1, 13):
                        for attr in ["Price", "Salary", "Recruitment", "Churn", "Progression", "UTR"]:
                            col_name = f"{attr}_{i}"
                            if col_name in row and not pd.isna(row[col_name]):
                                field_name = col_name.lower()
                                
                                try:
                                    # Handle different value types from Excel
                                    value = row[col_name]
                                    
                                    # If it's already a number, use it directly
                                    if isinstance(value, (int, float)):
                                        converted_value = float(value)
                                    # If it's a string, handle European decimal format (comma separator)
                                    elif isinstance(value, str):
                                        # Replace comma with dot for European decimal format
                                        cleaned_value = value.replace(',', '.')
                                        converted_value = float(cleaned_value)
                                    else:
                                        # Try direct conversion for other types
                                        converted_value = float(value)
                                    
                                    # Set the converted value
                                    target_config[field_name] = converted_value
                                    print(f"[CONFIG_SERVICE] Set {field_name} = {converted_value} (from '{value}')")
                                    updated_count += 1
                                    
                                except (ValueError, TypeError) as e:
                                    print(f"[CONFIG_SERVICE] Error converting {col_name}='{row[col_name]}': {e}")
                                    continue
        
        print(f"[CONFIG_SERVICE] ✅ Import complete: {updated_count} rows updated")
        return updated_count
    
    def reset_to_defaults(self):
        """Reset configuration back to defaults"""
        print("[CONFIG_SERVICE] 🔄 Resetting configuration to defaults...")
        self._initialize_config()
        print("[CONFIG_SERVICE] ✅ Configuration reset to defaults")

# Global configuration service instance
config_service = ConfigurationService() 