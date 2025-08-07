"""
Snapshot Loader V2 - Population Initialization Component

Handles loading and initialization of workforce from population snapshots:
- Load population snapshots from storage
- Convert snapshot data to Person objects
- Validate snapshot data integrity  
- Initialize office workforce from snapshots
- Handle snapshot-to-simulation data transformation
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date, timedelta
import json
import logging
from pathlib import Path
from dataclasses import asdict

from .simulation_engine_v2 import (
    Person, PopulationSnapshot, WorkforceEntry, OfficeState,
    SnapshotLoaderInterface, ValidationResult, EngineValidator
)

# Set up logging
logger = logging.getLogger(__name__)


class SnapshotValidationError(Exception):
    """Exception raised when snapshot data is invalid"""
    pass


class SnapshotLoaderV2(SnapshotLoaderInterface):
    """
    Loads and initializes workforce from population snapshots
    
    Key capabilities:
    - Load snapshots from various sources (JSON files, database, API)
    - Validate snapshot data integrity
    - Convert WorkforceEntry to Person objects with proper initialization
    - Handle different snapshot formats and versions
    - Create initial office states from snapshot data
    """
    
    def __init__(self, storage_path: str = None):
        self.storage_path = Path(storage_path) if storage_path else Path("data/snapshots")
        self.loaded_snapshots: Dict[str, PopulationSnapshot] = {}
        self.validation_rules = self._setup_validation_rules()
        
    def initialize(self, **kwargs) -> bool:
        """Initialize snapshot loader with configuration"""
        if 'storage_path' in kwargs:
            self.storage_path = Path(kwargs['storage_path'])
        
        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SnapshotLoaderV2 initialized with storage path: {self.storage_path}")
        return True
    
    def load_office_snapshot(self, office_id: str, snapshot_id: str) -> List[Person]:
        """
        Load snapshot and return list of Person objects
        
        Args:
            office_id: Office identifier
            snapshot_id: Snapshot identifier
            
        Returns:
            List of Person objects initialized from snapshot
        """
        # Try to load from cache first
        cache_key = f"{office_id}_{snapshot_id}"
        if cache_key in self.loaded_snapshots:
            snapshot = self.loaded_snapshots[cache_key]
        else:
            # Load from storage
            snapshot = self._load_snapshot_from_storage(office_id, snapshot_id)
            if snapshot:
                self.loaded_snapshots[cache_key] = snapshot
        
        if not snapshot:
            logger.error(f"Could not load snapshot {snapshot_id} for office {office_id}")
            return []
        
        # Validate snapshot
        validation_result = self.validate_snapshot_data(snapshot)
        if not validation_result.is_valid:
            raise SnapshotValidationError(f"Invalid snapshot data: {validation_result.errors}")
        
        # Convert to Person objects
        people = self.create_initial_people(snapshot.workforce)
        
        logger.info(f"Loaded {len(people)} people from snapshot {snapshot_id} for office {office_id}")
        return people
    
    def create_initial_people(self, workforce_entries: List[WorkforceEntry]) -> List[Person]:
        """
        Create Person objects from workforce entries
        
        Args:
            workforce_entries: List of WorkforceEntry from snapshot
            
        Returns:
            List of initialized Person objects
        """
        people = []
        
        for entry in workforce_entries:
            # Parse dates
            hire_date = self._parse_date(entry.hire_date)
            level_start_date = self._parse_date(entry.level_start_date)
            
            if not hire_date or not level_start_date:
                logger.warning(f"Invalid dates for workforce entry {entry.id}, skipping")
                continue
            
            # Create Person object
            person = Person(
                id=entry.id,
                current_role=entry.role,
                current_level=entry.level,
                current_office=entry.office,
                hire_date=hire_date,
                current_level_start=level_start_date,
                events=[],
                is_active=True
            )
            
            people.append(person)
        
        return people
    
    def validate_snapshot_data(self, snapshot: PopulationSnapshot) -> ValidationResult:
        """
        Validate snapshot data integrity
        
        Args:
            snapshot: PopulationSnapshot to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(True)
        
        # Basic snapshot validation
        if not snapshot.id:
            result.add_error("Snapshot ID is required")
        
        if not snapshot.office_id:
            result.add_error("Office ID is required")
        
        if not snapshot.snapshot_date:
            result.add_error("Snapshot date is required")
        
        if not snapshot.workforce:
            result.add_error("Workforce data is required")
        
        # Validate snapshot date format
        if snapshot.snapshot_date:
            try:
                datetime.strptime(snapshot.snapshot_date, "%Y-%m")
            except ValueError:
                result.add_error(f"Invalid snapshot date format: {snapshot.snapshot_date}. Expected YYYY-MM")
        
        # Validate workforce entries
        for i, entry in enumerate(snapshot.workforce or []):
            entry_errors = self._validate_workforce_entry(entry, i)
            result.errors.extend(entry_errors)
            if entry_errors:
                result.is_valid = False
        
        # Business rule validations
        if result.is_valid:
            business_rule_errors = self._validate_business_rules(snapshot)
            result.errors.extend(business_rule_errors)
            if business_rule_errors:
                result.is_valid = False
        
        return result
    
    def create_office_state_from_snapshot(self, office_config: Dict[str, Any], snapshot: PopulationSnapshot) -> OfficeState:
        """
        Create OfficeState initialized from snapshot data
        
        Args:
            office_config: Office configuration data
            snapshot: Population snapshot
            
        Returns:
            OfficeState initialized with snapshot workforce
        """
        # Load people from snapshot
        people = self.create_initial_people(snapshot.workforce)
        
        # Organize workforce by role and level
        workforce = {}
        for person in people:
            if person.current_role not in workforce:
                workforce[person.current_role] = {}
            if person.current_level not in workforce[person.current_role]:
                workforce[person.current_role][person.current_level] = []
            workforce[person.current_role][person.current_level].append(person)
        
        # Create OfficeState (would need actual business plan, CAT matrix, etc.)
        office_state = OfficeState(
            name=office_config.get('name', 'Unknown Office'),
            workforce=workforce,
            business_plan=None,  # Would be loaded separately
            snapshot=snapshot,
            cat_matrix=None,     # Would be loaded separately
            economic_parameters=None  # Would be loaded separately
        )
        
        return office_state
    
    def save_snapshot(self, snapshot: PopulationSnapshot) -> bool:
        """
        Save snapshot to storage
        
        Args:
            snapshot: PopulationSnapshot to save
            
        Returns:
            True if saved successfully
        """
        try:
            file_path = self.storage_path / f"{snapshot.office_id}_{snapshot.id}.json"
            
            # Convert to dict for JSON serialization
            snapshot_dict = {
                "id": snapshot.id,
                "office_id": snapshot.office_id,
                "snapshot_date": snapshot.snapshot_date,
                "name": snapshot.name,
                "workforce": [asdict(entry) for entry in snapshot.workforce]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot_dict, f, indent=2, ensure_ascii=False)
            
            # Update cache
            cache_key = f"{snapshot.office_id}_{snapshot.id}"
            self.loaded_snapshots[cache_key] = snapshot
            
            logger.info(f"Saved snapshot {snapshot.id} to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save snapshot {snapshot.id}: {str(e)}")
            return False
    
    def list_available_snapshots(self, office_id: str = None) -> List[Dict[str, Any]]:
        """
        List available snapshots
        
        Args:
            office_id: Optional office filter
            
        Returns:
            List of snapshot metadata
        """
        snapshots = []
        
        try:
            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Filter by office if specified
                    if office_id and data.get('office_id') != office_id:
                        continue
                    
                    snapshots.append({
                        "id": data.get('id'),
                        "office_id": data.get('office_id'),
                        "name": data.get('name'),
                        "snapshot_date": data.get('snapshot_date'),
                        "workforce_count": len(data.get('workforce', [])),
                        "file_path": str(file_path)
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not read snapshot file {file_path}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error listing snapshots: {str(e)}")
        
        return sorted(snapshots, key=lambda x: x.get('snapshot_date', ''), reverse=True)
    
    def get_snapshot_statistics(self, snapshot: PopulationSnapshot) -> Dict[str, Any]:
        """Get comprehensive statistics for a snapshot"""
        workforce_by_role_level = snapshot.get_workforce_by_role_level()
        
        stats = {
            "total_workforce": len(snapshot.workforce),
            "snapshot_date": snapshot.snapshot_date,
            "roles": list(workforce_by_role_level.keys()),
            "role_counts": {},
            "level_distribution": {},
            "office_id": snapshot.office_id
        }
        
        # Count by role and level
        for role, levels in workforce_by_role_level.items():
            role_total = sum(len(entries) for entries in levels.values())
            stats["role_counts"][role] = role_total
            
            for level, entries in levels.items():
                level_key = f"{role}_{level}"
                stats["level_distribution"][level_key] = len(entries)
        
        return stats
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _load_snapshot_from_storage(self, office_id: str, snapshot_id: str) -> Optional[PopulationSnapshot]:
        """Load snapshot from storage (JSON file, database, etc.)"""
        # Try multiple file naming patterns
        possible_files = [
            self.storage_path / f"{office_id}_{snapshot_id}.json",
            self.storage_path / f"{snapshot_id}.json",
            self.storage_path / office_id / f"{snapshot_id}.json"
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Convert workforce entries
                    workforce_entries = []
                    for entry_data in data.get('workforce', []):
                        entry = WorkforceEntry(
                            id=entry_data['id'],
                            role=entry_data['role'],
                            level=entry_data['level'],
                            hire_date=entry_data['hire_date'],
                            level_start_date=entry_data['level_start_date'],
                            office=entry_data['office']
                        )
                        workforce_entries.append(entry)
                    
                    snapshot = PopulationSnapshot(
                        id=data['id'],
                        office_id=data['office_id'],
                        snapshot_date=data['snapshot_date'],
                        name=data['name'],
                        workforce=workforce_entries
                    )
                    
                    return snapshot
                    
                except Exception as e:
                    logger.error(f"Error loading snapshot from {file_path}: {str(e)}")
                    continue
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object"""
        try:
            # Handle both YYYY-MM and YYYY-MM-DD formats
            if len(date_str) == 7:  # YYYY-MM
                dt = datetime.strptime(date_str, "%Y-%m")
                return date(dt.year, dt.month, 1)  # First day of month
            elif len(date_str) == 10:  # YYYY-MM-DD
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.date()
        except ValueError:
            pass
        
        return None
    
    def _validate_workforce_entry(self, entry: WorkforceEntry, index: int) -> List[str]:
        """Validate individual workforce entry"""
        errors = []
        
        if not entry.id:
            errors.append(f"Workforce entry {index}: ID is required")
        
        if not entry.role:
            errors.append(f"Workforce entry {index}: Role is required")
        
        if not entry.level:
            errors.append(f"Workforce entry {index}: Level is required")
        
        if not entry.office:
            errors.append(f"Workforce entry {index}: Office is required")
        
        if not entry.hire_date:
            errors.append(f"Workforce entry {index}: Hire date is required")
        elif not self._parse_date(entry.hire_date):
            errors.append(f"Workforce entry {index}: Invalid hire date format")
        
        if not entry.level_start_date:
            errors.append(f"Workforce entry {index}: Level start date is required")
        elif not self._parse_date(entry.level_start_date):
            errors.append(f"Workforce entry {index}: Invalid level start date format")
        
        # Validate date logic
        if entry.hire_date and entry.level_start_date:
            hire_date = self._parse_date(entry.hire_date)
            level_date = self._parse_date(entry.level_start_date)
            if hire_date and level_date and level_date < hire_date:
                errors.append(f"Workforce entry {index}: Level start date cannot be before hire date")
        
        return errors
    
    def _validate_business_rules(self, snapshot: PopulationSnapshot) -> List[str]:
        """Validate business rules for snapshot"""
        errors = []
        
        # Check for duplicate IDs
        ids = [entry.id for entry in snapshot.workforce]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate person IDs found in workforce")
        
        # Check for reasonable workforce size
        if len(snapshot.workforce) > 10000:
            errors.append("Workforce size exceeds reasonable limit (10,000)")
        
        # Check for valid roles and levels
        valid_roles = {"Consultant", "Sales", "Recruitment", "Operations"}  # Would be configurable
        valid_levels = {"A", "AC", "C", "SrC", "M", "SrM", "Operations"}   # Would be configurable
        
        for entry in snapshot.workforce:
            if entry.role not in valid_roles:
                logger.warning(f"Unknown role '{entry.role}' in snapshot")
            
            if entry.level not in valid_levels:
                logger.warning(f"Unknown level '{entry.level}' in snapshot")
        
        return errors
    
    def _setup_validation_rules(self) -> Dict[str, Any]:
        """Setup validation rules configuration"""
        return {
            "max_workforce_size": 10000,
            "required_fields": ["id", "role", "level", "office", "hire_date", "level_start_date"],
            "date_format": "%Y-%m",
            "valid_roles": {"Consultant", "Sales", "Recruitment", "Operations"},
            "valid_levels": {"A", "AC", "C", "SrC", "M", "SrM", "Operations"}
        }


# ============================================================================
# Snapshot Utilities
# ============================================================================

class SnapshotUtilities:
    """Utility functions for snapshot operations"""
    
    @staticmethod
    def create_sample_snapshot(office_id: str, snapshot_date: str, num_people: int = 100) -> PopulationSnapshot:
        """Create a sample snapshot for testing"""
        import random
        
        roles = ["Consultant", "Sales", "Recruitment", "Operations"]
        levels = {
            "Consultant": ["A", "AC", "C", "SrC", "M"],
            "Sales": ["A", "AC", "C", "SrC"],
            "Recruitment": ["A", "AC", "C"],
            "Operations": ["Operations"]
        }
        
        workforce = []
        for i in range(num_people):
            role = random.choice(roles)
            level = random.choice(levels[role])
            
            # Generate realistic hire dates (within last 5 years)
            base_date = datetime.strptime(snapshot_date, "%Y-%m")
            months_ago = random.randint(1, 60)
            hire_date = date(base_date.year, base_date.month, 1) - timedelta(days=months_ago * 30)
            
            # Level start date (same or after hire date)
            level_months_ago = random.randint(0, months_ago)
            level_start_date = date(base_date.year, base_date.month, 1) - timedelta(days=level_months_ago * 30)
            
            entry = WorkforceEntry(
                id=f"person_{i:04d}",
                role=role,
                level=level,
                hire_date=hire_date.strftime("%Y-%m"),
                level_start_date=level_start_date.strftime("%Y-%m"),
                office=office_id
            )
            workforce.append(entry)
        
        return PopulationSnapshot(
            id=f"sample_{snapshot_date}",
            office_id=office_id,
            snapshot_date=snapshot_date,
            name=f"Sample Snapshot for {office_id}",
            workforce=workforce
        )
    
    @staticmethod
    def merge_snapshots(snapshots: List[PopulationSnapshot], merged_name: str) -> PopulationSnapshot:
        """Merge multiple snapshots into one"""
        if not snapshots:
            raise ValueError("At least one snapshot is required")
        
        # Use first snapshot as base
        base = snapshots[0]
        merged_workforce = list(base.workforce)
        
        # Add workforce from other snapshots
        for snapshot in snapshots[1:]:
            merged_workforce.extend(snapshot.workforce)
        
        return PopulationSnapshot(
            id=f"merged_{len(snapshots)}_snapshots",
            office_id="merged",
            snapshot_date=base.snapshot_date,
            name=merged_name,
            workforce=merged_workforce
        )


# ============================================================================
# Module Exports  
# ============================================================================

__all__ = [
    'SnapshotLoaderV2',
    'SnapshotValidationError',
    'SnapshotUtilities'
]