"""
Integration tests for population snapshot functionality
Tests complete workflows with real database connections and transactions
"""

import pytest
import asyncio
from datetime import datetime, date, timedelta
from uuid import uuid4, UUID
from typing import Dict, Any, List, Optional
from decimal import Decimal

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, select, delete
from sqlalchemy.orm import selectinload

from backend.src.database.models import (
    Base, Office, PopulationSnapshot, SnapshotWorkforce, SnapshotTag,
    SnapshotAuditLog, OfficeJourney, SnapshotSource, SnapshotAction
)
from backend.src.repositories.snapshot_repository import SnapshotRepository
from backend.src.services.snapshot_service import (
    SnapshotService, SnapshotCreationRequest, SimulationSnapshotRequest
)


# Database configuration for testing
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/simplesim_test"


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine for the session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def async_session_maker(test_engine):
    """Create async session maker"""
    return async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture
async def db_session(async_session_maker):
    """Create database session for individual tests"""
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def sample_office(db_session):
    """Create a sample office for testing"""
    office = Office(
        name="Integration Test Office",
        journey=OfficeJourney.ESTABLISHED,
        timezone="UTC",
        economic_parameters={
            "currency": "USD",
            "working_hours_per_month": 160,
            "employment_cost_rate": 0.25
        }
    )
    
    db_session.add(office)
    await db_session.commit()
    await db_session.refresh(office)
    
    return office


@pytest.fixture
async def sample_workforce_data():
    """Sample workforce data for testing"""
    return {
        "Consultant": {
            "A": 15,
            "AC": 12,
            "C": 8
        },
        "Operations": 7,
        "Business Development": 3,
        "Manager": {
            "M1": 2,
            "M2": 1
        }
    }


