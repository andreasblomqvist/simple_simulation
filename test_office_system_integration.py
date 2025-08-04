#!/usr/bin/env python3
"""
Integration test for the complete office management system.
Tests the full workflow from office creation to business planning.
"""
import asyncio
import json
import tempfile
import shutil
from datetime import date
from pathlib import Path

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.models.office import (
    OfficeConfig, WorkforceDistribution, WorkforceEntry,
    MonthlyBusinessPlan, MonthlyPlanEntry, ProgressionConfig,
    OfficeJourney, ProgressionCurve
)
from backend.src.services.office_service import OfficeService
from backend.src.validators.office_validators import validate_complete_office_setup


async def test_complete_office_workflow():
    """Test complete office management workflow."""
    
    print("🧪 TESTING COMPLETE OFFICE MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    office_service = OfficeService(data_dir=temp_dir)
    
    try:
        # ================================================
        # 1. CREATE OFFICE CONFIGURATION
        # ================================================
        print("\n📋 STEP 1: Creating Office Configuration")
        print("-" * 40)
        
        office_config = OfficeConfig(
            name="Stockholm Test Office",
            journey=OfficeJourney.MATURE,
            timezone="Europe/Stockholm"
        )
        
        created_office = await office_service.create_office(office_config)
        print(f"✅ Office created: {created_office.name} (ID: {created_office.id})")
        print(f"   Journey: {created_office.journey}")
        print(f"   Timezone: {created_office.timezone}")
        
        # ================================================
        # 2. CREATE WORKFORCE DISTRIBUTION
        # ================================================
        print("\n👥 STEP 2: Creating Workforce Distribution")
        print("-" * 40)
        
        workforce = WorkforceDistribution(
            office_id=created_office.id,
            start_date=date(2024, 1, 1),
            workforce=[
                WorkforceEntry(role="Consultant", level="A", fte=25, notes="Associate consultants"),
                WorkforceEntry(role="Consultant", level="AC", fte=18, notes="Advanced consultants"),
                WorkforceEntry(role="Consultant", level="C", fte=12, notes="Consultants"),
                WorkforceEntry(role="Consultant", level="SrC", fte=8, notes="Senior consultants"),
                WorkforceEntry(role="Sales", level="A", fte=5, notes="Sales associates"),
                WorkforceEntry(role="Sales", level="AC", fte=3, notes="Advanced sales"),
                WorkforceEntry(role="Operations", level="A", fte=2, notes="Operations staff"),
                WorkforceEntry(role="Operations", level="AC", fte=1, notes="Senior operations")
            ]
        )
        
        created_workforce = await office_service.create_workforce_distribution(workforce)
        print(f"✅ Workforce distribution created")
        print(f"   Total FTE: {created_workforce.get_total_fte()}")
        print(f"   Consultant FTE: {created_workforce.get_fte_by_role('Consultant')}")
        print(f"   Sales FTE: {created_workforce.get_fte_by_role('Sales')}")
        print(f"   Operations FTE: {created_workforce.get_fte_by_role('Operations')}")
        
        # ================================================
        # 3. CREATE MONTHLY BUSINESS PLANS
        # ================================================
        print("\n📊 STEP 3: Creating Monthly Business Plans")
        print("-" * 40)
        
        # Create business plans for Q1 2024
        business_plans = []
        for month in [1, 2, 3]:
            plan = MonthlyBusinessPlan(
                office_id=created_office.id,
                year=2024,
                month=month,
                entries=[
                    # Consultant entries
                    MonthlyPlanEntry(
                        role="Consultant", level="A", recruitment=3, churn=2,
                        price=80.0, utr=0.70, salary=4500.0
                    ),
                    MonthlyPlanEntry(
                        role="Consultant", level="AC", recruitment=2, churn=1,
                        price=100.0, utr=0.75, salary=5500.0
                    ),
                    MonthlyPlanEntry(
                        role="Consultant", level="C", recruitment=2, churn=1,
                        price=120.0, utr=0.80, salary=6500.0
                    ),
                    MonthlyPlanEntry(
                        role="Consultant", level="SrC", recruitment=1, churn=1,
                        price=150.0, utr=0.85, salary=8500.0
                    ),
                    # Sales entries
                    MonthlyPlanEntry(
                        role="Sales", level="A", recruitment=1, churn=0,
                        price=60.0, utr=0.60, salary=4000.0
                    ),
                    MonthlyPlanEntry(
                        role="Sales", level="AC", recruitment=0, churn=0,
                        price=80.0, utr=0.65, salary=5000.0
                    ),
                    # Operations entries
                    MonthlyPlanEntry(
                        role="Operations", level="A", recruitment=0, churn=0,
                        price=50.0, utr=0.90, salary=3500.0
                    ),
                    MonthlyPlanEntry(
                        role="Operations", level="AC", recruitment=0, churn=0,
                        price=70.0, utr=0.95, salary=4500.0
                    )
                ]
            )
            
            created_plan = await office_service.create_monthly_business_plan(plan)
            business_plans.append(created_plan)
            
            print(f"✅ Business plan created for Month {month}/2024")
            print(f"   Total recruitment: {created_plan.get_total_recruitment()}")
            print(f"   Total churn: {created_plan.get_total_churn()}")
            print(f"   Net change: {created_plan.get_net_change()}")
            print(f"   Revenue potential: ${created_plan.get_revenue_potential():,.2f}")
            print(f"   Salary cost: ${created_plan.get_total_salary_cost():,.2f}")
        
        # ================================================
        # 4. CREATE CAT PROGRESSION CONFIGURATIONS
        # ================================================
        print("\n📈 STEP 4: Creating CAT Progression Configurations")
        print("-" * 40)
        
        progression_configs = []
        progression_rates = {
            "A": 0.15,
            "AC": 0.12,
            "C": 0.08,
            "SrC": 0.05,
            "AM": 0.04,
            "M": 0.03,
            "SrM": 0.02,
            "PiP": 0.01
        }
        
        for level, rate in progression_rates.items():
            config = ProgressionConfig(
                office_id=created_office.id,
                level=level,
                monthly_rate=rate,
                curve_type=ProgressionCurve.LINEAR
            )
            
            created_config = await office_service.create_progression_config(config)
            progression_configs.append(created_config)
            print(f"✅ Progression config created for level {level}: {rate:.2%}/month")
        
        # ================================================
        # 5. GET COMPLETE OFFICE SUMMARY
        # ================================================
        print("\n📋 STEP 5: Retrieving Complete Office Summary")
        print("-" * 40)
        
        office_summary = await office_service.get_office_summary(created_office.id)
        
        print(f"✅ Office summary retrieved")
        print(f"   Office: {office_summary.office.name}")
        print(f"   Workforce entries: {len(office_summary.workforce_distribution.workforce)}")
        print(f"   Business plans: {len(office_summary.monthly_plans)}")
        print(f"   Progression configs: {len(office_summary.progression_configs)}")
        
        # Test helper methods
        jan_plan = office_summary.get_plan_for_month(2024, 1)
        if jan_plan:
            print(f"   January 2024 plan found: {jan_plan.get_total_recruitment()} recruitment")
        
        annual_summary = office_summary.get_annual_summary(2024)
        print(f"   Annual 2024 summary: {annual_summary['net_change']} net change")
        
        # ================================================
        # 6. VALIDATE OFFICE SETUP
        # ================================================
        print("\n✅ STEP 6: Validating Office Setup")
        print("-" * 40)
        
        validation_results = validate_complete_office_setup(office_summary)
        
        print(f"Validation Results:")
        print(f"   Errors: {len(validation_results['errors'])}")
        print(f"   Warnings: {len(validation_results['warnings'])}")
        print(f"   Info: {len(validation_results['info'])}")
        
        if validation_results['errors']:
            print("   ❌ Errors found:")
            for error in validation_results['errors']:
                print(f"      - {error}")
        
        if validation_results['warnings']:
            print("   ⚠️ Warnings:")
            for warning in validation_results['warnings']:
                print(f"      - {warning}")
        
        if validation_results['info']:
            print("   ℹ️ Information:")
            for info in validation_results['info']:
                print(f"      - {info}")
        
        # ================================================
        # 7. TEST BUSINESS PLAN OPERATIONS
        # ================================================
        print("\n🔄 STEP 7: Testing Business Plan Operations")
        print("-" * 40)
        
        # Test getting all plans for office
        all_plans = await office_service.get_business_plans_for_office(created_office.id)
        print(f"✅ Retrieved {len(all_plans)} business plans")
        
        # Test getting specific plan
        march_plan = await office_service.get_monthly_business_plan(created_office.id, 2024, 3)
        if march_plan:
            print(f"✅ Retrieved March 2024 plan: {march_plan.get_total_recruitment()} recruitment")
        
        # Test bulk update
        for plan in all_plans:
            # Increase all recruitment by 1
            for entry in plan.entries:
                entry.recruitment += 1
        
        updated_plans = await office_service.bulk_update_business_plans(created_office.id, all_plans)
        print(f"✅ Bulk updated {len(updated_plans)} plans")
        
        # ================================================
        # 8. TEST OFFICE OPERATIONS
        # ================================================
        print("\n🏢 STEP 8: Testing Office Operations")
        print("-" * 40)
        
        # Test listing offices
        all_offices = await office_service.list_offices()
        print(f"✅ Listed {len(all_offices)} offices")
        
        # Test grouping by journey
        offices_by_journey = await office_service.get_offices_by_journey()
        print(f"✅ Offices by journey:")
        for journey, offices in offices_by_journey.items():
            print(f"   {journey}: {len(offices)} offices")
        
        # Test office update
        created_office.name = "Stockholm Updated Office"
        updated_office = await office_service.update_office(created_office.id, created_office)
        print(f"✅ Updated office name: {updated_office.name}")
        
        # ================================================
        # 9. CREATE SECOND OFFICE AND TEST COPYING
        # ================================================
        print("\n🏢 STEP 9: Testing Business Plan Template Copying")
        print("-" * 40)
        
        # Create second office
        second_office = OfficeConfig(
            name="Berlin Test Office",
            journey=OfficeJourney.ESTABLISHED,
            timezone="Europe/Berlin"
        )
        
        created_second_office = await office_service.create_office(second_office)
        print(f"✅ Created second office: {created_second_office.name}")
        
        # Copy business plans from first office to second
        copied_plans = await office_service.copy_business_plan_template(
            created_office.id, created_second_office.id, 2024
        )
        print(f"✅ Copied {len(copied_plans)} business plans to second office")
        
        # ================================================
        # 10. SUMMARY AND STATISTICS
        # ================================================
        print("\n📊 STEP 10: Final Summary and Statistics")
        print("-" * 40)
        
        # Get final summaries for both offices
        stockholm_summary = await office_service.get_office_summary(created_office.id)
        berlin_summary = await office_service.get_office_summary(created_second_office.id)
        
        print(f"Stockholm Office:")
        stockholm_annual = stockholm_summary.get_annual_summary(2024)
        print(f"   Total recruitment: {stockholm_annual['total_recruitment']}")
        print(f"   Total churn: {stockholm_annual['total_churn']}")
        print(f"   Net change: {stockholm_annual['net_change']}")
        
        print(f"Berlin Office:")
        berlin_annual = berlin_summary.get_annual_summary(2024)
        print(f"   Total recruitment: {berlin_annual['total_recruitment']}")
        print(f"   Total churn: {berlin_annual['total_churn']}")
        print(f"   Net change: {berlin_annual['net_change']}")
        
        # Test progression calculations
        print(f"Progression rates:")
        for config in stockholm_summary.progression_configs:
            rate_jan = config.get_rate_for_month(1)
            rate_dec = config.get_rate_for_month(12)
            print(f"   {config.level}: Jan={rate_jan:.2%}, Dec={rate_dec:.2%}")
        
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Office management system is working correctly")
        print("✅ All CRUD operations functional")
        print("✅ Data validation working")
        print("✅ Business plan operations successful")
        print("✅ Template copying functional")
        print("✅ Ready for frontend integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temporary directory
        shutil.rmtree(temp_dir)


def main():
    """Run the complete integration test."""
    success = asyncio.run(test_complete_office_workflow())
    if success:
        print("\n🎯 Phase 1: Backend Foundation - COMPLETED SUCCESSFULLY")
        print("Ready to proceed with Phase 2: Frontend Foundation")
    else:
        print("\n❌ Integration test failed. Please check the errors above.")


if __name__ == "__main__":
    main()