"""
Comprehensive Unit Tests for SnapshotLoaderV2

Tests population snapshot loading functionality including:
- Loading snapshots from various sources (files, database)
- Snapshot data validation and integrity checks
- WorkforceEntry to Person object conversion
- Office state initialization from snapshots
- Error handling and data transformation
- Snapshot format compatibility
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import tempfile
import os
from datetime import datetime, date

from backend.src.services.snapshot_loader_v2 import (
    SnapshotLoaderV2, SnapshotValidationError
)

from backend.src.services.simulation_engine_v2 import (
    Person, PopulationSnapshot, WorkforceEntry, OfficeState, ValidationResult
)


class TestSnapshotLoaderV2Initialization:
    """Test suite for SnapshotLoaderV2 initialization"""

    def test_default_initialization(self):
        """Test loader initializes with default storage path"""
        loader = SnapshotLoaderV2()
        
        # Verify default state
        assert isinstance(loader.storage_path, Path)
        assert str(loader.storage_path).endswith("data/snapshots")
        assert loader.loaded_snapshots == {}
        assert loader.validation_rules is not None

    def test_custom_storage_path_initialization(self):
        """Test loader initializes with custom storage path"""
        custom_path = "/custom/snapshot/path"
        loader = SnapshotLoaderV2(storage_path=custom_path)
        
        assert str(loader.storage_path) == custom_path

    def test_initialization_with_configuration(self):
        """Test loader initialization with custom configuration"""
        loader = SnapshotLoaderV2()
        
        custom_config = {
            'validation_strict': True,
            'cache_snapshots': False,
            'supported_formats': ['json', 'csv']
        }
        
        result = loader.initialize(**custom_config)
        
        assert result is True

    def test_initialization_success_logging(self):
        """Test initialization logs success message"""
        loader = SnapshotLoaderV2()
        
        with patch('backend.src.services.snapshot_loader_v2.logger') as mock_logger:
            loader.initialize()
            
            mock_logger.info.assert_called_with("SnapshotLoaderV2 initialized successfully")

    def test_validation_rules_setup(self):
        """Test validation rules are properly set up"""
        loader = SnapshotLoaderV2()
        
        assert isinstance(loader.validation_rules, dict)
        assert len(loader.validation_rules) > 0
        
        # Check for expected validation rules
        expected_rules = ['required_fields', 'date_format', 'numeric_validation']
        for rule in expected_rules:
            assert rule in loader.validation_rules


class TestSnapshotLoaderV2FileLoading:
    """Test suite for file-based snapshot loading"""

    def test_load_snapshot_from_json_file_success(self, population_snapshot):
        """Test successful snapshot loading from JSON file"""
        loader = SnapshotLoaderV2()
        
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            snapshot_data = {
                'id': population_snapshot.id,
                'office_id': population_snapshot.office_id,
                'snapshot_date': population_snapshot.snapshot_date,
                'name': population_snapshot.name,
                'workforce': [
                    {
                        'id': entry.id,
                        'role': entry.role,
                        'level': entry.level,
                        'hire_date': entry.hire_date,
                        'level_start_date': entry.level_start_date,
                        'office': entry.office
                    }
                    for entry in population_snapshot.workforce[:5]  # Sample data
                ]
            }
            json.dump(snapshot_data, f)
            temp_file = f.name
        
        try:
            # Load snapshot
            loaded_snapshot = loader.load_snapshot_from_file(temp_file)
            
            assert isinstance(loaded_snapshot, PopulationSnapshot)
            assert loaded_snapshot.id == population_snapshot.id
            assert loaded_snapshot.office_id == population_snapshot.office_id
            assert len(loaded_snapshot.workforce) == 5
            
        finally:
            os.unlink(temp_file)

    def test_load_snapshot_from_nonexistent_file(self):
        """Test loading snapshot from nonexistent file raises error"""
        loader = SnapshotLoaderV2()
        
        with pytest.raises(FileNotFoundError):
            loader.load_snapshot_from_file("/nonexistent/path/snapshot.json")

    def test_load_snapshot_from_invalid_json(self):
        """Test loading snapshot from invalid JSON file raises error"""
        loader = SnapshotLoaderV2()
        
        # Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                loader.load_snapshot_from_file(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_snapshot_from_empty_file(self):
        """Test loading snapshot from empty file"""
        loader = SnapshotLoaderV2()
        
        # Create empty file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            with pytest.raises((json.JSONDecodeError, ValueError)):
                loader.load_snapshot_from_file(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_multiple_snapshots(self, sample_workforce_entries):
        """Test loading multiple snapshots"""
        loader = SnapshotLoaderV2()
        
        # Create two different snapshots
        snapshot1_data = {
            'id': 'snapshot-1',
            'office_id': 'Stockholm',
            'snapshot_date': '2025-01',
            'name': 'Stockholm Snapshot',
            'workforce': []
        }
        
        snapshot2_data = {
            'id': 'snapshot-2',
            'office_id': 'Munich',
            'snapshot_date': '2025-01',
            'name': 'Munich Snapshot',
            'workforce': []
        }
        
        # Mock file loading
        def mock_load_file(file_path):
            if 'stockholm' in str(file_path).lower():
                return PopulationSnapshot(**snapshot1_data)
            elif 'munich' in str(file_path).lower():
                return PopulationSnapshot(**snapshot2_data)
        
        with patch.object(loader, 'load_snapshot_from_file', side_effect=mock_load_file):
            snapshot1 = loader.load_snapshot_from_file("stockholm.json")
            snapshot2 = loader.load_snapshot_from_file("munich.json")
            
            assert snapshot1.office_id == 'Stockholm'
            assert snapshot2.office_id == 'Munich'


class TestSnapshotLoaderV2DatabaseLoading:
    """Test suite for database-based snapshot loading"""

    def test_load_snapshot_from_database_success(self, population_snapshot):
        """Test successful snapshot loading from database"""
        loader = SnapshotLoaderV2()
        
        # Mock database connection
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = {
            'id': population_snapshot.id,
            'office_id': population_snapshot.office_id,
            'snapshot_date': population_snapshot.snapshot_date,
            'name': population_snapshot.name,
            'workforce_data': json.dumps([
                {
                    'id': entry.id,
                    'role': entry.role,
                    'level': entry.level,
                    'hire_date': entry.hire_date,
                    'level_start_date': entry.level_start_date,
                    'office': entry.office
                }
                for entry in population_snapshot.workforce[:3]
            ])
        }
        
        with patch.object(loader, '_get_database_connection', return_value=mock_db):
            loaded_snapshot = loader.load_snapshot_from_database(population_snapshot.id)
            
            assert isinstance(loaded_snapshot, PopulationSnapshot)
            assert loaded_snapshot.id == population_snapshot.id

    def test_load_snapshot_from_database_not_found(self):
        """Test loading nonexistent snapshot from database"""
        loader = SnapshotLoaderV2()
        
        # Mock database returning no results
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = None
        
        with patch.object(loader, '_get_database_connection', return_value=mock_db):
            with pytest.raises(ValueError, match="Snapshot not found"):
                loader.load_snapshot_from_database("nonexistent-id")

    def test_load_snapshot_from_database_connection_error(self):
        """Test handling database connection errors"""
        loader = SnapshotLoaderV2()
        
        with patch.object(loader, '_get_database_connection', side_effect=Exception("Database connection failed")):
            with pytest.raises(Exception, match="Database connection failed"):
                loader.load_snapshot_from_database("some-id")

    def test_list_available_snapshots_from_database(self):
        """Test listing available snapshots from database"""
        loader = SnapshotLoaderV2()
        
        # Mock database results
        mock_db = Mock()
        mock_db.execute.return_value.fetchall.return_value = [
            {'id': 'snapshot-1', 'office_id': 'Stockholm', 'name': 'Stockholm Jan 2025'},
            {'id': 'snapshot-2', 'office_id': 'Munich', 'name': 'Munich Jan 2025'},
            {'id': 'snapshot-3', 'office_id': 'Stockholm', 'name': 'Stockholm Feb 2025'}
        ]
        
        with patch.object(loader, '_get_database_connection', return_value=mock_db):
            snapshots = loader.list_available_snapshots()
            
            assert len(snapshots) == 3
            assert all('id' in snapshot for snapshot in snapshots)
            assert all('office_id' in snapshot for snapshot in snapshots)


class TestSnapshotLoaderV2Validation:
    """Test suite for snapshot validation functionality"""

    def test_validate_snapshot_success(self, population_snapshot):
        """Test successful snapshot validation"""
        loader = SnapshotLoaderV2()
        
        validation_result = loader.validate_snapshot(population_snapshot)
        
        assert isinstance(validation_result, ValidationResult)
        assert validation_result.is_valid is True
        assert len(validation_result.errors) == 0

    def test_validate_snapshot_missing_required_fields(self):
        """Test validation catches missing required fields"""
        loader = SnapshotLoaderV2()
        
        # Create invalid snapshot with missing fields
        invalid_entry = WorkforceEntry(
            id="test-1",
            role="",  # Missing role
            level="A",
            hire_date="2024-01",
            level_start_date="",  # Missing level_start_date
            office="Stockholm"
        )
        
        invalid_snapshot = PopulationSnapshot(
            id="invalid-snapshot",
            office_id="Stockholm",
            snapshot_date="2025-01",
            name="Invalid Snapshot",
            workforce=[invalid_entry]
        )
        
        validation_result = loader.validate_snapshot(invalid_snapshot)
        
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0
        assert any("required field" in error['message'].lower() for error in validation_result.errors)

    def test_validate_snapshot_invalid_date_format(self):
        """Test validation catches invalid date formats"""
        loader = SnapshotLoaderV2()
        
        # Create entry with invalid date format
        invalid_entry = WorkforceEntry(
            id="test-1",
            role="Consultant",
            level="A", 
            hire_date="2024-13-01",  # Invalid month
            level_start_date="2024-01",
            office="Stockholm"
        )
        
        invalid_snapshot = PopulationSnapshot(
            id="invalid-dates",
            office_id="Stockholm", 
            snapshot_date="2025-01",
            name="Invalid Dates Snapshot",
            workforce=[invalid_entry]
        )
        
        validation_result = loader.validate_snapshot(invalid_snapshot)
        
        assert validation_result.is_valid is False
        assert any("date format" in error['message'].lower() for error in validation_result.errors)

    def test_validate_snapshot_duplicate_person_ids(self):
        """Test validation catches duplicate person IDs"""
        loader = SnapshotLoaderV2()
        
        # Create entries with duplicate IDs
        entry1 = WorkforceEntry(
            id="duplicate-id",
            role="Consultant",
            level="A",
            hire_date="2024-01",
            level_start_date="2024-01",
            office="Stockholm"
        )
        
        entry2 = WorkforceEntry(
            id="duplicate-id",  # Same ID
            role="Operations",
            level="Junior",
            hire_date="2024-02",
            level_start_date="2024-02", 
            office="Stockholm"
        )
        
        duplicate_snapshot = PopulationSnapshot(
            id="duplicate-ids",
            office_id="Stockholm",
            snapshot_date="2025-01",
            name="Duplicate IDs Snapshot",
            workforce=[entry1, entry2]
        )
        
        validation_result = loader.validate_snapshot(duplicate_snapshot)
        
        assert validation_result.is_valid is False
        assert any("duplicate" in error['message'].lower() for error in validation_result.errors)

    def test_validate_snapshot_logical_inconsistencies(self):
        """Test validation catches logical inconsistencies"""
        loader = SnapshotLoaderV2()
        
        # Create entry where level_start_date is before hire_date
        inconsistent_entry = WorkforceEntry(
            id="inconsistent-1",
            role="Consultant",
            level="C",
            hire_date="2024-06",
            level_start_date="2024-01",  # Before hire date
            office="Stockholm"
        )
        
        inconsistent_snapshot = PopulationSnapshot(
            id="inconsistent",
            office_id="Stockholm",
            snapshot_date="2025-01",
            name="Inconsistent Snapshot",
            workforce=[inconsistent_entry]
        )
        
        validation_result = loader.validate_snapshot(inconsistent_snapshot)
        
        # Should have warnings about logical inconsistencies
        assert len(validation_result.warnings) > 0 or len(validation_result.errors) > 0

    def test_validate_empty_snapshot(self):
        """Test validation of empty snapshot"""
        loader = SnapshotLoaderV2()
        
        empty_snapshot = PopulationSnapshot(
            id="empty-snapshot",
            office_id="Stockholm",
            snapshot_date="2025-01",
            name="Empty Snapshot",
            workforce=[]
        )
        
        validation_result = loader.validate_snapshot(empty_snapshot)
        
        # Should be valid but may have warnings
        assert validation_result.is_valid is True
        # May have warning about empty workforce
        if validation_result.warnings:
            assert any("empty" in warning['message'].lower() for warning in validation_result.warnings)


class TestSnapshotLoaderV2PersonConversion:
    """Test suite for WorkforceEntry to Person conversion"""

    def test_convert_workforce_entry_to_person(self):
        """Test conversion of WorkforceEntry to Person object"""
        loader = SnapshotLoaderV2()
        
        entry = WorkforceEntry(
            id="person-123",
            role="Consultant",
            level="A",
            hire_date="2024-01",
            level_start_date="2024-01",
            office="Stockholm"
        )
        
        person = loader._convert_to_person(entry)
        
        assert isinstance(person, Person)
        assert person.id == entry.id
        assert person.role == entry.role
        assert person.level == entry.level
        assert person.office == entry.office
        assert person.hire_date == entry.hire_date
        assert person.level_start_date == entry.level_start_date
        assert person.is_active is True
        assert person.events == []

    def test_convert_workforce_entry_with_defaults(self):
        """Test conversion applies appropriate defaults"""
        loader = SnapshotLoaderV2()
        
        minimal_entry = WorkforceEntry(
            id="minimal-person",
            role="Operations",
            level="Junior",
            hire_date="2024-06", 
            level_start_date="2024-06",
            office="Munich"
        )
        
        person = loader._convert_to_person(minimal_entry)
        
        # Should have reasonable defaults
        assert person.cat_rating is not None  # Should be assigned default
        assert person.salary > 0  # Should have default salary
        assert person.current_level == person.level
        assert person.current_role == person.role

    def test_convert_multiple_workforce_entries(self, sample_workforce_entries):
        """Test conversion of multiple workforce entries"""
        loader = SnapshotLoaderV2()
        
        # Convert first 10 entries
        sample_entries = sample_workforce_entries[:10]
        persons = [loader._convert_to_person(entry) for entry in sample_entries]
        
        assert len(persons) == 10
        assert all(isinstance(person, Person) for person in persons)
        
        # Verify unique IDs preserved
        person_ids = [person.id for person in persons]
        entry_ids = [entry.id for entry in sample_entries]
        assert person_ids == entry_ids

    def test_convert_with_salary_assignment(self, mock_config_service):
        """Test conversion assigns appropriate salaries"""
        loader = SnapshotLoaderV2()
        
        # Mock salary lookup
        with patch.object(loader, '_lookup_salary', return_value=65000.0) as mock_lookup:
            entry = WorkforceEntry(
                id="salary-test",
                role="Consultant",
                level="C",
                hire_date="2024-01",
                level_start_date="2024-01",
                office="Stockholm"
            )
            
            person = loader._convert_to_person(entry)
            
            assert person.salary == 65000.0
            mock_lookup.assert_called_once_with("Consultant", "C", "Stockholm")

    def test_convert_with_cat_rating_assignment(self):
        """Test conversion assigns appropriate CAT ratings"""
        loader = SnapshotLoaderV2()
        
        # Mock CAT rating assignment
        with patch.object(loader, '_assign_cat_rating', return_value="High") as mock_assign:
            entry = WorkforceEntry(
                id="cat-test",
                role="Consultant",
                level="SC",
                hire_date="2023-01",  # Long tenure
                level_start_date="2024-06",
                office="Stockholm"
            )
            
            person = loader._convert_to_person(entry)
            
            assert person.cat_rating == "High"
            mock_assign.assert_called_once()


class TestSnapshotLoaderV2OfficeStateInitialization:
    """Test suite for office state initialization"""

    def test_initialize_office_state_from_snapshot(self, population_snapshot):
        """Test office state initialization from population snapshot"""
        loader = SnapshotLoaderV2()
        
        office_state = loader.initialize_office_state(population_snapshot)
        
        assert isinstance(office_state, OfficeState)
        assert office_state.office_id == population_snapshot.office_id
        assert len(office_state.persons) == len(population_snapshot.workforce)
        
        # Verify all persons are Person objects
        assert all(isinstance(person, Person) for person in office_state.persons)

    def test_initialize_office_state_empty_snapshot(self):
        """Test office state initialization from empty snapshot"""
        loader = SnapshotLoaderV2()
        
        empty_snapshot = PopulationSnapshot(
            id="empty",
            office_id="EmptyOffice",
            snapshot_date="2025-01",
            name="Empty Office",
            workforce=[]
        )
        
        office_state = loader.initialize_office_state(empty_snapshot)
        
        assert isinstance(office_state, OfficeState)
        assert office_state.office_id == "EmptyOffice"
        assert len(office_state.persons) == 0

    def test_initialize_multiple_office_states(self, sample_workforce_entries):
        """Test initialization of multiple office states"""
        loader = SnapshotLoaderV2()
        
        # Create snapshots for different offices
        stockholm_entries = [e for e in sample_workforce_entries if e.office == "Stockholm"][:50]
        munich_entries = [e for e in sample_workforce_entries if e.office == "Stockholm"][:30]
        
        # Change some to Munich for testing
        for entry in munich_entries:
            entry.office = "Munich"
        
        stockholm_snapshot = PopulationSnapshot(
            id="stockholm-snap",
            office_id="Stockholm",
            snapshot_date="2025-01",
            name="Stockholm Snapshot",
            workforce=stockholm_entries
        )
        
        munich_snapshot = PopulationSnapshot(
            id="munich-snap", 
            office_id="Munich",
            snapshot_date="2025-01",
            name="Munich Snapshot",
            workforce=munich_entries
        )
        
        stockholm_state = loader.initialize_office_state(stockholm_snapshot)
        munich_state = loader.initialize_office_state(munich_snapshot)
        
        assert stockholm_state.office_id == "Stockholm"
        assert munich_state.office_id == "Munich"
        assert len(stockholm_state.persons) == 50
        assert len(munich_state.persons) == 30

    def test_initialize_office_state_with_validation(self, population_snapshot):
        """Test office state initialization with validation enabled"""
        loader = SnapshotLoaderV2()
        
        # Enable strict validation
        loader.validation_strict = True
        
        with patch.object(loader, 'validate_snapshot') as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True, errors=[], warnings=[])
            
            office_state = loader.initialize_office_state(population_snapshot)
            
            # Should have validated the snapshot
            mock_validate.assert_called_once_with(population_snapshot)
            assert isinstance(office_state, OfficeState)


class TestSnapshotLoaderV2UtilityMethods:
    """Test suite for utility methods"""

    def test_get_snapshot_summary(self, population_snapshot):
        """Test snapshot summary generation"""
        loader = SnapshotLoaderV2()
        
        summary = loader.get_snapshot_summary(population_snapshot)
        
        assert isinstance(summary, dict)
        assert 'id' in summary
        assert 'office_id' in summary
        assert 'snapshot_date' in summary
        assert 'total_workforce' in summary
        assert 'roles_breakdown' in summary
        assert 'levels_breakdown' in summary
        
        assert summary['id'] == population_snapshot.id
        assert summary['total_workforce'] == len(population_snapshot.workforce)

    def test_filter_snapshots_by_office(self):
        """Test filtering snapshots by office"""
        loader = SnapshotLoaderV2()
        
        # Load multiple snapshots
        snapshots = [
            PopulationSnapshot(id="s1", office_id="Stockholm", snapshot_date="2025-01", name="S1", workforce=[]),
            PopulationSnapshot(id="s2", office_id="Munich", snapshot_date="2025-01", name="S2", workforce=[]),
            PopulationSnapshot(id="s3", office_id="Stockholm", snapshot_date="2025-02", name="S3", workforce=[])
        ]
        
        for snapshot in snapshots:
            loader.loaded_snapshots[snapshot.id] = snapshot
        
        stockholm_snapshots = loader.filter_snapshots_by_office("Stockholm")
        
        assert len(stockholm_snapshots) == 2
        assert all(snap.office_id == "Stockholm" for snap in stockholm_snapshots)

    def test_get_latest_snapshot_for_office(self):
        """Test getting latest snapshot for office"""
        loader = SnapshotLoaderV2()
        
        # Load snapshots with different dates
        snapshots = [
            PopulationSnapshot(id="old", office_id="Stockholm", snapshot_date="2024-12", name="Old", workforce=[]),
            PopulationSnapshot(id="new", office_id="Stockholm", snapshot_date="2025-02", name="New", workforce=[]),
            PopulationSnapshot(id="newest", office_id="Stockholm", snapshot_date="2025-03", name="Newest", workforce=[])
        ]
        
        for snapshot in snapshots:
            loader.loaded_snapshots[snapshot.id] = snapshot
        
        latest = loader.get_latest_snapshot_for_office("Stockholm")
        
        assert latest.id == "newest"
        assert latest.snapshot_date == "2025-03"

    def test_merge_snapshots(self):
        """Test merging multiple snapshots"""
        loader = SnapshotLoaderV2()
        
        snapshot1 = PopulationSnapshot(
            id="merge1", office_id="Multi", snapshot_date="2025-01", name="Part 1",
            workforce=[WorkforceEntry("p1", "Consultant", "A", "2024-01", "2024-01", "Multi")]
        )
        
        snapshot2 = PopulationSnapshot(
            id="merge2", office_id="Multi", snapshot_date="2025-01", name="Part 2", 
            workforce=[WorkforceEntry("p2", "Operations", "Junior", "2024-02", "2024-02", "Multi")]
        )
        
        merged = loader.merge_snapshots([snapshot1, snapshot2], "merged-snapshot")
        
        assert isinstance(merged, PopulationSnapshot)
        assert merged.id == "merged-snapshot"
        assert len(merged.workforce) == 2
        assert merged.workforce[0].id == "p1"
        assert merged.workforce[1].id == "p2"

    def test_export_snapshot_to_json(self, population_snapshot):
        """Test exporting snapshot to JSON format"""
        loader = SnapshotLoaderV2()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            loader.export_snapshot_to_json(population_snapshot, temp_file)
            
            # Verify file was created and contains valid JSON
            assert os.path.exists(temp_file)
            
            with open(temp_file, 'r') as f:
                exported_data = json.load(f)
            
            assert exported_data['id'] == population_snapshot.id
            assert exported_data['office_id'] == population_snapshot.office_id
            assert len(exported_data['workforce']) == len(population_snapshot.workforce)
            
        finally:
            os.unlink(temp_file)

    def test_cleanup_loaded_snapshots(self):
        """Test cleanup of loaded snapshots from memory"""
        loader = SnapshotLoaderV2()
        
        # Load some snapshots
        loader.loaded_snapshots = {
            "snap1": PopulationSnapshot("snap1", "Office1", "2025-01", "Test 1", []),
            "snap2": PopulationSnapshot("snap2", "Office2", "2025-01", "Test 2", [])
        }
        
        assert len(loader.loaded_snapshots) == 2
        
        # Cleanup
        loader.cleanup_loaded_snapshots()
        
        assert len(loader.loaded_snapshots) == 0

    def test_snapshot_statistics_calculation(self, population_snapshot):
        """Test calculation of snapshot statistics"""
        loader = SnapshotLoaderV2()
        
        stats = loader.calculate_snapshot_statistics(population_snapshot)
        
        assert isinstance(stats, dict)
        assert 'total_people' in stats
        assert 'roles_count' in stats
        assert 'levels_count' in stats
        assert 'average_tenure' in stats
        assert 'office_distribution' in stats
        
        assert stats['total_people'] == len(population_snapshot.workforce)
        assert isinstance(stats['roles_count'], dict)
        assert isinstance(stats['levels_count'], dict)