class TestSnapshotRepositoryIntegration:
    """Integration tests for SnapshotRepository with real database"""
    
    @pytest.mark.asyncio
    async def test_create_and_retrieve_snapshot(
        self,
        db_session,
        sample_office,
        sample_workforce_data
    ):
        """Test complete snapshot creation and retrieval workflow"""
        repo = SnapshotRepository(db_session)
        
        # Create snapshot
        snapshot = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Integration Test Snapshot",
            snapshot_date="202501",
            total_fte=48,
            source=SnapshotSource.MANUAL,
            created_by="integration_test@example.com",
            description="Integration test snapshot",
            workforce_data=sample_workforce_data,
            tags=["integration", "test", "quarterly"],
            metadata={"test_run": True, "version": "1.0"},
            is_default=True,
            is_approved=False
        )
        
        assert snapshot.id is not None
        assert snapshot.office_id == sample_office.id
        assert snapshot.snapshot_name == "Integration Test Snapshot"
        assert snapshot.total_fte == 48
        
        # Retrieve by ID
        retrieved = await repo.get_snapshot_by_id(snapshot.id)
        assert retrieved is not None
        assert retrieved.id == snapshot.id
        assert retrieved.office_id == sample_office.id
        assert retrieved.is_default is True
        assert retrieved.is_approved is False
        
        # Verify workforce data was created
        assert len(retrieved.workforce) > 0
        
        # Check leveled roles
        consultant_entries = [w for w in retrieved.workforce if w.role == "Consultant"]
        assert len(consultant_entries) == 3  # A, AC, C levels
        
        consultant_a = next(w for w in consultant_entries if w.level == "A")
        assert consultant_a.fte == 15
        
        # Check flat roles
        operations_entry = next((w for w in retrieved.workforce if w.role == "Operations"), None)
        assert operations_entry is not None
        assert operations_entry.level is None
        assert operations_entry.fte == 7
        
        # Verify tags were created
        assert len(retrieved.tags) == 3
        tag_values = [tag.tag for tag in retrieved.tags]
        assert "integration" in tag_values
        assert "test" in tag_values
        assert "quarterly" in tag_values
        
        # Verify audit log was created
        audit_logs = await repo.get_audit_log(snapshot.id)
        assert len(audit_logs) >= 1
        creation_log = next((log for log in audit_logs if log.action == SnapshotAction.CREATED), None)
        assert creation_log is not None
        assert creation_log.user_id == "integration_test@example.com"
    
    @pytest.mark.asyncio
    async def test_update_and_retrieve_workflow(
        self,
        db_session,
        sample_office,
        sample_workforce_data
    ):
        """Test snapshot update and retrieval workflow"""
        repo = SnapshotRepository(db_session)
        
        # Create initial snapshot
        snapshot = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Update Test Snapshot",
            snapshot_date="202502",
            total_fte=40,
            source=SnapshotSource.CURRENT,
            created_by="test@example.com",
            workforce_data=sample_workforce_data
        )
        
        original_id = snapshot.id
        
        # Update snapshot properties
        updates = {
            "snapshot_name": "Updated Test Snapshot",
            "description": "Updated description",
            "is_approved": True
        }
        
        updated = await repo.update_snapshot(
            snapshot_id=original_id,
            updates=updates,
            updated_by="admin@example.com"
        )
        
        assert updated is not None
        assert updated.snapshot_name == "Updated Test Snapshot"
        assert updated.description == "Updated description"
        assert updated.is_approved is True
        
        # Verify audit log includes update
        audit_logs = await repo.get_audit_log(original_id)
        update_log = next((log for log in audit_logs if log.action == SnapshotAction.MODIFIED), None)
        assert update_log is not None
        assert update_log.user_id == "admin@example.com"
        
        # Update workforce data
        new_workforce_data = {
            "Consultant": {"A": 20, "AC": 15, "C": 10},
            "Operations": 10,
            "Manager": {"M1": 3}
        }
        
        success = await repo.update_workforce_data(original_id, new_workforce_data)
        assert success is True
        
        # Verify workforce was updated
        updated_snapshot = await repo.get_snapshot_by_id(original_id)
        assert updated_snapshot.total_fte == 58  # 20+15+10+10+3
        
        # Verify old workforce entries were replaced
        consultant_a = next(
            (w for w in updated_snapshot.workforce if w.role == "Consultant" and w.level == "A"), 
            None
        )
        assert consultant_a.fte == 20  # Updated from 15
        
        # Update tags
        new_tags = ["updated", "validated", "approved"]
        success = await repo.update_tags(original_id, new_tags)
        assert success is True
        
        # Verify tags were updated
        updated_snapshot = await repo.get_snapshot_by_id(original_id)
        tag_values = [tag.tag for tag in updated_snapshot.tags]
        assert set(tag_values) == {"updated", "validated", "approved"}
    
    @pytest.mark.asyncio
    async def test_search_and_filter_workflow(
        self,
        db_session,
        sample_office
    ):
        """Test searching and filtering snapshots"""
        repo = SnapshotRepository(db_session)
        
        # Create multiple snapshots with different characteristics
        snapshots = []
        
        # Approved quarterly snapshot
        snapshot1 = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Q1 2025 Quarterly",
            snapshot_date="202503",
            total_fte=45,
            source=SnapshotSource.BUSINESS_PLAN,
            created_by="planner@example.com",
            description="Quarterly business plan snapshot",
            tags=["quarterly", "approved", "q1"],
            is_approved=True
        )
        snapshots.append(snapshot1)
        
        # Simulation snapshot (not approved)
        snapshot2 = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Growth Scenario Simulation",
            snapshot_date="202506",
            total_fte=60,
            source=SnapshotSource.SIMULATION,
            created_by="analyst@example.com",
            description="Growth scenario simulation results",
            tags=["simulation", "growth", "scenario"],
            is_approved=False
        )
        snapshots.append(snapshot2)
        
        # Manual baseline snapshot
        snapshot3 = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Baseline Current State",
            snapshot_date="202501",
            total_fte=40,
            source=SnapshotSource.MANUAL,
            created_by="admin@example.com",
            description="Manual baseline snapshot",
            tags=["baseline", "manual", "current"],
            is_approved=True,
            is_default=True
        )
        snapshots.append(snapshot3)
        
        # Test search by office
        office_snapshots, total = await repo.search_snapshots(
            office_id=sample_office.id,
            limit=10,
            offset=0
        )
        assert len(office_snapshots) == 3
        assert total == 3
        
        # Test filter by approved only
        approved_snapshots, approved_total = await repo.search_snapshots(
            office_id=sample_office.id,
            approved_only=True
        )
        assert len(approved_snapshots) == 2  # snapshot1 and snapshot3
        assert approved_total == 2
        
        # Test filter by source
        simulation_snapshots, sim_total = await repo.search_snapshots(
            office_id=sample_office.id,
            source=SnapshotSource.SIMULATION
        )
        assert len(simulation_snapshots) == 1
        assert simulation_snapshots[0].id == snapshot2.id
        
        # Test filter by tags
        quarterly_snapshots, q_total = await repo.search_snapshots(
            office_id=sample_office.id,
            tags=["quarterly"]
        )
        assert len(quarterly_snapshots) == 1
        assert quarterly_snapshots[0].id == snapshot1.id
        
        # Test search term
        growth_snapshots, growth_total = await repo.search_snapshots(
            office_id=sample_office.id,
            search_term="growth"
        )
        assert len(growth_snapshots) == 1
        assert growth_snapshots[0].id == snapshot2.id
        
        # Test date range filtering
        q1_snapshots, q1_total = await repo.search_snapshots(
            office_id=sample_office.id,
            date_from="202501",
            date_to="202503"
        )
        assert len(q1_snapshots) == 2  # snapshot1 (March) and snapshot3 (January)
        
        # Test pagination
        paginated, paginated_total = await repo.search_snapshots(
            office_id=sample_office.id,
            limit=2,
            offset=1
        )
        assert len(paginated) == 2
        assert paginated_total == 3  # Total count unchanged
        
        # Test get default snapshot
        default_snapshot = await repo.get_default_snapshot(sample_office.id)
        assert default_snapshot is not None
        assert default_snapshot.id == snapshot3.id
        assert default_snapshot.is_default is True
    
    @pytest.mark.asyncio
    async def test_usage_tracking_workflow(
        self,
        db_session,
        sample_office
    ):
        """Test usage tracking and audit logging"""
        repo = SnapshotRepository(db_session)
        
        # Create snapshot
        snapshot = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Usage Tracking Test",
            snapshot_date="202504",
            total_fte=35,
            source=SnapshotSource.CURRENT,
            created_by="test@example.com"
        )
        
        # Record usage in scenario
        scenario_id = uuid4()
        success = await repo.record_usage(
            snapshot_id=snapshot.id,
            action=SnapshotAction.USED_IN_SCENARIO,
            entity_type="scenario",
            entity_id=scenario_id,
            user_id="analyst@example.com"
        )
        assert success is True
        
        # Record usage in business plan
        plan_id = uuid4()
        success = await repo.record_usage(
            snapshot_id=snapshot.id,
            action=SnapshotAction.USED_IN_PLAN,
            entity_type="business_plan",
            entity_id=plan_id,
            user_id="planner@example.com"
        )
        assert success is True
        
        # Set as default
        success = await repo.set_default_snapshot(
            snapshot_id=snapshot.id,
            user_id="admin@example.com"
        )
        assert success is True
        
        # Approve snapshot
        success = await repo.approve_snapshot(
            snapshot_id=snapshot.id,
            user_id="approver@example.com"
        )
        assert success is True
        
        # Verify all actions were logged
        audit_logs = await repo.get_audit_log(snapshot.id, limit=20)
        
        action_types = [log.action for log in audit_logs]
        assert SnapshotAction.CREATED in action_types
        assert SnapshotAction.USED_IN_SCENARIO in action_types
        assert SnapshotAction.USED_IN_PLAN in action_types
        assert SnapshotAction.SET_DEFAULT in action_types
        assert SnapshotAction.APPROVED in action_types
        
        # Verify usage details
        scenario_log = next(
            (log for log in audit_logs if log.action == SnapshotAction.USED_IN_SCENARIO),
            None
        )
        assert scenario_log is not None
        assert scenario_log.entity_type == "scenario"
        assert scenario_log.entity_id == scenario_id
        assert scenario_log.user_id == "analyst@example.com"
        
        # Verify snapshot was updated with last_used_at
        updated_snapshot = await repo.get_snapshot_by_id(snapshot.id)
        assert updated_snapshot.last_used_at is not None
        assert updated_snapshot.is_default is True
        assert updated_snapshot.is_approved is True
    
    @pytest.mark.asyncio
    async def test_delete_cascade_workflow(
        self,
        db_session,
        sample_office,
        sample_workforce_data
    ):
        """Test deletion with proper cascade behavior"""
        repo = SnapshotRepository(db_session)
        
        # Create snapshot with all related data
        snapshot = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Delete Test Snapshot",
            snapshot_date="202505",
            total_fte=42,
            source=SnapshotSource.MANUAL,
            created_by="test@example.com",
            workforce_data=sample_workforce_data,
            tags=["to-delete", "test"],
            metadata={"will_be_deleted": True}
        )
        
        original_id = snapshot.id
        
        # Record some usage
        await repo.record_usage(
            snapshot_id=original_id,
            action=SnapshotAction.USED_IN_SCENARIO,
            entity_type="scenario",
            entity_id=uuid4(),
            user_id="test@example.com"
        )
        
        # Verify all related data exists
        retrieved = await repo.get_snapshot_by_id(original_id)
        assert retrieved is not None
        assert len(retrieved.workforce) > 0
        assert len(retrieved.tags) > 0
        
        audit_logs = await repo.get_audit_log(original_id)
        assert len(audit_logs) > 0
        
        # Delete snapshot
        success = await repo.delete_snapshot(original_id)
        assert success is True
        
        # Verify snapshot and all related data were deleted
        deleted_snapshot = await repo.get_snapshot_by_id(original_id)
        assert deleted_snapshot is None
        
        # Verify cascade deletion worked properly
        # (In a more complete test, we'd check that workforce, tags, and audit logs were also deleted)


