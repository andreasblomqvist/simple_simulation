"""
Examples of how to integrate and use the population snapshot system
"""
import asyncio
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, Any, List

# These would be the actual imports in the real system
from src.services.snapshot_service import (
    get_snapshot_service,
    SnapshotCreationRequest,
    SimulationSnapshotRequest
)
from src.services.snapshot_integration_service import get_snapshot_integration_service
from src.database.models import SnapshotSource

async def example_create_current_snapshot():
    """Example: Create a snapshot from current workforce"""
    
    snapshot_service = get_snapshot_service()
    
    # Create a snapshot from current office state
    request = SnapshotCreationRequest(
        office_id=UUID("12345678-1234-5678-9012-123456789abc"),
        snapshot_name="Q1 2025 Baseline",
        description="Current workforce as of Q1 2025 planning cycle",
        tags=["baseline", "q1-2025", "planning"],
        is_default=True,
        created_by="planning_team"
    )
    
    snapshot = await snapshot_service.create_snapshot_from_current(request)
    print(f"Created current snapshot: {snapshot.id}")
    
    return snapshot

async def example_create_simulation_snapshot():
    """Example: Create a snapshot from simulation results"""
    
    snapshot_service = get_snapshot_service()
    
    # Sample simulation results structure
    simulation_results = {
        "2025": {
            "London": {
                "roles": {
                    "Consultant": {
                        "A": [10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 26, 28],
                        "B": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                        "C": [2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 8]
                    },
                    "Operations": [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
                }
            }
        }
    }
    
    request = SimulationSnapshotRequest(
        office_name="London",
        simulation_results=simulation_results,
        snapshot_date="202512",  # December 2025
        snapshot_name="Growth Scenario - End State",
        description="Final workforce state from aggressive growth scenario",
        tags=["scenario", "growth", "year-end"],
        created_by="scenario_engine"
    )
    
    snapshot = await snapshot_service.create_snapshot_from_simulation(request)
    print(f"Created simulation snapshot: {snapshot.id}")
    
    return snapshot

async def example_compare_snapshots():
    """Example: Compare two snapshots"""
    
    snapshot_service = get_snapshot_service()
    
    # Assume we have two snapshot IDs
    baseline_id = UUID("12345678-1234-5678-9012-123456789abc")
    result_id = UUID("87654321-4321-8765-2109-cba987654321")
    
    comparison = await snapshot_service.compare_snapshots(
        snapshot_1_id=baseline_id,
        snapshot_2_id=result_id,
        user_id="analyst_user"
    )
    
    print(f"Total FTE Change: {comparison.total_fte_delta}")
    print(f"Workforce Changes: {comparison.workforce_changes}")
    print(f"Insights: {comparison.insights}")
    
    return comparison

async def example_scenario_integration():
    """Example: Full scenario integration with snapshots"""
    
    integration_service = get_snapshot_integration_service()
    
    # 1. Get baseline for scenario
    baseline_data = await integration_service.get_baseline_for_scenario(
        office_name="London",
        baseline_type="default"  # Use office default snapshot
    )
    
    print("Using baseline data for scenario...")
    
    # 2. Run scenario (this would be done by the simulation engine)
    # ... scenario execution code ...
    
    # 3. Create snapshot from results
    simulation_results = {
        "2025": {
            "London": {
                "roles": {
                    "Consultant": {
                        "A": [20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42],
                        "B": [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]
                    }
                }
            }
        }
    }
    
    result_snapshot_id = await integration_service.create_snapshot_from_scenario_result(
        scenario_id="growth_scenario_2025",
        simulation_results=simulation_results,
        snapshot_date="202512",
        office_name="London",
        created_by="scenario_system"
    )
    
    print(f"Created result snapshot: {result_snapshot_id}")
    
    # 4. Create timeline snapshots
    timeline_snapshots = await integration_service.create_snapshots_from_simulation_timeline(
        simulation_results=simulation_results,
        office_name="London",
        scenario_id="growth_scenario_2025",
        months_to_snapshot=["202503", "202506", "202509", "202512"],  # Quarterly
        created_by="scenario_system"
    )
    
    print(f"Created timeline snapshots: {timeline_snapshots}")

async def example_business_plan_integration():
    """Example: Create snapshot from business plan data"""
    
    snapshot_service = get_snapshot_service()
    
    # Sample business plan data
    business_plan_data = {
        "entries": [
            {
                "year": 2025,
                "month": 6,
                "role": "Consultant",
                "level": "A",
                "recruitment": 5,
                "churn": 1
            },
            {
                "year": 2025,
                "month": 6,
                "role": "Consultant",
                "level": "B",
                "recruitment": 3,
                "churn": 0
            },
            {
                "year": 2025,
                "month": 6,
                "role": "Operations",
                "level": None,  # Flat role
                "recruitment": 2,
                "churn": 1
            }
        ]
    }
    
    snapshot = await snapshot_service.create_snapshot_from_business_plan(
        office_id=UUID("12345678-1234-5678-9012-123456789abc"),
        business_plan_data=business_plan_data,
        snapshot_name="Mid-Year Business Plan Target",
        snapshot_date="202506",
        created_by="business_planning_team",
        description="Target workforce state from business plan for June 2025",
        tags=["business-plan", "mid-year", "target"]
    )
    
    print(f"Created business plan snapshot: {snapshot.id}")
    return snapshot

async def example_snapshot_management():
    """Example: Snapshot management operations"""
    
    snapshot_service = get_snapshot_service()
    
    # Search snapshots
    snapshots, total_count = await snapshot_service.search_snapshots(
        office_id=UUID("12345678-1234-5678-9012-123456789abc"),
        tags=["baseline", "planning"],
        approved_only=True,
        limit=10
    )
    
    print(f"Found {len(snapshots)} snapshots out of {total_count} total")
    
    # Update a snapshot
    if snapshots:
        snapshot_id = snapshots[0].id
        
        await snapshot_service.update_snapshot(
            snapshot_id=snapshot_id,
            updates={
                "description": "Updated description with more context",
                "is_approved": True
            },
            updated_by="admin_user"
        )
        
        print(f"Updated snapshot: {snapshot_id}")
        
        # Set as default
        await snapshot_service.set_default_snapshot(
            snapshot_id=snapshot_id,
            user_id="admin_user"
        )
        
        print(f"Set snapshot as default: {snapshot_id}")
        
        # Get audit log
        audit_logs = await snapshot_service.get_audit_log(snapshot_id, limit=5)
        print(f"Audit log entries: {len(audit_logs)}")
        for log in audit_logs[:2]:  # Show first 2
            print(f"  - {log['action']} by {log['user_id']} at {log['timestamp']}")

async def example_office_history():
    """Example: Get office snapshot history"""
    
    integration_service = get_snapshot_integration_service()
    
    history = await integration_service.get_office_snapshot_history(
        office_name="London",
        include_simulation_snapshots=True
    )
    
    print(f"Office has {len(history)} historical snapshots:")
    for snapshot in history[:5]:  # Show first 5
        print(f"  - {snapshot['name']} ({snapshot['date']}) - {snapshot['total_fte']} FTE")

async def example_validation():
    """Example: Validate snapshot for simulation use"""
    
    integration_service = get_snapshot_integration_service()
    
    snapshot_id = UUID("12345678-1234-5678-9012-123456789abc")
    
    validation_result = await integration_service.validate_snapshot_for_simulation(snapshot_id)
    
    if validation_result["valid"]:
        print("Snapshot is valid for simulation")
        print(f"Summary: {validation_result['summary']}")
        if validation_result.get("warnings"):
            print(f"Warnings: {validation_result['warnings']}")
    else:
        print(f"Snapshot is not valid: {validation_result['error']}")

async def main():
    """Run all examples"""
    print("=== Population Snapshot Integration Examples ===\n")
    
    try:
        print("1. Creating current workforce snapshot...")
        await example_create_current_snapshot()
        print()
        
        print("2. Creating simulation result snapshot...")
        await example_create_simulation_snapshot()
        print()
        
        print("3. Comparing snapshots...")
        await example_compare_snapshots()
        print()
        
        print("4. Full scenario integration...")
        await example_scenario_integration()
        print()
        
        print("5. Business plan integration...")
        await example_business_plan_integration()
        print()
        
        print("6. Snapshot management...")
        await example_snapshot_management()
        print()
        
        print("7. Office history...")
        await example_office_history()
        print()
        
        print("8. Snapshot validation...")
        await example_validation()
        print()
        
        print("=== All examples completed ===")
        
    except Exception as e:
        print(f"Error running examples: {e}")

if __name__ == "__main__":
    # Note: In a real system, this would need proper database setup
    print("These are example functions showing snapshot integration patterns.")
    print("To run them, ensure the database is set up and services are initialized.")
    
    # Uncomment to run examples (requires database setup):
    # asyncio.run(main())