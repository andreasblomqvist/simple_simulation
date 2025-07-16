"""
Data Transformation Service for Unified Data Structures

Handles transformation between different data formats and provides utilities
for migrating legacy data to the unified structure.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import logging
import copy
import json

from .unified_data_models import (
    ScenarioDefinition,
    TimeRange,
    EconomicParameters,
    BaselineInput,
    MonthlyValues,
    RoleData,
    LevelData,
    Levers,
    migrate_old_scenario_to_unified
)

logger = logging.getLogger(__name__)


class DataTransformationService:
    """Service for transforming data between different formats"""
    
    def __init__(self):
        self.transformation_log = []
    
    def log_transformation(self, operation: str, details: str):
        """Log a transformation operation"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'details': details
        }
        self.transformation_log.append(log_entry)
        logger.info(f"Transformation: {operation} - {details}")
    
    def transform_legacy_scenario(self, legacy_data: Dict[str, Any]) -> ScenarioDefinition:
        """
        Transform legacy scenario data to unified structure.
        Handles field name changes, structure updates, and validation.
        """
        self.log_transformation("legacy_scenario_transform", f"Processing scenario: {legacy_data.get('name', 'Unknown')}")
        
        # Create a working copy
        working_data = copy.deepcopy(legacy_data)
        
        # Handle field name standardization
        self._standardize_field_names(working_data)
        
        # Handle structure transformations
        self._transform_baseline_input_structure(working_data)
        
        # Handle time range format
        self._standardize_time_range(working_data)
        
        # Handle economic parameters
        self._standardize_economic_params(working_data)
        
        # Handle levers structure
        self._standardize_levers(working_data)
        
        # Remove deprecated fields
        self._remove_deprecated_fields(working_data)
        
        # Use unified model for final validation
        return migrate_old_scenario_to_unified(working_data)
    
    def _standardize_field_names(self, data: Dict[str, Any]):
        """Standardize field names throughout the data structure"""
        
        # Field name mappings
        field_mappings = {
            'total': 'fte',
            'Price_1': 'price_1',
            'Price_2': 'price_2',
            'Price_3': 'price_3',
            'Price_4': 'price_4',
            'Price_5': 'price_5',
            'Price_6': 'price_6',
            'Price_7': 'price_7',
            'Price_8': 'price_8',
            'Price_9': 'price_9',
            'Price_10': 'price_10',
            'Price_11': 'price_11',
            'Price_12': 'price_12',
        }
        
        self._apply_field_mappings(data, field_mappings)
        self.log_transformation("field_name_standardization", f"Applied {len(field_mappings)} field mappings")
    
    def _apply_field_mappings(self, data: Union[Dict, List], mappings: Dict[str, str]):
        """Recursively apply field name mappings to nested structures"""
        
        if isinstance(data, dict):
            # Apply mappings to current level
            for old_name, new_name in mappings.items():
                if old_name in data:
                    data[new_name] = data.pop(old_name)
            
            # Recursively apply to nested structures
            for key, value in data.items():
                self._apply_field_mappings(value, mappings)
        
        elif isinstance(data, list):
            for item in data:
                self._apply_field_mappings(item, mappings)
    
    def _transform_baseline_input_structure(self, data: Dict[str, Any]):
        """Transform baseline input to unified structure"""
        
        baseline_input = data.get('baseline_input', {})
        if not baseline_input:
            return
        
        # Ensure global structure exists
        if 'global' not in baseline_input:
            # If baseline_input doesn't have 'global', wrap it
            global_data = baseline_input.copy()
            baseline_input.clear()
            baseline_input['global'] = global_data
        
        global_data = baseline_input['global']
        
        # Ensure recruitment and churn sections exist
        for section in ['recruitment', 'churn']:
            if section not in global_data:
                global_data[section] = {}
        
        # Transform to unified RoleData structure
        self._transform_to_unified_baseline_structure(global_data)
        
        self.log_transformation("baseline_input_structure", "Transformed baseline input structure")
    
    def _transform_to_unified_baseline_structure(self, global_data: Dict[str, Any]):
        """Transform global baseline data to unified RoleData structure"""
        
        # For baseline input, the structure should be simpler:
        # Current: { recruitment: { Consultant: { A: {202501: 20} } }, churn: { Consultant: { A: {202501: 2} } } }
        # Target: { recruitment: { Consultant: { levels: { A: { recruitment: {values: {202501: 20}}, churn: {values: {202501: 2}} } } } } }
        # BUT in baseline input context, we need to merge recruitment and churn data for the same role
        
        recruitment_data = global_data.get('recruitment', {})
        churn_data = global_data.get('churn', {})
        
        # Get all role names from both sections
        all_roles = set(recruitment_data.keys()) | set(churn_data.keys())
        
        # Create unified structure by merging recruitment and churn data
        for role_name in all_roles:
            role_recruitment = recruitment_data.get(role_name, {})
            role_churn = churn_data.get(role_name, {})
            
            # Check if this is leveled data
            if self._is_leveled_role_data(role_recruitment) or self._is_leveled_role_data(role_churn):
                # Create unified leveled role structure
                unified_role = self._create_unified_baseline_role_data(role_recruitment, role_churn)
            else:
                # Create unified flat role structure
                self._ensure_monthly_format(role_recruitment)
                self._ensure_monthly_format(role_churn)
                unified_role = {
                    'recruitment': {'values': role_recruitment},
                    'churn': {'values': role_churn}
                }
            
            # Update both sections with the unified role data
            global_data['recruitment'][role_name] = unified_role
            global_data['churn'][role_name] = unified_role
    
    def _create_unified_baseline_role_data(self, role_recruitment: Dict, role_churn: Dict) -> Dict[str, Any]:
        """Create unified RoleData structure for baseline input"""
        
        # Get all level names from both recruitment and churn
        all_levels = set(role_recruitment.keys()) | set(role_churn.keys())
        
        unified_levels = {}
        for level_name in all_levels:
            recruitment_monthly = role_recruitment.get(level_name, {})
            churn_monthly = role_churn.get(level_name, {})
            
            # Ensure monthly format
            self._ensure_monthly_format(recruitment_monthly)
            self._ensure_monthly_format(churn_monthly)
            
            # Create LevelData structure
            unified_levels[level_name] = {
                'recruitment': {'values': recruitment_monthly},
                'churn': {'values': churn_monthly}
            }
        
        return {'levels': unified_levels}
    
    def _transform_role_data_structure(self, role_data: Dict[str, Any], context: str):
        """Transform role data to match unified structure"""
        
        # Check if this looks like old monthly fields structure
        monthly_fields = [f'value_{i}' for i in range(1, 13)]
        has_monthly_fields = any(field in role_data for field in monthly_fields)
        
        if has_monthly_fields:
            # Transform monthly fields to YYYYMM format
            current_year = datetime.now().year
            monthly_values = {}
            
            for i in range(1, 13):
                field_name = f'value_{i}'
                if field_name in role_data:
                    month_key = f"{current_year}{i:02d}"
                    monthly_values[month_key] = role_data.pop(field_name)
            
            # Clear old structure and add new structure
            role_data.clear()
            role_data.update(monthly_values)
            
            self.log_transformation("role_data_structure", f"Transformed monthly fields for {context}")
        
        # Check if this looks like a leveled role structure (has level names as keys)
        elif self._is_leveled_role_data(role_data):
            # This is a leveled role - transform to unified structure
            self._transform_to_unified_role_structure(role_data, context)
        else:
            # This is a flat role - ensure proper YYYYMM format
            self._ensure_monthly_format(role_data)
    
    def _transform_to_unified_role_structure(self, role_data: Dict[str, Any], context: str):
        """Transform leveled role data to unified structure with 'levels', 'recruitment', 'churn'"""
        
        # Current structure: { "A": { "202501": 20 }, "AC": { "202501": 15 } }
        # Target structure: { "levels": { "A": { "recruitment": {...}, "churn": {...} } } }
        
        # Check if already in unified format
        if 'levels' in role_data:
            # Already in unified format, just validate the nested structure
            for level_name, level_data in role_data['levels'].items():
                if isinstance(level_data, dict):
                    for data_type in ['recruitment', 'churn']:
                        if data_type in level_data and isinstance(level_data[data_type], dict):
                            if 'values' in level_data[data_type]:
                                # Already in proper format with 'values' wrapper
                                self._ensure_monthly_format(level_data[data_type]['values'])
                            else:
                                # Direct monthly values, need to wrap in 'values'
                                monthly_data = level_data[data_type]
                                self._ensure_monthly_format(monthly_data)
                                level_data[data_type] = {'values': monthly_data}
            return
        
        # Transform flat level structure to unified format
        # Store original level data
        original_levels = role_data.copy()
        role_data.clear()
        
        # Create unified structure
        unified_levels = {}
        
        for level_name, level_monthly_data in original_levels.items():
            if isinstance(level_monthly_data, dict):
                # Ensure monthly format
                self._ensure_monthly_format(level_monthly_data)
                
                # Create level data structure for baseline input
                # In baseline_input context, we need recruitment/churn structure
                if 'recruitment' in context or 'churn' in context:
                    # This is baseline data - the monthly values go directly under the level
                    unified_levels[level_name] = level_monthly_data
                else:
                    # This might be configuration data - create full structure
                    unified_levels[level_name] = {
                        'recruitment': {'values': level_monthly_data.copy()},
                        'churn': {'values': level_monthly_data.copy()}
                    }
        
        # Update role_data with unified structure
        if 'recruitment' in context or 'churn' in context:
            # For baseline input, keep the flat structure
            role_data.update(unified_levels)
        else:
            # For other contexts, use levels wrapper
            role_data['levels'] = unified_levels
        
        self.log_transformation("unified_role_structure", f"Transformed role to unified structure for {context}")
    
    def _is_leveled_role_data(self, role_data: Dict[str, Any]) -> bool:
        """Check if role data represents a leveled role"""
        if not role_data:
            return False
        
        # Check for unified structure indicators
        if 'levels' in role_data:
            return True
        
        # Check if keys look like level names (A, AC, C, etc.) rather than month keys
        keys = list(role_data.keys())
        month_keys = [k for k in keys if len(k) == 6 and k.isdigit()]
        level_like_keys = [k for k in keys if len(k) <= 3 and k.isalpha()]
        
        # If most keys are month keys (YYYYMM format), it's a flat role
        if len(month_keys) > len(keys) * 0.5:
            return False
        
        # If we have level-like keys (short alphabetic), it's probably leveled
        if len(level_like_keys) > 0:
            return True
        
        # Check if any values are dictionaries (indicating nested structure)
        has_nested_dicts = any(isinstance(v, dict) for v in role_data.values())
        if has_nested_dicts:
            return True
        
        # Default to flat role
        return False
    
    def _ensure_monthly_format(self, data: Dict[str, Any]):
        """Ensure data uses YYYYMM format for month keys"""
        # Already in correct format if all keys are YYYYMM
        if all(len(k) == 6 and k.isdigit() for k in data.keys()):
            return
        
        # Transform if needed
        current_year = datetime.now().year
        new_data = {}
        
        for key, value in data.items():
            if key.isdigit() and len(key) <= 2:
                # Convert month number to YYYYMM
                month_key = f"{current_year}{int(key):02d}"
                new_data[month_key] = value
            else:
                new_data[key] = value
        
        data.clear()
        data.update(new_data)
    
    def _standardize_time_range(self, data: Dict[str, Any]):
        """Standardize time range format"""
        
        time_range = data.get('time_range', {})
        if not time_range:
            return
        
        # Ensure all required fields exist
        required_fields = ['start_year', 'start_month', 'end_year', 'end_month']
        for field in required_fields:
            if field not in time_range:
                # Set default values if missing
                if field == 'start_year':
                    time_range[field] = datetime.now().year
                elif field == 'start_month':
                    time_range[field] = 1
                elif field == 'end_year':
                    time_range[field] = datetime.now().year + 5
                elif field == 'end_month':
                    time_range[field] = 12
        
        # Ensure values are integers
        for field in required_fields:
            if field in time_range:
                time_range[field] = int(time_range[field])
        
        self.log_transformation("time_range_standardization", "Standardized time range format")
    
    def _standardize_economic_params(self, data: Dict[str, Any]):
        """Standardize economic parameters"""
        
        economic_params = data.get('economic_params', {})
        if not economic_params:
            # Set default economic parameters
            data['economic_params'] = {
                'working_hours_per_month': 160.0,
                'employment_cost_rate': 0.3,
                'unplanned_absence': 0.05,
                'other_expense': 1000000.0
            }
        else:
            # Ensure all required fields exist with defaults
            defaults = {
                'working_hours_per_month': 160.0,
                'employment_cost_rate': 0.3,
                'unplanned_absence': 0.05,
                'other_expense': 1000000.0
            }
            
            for field, default_value in defaults.items():
                if field not in economic_params:
                    economic_params[field] = default_value
        
        self.log_transformation("economic_params_standardization", "Standardized economic parameters")
    
    def _standardize_levers(self, data: Dict[str, Any]):
        """Standardize levers structure"""
        
        levers = data.get('levers', {})
        if not levers:
            # Set default levers
            data['levers'] = {
                'recruitment': {},
                'churn': {},
                'progression': {}
            }
        else:
            # Ensure all required sections exist
            required_sections = ['recruitment', 'churn', 'progression']
            for section in required_sections:
                if section not in levers:
                    levers[section] = {}
        
        self.log_transformation("levers_standardization", "Standardized levers structure")
    
    def _remove_deprecated_fields(self, data: Dict[str, Any]):
        """Remove deprecated fields from data structure"""
        
        deprecated_fields = [
            'progression_rate',
            'total',  # Use 'fte' instead
            'legacy_field_1',
            'legacy_field_2'
        ]
        
        removed_count = 0
        
        def remove_from_dict(d):
            nonlocal removed_count
            if isinstance(d, dict):
                for field in deprecated_fields:
                    if field in d:
                        del d[field]
                        removed_count += 1
                
                # Recursively process nested structures
                for key, value in d.items():
                    remove_from_dict(value)
            elif isinstance(d, list):
                for item in d:
                    remove_from_dict(item)
        
        remove_from_dict(data)
        
        if removed_count > 0:
            self.log_transformation("deprecated_fields_removal", f"Removed {removed_count} deprecated fields")
    
    def transform_frontend_to_backend(self, frontend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform frontend data format to backend format.
        Handles differences in structure and field names.
        """
        self.log_transformation("frontend_to_backend", "Transforming frontend data to backend format")
        
        # Create working copy
        backend_data = copy.deepcopy(frontend_data)
        
        # Handle BaselineInputGrid format transformation
        if 'baseline_input' in backend_data:
            self._transform_baseline_input_from_frontend(backend_data['baseline_input'])
        
        # Ensure proper structure for backend processing
        self._ensure_backend_structure(backend_data)
        
        return backend_data
    
    def _transform_baseline_input_from_frontend(self, baseline_input: Dict[str, Any]):
        """Transform baseline input from frontend format to backend format"""
        
        # Frontend sends: { global: { recruitment: { Role: { Level: { "202501": 20 } } } } }
        # Backend expects same structure but with validation
        
        global_data = baseline_input.get('global', {})
        
        for section_name in ['recruitment', 'churn']:
            section_data = global_data.get(section_name, {})
            
            for role_name, role_data in section_data.items():
                if isinstance(role_data, dict):
                    # Check if this is leveled role data
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, dict):
                            # Ensure all month keys are strings and values are numbers
                            for month_key, value in level_data.items():
                                if isinstance(value, str) and value.isdigit():
                                    level_data[month_key] = float(value)
                                elif value is None:
                                    level_data[month_key] = 0.0
        
        self.log_transformation("baseline_input_from_frontend", "Transformed baseline input from frontend")
    
    def _ensure_backend_structure(self, data: Dict[str, Any]):
        """Ensure data has proper structure for backend processing"""
        
        # Ensure timestamps exist
        if 'created_at' not in data:
            data['created_at'] = datetime.now().isoformat()
        
        if 'updated_at' not in data:
            data['updated_at'] = datetime.now().isoformat()
        
        # Ensure required fields exist
        required_fields = {
            'name': 'Untitled Scenario',
            'description': 'No description',
            'office_scope': ['Group']
        }
        
        for field, default_value in required_fields.items():
            if field not in data:
                data[field] = default_value
        
        self.log_transformation("backend_structure", "Ensured proper backend structure")
    
    def transform_backend_to_frontend(self, backend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform backend data format to frontend format.
        Handles serialization and format differences.
        """
        self.log_transformation("backend_to_frontend", "Transforming backend data to frontend format")
        
        # Create working copy
        frontend_data = copy.deepcopy(backend_data)
        
        # Handle datetime serialization
        self._serialize_datetimes(frontend_data)
        
        # Handle enum serialization
        self._serialize_enums(frontend_data)
        
        # Ensure frontend-friendly structure
        self._ensure_frontend_structure(frontend_data)
        
        return frontend_data
    
    def _serialize_datetimes(self, data: Union[Dict, List]):
        """Convert datetime objects to ISO strings for frontend"""
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                elif isinstance(value, (dict, list)):
                    self._serialize_datetimes(value)
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._serialize_datetimes(item)
    
    def _serialize_enums(self, data: Union[Dict, List]):
        """Convert enum objects to their values for frontend"""
        
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(value, 'value'):  # Enum-like object
                    data[key] = value.value
                elif isinstance(value, (dict, list)):
                    self._serialize_enums(value)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if hasattr(item, 'value'):  # Enum-like object
                    data[i] = item.value
                elif isinstance(item, (dict, list)):
                    self._serialize_enums(item)
    
    def _ensure_frontend_structure(self, data: Dict[str, Any]):
        """Ensure data has proper structure for frontend consumption"""
        
        # Ensure ID exists
        if 'id' not in data or data['id'] is None:
            data['id'] = f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Ensure all required fields for frontend exist
        frontend_required = {
            'name': 'Untitled Scenario',
            'description': 'No description',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        for field, default_value in frontend_required.items():
            if field not in data:
                data[field] = default_value
        
        self.log_transformation("frontend_structure", "Ensured proper frontend structure")
    
    def generate_month_keys(self, start_year: int, start_month: int, end_year: int, end_month: int) -> List[str]:
        """Generate YYYYMM format month keys for a given time range"""
        
        month_keys = []
        current_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1)
        
        while current_date <= end_date:
            month_key = current_date.strftime("%Y%m")
            month_keys.append(month_key)
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return month_keys
    
    def validate_month_key(self, month_key: str) -> bool:
        """Validate that a month key is in correct YYYYMM format"""
        
        if not isinstance(month_key, str) or len(month_key) != 6:
            return False
        
        try:
            year = int(month_key[:4])
            month = int(month_key[4:6])
            
            # Validate ranges
            if not (2020 <= year <= 2040):
                return False
            
            if not (1 <= month <= 12):
                return False
            
            return True
        
        except ValueError:
            return False
    
    def parse_month_key(self, month_key: str) -> Optional[Dict[str, int]]:
        """Parse YYYYMM format month key into year and month"""
        
        if not self.validate_month_key(month_key):
            return None
        
        try:
            year = int(month_key[:4])
            month = int(month_key[4:6])
            return {'year': year, 'month': month}
        
        except ValueError:
            return None
    
    def format_month_key(self, year: int, month: int) -> str:
        """Format year and month into YYYYMM format"""
        
        return f"{year:04d}{month:02d}"
    
    def get_transformation_log(self) -> List[Dict[str, Any]]:
        """Get the transformation log for debugging"""
        return self.transformation_log.copy()
    
    def clear_transformation_log(self):
        """Clear the transformation log"""
        self.transformation_log.clear()


# Convenience functions for external use

def transform_legacy_scenario(legacy_data: Dict[str, Any]) -> ScenarioDefinition:
    """Convenience function to transform legacy scenario data"""
    service = DataTransformationService()
    return service.transform_legacy_scenario(legacy_data)


def transform_frontend_data(frontend_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to transform frontend data to backend format"""
    service = DataTransformationService()
    return service.transform_frontend_to_backend(frontend_data)


def transform_backend_data(backend_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to transform backend data to frontend format"""
    service = DataTransformationService()
    return service.transform_backend_to_frontend(backend_data)


def generate_month_keys(start_year: int, start_month: int, end_year: int, end_month: int) -> List[str]:
    """Convenience function to generate month keys"""
    service = DataTransformationService()
    return service.generate_month_keys(start_year, start_month, end_year, end_month)