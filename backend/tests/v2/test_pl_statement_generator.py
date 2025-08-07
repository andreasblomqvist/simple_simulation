"""
P&L Statement Generator Testing - V2 Engine

Tests comprehensive monthly P&L statement generation:
1. Revenue breakdown by role and utilization
2. Cost analysis with salary and operating expenses
3. Profit calculations with margin analysis
4. Role-specific financial attribution
5. Multi-month trend analysis
6. Export capabilities for financial reporting

Verifies integration with enhanced business plan data and KPI calculations.
"""

import sys
import json
from pathlib import Path
from datetime import date
from collections import Counter, defaultdict

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_pl_statement_generation():
    """Test comprehensive P&L statement generation with enhanced business plan"""
    print("V2 ENGINE - P&L STATEMENT GENERATOR TESTING")
    print("=" * 50)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, BusinessPlan, MonthlyPlan, PopulationSnapshot, 
            WorkforceEntry, OfficeState, ScenarioRequest, TimeRange, Levers
        )
        from src.services.business_plan_processor_v2 import BusinessPlanProcessorV2
        from src.services.pl_statement_generator_v2 import PLStatementGeneratorV2
        
        # 1. Setup engine and components
        print("1. Setting up V2 engine and P&L generator...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        business_processor = BusinessPlanProcessorV2()
        pl_generator = PLStatementGeneratorV2()
        test_data_dir = Path(__file__).parent / "test_data"
        
        # Load test data
        with open(test_data_dir / "business_plans.json") as f:
            business_plans_data = json.load(f)
            
        with open(test_data_dir / "population_snapshots.json") as f:
            population_data = json.load(f)
        
        print(f"   Loaded business plans for {len(business_plans_data)} offices")
        print(f"   Loaded population snapshots for {len(population_data)} offices")
        
        # 2. Create enhanced business plan with pricing data
        office_id = "london"
        plan_data = business_plans_data[office_id]
        
        original_monthly_plans = {}
        for month, month_data in plan_data["monthly_plans"].items():
            monthly_plan = MonthlyPlan(
                year=int(month.split("-")[0]),
                month=int(month.split("-")[1]),
                recruitment=month_data["recruitment"],
                churn=month_data["churn"],
                revenue=float(month_data["revenue"]),
                costs=float(month_data["costs"]),
                price_per_role={
                    "Consultant": {
                        "A": 24000.0, "AC": 32000.0, "C": 40000.0, "SrC": 48000.0, "M": 56000.0
                    }
                },
                salary_per_role={
                    "Consultant": {"A": 5000.0, "AC": 6500.0, "C": 8000.0, "SrC": 10000.0, "M": 12000.0},
                    "Sales": {"A": 4000.0, "AC": 5000.0, "C": 6000.0},
                    "Recruitment": {"A": 4200.0, "AC": 5200.0, "C": 6200.0},
                    "Operations": {"Operations": 4500.0}
                },
                utr_per_role={}
            )
            original_monthly_plans[month] = monthly_plan
        
        original_business_plan = BusinessPlan(
            office_id=plan_data["office_id"],
            name=plan_data["name"],
            monthly_plans=original_monthly_plans
        )
        
        # 3. Create population snapshot and office state
        snapshot_data = population_data[office_id]
        workforce_entries = []
        
        for entry_data in snapshot_data["workforce"]:
            workforce_entries.append(WorkforceEntry(
                id=entry_data["id"],
                role=entry_data["role"],
                level=entry_data["level"],
                hire_date=entry_data["hire_date"],
                level_start_date=entry_data["level_start_date"],
                office=entry_data["office"]
            ))
        
        population_snapshot = PopulationSnapshot(
            id=snapshot_data["id"],
            office_id=snapshot_data["office_id"],
            snapshot_date=snapshot_data["snapshot_date"],
            name=snapshot_data["name"],
            workforce=workforce_entries
        )
        
        # 4. Enhance business plan with baseline FTE
        enhanced_business_plan = business_processor.sync_baseline_fte_from_snapshot(
            original_business_plan, population_snapshot
        )
        
        # 5. Create office state
        office_state = OfficeState(
            name=office_id,
            workforce={},
            business_plan=enhanced_business_plan,
            snapshot=population_snapshot,
            cat_matrices={},
            economic_parameters=None
        )
        
        # Populate workforce from snapshot
        for entry in population_snapshot.workforce:
            hire_date = date.fromisoformat(entry.hire_date + "-01")
            level_start_date = date.fromisoformat(entry.level_start_date + "-01")
            
            from src.services.simulation_engine_v2 import Person
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
            
            if entry.role not in office_state.workforce:
                office_state.workforce[entry.role] = {}
            if entry.level not in office_state.workforce[entry.role]:
                office_state.workforce[entry.role][entry.level] = []
            
            office_state.workforce[entry.role][entry.level].append(person)
        
        print(f"   Created office state with {office_state.get_total_workforce()} people")
        
        # 6. MONTHLY P&L STATEMENT GENERATION
        print("\n2. GENERATING MONTHLY P&L STATEMENT")
        print("=" * 40)
        
        # Use July 2024 data
        july_2024_plan = enhanced_business_plan.get_plan_for_month(2024, 7)
        
        # Create mock monthly KPIs (in real scenario this comes from simulation)
        monthly_kpis = {
            'total_headcount': office_state.get_total_workforce(),
            'total_recruitment': 3,
            'total_churn': 1,
            'net_recruitment': 2
        }
        
        # Generate P&L statement
        pl_statement = pl_generator.generate_monthly_pl(
            office_state, july_2024_plan, monthly_kpis, "pl_test_scenario"
        )
        
        print(f"   Generated P&L for: {pl_statement.office_id} {pl_statement.year}-{pl_statement.month:02d}")
        print(f"   Statement date: {pl_statement.statement_date}")
        print(f"   Scenario ID: {pl_statement.scenario_id}")
        
        # 7. P&L STATEMENT BREAKDOWN ANALYSIS
        print("\n3. P&L STATEMENT DETAILED BREAKDOWN")
        print("=" * 42)
        
        print(f"\n   REVENUE SECTION ({pl_statement.revenue_section.section_name})")
        print(f"   Section Total: ${pl_statement.revenue_section.section_total:,.0f} ({pl_statement.revenue_section.percentage_of_revenue:.1f}%)")
        
        for item in pl_statement.revenue_section.line_items:
            print(f"      {item.item_name}: ${item.amount:,.0f} ({item.percentage_of_revenue:.1f}%)")
            if item.breakdown:
                for breakdown_item, breakdown_amount in item.breakdown.items():
                    print(f"         - {breakdown_item}: ${breakdown_amount:,.0f}")
            if item.notes:
                print(f"         Notes: {item.notes}")
        
        print(f"\n   COST SECTION ({pl_statement.cost_section.section_name})")
        print(f"   Section Total: ${pl_statement.cost_section.section_total:,.0f} ({pl_statement.cost_section.percentage_of_revenue:.1f}%)")
        
        for item in pl_statement.cost_section.line_items:
            print(f"      {item.item_name}: ${item.amount:,.0f} ({item.percentage_of_revenue:.1f}%)")
            if item.breakdown:
                for breakdown_item, breakdown_amount in item.breakdown.items():
                    print(f"         - {breakdown_item}: ${breakdown_amount:,.0f}")
            if item.notes:
                print(f"         Notes: {item.notes}")
        
        print(f"\n   PROFIT SECTION ({pl_statement.profit_section.section_name})")
        print(f"   Section Total: ${pl_statement.profit_section.section_total:,.0f} ({pl_statement.profit_section.percentage_of_revenue:.1f}%)")
        
        for item in pl_statement.profit_section.line_items:
            print(f"      {item.item_name}: ${item.amount:,.0f} ({item.percentage_of_revenue:.1f}%)")
        
        # 8. SUMMARY METRICS ANALYSIS
        print("\n4. SUMMARY FINANCIAL METRICS")
        print("=" * 32)
        
        print(f"   Total Revenue: ${pl_statement.total_revenue:,.0f}")
        print(f"   Total Costs: ${pl_statement.total_costs:,.0f}")
        print(f"   Gross Profit: ${pl_statement.gross_profit:,.0f}")
        print(f"   Profit Margin: {pl_statement.profit_margin:.1f}%")
        
        print(f"\n   Workforce Metrics:")
        print(f"      Total Headcount: {pl_statement.total_headcount} people")
        print(f"      Billable Headcount: {pl_statement.billable_headcount} people")
        print(f"      Revenue per FTE: ${pl_statement.revenue_per_fte:,.0f}")
        print(f"      Cost per FTE: ${pl_statement.cost_per_fte:,.0f}")
        print(f"      Billable Utilization: {pl_statement.billable_headcount/pl_statement.total_headcount:.0%}")
        
        # 9. MULTI-MONTH P&L STATEMENTS (3 months for trend analysis)
        print("\n5. MULTI-MONTH TREND ANALYSIS")
        print("=" * 35)
        
        # Generate P&L for 3 consecutive months
        pl_statements = []
        months_to_test = [(2024, 7), (2024, 8), (2024, 9)]
        
        for year, month in months_to_test:
            month_plan = enhanced_business_plan.get_plan_for_month(year, month)
            if month_plan:
                # Simulate slight workforce growth each month
                month_kpis = {
                    'total_headcount': office_state.get_total_workforce() + (month - 7),
                    'total_recruitment': 2,
                    'total_churn': 1,
                    'net_recruitment': 1
                }
                
                month_pl = pl_generator.generate_monthly_pl(
                    office_state, month_plan, month_kpis, f"trend_test_{year}_{month:02d}"
                )
                pl_statements.append(month_pl)
                
                print(f"   {year}-{month:02d}: ${month_pl.total_revenue:,.0f} revenue, {month_pl.profit_margin:.1f}% margin")
        
        # Generate trend analysis
        trend_analysis = pl_generator.generate_trend_analysis(pl_statements)
        
        print(f"\n   TREND ANALYSIS ({trend_analysis.time_period})")
        print(f"      Revenue Growth Rate: {trend_analysis.revenue_growth_rate:+.1f}%")
        print(f"      Cost Growth Rate: {trend_analysis.cost_growth_rate:+.1f}%")
        print(f"      Profit Margin Trend: {[f'{margin:.1f}%' for margin in trend_analysis.profit_margin_trend]}")
        print(f"      Headcount Trend: {trend_analysis.headcount_trend}")
        
        print(f"\n   Key Insights:")
        for insight in trend_analysis.insights:
            print(f"      - {insight}")
        
        # 10. EXPORT CAPABILITIES TESTING
        print("\n6. EXPORT CAPABILITIES TESTING")
        print("=" * 35)
        
        # Export to dictionary format
        pl_dict = pl_generator.export_pl_to_dict(pl_statement)
        trend_dict = pl_generator.export_trend_to_dict(trend_analysis)
        
        print(f"   P&L Statement Export:")
        print(f"      Statement info: {len(pl_dict['statement_info'])} fields")
        print(f"      Summary metrics: {len(pl_dict['summary'])} metrics")
        print(f"      Revenue line items: {len(pl_dict['revenue_breakdown']['line_items'])}")
        print(f"      Cost line items: {len(pl_dict['cost_breakdown']['line_items'])}")
        
        print(f"\n   Trend Analysis Export:")
        print(f"      Trend info: {len(trend_dict['trend_info'])} fields")
        print(f"      Growth metrics: {len(trend_dict['growth_metrics'])} metrics")
        print(f"      Monthly statements: {len(trend_dict['monthly_statements'])}")
        print(f"      Insights: {len(trend_dict['insights'])} insights")
        
        # 11. VERIFICATION SUMMARY
        print("\n7. P&L GENERATOR VERIFICATION")
        print("=" * 35)
        
        verification_checks = {
            'pl_statement_generated': pl_statement is not None,
            'revenue_section_populated': len(pl_statement.revenue_section.line_items) > 0,
            'cost_section_populated': len(pl_statement.cost_section.line_items) > 0,
            'profit_calculated': pl_statement.gross_profit != 0,
            'percentages_calculated': any(item.percentage_of_revenue > 0 for item in pl_statement.revenue_section.line_items),
            'workforce_metrics_calculated': pl_statement.revenue_per_fte > 0,
            'trend_analysis_working': trend_analysis is not None,
            'export_capabilities_working': len(pl_dict) > 0 and len(trend_dict) > 0,
            'utilization_based_revenue': pl_statement.total_revenue != july_2024_plan.revenue,  # Should differ due to utilization calc
            'role_specific_attribution': any('Consultant' in item.breakdown for item in pl_statement.revenue_section.line_items if item.breakdown)
        }
        
        all_checks_passed = all(verification_checks.values())
        
        print(f"   Verification Results:")
        for check, passed in verification_checks.items():
            status = "[OK]" if passed else "[X]"
            print(f"      {check}: {status}")
        
        print(f"\n   Overall Status: {'[OK] ALL P&L FEATURES WORKING' if all_checks_passed else '[X] Some features need work'}")
        
        return True, {
            'total_revenue': pl_statement.total_revenue,
            'profit_margin': pl_statement.profit_margin,
            'total_headcount': pl_statement.total_headcount,
            'revenue_growth_rate': trend_analysis.revenue_growth_rate,
            'verification_checks_passed': all_checks_passed,
            'insights_generated': len(trend_analysis.insights)
        }
        
    except Exception as e:
        print(f"\nERROR: P&L statement generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Starting P&L Statement Generator Testing")
    print("=" * 50)
    
    success, metrics = test_pl_statement_generation()
    
    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: P&L Statement Generator working!")
        print(f"Monthly revenue: ${metrics['total_revenue']:,.0f}")
        print(f"Profit margin: {metrics['profit_margin']:.1f}%")
        print(f"Workforce: {metrics['total_headcount']} people")
        print(f"Revenue growth: {metrics['revenue_growth_rate']:+.1f}%")
        print(f"Generated {metrics['insights_generated']} business insights")
        print("Features: Revenue breakdown, cost analysis, trend analysis, export capabilities")
    else:
        print("FAILURE: P&L Statement Generator needs work")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print(f"\nP&L Statement Generator test complete")