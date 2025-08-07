"""
Unit tests for population snapshot SQLAlchemy models
Tests model validation, relationships, constraints, and business logic
"""

import pytest
from datetime import datetime, date
from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from backend.src.database.models import (
    Base, Office, OfficeWorkforce, PopulationSnapshot, 
    SnapshotWorkforce, SnapshotTag, SnapshotAuditLog,
    OfficeJourney, SnapshotSource, SnapshotAction
)
from backend.src.models.population_snapshot import (
    SnapshotType, EmployeeStatus, EmployeeRecord, 
    RoleLevelPopulation, PopulationSummary,
    OfficeSettings, SnapshotValidationResult
)


class TestPopulationSnapshotModels:
    """Test Pydantic models for population snapshots"""
    
    def test_employee_record_validation(self):
        """Test EmployeeRecord validation and constraints"""
        # Valid employee record
        valid_record = EmployeeRecord(
            employee_id="EMP001",
            role="Consultant",
            level="A",
            status=EmployeeStatus.ACTIVE,
            fte_percentage=Decimal("1.0"),
            start_date=date.today(),
            current_salary=Decimal("5000.00")
        )
        
        assert valid_record.employee_id == "EMP001"
        assert valid_record.role == "Consultant"
        assert valid_record.level == "A"
        assert valid_record.status == EmployeeStatus.ACTIVE
        assert valid_record.fte_percentage == Decimal("1.0")
        
    def test_employee_record_fte_validation(self):
        """Test FTE percentage validation"""
        # Valid FTE percentages
        for fte in [0.0, 0.5, 1.0, 1.5, 2.0]:
            record = EmployeeRecord(
                employee_id="EMP001",
                role="Consultant",
                level="A",
                status=EmployeeStatus.ACTIVE,
                fte_percentage=Decimal(str(fte)),
                start_date=date.today()
            )
            assert record.fte_percentage == Decimal(str(fte))
        
        # Invalid FTE percentages
        with pytest.raises(ValueError, match="FTE percentage must be between 0 and 2.0"):
            EmployeeRecord(
                employee_id="EMP001",
                role="Consultant",
                level="A",
                status=EmployeeStatus.ACTIVE,
                fte_percentage=Decimal("2.5"),
                start_date=date.today()
            )
        
        with pytest.raises(ValueError, match="FTE percentage must be between 0 and 2.0"):
            EmployeeRecord(
                employee_id="EMP001",
                role="Consultant",
                level="A",
                status=EmployeeStatus.ACTIVE,
                fte_percentage=Decimal("-0.1"),
                start_date=date.today()
            )
    
    def test_role_level_population_calculations(self):
        """Test RoleLevelPopulation calculations"""
        population = RoleLevelPopulation(
            role="Consultant",
            level="A",
            total_count=10,
            active_count=9,
            total_fte=Decimal("9.5"),
            active_fte=Decimal("9.0"),
            average_salary=Decimal("5000.00"),
            average_utilization=Decimal("0.85"),
            contractors_count=1,
            interns_count=0,
            on_leave_count=1,
            total_monthly_cost=Decimal("50000.00")
        )
        
        assert population.role == "Consultant"
        assert population.level == "A"
        assert population.total_count == 10
        assert population.active_count == 9
        assert population.total_fte == Decimal("9.5")
        assert population.cost_per_fte is None  # Not provided, should calculate separately
        
    def test_population_summary_aggregation(self):
        """Test PopulationSummary data aggregation"""
        summary = PopulationSummary(
            total_headcount=25,
            total_fte=Decimal("23.5"),
            active_headcount=23,
            active_fte=Decimal("22.0"),
            permanent_count=22,
            contractor_count=2,
            intern_count=1,
            on_leave_count=1,
            notice_period_count=1,
            total_monthly_salary_cost=Decimal("125000.00"),
            average_salary=Decimal("5434.78")
        )
        
        assert summary.total_headcount == 25
        assert summary.total_fte == Decimal("23.5")
        assert summary.permanent_count + summary.contractor_count + summary.intern_count == 25
        assert summary.active_headcount == 23
        
    def test_office_settings_structure(self):
        """Test OfficeSettings model structure"""
        settings = OfficeSettings(
            office_id="office-001",
            office_name="London Office",
            office_journey=OfficeJourney.ESTABLISHED,
            country="UK",
            city="London",
            timezone="Europe/London",
            currency="GBP",
            working_hours_per_month=Decimal("160.0"),
            employment_cost_rate=Decimal("0.25"),
            billing_rates={
                "Consultant": {
                    "A": Decimal("150.00"),
                    "AC": Decimal("200.00"),
                    "C": Decimal("250.00")
                }
            },
            salary_bands={
                "Consultant": {
                    "A": Decimal("4500.00"),
                    "AC": Decimal("6000.00"),
                    "C": Decimal("8000.00")
                }
            }
        )
        
        assert settings.office_id == "office-001"
        assert settings.office_journey == OfficeJourney.ESTABLISHED
        assert settings.currency == "GBP"
        assert "Consultant" in settings.billing_rates
        assert settings.billing_rates["Consultant"]["A"] == Decimal("150.00")


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_office(db_session):
    """Create a sample office for testing"""
    office = Office(
        id=uuid4(),
        name="Test Office",
        journey=OfficeJourney.ESTABLISHED,
        timezone="UTC",
        economic_parameters={"currency": "USD"}
    )
    db_session.add(office)
    db_session.commit()
    return office


