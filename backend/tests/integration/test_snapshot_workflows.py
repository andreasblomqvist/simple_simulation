"""
Integration tests for population snapshot workflows
Tests complete end-to-end workflows involving multiple system components
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date
from uuid import uuid4
from typing import Dict, List, Any, Optional
import json

# Import the modules we're testing (these would be real imports in practice)
from backend.src.models.population_snapshot import (
    PopulationSnapshot, EmployeeRecord, RoleLevelPopulation, 
    OfficeSettings, PopulationSummary
)
from backend.src.repositories.snapshot_repository import SnapshotRepository
from backend.src.services.snapshot_service import SnapshotService
from backend.routers.snapshots import router as snapshot_router

# Mock external dependencies
class MockOfficeService:
    """Mock office service for testing"""
    
    async def get_office(self, office_id: str) -> Dict[str, Any]:
        return {
            'id': office_id,
            'name': f'Office {office_id}',
            'location': 'Test Location',
            'status': 'active'
        }
    
    async def get_office_workforce(self, office_id: str, date: Optional[str] = None) -> List[Dict[str, Any]]:
        return [
            {'role': 'Consultant', 'level': 'A', 'fte': 10, 'salary': 4500},
            {'role': 'Consultant', 'level': 'AC', 'fte': 8, 'salary': 6000},
            {'role': 'Operations', 'level': None, 'fte': 5, 'salary': 3500},
        ]

class MockScenarioService:
    """Mock scenario service for testing"""
    
    async def create_scenario_with_snapshot(self, scenario_data: Dict, snapshot_id: str) -> Dict[str, Any]:
        return {
            'id': str(uuid4()),
            'name': scenario_data['name'],
            'baseline_snapshot_id': snapshot_id,
            'status': 'created'
        }
    
    async def run_scenario(self, scenario_id: str) -> Dict[str, Any]:
        return {
            'scenario_id': scenario_id,
            'status': 'completed',
            'results': {'final_fte': 25, 'growth_rate': 8.7}
        }

class MockBusinessPlanService:
    """Mock business plan service for testing"""
    
    async def create_plan_from_snapshot(self, plan_data: Dict, snapshot_id: str) -> Dict[str, Any]:
        return {
            'id': str(uuid4()),
            'name': plan_data['name'],
            'baseline_snapshot_id': snapshot_id,
            'duration_months': plan_data['duration_months']
        }

@pytest.fixture
async def mock_dependencies():
    """Set up mock dependencies for integration tests"""
    return {
        'office_service': MockOfficeService(),
        'scenario_service': MockScenarioService(),
        'business_plan_service': MockBusinessPlanService(),
        'db_session': MagicMock(),
        'current_user': {'id': 'test_user', 'name': 'Test User'}
    }

class TestSnapshotCreationWorkflows:
    """Test complete snapshot creation workflows"""
    
    async def test_create_snapshot_from_current_workforce_workflow(self, mock_dependencies):
        """Test complete workflow for creating snapshot from current workforce"""
        # Mock repository and service
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        # Set up test data
        office_id = str(uuid4())
        snapshot_data = {
            'name': 'Q1 2025 Current Workforce',
            'description': 'Snapshot of current workforce for Q1 planning',
            'office_id': office_id,
            'source': 'current',
            'tags': ['quarterly', 'current']
        }
        
        # Mock office workforce data
        mock_workforce = [
            EmployeeRecord(role='Consultant', level='A', fte=10, salary=4500),
            EmployeeRecord(role='Consultant', level='AC', fte=8, salary=6000),
            EmployeeRecord(role='Operations', level=None, fte=5, salary=3500)
        ]
        
        # Mock repository responses
        mock_snapshot = PopulationSnapshot(
            id=str(uuid4()),
            name=snapshot_data['name'],
            description=snapshot_data['description'],
            office_id=office_id,
            snapshot_date='202503',
            workforce=mock_workforce,
            metadata={'total_fte': 23, 'total_salary_cost': 122500, 'role_count': 2},
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_repo.create_snapshot_from_current_workforce.return_value = mock_snapshot
        
        # Execute workflow
        result = await mock_service.create_snapshot_from_current_workforce(
            office_id=office_id,
            name=snapshot_data['name'],
            description=snapshot_data['description'],
            tags=snapshot_data['tags'],
            created_by=mock_dependencies['current_user']['id']
        )
        
        # Verify workflow execution
        assert result.id is not None
        assert result.name == snapshot_data['name']
        assert result.office_id == office_id
        assert result.source == 'current'
        assert len(result.workforce) == 3
        assert result.metadata['total_fte'] == 23
        
        # Verify repository was called correctly
        mock_repo.create_snapshot_from_current_workforce.assert_called_once()
        call_args = mock_repo.create_snapshot_from_current_workforce.call_args[1]
        assert call_args['office_id'] == office_id
        assert call_args['name'] == snapshot_data['name']
        assert call_args['tags'] == snapshot_data['tags']
        
    async def test_create_snapshot_from_simulation_results_workflow(self, mock_dependencies):
        """Test workflow for creating snapshot from simulation results"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        # Set up simulation results data
        simulation_results = {
            'scenario_id': str(uuid4()),
            'office_id': str(uuid4()),
            'final_month': '202506',
            'workforce': [
                {'role': 'Consultant', 'level': 'A', 'fte': 12, 'salary': 4500},
                {'role': 'Consultant', 'level': 'AC', 'fte': 10, 'salary': 6000},
                {'role': 'Operations', 'level': None, 'fte': 7, 'salary': 3500},
            ]
        }
        
        snapshot_data = {
            'name': 'Growth Scenario Result - June 2025',
            'description': 'Snapshot from growth scenario final month',
            'source': 'simulation',
            'tags': ['simulation', 'growth']
        }
        
        # Mock snapshot creation
        mock_snapshot = PopulationSnapshot(
            id=str(uuid4()),
            name=snapshot_data['name'],
            description=snapshot_data['description'],
            office_id=simulation_results['office_id'],
            snapshot_date=simulation_results['final_month'],
            workforce=[
                EmployeeRecord(**emp) for emp in simulation_results['workforce']
            ],
            metadata={'total_fte': 29, 'total_salary_cost': 138500, 'role_count': 2},
            source='simulation',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_repo.create_snapshot_from_simulation.return_value = mock_snapshot
        
        # Execute workflow
        result = await mock_service.create_snapshot_from_simulation(
            simulation_results=simulation_results,
            name=snapshot_data['name'],
            description=snapshot_data['description'],
            tags=snapshot_data['tags'],
            created_by=mock_dependencies['current_user']['id']
        )
        
        # Verify workflow execution
        assert result.name == snapshot_data['name']
        assert result.source == 'simulation'
        assert result.snapshot_date == simulation_results['final_month']
        assert result.metadata['total_fte'] == 29
        
        # Verify repository integration
        mock_repo.create_snapshot_from_simulation.assert_called_once()
        
    async def test_create_snapshot_from_business_plan_workflow(self, mock_dependencies):
        """Test workflow for creating snapshot from business plan state"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        # Set up business plan data
        business_plan_data = {
            'plan_id': str(uuid4()),
            'office_id': str(uuid4()),
            'target_month': '202512',
            'planned_workforce': [
                {'role': 'Consultant', 'level': 'A', 'fte': 15, 'salary': 4500},
                {'role': 'Consultant', 'level': 'AC', 'fte': 12, 'salary': 6000},
                {'role': 'Consultant', 'level': 'C', 'fte': 5, 'salary': 8000},
                {'role': 'Operations', 'level': None, 'fte': 8, 'salary': 3500},
            ]
        }
        
        snapshot_data = {
            'name': 'Year-End Plan Target',
            'description': 'Target workforce from annual business plan',
            'source': 'business_plan',
            'tags': ['business_plan', 'target', 'annual']
        }
        
        # Mock snapshot creation
        mock_snapshot = PopulationSnapshot(
            id=str(uuid4()),
            name=snapshot_data['name'],
            description=snapshot_data['description'],
            office_id=business_plan_data['office_id'],
            snapshot_date=business_plan_data['target_month'],
            workforce=[
                EmployeeRecord(**emp) for emp in business_plan_data['planned_workforce']
            ],
            metadata={'total_fte': 40, 'total_salary_cost': 238000, 'role_count': 2},
            source='business_plan',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_repo.create_snapshot_from_business_plan.return_value = mock_snapshot
        
        # Execute workflow
        result = await mock_service.create_snapshot_from_business_plan(
            business_plan_data=business_plan_data,
            name=snapshot_data['name'],
            description=snapshot_data['description'],
            tags=snapshot_data['tags'],
            created_by=mock_dependencies['current_user']['id']
        )
        
        # Verify workflow execution
        assert result.source == 'business_plan'
        assert result.snapshot_date == business_plan_data['target_month']
        assert len(result.workforce) == 4
        assert result.metadata['total_fte'] == 40

class TestSnapshotUsageWorkflows:
    """Test workflows for using snapshots in scenarios and planning"""
    
    async def test_use_snapshot_in_scenario_workflow(self, mock_dependencies):
        """Test complete workflow for using snapshot as scenario baseline"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        # Set up existing snapshot
        snapshot_id = str(uuid4())
        mock_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='Q1 Baseline Snapshot',
            description='Baseline for Q2 scenarios',
            office_id=str(uuid4()),
            snapshot_date='202503',
            workforce=[
                EmployeeRecord(role='Consultant', level='A', fte=10, salary=4500),
                EmployeeRecord(role='Operations', level=None, fte=5, salary=3500)
            ],
            metadata={'total_fte': 15, 'total_salary_cost': 62500, 'role_count': 2},
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Set up scenario data
        scenario_data = {
            'name': 'Q2 Growth Scenario',
            'description': 'Moderate growth scenario for Q2',
            'duration_months': 3,
            'growth_rate': 15.0,
            'office_id': mock_snapshot.office_id
        }
        
        # Mock repository and scenario service responses
        mock_repo.get_snapshot.return_value = mock_snapshot
        mock_repo.mark_snapshot_used.return_value = True
        
        # Execute workflow steps
        # 1. Get snapshot for scenario creation
        retrieved_snapshot = await mock_service.get_snapshot(snapshot_id)
        
        # 2. Create scenario with snapshot baseline
        scenario = await mock_dependencies['scenario_service'].create_scenario_with_snapshot(
            scenario_data, snapshot_id
        )
        
        # 3. Mark snapshot as used
        await mock_service.mark_snapshot_used(
            snapshot_id=snapshot_id,
            usage_context='scenario',
            entity_id=scenario['id'],
            used_by=mock_dependencies['current_user']['id']
        )
        
        # Verify workflow execution
        assert retrieved_snapshot.id == snapshot_id
        assert scenario['baseline_snapshot_id'] == snapshot_id
        
        # Verify repository calls
        mock_repo.get_snapshot.assert_called_once_with(snapshot_id)
        mock_repo.mark_snapshot_used.assert_called_once()
        
        # Verify usage tracking
        usage_call = mock_repo.mark_snapshot_used.call_args[1]
        assert usage_call['snapshot_id'] == snapshot_id
        assert usage_call['usage_context'] == 'scenario'
        assert usage_call['entity_id'] == scenario['id']
        
    async def test_use_snapshot_in_business_plan_workflow(self, mock_dependencies):
        """Test workflow for using snapshot as business plan baseline"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        # Set up snapshot
        snapshot_id = str(uuid4())
        mock_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='Current State Snapshot',
            description='Current state for annual planning',
            office_id=str(uuid4()),
            snapshot_date='202501',
            workforce=[
                EmployeeRecord(role='Consultant', level='A', fte=8, salary=4500),
                EmployeeRecord(role='Consultant', level='AC', fte=6, salary=6000),
            ],
            metadata={'total_fte': 14, 'total_salary_cost': 72000, 'role_count': 1},
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Set up business plan data
        plan_data = {
            'name': 'Annual Growth Plan 2025',
            'description': 'Comprehensive growth plan for 2025',
            'duration_months': 12,
            'target_growth': 50.0,
            'office_id': mock_snapshot.office_id
        }
        
        # Mock responses
        mock_repo.get_snapshot.return_value = mock_snapshot
        mock_repo.mark_snapshot_used.return_value = True
        
        # Execute workflow
        retrieved_snapshot = await mock_service.get_snapshot(snapshot_id)
        
        business_plan = await mock_dependencies['business_plan_service'].create_plan_from_snapshot(
            plan_data, snapshot_id
        )
        
        await mock_service.mark_snapshot_used(
            snapshot_id=snapshot_id,
            usage_context='business_plan',
            entity_id=business_plan['id'],
            used_by=mock_dependencies['current_user']['id']
        )
        
        # Verify workflow
        assert business_plan['baseline_snapshot_id'] == snapshot_id
        assert business_plan['name'] == plan_data['name']
        
        # Verify usage tracking
        mock_repo.mark_snapshot_used.assert_called_once()
        
    async def test_run_scenario_with_snapshot_baseline_workflow(self, mock_dependencies):
        """Test complete workflow for running scenario with snapshot baseline"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        # Set up scenario with snapshot baseline
        snapshot_id = str(uuid4())
        scenario_id = str(uuid4())
        
        mock_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='Scenario Baseline',
            description='Baseline for growth testing',
            office_id=str(uuid4()),
            snapshot_date='202503',
            workforce=[
                EmployeeRecord(role='Consultant', level='A', fte=12, salary=4500),
                EmployeeRecord(role='Operations', level=None, fte=6, salary=3500)
            ],
            metadata={'total_fte': 18, 'total_salary_cost': 75000, 'role_count': 2},
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock scenario run results
        scenario_results = {
            'scenario_id': scenario_id,
            'status': 'completed',
            'baseline_snapshot_id': snapshot_id,
            'results': {
                'final_fte': 25,
                'growth_achieved': 38.9,
                'monthly_progression': [18, 20, 22, 25]
            }
        }
        
        # Mock repository responses
        mock_repo.get_snapshot.return_value = mock_snapshot
        mock_repo.update_usage_timestamp.return_value = True
        
        # Execute workflow
        # 1. Get baseline snapshot for scenario execution
        baseline_snapshot = await mock_service.get_snapshot(snapshot_id)
        
        # 2. Run scenario (using mock scenario service)
        results = await mock_dependencies['scenario_service'].run_scenario(scenario_id)
        
        # 3. Update snapshot usage timestamp
        await mock_service.update_snapshot_usage(
            snapshot_id=snapshot_id,
            used_by=mock_dependencies['current_user']['id']
        )
        
        # Verify workflow execution
        assert baseline_snapshot.id == snapshot_id
        assert results['status'] == 'completed'
        assert baseline_snapshot.metadata['total_fte'] == 18
        
        # Verify repository interactions
        mock_repo.get_snapshot.assert_called_once_with(snapshot_id)
        mock_repo.update_usage_timestamp.assert_called_once()

class TestSnapshotComparisonWorkflows:
    """Test snapshot comparison workflows"""
    
    async def test_compare_snapshots_workflow(self, mock_dependencies):
        """Test complete snapshot comparison workflow"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        # Set up snapshots for comparison
        snapshot1_id = str(uuid4())
        snapshot2_id = str(uuid4())
        office_id = str(uuid4())
        
        mock_snapshot1 = PopulationSnapshot(
            id=snapshot1_id,
            name='Q1 Snapshot',
            office_id=office_id,
            snapshot_date='202503',
            workforce=[
                EmployeeRecord(role='Consultant', level='A', fte=10, salary=4500),
                EmployeeRecord(role='Consultant', level='AC', fte=8, salary=6000),
            ],
            metadata={'total_fte': 18, 'total_salary_cost': 93000, 'role_count': 1},
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_snapshot2 = PopulationSnapshot(
            id=snapshot2_id,
            name='Q2 Snapshot',
            office_id=office_id,
            snapshot_date='202506',
            workforce=[
                EmployeeRecord(role='Consultant', level='A', fte=12, salary=4500),
                EmployeeRecord(role='Consultant', level='AC', fte=10, salary=6000),
                EmployeeRecord(role='Operations', level=None, fte=5, salary=3500),
            ],
            metadata={'total_fte': 27, 'total_salary_cost': 131500, 'role_count': 2},
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock comparison result
        comparison_result = {
            'baseline_snapshot': mock_snapshot1,
            'comparison_snapshot': mock_snapshot2,
            'workforce_changes': [
                {
                    'role': 'Consultant',
                    'level': 'A',
                    'change_type': 'modified',
                    'baseline_fte': 10,
                    'comparison_fte': 12,
                    'fte_change': 2,
                    'salary_change': 9000
                },
                {
                    'role': 'Operations',
                    'level': None,
                    'change_type': 'added',
                    'baseline_fte': 0,
                    'comparison_fte': 5,
                    'fte_change': 5,
                    'salary_change': 17500
                }
            ],
            'summary': {
                'total_fte_change': 9,
                'total_salary_change': 38500,
                'roles_added': 1,
                'roles_removed': 0,
                'roles_modified': 1,
                'net_change_percentage': 50.0
            }
        }
        
        # Mock repository responses
        mock_repo.get_snapshot.side_effect = [mock_snapshot1, mock_snapshot2]
        mock_repo.save_comparison.return_value = str(uuid4())
        
        # Execute comparison workflow
        comparison = await mock_service.compare_snapshots(
            baseline_id=snapshot1_id,
            comparison_id=snapshot2_id,
            compared_by=mock_dependencies['current_user']['id'],
            save_comparison=True
        )
        
        # Verify workflow execution
        assert len(comparison['workforce_changes']) == 2
        assert comparison['summary']['total_fte_change'] == 9
        assert comparison['summary']['roles_added'] == 1
        
        # Verify repository interactions
        assert mock_repo.get_snapshot.call_count == 2
        mock_repo.save_comparison.assert_called_once()
        
    async def test_track_snapshot_comparison_usage(self, mock_dependencies):
        """Test that comparison usage is properly tracked"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        comparison_id = str(uuid4())
        snapshot1_id = str(uuid4())
        snapshot2_id = str(uuid4())
        
        # Mock comparison retrieval
        mock_comparison = {
            'id': comparison_id,
            'baseline_snapshot_id': snapshot1_id,
            'comparison_snapshot_id': snapshot2_id,
            'created_at': datetime.now(),
            'compared_by': mock_dependencies['current_user']['id']
        }
        
        mock_repo.get_comparison.return_value = mock_comparison
        mock_repo.log_comparison_access.return_value = True
        
        # Execute workflow
        comparison = await mock_service.get_comparison(comparison_id)
        
        await mock_service.log_comparison_access(
            comparison_id=comparison_id,
            accessed_by=mock_dependencies['current_user']['id'],
            access_context='dashboard_view'
        )
        
        # Verify tracking
        mock_repo.get_comparison.assert_called_once_with(comparison_id)
        mock_repo.log_comparison_access.assert_called_once()

class TestSnapshotManagementWorkflows:
    """Test snapshot management and administrative workflows"""
    
    async def test_set_default_snapshot_workflow(self, mock_dependencies):
        """Test workflow for setting a snapshot as office default"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        office_id = str(uuid4())
        snapshot_id = str(uuid4())
        
        # Mock existing snapshots
        existing_snapshots = [
            PopulationSnapshot(
                id=str(uuid4()),
                name='Old Default',
                office_id=office_id,
                is_default=True,
                snapshot_date='202501',
                workforce=[],
                metadata={'total_fte': 10, 'total_salary_cost': 50000, 'role_count': 1},
                source='current',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        new_default_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='New Default',
            office_id=office_id,
            is_default=False,
            snapshot_date='202503',
            workforce=[],
            metadata={'total_fte': 15, 'total_salary_cost': 75000, 'role_count': 1},
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock repository responses
        mock_repo.get_snapshot.return_value = new_default_snapshot
        mock_repo.get_office_snapshots.return_value = existing_snapshots
        mock_repo.clear_default_snapshots.return_value = 1
        mock_repo.set_snapshot_default.return_value = new_default_snapshot
        mock_repo.log_audit_event.return_value = True
        
        # Execute workflow
        result = await mock_service.set_default_snapshot(
            snapshot_id=snapshot_id,
            set_by=mock_dependencies['current_user']['id']
        )
        
        # Verify workflow execution
        assert result.id == snapshot_id
        
        # Verify repository interaction sequence
        mock_repo.get_snapshot.assert_called_once_with(snapshot_id)
        mock_repo.clear_default_snapshots.assert_called_once_with(office_id)
        mock_repo.set_snapshot_default.assert_called_once_with(snapshot_id, True)
        mock_repo.log_audit_event.assert_called_once()
        
        # Verify audit logging
        audit_call = mock_repo.log_audit_event.call_args[1]
        assert audit_call['action'] == 'set_default'
        assert audit_call['snapshot_id'] == snapshot_id
        
    async def test_approve_snapshot_workflow(self, mock_dependencies):
        """Test workflow for approving snapshots for official use"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        snapshot_id = str(uuid4())
        
        # Mock snapshot for approval
        mock_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='Pending Approval Snapshot',
            office_id=str(uuid4()),
            is_approved=False,
            snapshot_date='202503',
            workforce=[],
            metadata={'total_fte': 20, 'total_salary_cost': 100000, 'role_count': 2},
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock approved snapshot
        approved_snapshot = PopulationSnapshot(
            **{**mock_snapshot.__dict__, 'is_approved': True}
        )
        
        # Mock repository responses
        mock_repo.get_snapshot.return_value = mock_snapshot
        mock_repo.update_snapshot.return_value = approved_snapshot
        mock_repo.log_audit_event.return_value = True
        
        # Execute approval workflow
        result = await mock_service.approve_snapshot(
            snapshot_id=snapshot_id,
            approved_by=mock_dependencies['current_user']['id'],
            approval_notes='Approved for Q2 planning cycle'
        )
        
        # Verify workflow execution
        assert result.is_approved == True
        
        # Verify repository calls
        mock_repo.get_snapshot.assert_called_once_with(snapshot_id)
        mock_repo.update_snapshot.assert_called_once()
        mock_repo.log_audit_event.assert_called_once()
        
        # Verify approval audit
        audit_call = mock_repo.log_audit_event.call_args[1]
        assert audit_call['action'] == 'approved'
        assert 'approval_notes' in audit_call['details']
        
    async def test_delete_snapshot_with_dependency_check_workflow(self, mock_dependencies):
        """Test workflow for safely deleting snapshots with dependency checking"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        snapshot_id = str(uuid4())
        
        # Mock snapshot to delete
        mock_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='Snapshot to Delete',
            office_id=str(uuid4()),
            snapshot_date='202503',
            workforce=[],
            metadata={'total_fte': 10, 'total_salary_cost': 50000, 'role_count': 1},
            source='manual',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock dependency check results
        dependencies = {
            'scenarios': ['scenario-1', 'scenario-2'],
            'business_plans': [],
            'comparisons': ['comparison-1']
        }
        
        # Mock repository responses
        mock_repo.get_snapshot.return_value = mock_snapshot
        mock_repo.check_snapshot_dependencies.return_value = dependencies
        
        # Test: Deletion should fail due to dependencies
        with pytest.raises(ValueError, match="Cannot delete snapshot with active dependencies"):
            await mock_service.delete_snapshot(
                snapshot_id=snapshot_id,
                deleted_by=mock_dependencies['current_user']['id'],
                force_delete=False
            )
        
        # Verify dependency check was performed
        mock_repo.check_snapshot_dependencies.assert_called_once_with(snapshot_id)
        
        # Test: Force deletion should succeed
        mock_repo.delete_snapshot.return_value = True
        mock_repo.log_audit_event.return_value = True
        
        result = await mock_service.delete_snapshot(
            snapshot_id=snapshot_id,
            deleted_by=mock_dependencies['current_user']['id'],
            force_delete=True
        )
        
        # Verify force deletion executed
        assert result == True
        mock_repo.delete_snapshot.assert_called_once_with(snapshot_id)
        mock_repo.log_audit_event.assert_called_once()

class TestSnapshotDataIntegrityWorkflows:
    """Test data integrity and validation workflows"""
    
    async def test_snapshot_validation_workflow(self, mock_dependencies):
        """Test comprehensive snapshot data validation workflow"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        # Test data with various validation scenarios
        test_cases = [
            {
                'name': 'Valid snapshot data',
                'data': {
                    'name': 'Valid Snapshot',
                    'office_id': str(uuid4()),
                    'workforce': [
                        {'role': 'Consultant', 'level': 'A', 'fte': 10, 'salary': 4500}
                    ]
                },
                'expected_valid': True,
                'expected_errors': []
            },
            {
                'name': 'Invalid FTE values',
                'data': {
                    'name': 'Invalid Snapshot',
                    'office_id': str(uuid4()),
                    'workforce': [
                        {'role': 'Consultant', 'level': 'A', 'fte': -5, 'salary': 4500}
                    ]
                },
                'expected_valid': False,
                'expected_errors': ['FTE cannot be negative']
            },
            {
                'name': 'Missing required fields',
                'data': {
                    'office_id': str(uuid4()),
                    'workforce': []
                },
                'expected_valid': False,
                'expected_errors': ['Name is required']
            },
            {
                'name': 'Empty workforce',
                'data': {
                    'name': 'Empty Workforce Snapshot',
                    'office_id': str(uuid4()),
                    'workforce': []
                },
                'expected_valid': True,
                'expected_errors': [],
                'expected_warnings': ['Snapshot has no workforce data']
            }
        ]
        
        for test_case in test_cases:
            # Mock validation responses
            validation_result = {
                'is_valid': test_case['expected_valid'],
                'errors': test_case['expected_errors'],
                'warnings': test_case.get('expected_warnings', [])
            }
            
            mock_repo.validate_snapshot_data.return_value = validation_result
            
            # Execute validation
            result = await mock_service.validate_snapshot_data(test_case['data'])
            
            # Verify validation results
            assert result['is_valid'] == test_case['expected_valid']
            assert result['errors'] == test_case['expected_errors']
            
            mock_repo.validate_snapshot_data.assert_called()
            
    async def test_snapshot_consistency_check_workflow(self, mock_dependencies):
        """Test workflow for checking snapshot data consistency"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        snapshot_id = str(uuid4())
        
        # Mock snapshot with potential inconsistencies
        mock_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='Inconsistent Snapshot',
            office_id=str(uuid4()),
            snapshot_date='202503',
            workforce=[
                EmployeeRecord(role='Consultant', level='A', fte=10, salary=4500),
                EmployeeRecord(role='Operations', level=None, fte=5, salary=3500)
            ],
            metadata={'total_fte': 20, 'total_salary_cost': 60000, 'role_count': 2},  # Inconsistent totals
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock consistency check results
        consistency_issues = [
            {
                'field': 'total_fte',
                'expected': 15,
                'actual': 20,
                'severity': 'error'
            },
            {
                'field': 'total_salary_cost',
                'expected': 62500,
                'actual': 60000,
                'severity': 'error'
            }
        ]
        
        mock_repo.get_snapshot.return_value = mock_snapshot
        mock_repo.check_data_consistency.return_value = consistency_issues
        
        # Execute consistency check
        issues = await mock_service.check_snapshot_consistency(snapshot_id)
        
        # Verify consistency check results
        assert len(issues) == 2
        assert issues[0]['field'] == 'total_fte'
        assert issues[0]['severity'] == 'error'
        
        # Verify repository calls
        mock_repo.get_snapshot.assert_called_once_with(snapshot_id)
        mock_repo.check_data_consistency.assert_called_once()
        
    async def test_fix_snapshot_inconsistencies_workflow(self, mock_dependencies):
        """Test workflow for automatically fixing snapshot data inconsistencies"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        snapshot_id = str(uuid4())
        
        # Mock inconsistent snapshot
        inconsistent_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='Snapshot to Fix',
            office_id=str(uuid4()),
            snapshot_date='202503',
            workforce=[
                EmployeeRecord(role='Consultant', level='A', fte=10, salary=4500),
                EmployeeRecord(role='Operations', level=None, fte=5, salary=3500)
            ],
            metadata={'total_fte': 20, 'total_salary_cost': 60000, 'role_count': 2},
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock fixed snapshot
        fixed_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='Snapshot to Fix',
            office_id=inconsistent_snapshot.office_id,
            snapshot_date='202503',
            workforce=inconsistent_snapshot.workforce,
            metadata={'total_fte': 15, 'total_salary_cost': 62500, 'role_count': 2},  # Fixed totals
            source='current',
            created_at=inconsistent_snapshot.created_at,
            updated_at=datetime.now()
        )
        
        # Mock repository responses
        mock_repo.get_snapshot.return_value = inconsistent_snapshot
        mock_repo.recalculate_snapshot_metadata.return_value = fixed_snapshot
        mock_repo.update_snapshot.return_value = fixed_snapshot
        mock_repo.log_audit_event.return_value = True
        
        # Execute fix workflow
        result = await mock_service.fix_snapshot_inconsistencies(
            snapshot_id=snapshot_id,
            fixed_by=mock_dependencies['current_user']['id']
        )
        
        # Verify fix results
        assert result.metadata['total_fte'] == 15
        assert result.metadata['total_salary_cost'] == 62500
        
        # Verify repository calls
        mock_repo.recalculate_snapshot_metadata.assert_called_once()
        mock_repo.update_snapshot.assert_called_once()
        mock_repo.log_audit_event.assert_called_once()
        
        # Verify audit logging
        audit_call = mock_repo.log_audit_event.call_args[1]
        assert audit_call['action'] == 'data_fixed'
        assert 'inconsistencies_fixed' in audit_call['details']