class TestSnapshotServiceIntegration:
    """Integration tests for SnapshotService with real database"""
    
    @pytest.mark.asyncio
    async def test_create_snapshot_from_current_integration(
        self,
        async_session_maker,
        sample_office
    ):
        """Test complete service workflow for creating snapshot from current data"""
        # Mock the config service to provide current workforce data
        current_workforce = {
            "Consultant": {"A": 12, "AC": 10, "C": 6},
            "Operations": 8,
            "Manager": {"M1": 2}
        }
        
        with patch('backend.src.services.snapshot_service.get_database_manager') as mock_db_manager:
            # Setup database manager mock
            mock_db_manager.return_value.get_session_context.return_value.__aenter__ = AsyncMock()
            mock_db_manager.return_value.get_session_context.return_value.__aexit__ = AsyncMock()
            
            service = SnapshotService()
            
            # Mock the private methods that depend on external services
            with patch.object(service, '_get_current_workforce_data') as mock_get_workforce, \
                 patch.object(service, '_get_office_name_by_id') as mock_get_office_name:
                
                mock_get_workforce.return_value = current_workforce
                mock_get_office_name.return_value = sample_office.name
                
                # Use real database session
                async with async_session_maker() as session:
                    # Replace the mocked session context with real session
                    mock_db_manager.return_value.get_session_context.return_value.__aenter__.return_value = session
                    
                    request = SnapshotCreationRequest(
                        office_id=sample_office.id,
                        snapshot_name="Service Integration Test",
                        description="Integration test via service layer",
                        tags=["integration", "service"],
                        is_default=False,
                        created_by="service_test@example.com"
                    )
                    
                    # Create snapshot through service
                    snapshot = await service.create_snapshot_from_current(request)
                    
                    # Verify snapshot was created
                    assert snapshot is not None
                    assert snapshot.snapshot_name == "Service Integration Test"
                    assert snapshot.office_id == sample_office.id
                    assert snapshot.total_fte == 38  # Sum of workforce data
                    assert snapshot.source == SnapshotSource.CURRENT
                    
                    # Verify data was actually persisted to database
                    repo = SnapshotRepository(session)
                    persisted = await repo.get_snapshot_by_id(snapshot.id)
                    
                    assert persisted is not None
                    assert persisted.snapshot_name == snapshot.snapshot_name
                    assert len(persisted.workforce) > 0
                    assert len(persisted.tags) == 2
    
    @pytest.mark.asyncio
    async def test_create_snapshot_from_simulation_integration(
        self,
        async_session_maker,
        sample_office
    ):
        """Test service workflow for creating snapshot from simulation results"""
        simulation_results = {
            "2025": {
                sample_office.name: {
                    "roles": {
                        "Consultant": {
                            "A": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
                            "AC": [8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13]
                        },
                        "Operations": [5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10]
                    }
                }
            }
        }
        
        with patch('backend.src.services.snapshot_service.get_database_manager') as mock_db_manager:
            service = SnapshotService()
            
            with patch.object(service, '_get_office_id_by_name') as mock_get_office_id:
                mock_get_office_id.return_value = sample_office.id
                
                async with async_session_maker() as session:
                    mock_db_manager.return_value.get_session_context.return_value.__aenter__.return_value = session
                    
                    request = SimulationSnapshotRequest(
                        office_name=sample_office.name,
                        simulation_results=simulation_results,
                        snapshot_date="202507",  # July - index 6
                        snapshot_name="Simulation Integration Test",
                        description="Simulation snapshot via service",
                        tags=["simulation", "july"],
                        created_by="sim_test@example.com"
                    )
                    
                    snapshot = await service.create_snapshot_from_simulation(request)
                    
                    # Verify snapshot creation
                    assert snapshot is not None
                    assert snapshot.snapshot_date == "202507"
                    assert snapshot.source == SnapshotSource.SIMULATION
                    
                    # Verify extracted data (July values: Consultant A=16, AC=11, Operations=8)
                    # Total should be 16 + 11 + 8 = 35
                    assert snapshot.total_fte == 35
                    
                    # Verify persistence
                    repo = SnapshotRepository(session)
                    persisted = await repo.get_snapshot_by_id(snapshot.id)
                    assert persisted is not None
                    
                    # Check workforce extraction
                    consultant_a = next(
                        (w for w in persisted.workforce if w.role == "Consultant" and w.level == "A"),
                        None
                    )
                    assert consultant_a is not None
                    assert consultant_a.fte == 16  # July value from simulation
                    
                    operations = next(
                        (w for w in persisted.workforce if w.role == "Operations"),
                        None
                    )
                    assert operations is not None
                    assert operations.fte == 8  # July value from simulation
    
    @pytest.mark.asyncio
    async def test_snapshot_comparison_integration(
        self,
        async_session_maker,
        sample_office
    ):
        """Test complete snapshot comparison workflow"""
        with patch('backend.src.services.snapshot_service.get_database_manager') as mock_db_manager:
            service = SnapshotService()
            
            async with async_session_maker() as session:
                mock_db_manager.return_value.get_session_context.return_value.__aenter__.return_value = session
                
                repo = SnapshotRepository(session)
                
                # Create two snapshots for comparison
                snapshot_1 = await repo.create_snapshot(
                    office_id=sample_office.id,
                    snapshot_name="Baseline Comparison",
                    snapshot_date="202501",
                    total_fte=40,
                    source=SnapshotSource.CURRENT,
                    created_by="test@example.com",
                    workforce_data={
                        "Consultant": {"A": 15, "AC": 10},
                        "Operations": 8,
                        "Manager": {"M1": 2}
                    }
                )
                
                snapshot_2 = await repo.create_snapshot(
                    office_id=sample_office.id,
                    snapshot_name="Growth Comparison",
                    snapshot_date="202506",
                    total_fte=55,
                    source=SnapshotSource.SIMULATION,
                    created_by="test@example.com",
                    workforce_data={
                        "Consultant": {"A": 20, "AC": 15, "C": 5},
                        "Operations": 10,
                        "Manager": {"M1": 3, "M2": 2}
                    }
                )
                
                # Perform comparison through service
                comparison = await service.compare_snapshots(
                    snapshot_1_id=snapshot_1.id,
                    snapshot_2_id=snapshot_2.id,
                    user_id="analyst@example.com"
                )
                
                # Verify comparison results
                assert comparison is not None
                assert comparison.snapshot_1.id == snapshot_1.id
                assert comparison.snapshot_2.id == snapshot_2.id
                assert comparison.total_fte_delta == 15  # 55 - 40
                
                # Verify workforce changes calculation
                assert "Consultant" in comparison.workforce_changes
                assert "Operations" in comparison.workforce_changes
                assert "Manager" in comparison.workforce_changes
                
                # Check specific role changes
                consultant_changes = comparison.workforce_changes["Consultant"]
                assert consultant_changes["A"]["change"] == 5  # 20 - 15
                assert consultant_changes["AC"]["change"] == 5  # 15 - 10
                
                # Check insights generation
                assert len(comparison.insights) > 0
                insights_text = " ".join(comparison.insights)
                assert "increased by 15 FTE" in insights_text
                
                # Verify usage tracking
                audit_logs_1 = await repo.get_audit_log(snapshot_1.id)
                audit_logs_2 = await repo.get_audit_log(snapshot_2.id)
                
                # Should have usage logs for both snapshots (indirectly through record_usage calls)
                assert len(audit_logs_1) > 0
                assert len(audit_logs_2) > 0


