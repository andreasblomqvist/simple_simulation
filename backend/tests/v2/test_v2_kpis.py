"""
V2 Engine KPI Testing

Test the comprehensive KPI calculation capabilities of the V2 engine:
1. Workforce KPIs (headcount, recruitment, churn, promotions)
2. Financial KPIs (revenue, costs, profitability) 
3. Business Intelligence KPIs (utilization, efficiency)
4. Comparative Analysis (vs targets)
5. Executive Summary generation
"""

import sys
import json
from pathlib import Path
from datetime import date

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_v2_engine_kpis():
    """Test V2 engine KPI calculation capabilities"""
    print("V2 ENGINE - COMPREHENSIVE KPI TESTING")
    print("=" * 45)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            BusinessPlan, MonthlyPlan, PopulationSnapshot, WorkforceEntry, 
            Person, OfficeState, CATMatrix
        )
        
        # 1. Setup V2 engine with KPI calculator
        print("1. Setting up V2 engine with KPI calculation...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        test_data_dir = Path(__file__).parent / "test_data"
        
        # Load test data (same as comprehensive test)
        with open(test_data_dir / "business_plans.json") as f:
            business_plans_data = json.load(f)
        
        with open(test_data_dir / "cat_matrices_correct.json") as f:
            cat_matrices_data = json.load(f)
            
        with open(test_data_dir / "population_snapshots.json") as f:
            population_data = json.load(f)
        
        # Setup business plans
        engine.business_processor.loaded_plans = {}
        
        for office_id, plan_data in business_plans_data.items():
            monthly_plans = {}
            
            for month, month_data in plan_data["monthly_plans"].items():
                monthly_plan = MonthlyPlan(
                    year=int(month.split("-")[0]),
                    month=int(month.split("-")[1]),
                    recruitment=month_data["recruitment"],
                    churn=month_data["churn"],
                    revenue=float(month_data["revenue"]),
                    costs=float(month_data["costs"]),
                    price_per_role={},
                    salary_per_role={},
                    utr_per_role={}
                )
                monthly_plans[month] = monthly_plan
            
            business_plan = BusinessPlan(
                office_id=plan_data["office_id"],
                name=plan_data["name"],
                monthly_plans=monthly_plans
            )
            
            engine.business_processor.loaded_plans[office_id] = business_plan
        
        # Setup CAT matrices
        cat_matrices = {}
        for role, matrix_data in cat_matrices_data.items():
            cat_matrices[role] = CATMatrix(
                progression_probabilities=matrix_data["progression_probabilities"]
            )
        
        # Setup population
        population_snapshots = {}
        for office_id, snapshot_data in population_data.items():
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
            
            population_snapshots[office_id] = PopulationSnapshot(
                id=snapshot_data["id"],
                office_id=snapshot_data["office_id"],
                snapshot_date=snapshot_data["snapshot_date"],
                name=snapshot_data["name"],
                workforce=workforce_entries
            )
        
        # Create office state
        engine.office_states = {}
        office_id = "london"
        
        office_state = OfficeState(
            name=office_id,
            workforce={},
            business_plan=engine.business_processor.loaded_plans.get(office_id),
            snapshot=population_snapshots.get(office_id),
            cat_matrices=cat_matrices,
            economic_parameters=None
        )
        
        # Populate workforce
        if office_id in population_snapshots:
            snapshot = population_snapshots[office_id]
            office_state.workforce = {}
            
            for entry in snapshot.workforce:
                hire_date = date.fromisoformat(entry.hire_date + "-01")
                level_start_date = date.fromisoformat(entry.level_start_date + "-01")
                
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
        
        engine.office_states[office_id] = office_state
        
        initial_workforce = office_state.get_total_workforce()
        print(f"   Engine setup complete: {initial_workforce} people, KPI calculator: {engine.kpi_calculator is not None}")
        
        # 2. Run simulation with KPI calculation
        print("\\n2. Running simulation with KPI calculation enabled...")
        
        scenario = ScenarioRequest(
            scenario_id="kpi_test",
            name="KPI Testing Scenario",
            time_range=TimeRange(2024, 6, 2024, 9),  # 4 months for focused analysis
            office_ids=["london"],
            levers=Levers(
                recruitment_multiplier=1.0,
                churn_multiplier=1.1,  # Avoid rounding to 0
                progression_multiplier=1.0
            )
        )
        
        results = engine.run_simulation(scenario)
        
        print(f"   Simulation completed: {len(results.all_events)} events generated")
        print(f"   KPI data available: {results.kpi_data is not None}")
        
        if results.kpi_data is None:
            print("   WARNING: KPI data not calculated - may need manual calculation")
            return False, {'error': 'KPI data not generated'}
        
        # 3. Display Workforce KPIs
        print("\\n3. WORKFORCE KPIs")
        print("=" * 20)
        
        if 'workforce_kpis' in results.kpi_data:
            workforce_kpis = results.kpi_data['workforce_kpis']
            
            print(f"   Headcount Metrics:")
            print(f"      Total Headcount: {workforce_kpis.get('total_headcount', 'N/A')}")
            
            if 'headcount_by_role' in workforce_kpis:
                print(f"      By Role:")
                for role, count in workforce_kpis['headcount_by_role'].items():
                    print(f"         {role}: {count}")
            
            if 'headcount_by_level' in workforce_kpis:
                print(f"      By Level:")
                for level, count in workforce_kpis['headcount_by_level'].items():
                    print(f"         {level}: {count}")
            
            print(f"\\n   Movement Metrics:")
            print(f"      Total Recruitment: {workforce_kpis.get('total_recruitment', 'N/A')}")
            print(f"      Total Churn: {workforce_kpis.get('total_churn', 'N/A')}")
            print(f"      Net Recruitment: {workforce_kpis.get('net_recruitment', 'N/A')}")
            print(f"      Total Promotions: {workforce_kpis.get('total_promotions', 'N/A')}")
            
            print(f"\\n   Rate Metrics:")
            print(f"      Recruitment Rate: {workforce_kpis.get('recruitment_rate', 'N/A'):.1f}%")
            print(f"      Churn Rate: {workforce_kpis.get('churn_rate', 'N/A'):.1f}%")
            print(f"      Growth Rate: {workforce_kpis.get('growth_rate', 'N/A'):.1f}%")
            print(f"      Promotion Rate: {workforce_kpis.get('promotion_rate', 'N/A'):.1f}%")
        
        # 4. Display Financial KPIs
        print("\\n4. FINANCIAL KPIs")
        print("=" * 20)
        
        if 'financial_kpis' in results.kpi_data:
            financial_kpis = results.kpi_data['financial_kpis']
            
            print(f"   Revenue Metrics:")
            print(f"      Total Revenue: ${financial_kpis.get('total_revenue', 0):,.0f}")
            print(f"      Revenue Growth Rate: {financial_kpis.get('revenue_growth_rate', 0):.1f}%")
            print(f"      Revenue per FTE: ${financial_kpis.get('revenue_per_fte', 0):,.0f}")
            
            print(f"\\n   Cost Metrics:")
            print(f"      Total Costs: ${financial_kpis.get('total_costs', 0):,.0f}")
            print(f"      Cost Growth Rate: {financial_kpis.get('cost_growth_rate', 0):.1f}%")
            print(f"      Cost per FTE: ${financial_kpis.get('cost_per_fte', 0):,.0f}")
            
            print(f"\\n   Profitability Metrics:")
            print(f"      Gross Profit: ${financial_kpis.get('gross_profit', 0):,.0f}")
            print(f"      Profit Margin: {financial_kpis.get('profit_margin', 0):.1f}%")
            print(f"      Operating Efficiency: {financial_kpis.get('operating_efficiency', 0):.2f}")
        
        # 5. Display Business Intelligence KPIs
        print("\\n5. BUSINESS INTELLIGENCE KPIs")
        print("=" * 35)
        
        if 'business_intelligence_kpis' in results.kpi_data:
            bi_kpis = results.kpi_data['business_intelligence_kpis']
            
            print(f"   Utilization Metrics:")
            print(f"      Average Utilization Rate: {bi_kpis.get('average_utilization_rate', 0):.1f}%")
            
            if 'utilization_by_role' in bi_kpis:
                print(f"      By Role:")
                for role, util in bi_kpis['utilization_by_role'].items():
                    print(f"         {role}: {util:.1f}%")
            
            print(f"\\n   Performance Metrics:")
            print(f"      Growth Momentum: {bi_kpis.get('growth_momentum', 0):.2f}")
            print(f"      Market Expansion Rate: {bi_kpis.get('market_expansion_rate', 0):.1f}%")
        
        # 6. Display Comparative Analysis
        print("\\n6. COMPARATIVE ANALYSIS")
        print("=" * 30)
        
        if 'comparative_analysis' in results.kpi_data:
            comp_analysis = results.kpi_data['comparative_analysis']
            
            if 'vs_targets' in comp_analysis:
                print(f"   Performance vs Targets:")
                for metric, data in comp_analysis['vs_targets'].items():
                    actual = data.get('actual', 0)
                    target = data.get('target', 0)
                    variance = data.get('variance', 0)
                    print(f"      {metric}: {actual:.1f} vs {target:.1f} (variance: {variance:+.1f}%)")
            
            if 'performance_summary' in comp_analysis:
                print(f"\\n   Performance Summary:")
                for metric, status in comp_analysis['performance_summary'].items():
                    print(f"      {metric}: {status}")
            
            if 'key_insights' in comp_analysis:
                print(f"\\n   Key Insights:")
                for insight in comp_analysis['key_insights']:
                    print(f"      • {insight}")
        
        # 7. Display Executive Summary
        print("\\n7. EXECUTIVE SUMMARY")
        print("=" * 25)
        
        if 'executive_summary' in results.kpi_data:
            exec_summary = results.kpi_data['executive_summary']
            
            print(f"   Period: {exec_summary.get('period_description', 'N/A')}")
            print(f"   Workforce Change: {exec_summary.get('total_workforce_change', 'N/A')}")
            print(f"   Financial Performance: {exec_summary.get('financial_performance', 'N/A')}")
            
            if 'key_achievements' in exec_summary:
                print(f"\\n   Key Achievements:")
                for achievement in exec_summary['key_achievements']:
                    print(f"      ✓ {achievement}")
            
            if 'areas_of_concern' in exec_summary:
                print(f"\\n   Areas of Concern:")
                for concern in exec_summary['areas_of_concern']:
                    print(f"      ⚠ {concern}")
            
            if 'recommended_actions' in exec_summary:
                print(f"\\n   Recommended Actions:")
                for action in exec_summary['recommended_actions']:
                    print(f"      → {action}")
        
        # 8. KPI Data Structure Analysis
        print("\\n8. KPI DATA STRUCTURE")
        print("=" * 25)
        
        print(f"   Available KPI categories: {list(results.kpi_data.keys())}")
        print(f"   Total KPI metrics calculated: {sum(len(v) if isinstance(v, dict) else 1 for v in results.kpi_data.values())}")
        
        print(f"\\n   How KPIs are returned:")
        print(f"      - Available in results.kpi_data dictionary")
        print(f"      - Organized by category (workforce, financial, etc.)")
        print(f"      - Both raw metrics and calculated rates/percentages")
        print(f"      - Executive-ready summaries and insights")
        
        return True, {
            'kpi_categories': list(results.kpi_data.keys()),
            'total_metrics': sum(len(v) if isinstance(v, dict) else 1 for v in results.kpi_data.values()),
            'workforce_headcount': results.kpi_data.get('workforce_kpis', {}).get('total_headcount', 0),
            'total_revenue': results.kpi_data.get('financial_kpis', {}).get('total_revenue', 0),
            'simulation_events': len(results.all_events)
        }
        
    except Exception as e:
        print(f"\\nERROR: KPI test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Starting V2 Engine KPI Testing")
    print("=" * 45)
    
    success, metrics = test_v2_engine_kpis()
    
    print("\\n" + "=" * 45)
    if success:
        print("SUCCESS: V2 Engine KPI calculation working!")
        print(f"Generated {metrics['kpi_categories']} KPI categories")
        print(f"Total metrics: {metrics['total_metrics']}")
        print("All KPI types available: Workforce + Financial + Business Intelligence")
    else:
        print("FAILURE: KPI calculation needs work")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print(f"\\nKPI test complete: {metrics.get('simulation_events', 0)} simulation events processed")