"""
Office Builder - Creates Office objects from config data.

This service has a single responsibility: convert config dictionaries
into Office, Level, and RoleData objects for the simulation engine.
"""
import logging
from typing import Dict, Any
from dataclasses import fields

from .simulation.models import Office, Level, RoleData, Journey, OfficeJourney, Month
from .people_initializer import PeopleInitializer

logger = logging.getLogger(__name__)

class OfficeBuilder:
    """
    Builds Office objects from config data.
    Focused solely on object creation and initialization.
    """
    
    def __init__(self):
        self.people_initializer = PeopleInitializer()
    
    def build_offices_from_config(self, config: Dict[str, Any], progression_config: Dict[str, Any]) -> Dict[str, Office]:
        """
        Convert config dict into Office objects.
        Returns: Dict[office_name, Office]
        """
        offices = {}
        
        for office_name, office_config in config.items():
            office = self._build_office_from_config(office_config, progression_config)
            offices[office_name] = office
        
        return offices
    
    def _build_office_from_config(self, office_config: Dict[str, Any], progression_config: Dict[str, Any]) -> Office:
        """Build a single Office object from config."""
        # Extract office metadata
        office_name = office_config.get('name', 'Unknown Office')
        total_fte = office_config.get('total_fte', 0)
        journey_name = office_config.get('journey', 'New Office')
        
        # Map journey name to enum
        journey = self._map_journey_name(journey_name)
        
        # Create office
        office = Office(
            name=office_name,
            total_fte=total_fte,
            journey=journey,
            roles={}
        )
        
        # Build roles and levels
        roles_config = office_config.get('roles', {})
        for role_name, role_data in roles_config.items():
            self._build_role_for_office(office, role_name, role_data, progression_config)
        
        return office
    
    def _build_role_for_office(self, office: Office, role_name: str, role_data: Dict[str, Any], progression_config: Dict[str, Any]):
        """Build a role (leveled or flat) for an office."""
        # Check if this is a leveled role (has nested levels) or flat role
        is_leveled_role = (
            isinstance(role_data, dict) and 
            any(isinstance(value, dict) for value in role_data.values())
        )
        
        if is_leveled_role:
            self._build_leveled_role(office, role_name, role_data, progression_config)
        else:
            self._build_flat_role(office, role_name, role_data)
    
    def _build_leveled_role(self, office: Office, role_name: str, role_data: Dict[str, Any], progression_config: Dict[str, Any]):
        """Build a leveled role (Consultant, Sales, Recruitment)."""
        office.roles[role_name] = {}
        
        for level_name, level_config in role_data.items():
            if not isinstance(level_config, dict):
                continue
            
            level = self._build_level_from_config(level_name, level_config, role_name, office.name)
            if level:
                office.roles[role_name][level_name] = level
    
    def _build_flat_role(self, office: Office, role_name: str, role_data: Dict[str, Any]):
        """Build a flat role (Operations)."""
        role_fte = role_data.get('fte', 0)
        if role_fte > 0:
            role = self._build_flat_role_from_config(role_name, role_data, office.name)
            if role:
                office.roles[role_name] = role
    
    def _build_level_from_config(self, level_name: str, level_config: Dict[str, Any], role_name: str, office_name: str) -> Level:
        """Build a Level object from config."""
        level_fte = level_config.get('fte', 0)
        if level_fte <= 0:
            return None
        
        # Prepare constructor arguments for Level dataclass
        level_fields = {f.name for f in fields(Level)}
        level_kwargs = {k: v for k, v in level_config.items() if k in level_fields}
        # Create level with config values for all dataclass fields
        level = Level(
            name=level_name,
            journey=self._get_journey_for_level(level_name),
            progression_months=[Month(1), Month(4), Month(7), Month(10)],
            **{k: level_kwargs.get(k, 0.0) for k in level_fields if k not in ['name', 'journey', 'progression_months', 'people', 'fractional_recruitment', 'fractional_churn']},
        )
        # Initialize people for this level (FTE will be computed automatically)
        self.people_initializer.initialize_people_for_level_or_role(
            level, int(level_fte), role_name, office_name
        )
        # Set any remaining attributes from config (for dynamic fields)
        # Skip read-only properties that are computed from other attributes
        readonly_properties = {'fte', 'total'}
        for key, value in level_config.items():
            if key in readonly_properties:
                logger.debug(f"[OFFICE BUILDER] Skipping read-only property '{key}' for {level_name}")
                continue
            if not hasattr(level, key) or getattr(level, key) != value:
                try:
                    setattr(level, key, value)
                except Exception as e:
                    logger.error(f"[OFFICE BUILDER] Could not set {key}={value} on level {level_name}: {e}")
        
        return level
    
    def _build_flat_role_from_config(self, role_name: str, role_config: Dict[str, Any], office_name: str) -> RoleData:
        """Build a flat RoleData object from config."""
        role_fte = role_config.get('fte', 0)
        if role_fte <= 0:
            return None
        
        role = RoleData()
        
        # Set all attributes from config, except read-only properties
        readonly_properties = {'fte', 'total'}
        for key, value in role_config.items():
            if key in readonly_properties:
                logger.debug(f"[OFFICE BUILDER] Skipping read-only property '{key}' for role {role_name}")
                continue
            if hasattr(role, key):
                try:
                    setattr(role, key, value)
                except Exception as e:
                    logger.error(f"[OFFICE BUILDER] Could not set {key}={value} on role {role_name}: {e}")
        
        # Initialize people for this role
        self.people_initializer.initialize_people_for_level_or_role(
            role, int(role_fte), role_name, office_name
        )
        
        return role
    
    def _map_journey_name(self, journey_name: str) -> OfficeJourney:
        """Map journey name string to OfficeJourney enum."""
        journey_map = {
            'New Office': OfficeJourney.NEW,
            'Emerging Office': OfficeJourney.EMERGING,
            'Mature Office': OfficeJourney.MATURE,
            'Established Office': OfficeJourney.ESTABLISHED
        }
        return journey_map.get(journey_name, OfficeJourney.NEW)
    
    def _get_journey_for_level(self, level_name: str) -> Journey:
        """Get the Journey enum for a given level name."""
        if level_name in ['A', 'AC', 'C']:
            return Journey.JOURNEY_1
        elif level_name in ['SrC', 'AM']:
            return Journey.JOURNEY_2
        elif level_name in ['M', 'SrM', 'Pi']:
            return Journey.JOURNEY_3
        elif level_name == 'P':
            return Journey.JOURNEY_4
        else:
            return Journey.JOURNEY_1 