@pytest.fixture
def sample_population_snapshot(db_session, sample_office):
    """Create a sample population snapshot for testing"""
    snapshot = PopulationSnapshot(
        id=uuid4(),
        office_id=sample_office.id,
        snapshot_name="Test Snapshot",
        snapshot_date="202501",
        total_fte=50,
        source=SnapshotSource.MANUAL,
        created_by="test_user",
        description="Test snapshot for unit testing",
        metadata={"test": True},
        is_default=False,
        is_approved=True
    )
    db_session.add(snapshot)
    db_session.commit()
    return snapshot


class TestSQLAlchemyModels:
    """Test SQLAlchemy ORM models"""
    
    def test_office_model_creation(self, db_session):
        """Test Office model creation and validation"""
        office = Office(
            name="London Office",
            journey=OfficeJourney.MATURE,
            timezone="Europe/London",
            economic_parameters={
                "currency": "GBP",
                "tax_rate": 0.2,
                "social_security_rate": 0.12
            }
        )
        
        db_session.add(office)
        db_session.commit()
        
        # Test that the office was created with correct attributes
        assert office.id is not None
        assert office.name == "London Office"
        assert office.journey == OfficeJourney.MATURE
        assert office.timezone == "Europe/London"
        assert office.economic_parameters["currency"] == "GBP"
        assert office.created_at is not None
        assert office.updated_at is not None
    
    def test_office_name_uniqueness(self, db_session):
        """Test that office names must be unique"""
        office1 = Office(name="Duplicate Office", journey=OfficeJourney.EMERGING)
        office2 = Office(name="Duplicate Office", journey=OfficeJourney.ESTABLISHED)
        
        db_session.add(office1)
        db_session.commit()
        
        db_session.add(office2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_population_snapshot_creation(self, sample_office, db_session):
        """Test PopulationSnapshot model creation"""
        snapshot = PopulationSnapshot(
            office_id=sample_office.id,
            snapshot_name="Q1 2025 Snapshot",
            snapshot_date="202503",
            total_fte=45,
            source=SnapshotSource.SIMULATION,
            created_by="analyst@company.com",
            description="Quarterly workforce snapshot",
            metadata={
                "quarter": "Q1",
                "year": 2025,
                "simulation_id": "sim_001"
            },
            is_default=True,
            is_approved=False
        )
        
        db_session.add(snapshot)
        db_session.commit()
        
        assert snapshot.id is not None
        assert snapshot.office_id == sample_office.id
        assert snapshot.snapshot_name == "Q1 2025 Snapshot"
        assert snapshot.snapshot_date == "202503"
        assert snapshot.total_fte == 45
        assert snapshot.source == SnapshotSource.SIMULATION
        assert snapshot.is_default is True
        assert snapshot.is_approved is False
        assert snapshot.created_at is not None
        
    def test_snapshot_workforce_creation(self, sample_population_snapshot, db_session):
        """Test SnapshotWorkforce model creation"""
        workforce_entries = [
            SnapshotWorkforce(
                snapshot_id=sample_population_snapshot.id,
                role="Consultant",
                level="A",
                fte=15
            ),
            SnapshotWorkforce(
                snapshot_id=sample_population_snapshot.id,
                role="Consultant",
                level="AC",
                fte=10
            ),
            SnapshotWorkforce(
                snapshot_id=sample_population_snapshot.id,
                role="Operations",
                level=None,  # Flat role
                fte=5
            )
        ]
        
        db_session.add_all(workforce_entries)
        db_session.commit()
        
        # Verify entries were created correctly
        consultant_a = workforce_entries[0]
        assert consultant_a.role == "Consultant"
        assert consultant_a.level == "A"
        assert consultant_a.fte == 15
        
        operations = workforce_entries[2]
        assert operations.role == "Operations"
        assert operations.level is None
        assert operations.fte == 5
        
        # Test constraint: FTE must be non-negative
        invalid_workforce = SnapshotWorkforce(
            snapshot_id=sample_population_snapshot.id,
            role="Manager",
            level="M",
            fte=-5  # Invalid negative FTE
        )
        db_session.add(invalid_workforce)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_snapshot_tags(self, sample_population_snapshot, db_session):
        """Test SnapshotTag model and relationships"""
        tags = [
            SnapshotTag(snapshot_id=sample_population_snapshot.id, tag="quarterly"),
            SnapshotTag(snapshot_id=sample_population_snapshot.id, tag="approved"),
            SnapshotTag(snapshot_id=sample_population_snapshot.id, tag="baseline")
        ]
        
        db_session.add_all(tags)
        db_session.commit()
        
        # Test that tags were created
        assert len(tags) == 3
        assert all(tag.snapshot_id == sample_population_snapshot.id for tag in tags)
        
        # Test tag values
        tag_values = [tag.tag for tag in tags]
        assert "quarterly" in tag_values
        assert "approved" in tag_values
        assert "baseline" in tag_values
    
    def test_snapshot_audit_log(self, sample_population_snapshot, db_session):
        """Test SnapshotAuditLog model"""
        audit_entries = [
            SnapshotAuditLog(
                snapshot_id=sample_population_snapshot.id,
                action=SnapshotAction.CREATED,
                user_id="admin@company.com",
                details={"initial_fte": 50, "source": "manual"}
            ),
            SnapshotAuditLog(
                snapshot_id=sample_population_snapshot.id,
                action=SnapshotAction.APPROVED,
                user_id="manager@company.com",
                details={"approval_reason": "data_validated"}
            ),
            SnapshotAuditLog(
                snapshot_id=sample_population_snapshot.id,
                action=SnapshotAction.USED_IN_SCENARIO,
                user_id="analyst@company.com",
                entity_type="scenario",
                entity_id=uuid4(),
                details={"scenario_name": "Growth Plan 2025"}
            )
        ]
        
        db_session.add_all(audit_entries)
        db_session.commit()
        
        # Verify audit log entries
        assert len(audit_entries) == 3
        
        created_entry = audit_entries[0]
        assert created_entry.action == SnapshotAction.CREATED
        assert created_entry.user_id == "admin@company.com"
        assert created_entry.details["initial_fte"] == 50
        
        usage_entry = audit_entries[2]
        assert usage_entry.action == SnapshotAction.USED_IN_SCENARIO
        assert usage_entry.entity_type == "scenario"
        assert usage_entry.entity_id is not None
    
    def test_office_workforce_constraints(self, sample_office, db_session):
        """Test OfficeWorkforce model constraints"""
        # Test unique constraint
        workforce1 = OfficeWorkforce(
            office_id=sample_office.id,
            start_date=datetime(2025, 1, 1),
            role="Consultant",
            level="A",
            fte=10
        )
        
        workforce2 = OfficeWorkforce(
            office_id=sample_office.id,
            start_date=datetime(2025, 1, 1),  # Same date
            role="Consultant",  # Same role
            level="A",  # Same level
            fte=5  # Different FTE, but should still violate unique constraint
        )
        
        db_session.add(workforce1)
        db_session.commit()
        
        db_session.add(workforce2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_model_relationships(self, sample_office, sample_population_snapshot, db_session):
        """Test relationships between models"""
        # Create related data
        workforce = SnapshotWorkforce(
            snapshot_id=sample_population_snapshot.id,
            role="Consultant",
            level="A",
            fte=10
        )
        
        tag = SnapshotTag(
            snapshot_id=sample_population_snapshot.id,
            tag="test"
        )
        
        audit = SnapshotAuditLog(
            snapshot_id=sample_population_snapshot.id,
            action=SnapshotAction.MODIFIED,
            user_id="test@company.com"
        )
        
        db_session.add_all([workforce, tag, audit])
        db_session.commit()
        
        # Test office -> snapshots relationship
        db_session.refresh(sample_office)
        assert len(sample_office.snapshots) == 1
        assert sample_office.snapshots[0].id == sample_population_snapshot.id
        
        # Test snapshot -> workforce relationship
        db_session.refresh(sample_population_snapshot)
        assert len(sample_population_snapshot.workforce) == 1
        assert sample_population_snapshot.workforce[0].role == "Consultant"
        
        # Test snapshot -> tags relationship
        assert len(sample_population_snapshot.tags) == 1
        assert sample_population_snapshot.tags[0].tag == "test"
        
        # Test snapshot -> audit_logs relationship
        assert len(sample_population_snapshot.audit_logs) == 1
        assert sample_population_snapshot.audit_logs[0].action == SnapshotAction.MODIFIED
    
    def test_cascade_deletion(self, sample_office, sample_population_snapshot, db_session):
        """Test that related objects are deleted when parent is deleted"""
        # Create related objects
        workforce = SnapshotWorkforce(
            snapshot_id=sample_population_snapshot.id,
            role="Consultant",
            level="A",
            fte=10
        )
        
        tag = SnapshotTag(
            snapshot_id=sample_population_snapshot.id,
            tag="will_be_deleted"
        )
        
        db_session.add_all([workforce, tag])
        db_session.commit()
        
        # Get IDs before deletion
        snapshot_id = sample_population_snapshot.id
        workforce_id = workforce.id
        tag_id = tag.id
        
        # Delete the snapshot
        db_session.delete(sample_population_snapshot)
        db_session.commit()
        
        # Verify that related objects were deleted
        assert db_session.get(PopulationSnapshot, snapshot_id) is None
        assert db_session.get(SnapshotWorkforce, workforce_id) is None
        assert db_session.get(SnapshotTag, tag_id) is None
    
    def test_model_repr_methods(self, sample_office, sample_population_snapshot):
        """Test __repr__ methods for debugging"""
        office_repr = repr(sample_office)
        assert "Test Office" in office_repr
        assert "ESTABLISHED" in office_repr
        
        snapshot_repr = repr(sample_population_snapshot)
        assert "Test Snapshot" in snapshot_repr
        assert str(sample_population_snapshot.id) in snapshot_repr
    
    def test_snapshot_date_validation(self, sample_office, db_session):
        """Test snapshot date format validation"""
        # Valid date formats
        valid_dates = ["202501", "202412", "202506"]
        
        for date_str in valid_dates:
            snapshot = PopulationSnapshot(
                office_id=sample_office.id,
                snapshot_name=f"Test {date_str}",
                snapshot_date=date_str,
                total_fte=10,
                source=SnapshotSource.MANUAL,
                created_by="test"
            )
            db_session.add(snapshot)
        
        db_session.commit()  # Should not raise any exceptions
        
        # Test querying by date
        snapshots = db_session.query(PopulationSnapshot).filter(
            PopulationSnapshot.snapshot_date.like("2025%")
        ).all()
        assert len(snapshots) == 1  # Only 202501 matches
    
    def test_metadata_json_field(self, sample_office, db_session):
        """Test JSON metadata field functionality"""
        complex_metadata = {
            "simulation_parameters": {
                "growth_rate": 0.15,
                "churn_rate": 0.08,
                "recruitment_target": 100
            },
            "data_sources": ["HRIS", "Finance", "Manual Input"],
            "validation_results": {
                "data_quality_score": 0.95,
                "completeness": 0.98,
                "accuracy": 0.92
            },
            "tags": ["quarterly", "validated", "approved"],
            "created_by_details": {
                "user_id": "analyst_001",
                "department": "HR Analytics",
                "timestamp": "2025-01-15T10:30:00Z"
            }
        }
        
        snapshot = PopulationSnapshot(
            office_id=sample_office.id,
            snapshot_name="Complex Metadata Test",
            snapshot_date="202501",
            total_fte=75,
            source=SnapshotSource.SIMULATION,
            created_by="analyst_001",
            metadata=complex_metadata
        )
        
        db_session.add(snapshot)
        db_session.commit()
        
        # Retrieve and verify metadata
        db_session.refresh(snapshot)
        assert snapshot.metadata["simulation_parameters"]["growth_rate"] == 0.15
        assert "HRIS" in snapshot.metadata["data_sources"]
        assert snapshot.metadata["validation_results"]["data_quality_score"] == 0.95
        assert len(snapshot.metadata["tags"]) == 3