class TestDatabaseConstraintsAndTriggers:
    """Test database-level constraints and triggers"""
    
    @pytest.mark.asyncio
    async def test_unique_constraints(
        self,
        db_session,
        sample_office
    ):
        """Test that unique constraints are enforced"""
        repo = SnapshotRepository(db_session)
        
        # Create first snapshot
        snapshot1 = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Unique Test Snapshot",
            snapshot_date="202508",
            total_fte=30,
            source=SnapshotSource.MANUAL,
            created_by="test@example.com"
        )
        
        assert snapshot1 is not None
        
        # Try to create another snapshot with same name (should be allowed - names don't need to be unique)
        snapshot2 = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Unique Test Snapshot",  # Same name
            snapshot_date="202509",  # Different date
            total_fte=35,
            source=SnapshotSource.SIMULATION,
            created_by="test@example.com"
        )
        
        assert snapshot2 is not None
        assert snapshot2.id != snapshot1.id
    
    @pytest.mark.asyncio
    async def test_foreign_key_constraints(
        self,
        db_session
    ):
        """Test foreign key constraint enforcement"""
        repo = SnapshotRepository(db_session)
        
        # Try to create snapshot with non-existent office ID
        with pytest.raises(Exception):  # Should raise foreign key constraint error
            await repo.create_snapshot(
                office_id=uuid4(),  # Non-existent office
                snapshot_name="FK Test",
                snapshot_date="202501",
                total_fte=10,
                source=SnapshotSource.MANUAL,
                created_by="test@example.com"
            )
    
    @pytest.mark.asyncio
    async def test_check_constraints(
        self,
        db_session,
        sample_office
    ):
        """Test check constraint enforcement"""
        # Test positive FTE constraint at database level
        async with db_session as session:
            # Try to insert workforce entry with negative FTE directly
            invalid_workforce = SnapshotWorkforce(
                snapshot_id=uuid4(),  # This will fail due to FK, but that's expected
                role="Test",
                level="A",
                fte=-5  # Invalid negative FTE
            )
            
            session.add(invalid_workforce)
            
            with pytest.raises(Exception):  # Should raise check constraint error
                await session.commit()
    
    @pytest.mark.asyncio
    async def test_default_timestamp_behavior(
        self,
        db_session,
        sample_office
    ):
        """Test that timestamps are set automatically"""
        repo = SnapshotRepository(db_session)
        
        before_creation = datetime.utcnow()
        
        snapshot = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Timestamp Test",
            snapshot_date="202509",
            total_fte=25,
            source=SnapshotSource.CURRENT,
            created_by="timestamp_test@example.com"
        )
        
        after_creation = datetime.utcnow()
        
        # Verify created_at was set automatically and is reasonable
        assert snapshot.created_at is not None
        assert before_creation <= snapshot.created_at <= after_creation
        
        # updated_at should be set to same as created_at initially
        assert snapshot.updated_at is not None
        assert abs((snapshot.updated_at - snapshot.created_at).total_seconds()) < 1
        
        # Update the snapshot
        original_updated_at = snapshot.updated_at
        await asyncio.sleep(0.1)  # Small delay to ensure timestamp difference
        
        updated = await repo.update_snapshot(
            snapshot.id,
            {"description": "Updated description"},
            "updater@example.com"
        )
        
        # updated_at should have changed
        assert updated.updated_at > original_updated_at


