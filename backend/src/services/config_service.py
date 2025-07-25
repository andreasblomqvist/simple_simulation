"""
Configuration Service - Manages configuration data from Excel imports and JSON
"""
import pandas as pd
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class OfficeConfig:
    name: str
    total_fte: float
    journey: str
    roles: Dict[str, Any]

class ConfigService:
    def __init__(self, config_file_path: str = None):
        # Use environment variable if available, otherwise use default
        if config_file_path is None:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to backend directory and then to config
            backend_dir = os.path.dirname(os.path.dirname(current_dir))
            config_file_path = os.path.join(backend_dir, "config", "office_configuration.json")
        self.config_file_path = config_file_path
        self.ensure_config_directory()
        self._cached_config: Optional[Dict[str, Any]] = None
        self._file_mtime: Optional[float] = None
    
    def ensure_config_directory(self):
        """Ensure the config directory exists"""
        config_dir = os.path.dirname(self.config_file_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
    
    def _is_cache_valid(self) -> bool:
        """Check if the cached config is still valid"""
        if self._cached_config is None:
            return False
        
        if not os.path.exists(self.config_file_path):
            return False
        
        current_mtime = os.path.getmtime(self.config_file_path)
        return self._file_mtime == current_mtime
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from JSON file and cache it"""
        if self._is_cache_valid():
            # print(f"✅ [CONFIG] Using cached configuration ({len(self._cached_config)} offices)")
            return self._cached_config
        
        if not os.path.exists(self.config_file_path):
            print(f"⚠️ [CONFIG] Configuration file not found: {self.config_file_path}")
            self._cached_config = {}
            self._file_mtime = None
            return {}
        
        try:
            # print(f"📖 [CONFIG] Loading configuration from {self.config_file_path}")
            with open(self.config_file_path, 'r') as f:
                self._cached_config = json.load(f)
            
            self._file_mtime = os.path.getmtime(self.config_file_path)
            # print(f"✅ [CONFIG] Loaded {len(self._cached_config)} offices from file")
            return self._cached_config
            
        except Exception as e:
            print(f"❌ [CONFIG] Error loading configuration: {e}")
            self._cached_config = {}
            self._file_mtime = None
            return {}
    
    def _save_to_file(self, config: Dict[str, Any]):
        """Save configuration to JSON file and update cache"""
        try:
            # print(f"💾 [CONFIG] Saving configuration to {self.config_file_path}")
            with open(self.config_file_path, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            
            self._cached_config = config
            self._file_mtime = os.path.getmtime(self.config_file_path)
            # print(f"✅ [CONFIG] Saved {len(config)} offices to file")
            
        except Exception as e:
            print(f"❌ [CONFIG] Error saving configuration: {e}")
    
    def get_config(self):
        """Return the current configuration. Uses cached config if valid, otherwise loads from file."""
        return self._load_from_file()
    
    def update_configuration(self, updates: Dict[str, Any]) -> int:
        """Update the configuration with provided changes and save to file
        
        Handles both nested format and flat dot-notation format from frontend:
        Nested: {"Stockholm": {"roles": {"Consultant": {"A": {"progression_1": 0.225}}}}}
        Flat: {"Stockholm.Consultant.A.progression_1": 0.225}
        """
        # Load current configuration
        current_config = self.get_config()
        updated_count = 0
        
        # Check if this is flat format (dot-notation keys)
        is_flat_format = any('.' in key for key in updates.keys())
        
        if is_flat_format:
            # Handle flat format from frontend
            print(f"[CONFIG_SERVICE] Processing {len(updates)} flat format updates")
            
            for flat_key, value in updates.items():
                parts = flat_key.split('.')
                if len(parts) < 4:
                    print(f"[CONFIG_SERVICE] Skipping invalid key format: {flat_key}")
                    continue
                
                office_name, role_name, level_name, field_name = parts[0], parts[1], parts[2], parts[3]
                
                # Initialize nested structure if needed
                if office_name not in current_config:
                    current_config[office_name] = {
                        "name": office_name,
                        "total_fte": 0,
                        "journey": "New Office",
                        "roles": {}
                    }
                
                if "roles" not in current_config[office_name]:
                    current_config[office_name]["roles"] = {}
                
                if role_name not in current_config[office_name]["roles"]:
                    current_config[office_name]["roles"][role_name] = {}
                
                if level_name not in current_config[office_name]["roles"][role_name]:
                    current_config[office_name]["roles"][role_name][level_name] = {}
                
                # Update the field
                current_value = current_config[office_name]["roles"][role_name][level_name].get(field_name)
                if current_value != value:
                    current_config[office_name]["roles"][role_name][level_name][field_name] = value
                    updated_count += 1
                    print(f"[CONFIG_SERVICE] Updated {flat_key} = {value}")
        else:
            # Handle nested format (original logic)
            print(f"[CONFIG_SERVICE] Processing {len(updates)} nested format updates")
            
            for office_name, office_updates in updates.items():
                if office_name not in current_config:
                    current_config[office_name] = {
                        "name": office_name,
                        "total_fte": 0,
                        "journey": "New Office",
                        "roles": {}
                    }
                
                # Update office-level fields
                for key, value in office_updates.items():
                    if key != "roles":  # Handle roles separately
                        if current_config[office_name].get(key) != value:
                            current_config[office_name][key] = value
                            updated_count += 1
                            print(f"[CONFIG_SERVICE] Updated {office_name}.{key} = {value}")
                    
                    # Handle roles updates if provided
                    elif key == "roles" and isinstance(value, dict):
                        if "roles" not in current_config[office_name]:
                            current_config[office_name]["roles"] = {}
                        
                        for role_name, role_updates in value.items():
                            if role_name not in current_config[office_name]["roles"]:
                                current_config[office_name]["roles"][role_name] = {}
                            
                            # Handle role-level updates
                            if isinstance(role_updates, dict):
                                for level_name, level_updates in role_updates.items():
                                    if level_name not in current_config[office_name]["roles"][role_name]:
                                        current_config[office_name]["roles"][role_name][level_name] = {}
                                    
                                    # Update level fields
                                    if isinstance(level_updates, dict):
                                        for field, field_value in level_updates.items():
                                            if current_config[office_name]["roles"][role_name][level_name].get(field) != field_value:
                                                current_config[office_name]["roles"][role_name][level_name][field] = field_value
                                                updated_count += 1
                                                print(f"[CONFIG_SERVICE] Updated {office_name}.{role_name}.{level_name}.{field} = {field_value}")
        
        # Save updated configuration
        self._save_to_file(current_config)
        
        return updated_count
    
    def set_value(self, office: str, role: str, level: str, attribute: str, value: Any):
        """Set a specific configuration value and save to file"""
        config = self.get_config()
        
        # Initialize nested structure if needed
        if office not in config:
            config[office] = {"name": office, "total_fte": 0, "journey": "New Office", "roles": {}}
        if role not in config[office]["roles"]:
            config[office]["roles"][role] = {}
        if level not in config[office]["roles"][role]:
            config[office]["roles"][role][level] = {}
        
        # Set the value
        config[office]["roles"][role][level][attribute] = value
        
        # Save to file
        self._save_to_file(config)
        
        print(f"[CONFIG_SERVICE] Set {office}.{role}.{level}.{attribute} = {value}")
    
    def import_from_excel(self, df: pd.DataFrame) -> int:
        """Import configuration from Excel DataFrame and merge with existing configuration"""
        print(f"[CONFIG_SERVICE] Starting Excel import with {len(df)} rows...")
        
        # Load existing configuration instead of starting with empty dict
        config = self.get_config()
        updated_count = 0
        
        # Track which offices are being updated from Excel
        updated_offices = set()
        
        for index, row in df.iterrows():
            try:
                office = str(row['Office'])
                role = str(row['Role'])
                # Handle NaN from pandas as 'N/A' for consistency
                level = 'N/A' if pd.isna(row['Level']) else str(row['Level'])
                
                # Initialize nested structure if office doesn't exist
                if office not in config:
                    config[office] = {
                        "name": office,
                        "total_fte": 0,
                        "journey": "New Office",
                        "roles": {}
                    }
                    print(f"[CONFIG_SERVICE] Created new office: {office}")
                
                if role not in config[office]["roles"]:
                    config[office]["roles"][role] = {}
                
                # If the role is 'Operations', merge data directly, don't create a level
                if role == 'Operations':
                    level_config = config[office]["roles"][role]
                else:
                    if level not in config[office]["roles"][role]:
                        config[office]["roles"][role][level] = {}
                    level_config = config[office]["roles"][role][level]
                
                # Import all attributes from the row
                for col in df.columns:
                    if col in ['Office', 'Role', 'Level']:
                        continue
                    
                    value = row[col]
                    if pd.isna(value):
                        continue
                    
                    # Convert string numbers with commas to float
                    if isinstance(value, str):
                        if ',' in value:
                            try:
                                value = float(value.replace(',', '.'))
                            except ValueError:
                                pass
                        elif value.replace('.', '').replace('-', '').isdigit():
                            try:
                                value = float(value)
                            except ValueError:
                                pass
                    
                    # Only update if value is different
                    current_value = level_config.get(col.lower())
                    if current_value != value:
                        level_config[col.lower()] = value
                        updated_count += 1
                        print(f"[CONFIG_SERVICE] Updated {office}.{role}.{level}.{col.lower()} = {value}")
                
                updated_offices.add(office)
                
            except Exception as e:
                print(f"[CONFIG_SERVICE] Error processing row {index}: {e}")
                continue
        
        # Recalculate total FTE only for offices that were updated
        for office_name in updated_offices:
            if office_name in config:
                total_fte = 0
                for role_name, role_data in config[office_name]["roles"].items():
                    # Handle flat roles like 'Operations' that have FTE at the top level
                    if role_name == 'Operations' and 'fte' in role_data and isinstance(role_data['fte'], (int, float)):
                        total_fte += role_data['fte']
                    # Handle hierarchical roles like 'Consultant'
                    elif isinstance(role_data, dict):
                        for level_name, level_data in role_data.items():
                            fte = level_data.get("fte", 0)
                            if isinstance(fte, (int, float)):
                                total_fte += fte
                
                config[office_name]["total_fte"] = total_fte
                
                # Update journey based on new FTE
                if total_fte >= 500:
                    config[office_name]["journey"] = "Mature Office"
                elif total_fte >= 200:
                    config[office_name]["journey"] = "Established Office"
                elif total_fte >= 25:
                    config[office_name]["journey"] = "Emerging Office"
                else:
                    config[office_name]["journey"] = "New Office"
                
                print(f"[CONFIG_SERVICE] Updated {office_name}: {total_fte} FTE, {config[office_name]['journey']}")
        
        # Save the merged configuration to file
        self._save_to_file(config)
        
        print(f"[CONFIG_SERVICE] ✅ Import complete: {updated_count} values updated")
        print(f"[CONFIG_SERVICE] Updated {len(updated_offices)} offices: {', '.join(updated_offices)}")
        print(f"[CONFIG_SERVICE] Total configuration now has {len(config)} offices")
        
        return updated_count
    
    def get_office_names(self) -> List[str]:
        """Get list of office names"""
        config = self.get_config()
        return list(config.keys())
    
    def get_office_config(self, office_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific office"""
        config = self.get_config()
        return config.get(office_name)
    
    def delete_office(self, office_name: str) -> bool:
        """Delete an office from the configuration"""
        config = self.get_config()
        
        if office_name in config:
            del config[office_name]
            self._save_to_file(config)
            print(f"[CONFIG_SERVICE] Deleted office: {office_name}")
            return True
        else:
            print(f"[CONFIG_SERVICE] Office not found for deletion: {office_name}")
            return False
    
    def clear_configuration(self):
        """Clear all configuration data"""
        if os.path.exists(self.config_file_path):
            os.remove(self.config_file_path)
        print("[CONFIG_SERVICE] Configuration cleared")
    
    def clear_cache(self):
        """Clear the cached configuration (forces reload from file)"""
        print("🗑️ [CONFIG] Clearing configuration cache")
        self._cached_config = None
        self._file_mtime = None

    def _load_config_from_file(self):
        """Load configuration from the default file."""
        config_path = "config/office_configuration.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_configuration(self):
        """Alias for get_config, for compatibility with code expecting get_configuration."""
        return self.get_config()
    
    def validate_absolute_percentage_fields(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate absolute and percentage fields for recruitment and churn.
        Returns validation results with warnings and errors.
        """
        validation_results = {
            "warnings": [],
            "errors": [],
            "validated_offices": 0,
            "validated_roles": 0,
            "validated_levels": 0
        }
        
        for office_name, office_data in config.items():
            if "roles" not in office_data:
                continue
                
            validation_results["validated_offices"] += 1
            
            for role_name, role_data in office_data["roles"].items():
                validation_results["validated_roles"] += 1
                
                # Handle flat roles like Operations
                if role_name == 'Operations':
                    self._validate_level_fields(role_data, office_name, role_name, "N/A", validation_results)
                else:
                    # Handle hierarchical roles
                    for level_name, level_data in role_data.items():
                        validation_results["validated_levels"] += 1
                        self._validate_level_fields(level_data, office_name, role_name, level_name, validation_results)
        
        return validation_results
    
    def _validate_level_fields(self, level_data: Dict[str, Any], office_name: str, role_name: str, level_name: str, validation_results: Dict[str, Any]):
        """Validate fields for a specific level"""
        
        for month in range(1, 13):
            # Check recruitment fields
            recruitment_pct = level_data.get(f"recruitment_{month}")
            recruitment_abs = level_data.get(f"recruitment_abs_{month}")
            
            # Check churn fields
            churn_pct = level_data.get(f"churn_{month}")
            churn_abs = level_data.get(f"churn_abs_{month}")
            
            # Validate recruitment fields
            if recruitment_abs is not None and recruitment_pct is not None:
                # Both present - check for reasonable consistency
                expected_from_pct = recruitment_pct * level_data.get("fte", 0)
                if abs(recruitment_abs - expected_from_pct) > 5:  # Allow 5 FTE difference
                    validation_results["warnings"].append(
                        f"{office_name}.{role_name}.{level_name}: Month {month} recruitment_abs_{month}={recruitment_abs} "
                        f"differs significantly from percentage-based calculation ({expected_from_pct:.1f})"
                    )
            elif recruitment_abs is None and recruitment_pct is None:
                # Neither present - warning
                validation_results["warnings"].append(
                    f"{office_name}.{role_name}.{level_name}: Month {month} has no recruitment value "
                    f"(neither recruitment_{month} nor recruitment_abs_{month})"
                )
            
            # Validate churn fields
            if churn_abs is not None and churn_pct is not None:
                # Both present - check for reasonable consistency
                expected_from_pct = churn_pct * level_data.get("fte", 0)
                if abs(churn_abs - expected_from_pct) > 3:  # Allow 3 FTE difference for churn
                    validation_results["warnings"].append(
                        f"{office_name}.{role_name}.{level_name}: Month {month} churn_abs_{month}={churn_abs} "
                        f"differs significantly from percentage-based calculation ({expected_from_pct:.1f})"
                    )
            elif churn_abs is None and churn_pct is None:
                # Neither present - warning
                validation_results["warnings"].append(
                    f"{office_name}.{role_name}.{level_name}: Month {month} has no churn value "
                    f"(neither churn_{month} nor churn_abs_{month})"
                )
            
            # Validate data types and ranges
            if recruitment_pct is not None and (recruitment_pct < 0 or recruitment_pct > 1):
                validation_results["errors"].append(
                    f"{office_name}.{role_name}.{level_name}: Month {month} recruitment_{month}={recruitment_pct} "
                    f"is outside valid range [0, 1]"
                )
            
            if churn_pct is not None and (churn_pct < 0 or churn_pct > 1):
                validation_results["errors"].append(
                    f"{office_name}.{role_name}.{level_name}: Month {month} churn_{month}={churn_pct} "
                    f"is outside valid range [0, 1]"
                )
            
            if recruitment_abs is not None and (recruitment_abs < 0 or recruitment_abs > 1000):
                validation_results["errors"].append(
                    f"{office_name}.{role_name}.{level_name}: Month {month} recruitment_abs_{month}={recruitment_abs} "
                    f"is outside valid range [0, 1000]"
                )
            
            if churn_abs is not None and (churn_abs < 0 or churn_abs > 1000):
                validation_results["errors"].append(
                    f"{office_name}.{role_name}.{level_name}: Month {month} churn_abs_{month}={churn_abs} "
                    f"is outside valid range [0, 1000]"
                )

# Global instance
config_service = ConfigService() 