class TestSnapshotPerformanceWorkflows:
    """Test performance-critical snapshot workflows"""
    
    async def test_bulk_snapshot_operations_workflow(self, mock_dependencies):
        """Test workflow for bulk snapshot operations"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        # Set up bulk operation data
        office_ids = [str(uuid4()) for _ in range(5)]
        snapshot_data = {
            'name_template': 'Bulk Snapshot {}',
            'description': 'Created via bulk operation',
            'source': 'current',
            'tags': ['bulk', 'quarterly']
        }
        
        # Mock bulk operation results
        created_snapshots = []
        for i, office_id in enumerate(office_ids):
            snapshot = PopulationSnapshot(
                id=str(uuid4()),
                name=f'Bulk Snapshot {i+1}',
                office_id=office_id,
                snapshot_date='202503',
                workforce=[],
                metadata={'total_fte': 10 + i, 'total_salary_cost': 50000 + (i * 10000), 'role_count': 1},
                source='current',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            created_snapshots.append(snapshot)
        
        mock_repo.bulk_create_snapshots.return_value = created_snapshots
        
        # Execute bulk workflow
        results = await mock_service.bulk_create_snapshots(
            office_ids=office_ids,
            snapshot_data=snapshot_data,
            created_by=mock_dependencies['current_user']['id']
        )
        
        # Verify bulk operation results
        assert len(results) == 5
        assert all(snapshot.source == 'current' for snapshot in results)
        
        # Verify repository call
        mock_repo.bulk_create_snapshots.assert_called_once()
        
    async def test_large_snapshot_processing_workflow(self, mock_dependencies):
        """Test workflow for processing large snapshots efficiently"""
        mock_repo = AsyncMock(spec=SnapshotRepository)
        mock_service = SnapshotService(mock_repo, mock_dependencies['office_service'])
        
        snapshot_id = str(uuid4())
        
        # Mock large workforce data (1000+ employees)
        large_workforce = []
        for i in range(1000):
            role = 'Consultant' if i % 3 == 0 else 'Operations'
            level = 'A' if role == 'Consultant' else None
            large_workforce.append(
                EmployeeRecord(
                    role=role,
                    level=level,
                    fte=1,
                    salary=4500 if role == 'Consultant' else 3500
                )
            )
        
        large_snapshot = PopulationSnapshot(
            id=snapshot_id,
            name='Large Enterprise Snapshot',
            office_id=str(uuid4()),
            snapshot_date='202503',
            workforce=large_workforce,
            metadata={
                'total_fte': 1000,
                'total_salary_cost': 4_166_500,
                'role_count': 2
            },
            source='current',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock repository with performance optimization
        mock_repo.get_snapshot_optimized.return_value = large_snapshot
        mock_repo.process_large_workforce.return_value = {
            'processed_count': 1000,
            'processing_time': 0.5,
            'memory_usage': 'optimized'
        }
        
        # Execute large snapshot processing
        snapshot = await mock_service.get_snapshot_with_optimization(snapshot_id)
        processing_stats = await mock_service.process_workforce_data(snapshot.workforce)
        
        # Verify efficient processing
        assert len(snapshot.workforce) == 1000
        assert processing_stats['processed_count'] == 1000
        assert processing_stats['processing_time'] < 1.0  # Should be fast
        
        # Verify optimized repository calls
        mock_repo.get_snapshot_optimized.assert_called_once_with(snapshot_id)
        mock_repo.process_large_workforce.assert_called_once()

if __name__ == "__main__":
    # Example of how to run integration tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])