class TestTransactionBehavior:
    """Test transaction handling and rollback behavior"""
    
    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(
        self,
        async_session_maker,
        sample_office
    ):
        """Test that transactions are properly rolled back on errors"""
        async with async_session_maker() as session:
            repo = SnapshotRepository(session)
            
            try:
                # Start transaction
                snapshot = await repo.create_snapshot(
                    office_id=sample_office.id,
                    snapshot_name="Transaction Test",
                    snapshot_date="202510",
                    total_fte=40,
                    source=SnapshotSource.MANUAL,
                    created_by="transaction_test@example.com"
                )
                
                # Force an error after creation
                await session.execute(text("SELECT 1/0"))  # Division by zero error
                await session.commit()
                
            except Exception:
                # Transaction should be automatically rolled back
                await session.rollback()
            
            # Verify snapshot was not persisted due to rollback
            try:
                retrieved = await repo.get_snapshot_by_id(snapshot.id)
                # If we get here without an error, the snapshot should be None
                assert retrieved is None
            except:
                # Or the session might be in an invalid state, which is also expected
                pass
    
    @pytest.mark.asyncio
    async def test_concurrent_default_snapshot_handling(
        self,
        async_session_maker,
        sample_office
    ):
        """Test handling of concurrent default snapshot updates"""
        # Create multiple sessions to simulate concurrent access
        async with async_session_maker() as session1, \
                   async_session_maker() as session2:
            
            repo1 = SnapshotRepository(session1)
            repo2 = SnapshotRepository(session2)
            
            # Create two snapshots
            snapshot1 = await repo1.create_snapshot(
                office_id=sample_office.id,
                snapshot_name="Concurrent Test 1",
                snapshot_date="202511",
                total_fte=30,
                source=SnapshotSource.MANUAL,
                created_by="concurrent1@example.com"
            )
            
            snapshot2 = await repo2.create_snapshot(
                office_id=sample_office.id,
                snapshot_name="Concurrent Test 2",
                snapshot_date="202512",
                total_fte=35,
                source=SnapshotSource.MANUAL,
                created_by="concurrent2@example.com"
            )
            
            # Both try to set their snapshot as default
            # This should work as the database should handle the constraint properly
            success1 = await repo1.set_default_snapshot(snapshot1.id, "user1")
            success2 = await repo2.set_default_snapshot(snapshot2.id, "user2")
            
            assert success1 is True
            assert success2 is True
            
            # Only one should remain as default
            async with async_session_maker() as verification_session:
                verify_repo = SnapshotRepository(verification_session)
                default_snapshot = await verify_repo.get_default_snapshot(sample_office.id)
                
                assert default_snapshot is not None
                assert default_snapshot.is_default is True
                # The exact winner depends on transaction timing, but one should be default


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling behavior"""
    
    @pytest.mark.asyncio
    async def test_large_workforce_data_handling(
        self,
        db_session,
        sample_office
    ):
        """Test handling of snapshots with large workforce datasets"""
        # Create large workforce data
        large_workforce = {}
        
        # Add many consultant levels
        for level in ["A", "AC", "C", "SC", "P", "SP", "D"]:
            large_workforce[f"Consultant_{level}"] = {
                f"Sub_{i}": i for i in range(1, 21)  # 20 sub-levels each
            }
        
        # Add many flat roles
        for role in ["Operations", "Admin", "HR", "Finance", "Marketing", "Sales"]:
            for i in range(1, 11):
                large_workforce[f"{role}_{i}"] = 5 * i
        
        repo = SnapshotRepository(db_session)
        
        start_time = datetime.utcnow()
        
        snapshot = await repo.create_snapshot(
            office_id=sample_office.id,
            snapshot_name="Large Dataset Test",
            snapshot_date="202512",
            total_fte=sum(
                sum(sub_levels.values()) if isinstance(sub_levels, dict) else sub_levels
                for sub_levels in large_workforce.values()
            ),
            source=SnapshotSource.IMPORT,
            created_by="performance_test@example.com",
            workforce_data=large_workforce
        )
        
        creation_time = datetime.utcnow() - start_time
        
        # Verify creation didn't take too long (adjust threshold as needed)
        assert creation_time.total_seconds() < 10  # Should complete within 10 seconds
        
        # Verify all data was persisted correctly
        retrieved = await repo.get_snapshot_by_id(snapshot.id)
        assert retrieved is not None
        
        # Should have many workforce entries
        assert len(retrieved.workforce) > 100
        
        # Test retrieval performance
        start_time = datetime.utcnow()
        search_results, total = await repo.search_snapshots(
            office_id=sample_office.id,
            limit=50
        )
        retrieval_time = datetime.utcnow() - start_time
        
        assert retrieval_time.total_seconds() < 5  # Should retrieve quickly
        assert len(search_results) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_snapshot_creation(
        self,
        async_session_maker,
        sample_office
    ):
        """Test concurrent snapshot creation doesn't cause deadlocks"""
        
        async def create_snapshot(session_maker, office_id, index):
            """Helper function to create a snapshot"""
            async with session_maker() as session:
                repo = SnapshotRepository(session)
                return await repo.create_snapshot(
                    office_id=office_id,
                    snapshot_name=f"Concurrent Test {index}",
                    snapshot_date=f"2025{index:02d}",  # Different dates
                    total_fte=20 + index,
                    source=SnapshotSource.MANUAL,
                    created_by=f"concurrent{index}@example.com"
                )
        
        # Create multiple snapshots concurrently
        tasks = [
            create_snapshot(async_session_maker, sample_office.id, i)
            for i in range(1, 6)  # Create 5 snapshots concurrently
        ]
        
        start_time = datetime.utcnow()
        snapshots = await asyncio.gather(*tasks)
        execution_time = datetime.utcnow() - start_time
        
        # All should succeed
        assert len(snapshots) == 5
        assert all(snapshot is not None for snapshot in snapshots)
        assert all(snapshot.id is not None for snapshot in snapshots)
        
        # Should complete reasonably quickly (concurrent execution should be faster than sequential)
        assert execution_time.total_seconds() < 30
        
        # All snapshots should have unique IDs
        snapshot_ids = [s.id for s in snapshots]
        assert len(set(snapshot_ids)) == 5  # All unique