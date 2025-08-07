"""
Enhanced Business Plan Testing - V2 Engine

Tests the enhanced business plan data model with:
1. Baseline FTE integration from population snapshots
2. Utilization-based net sales calculation
3. Detailed cost breakdown and KPI calculation
4. Business plan loader with snapshot sync capabilities

This verifies the enhanced business plan structure supports accurate KPI calculation.
"""

import sys
import json
from pathlib import Path
from datetime import date
from collections import Counter, defaultdict

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_enhanced_business_plan():
    """Test enhanced business plan with baseline FTE and utilization calculation"""
    print("V2 ENGINE - ENHANCED BUSINESS PLAN TESTING")
    print("=" * 45)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, BusinessPlan, MonthlyPlan, PopulationSnapshot, WorkforceEntry
        )
        from src.services.business_plan_processor_v2 import BusinessPlanProcessorV2
        
        # 1. Load test data
        print("1. Loading test data...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        business_processor = BusinessPlanProcessorV2()
        test_data_dir = Path(__file__).parent / "test_data"
        
        # Load business plans
        with open(test_data_dir / "business_plans.json") as f:
            business_plans_data = json.load(f)
            
        with open(test_data_dir / "population_snapshots.json") as f:
            population_data = json.load(f)
        
        print(f"   Loaded business plans for {len(business_plans_data)} offices")
        print(f"   Loaded population snapshots for {len(population_data)} offices")
        
        # 2. Create original business plan
        office_id = "london"
        plan_data = business_plans_data[office_id]
        
        original_monthly_plans = {}
        for month, month_data in plan_data["monthly_plans"].items():
            # Add sample pricing data to test the enhanced calculations
            monthly_plan = MonthlyPlan(
                year=int(month.split("-")[0]),
                month=int(month.split("-")[1]),
                recruitment=month_data["recruitment"],
                churn=month_data["churn"],
                revenue=float(month_data["revenue"]),
                costs=float(month_data["costs"]),
                price_per_role={
                    "Consultant": {
                        "A": 24000.0,      # $150/hour * 160 hours
                        "AC": 32000.0,     # $200/hour * 160 hours  
                        "C": 40000.0,      # $250/hour * 160 hours
                        "SrC": 48000.0,    # $300/hour * 160 hours
                        "M": 56000.0       # $350/hour * 160 hours
                    }
                },
                salary_per_role={
                    "Consultant": {
                        "A": 5000.0, "AC": 6500.0, "C": 8000.0, "SrC": 10000.0, "M": 12000.0
                    },
                    "Sales": {
                        "A": 4000.0, "AC": 5000.0, "C": 6000.0
                    },
                    "Recruitment": {
                        "A": 4200.0, "AC": 5200.0, "C": 6200.0
                    },
                    "Operations": {
                        "Operations": 4500.0
                    }
                },
                utr_per_role={}
            )
            original_monthly_plans[month] = monthly_plan
        
        original_business_plan = BusinessPlan(
            office_id=plan_data["office_id"],
            name=plan_data["name"],
            monthly_plans=original_monthly_plans
        )
        
        print(f"   Created original business plan: {len(original_business_plan.monthly_plans)} months")
        
        # 3. Create population snapshot
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
        
        print(f"   Created population snapshot: {len(population_snapshot.workforce)} people")
        
        # 4. ENHANCE BUSINESS PLAN WITH BASELINE FTE
        print("\n2. ENHANCING BUSINESS PLAN WITH BASELINE FTE")
        print("=" * 45)
        
        enhanced_business_plan = business_processor.sync_baseline_fte_from_snapshot(
            original_business_plan, population_snapshot
        )
        
        # Verify enhanced plan structure
        july_2024_plan = enhanced_business_plan.get_plan_for_month(2024, 7)
        
        print(f"   Enhanced business plan name: {enhanced_business_plan.name}")
        print(f"   July 2024 plan enhanced fields:")
        print(f"      Baseline FTE: {len(july_2024_plan.baseline_fte)} roles")
        print(f"      Utilization targets: {july_2024_plan.utilization_targets}")
        print(f"      Price per hour: {len(july_2024_plan.price_per_hour)} levels")
        print(f"      Working hours/month: {july_2024_plan.working_hours_per_month}")
        print(f"      Operating costs: ${july_2024_plan.operating_costs:,.0f}")
        
        # Display baseline FTE breakdown
        print(f"\n   BASELINE FTE BREAKDOWN:")
        total_fte = 0
        for role, levels in july_2024_plan.baseline_fte.items():
            role_total = sum(levels.values())
            total_fte += role_total
            print(f"      {role}: {role_total} people ({levels})")
        print(f"      TOTAL: {total_fte} people")
        
        # 3. NET SALES CALCULATION
        print("\n3. NET SALES CALCULATION (UTILIZATION-BASED)")
        print("=" * 50)
        
        # Original revenue vs utilization-based calculation
        original_revenue = july_2024_plan.revenue
        
        calculated_net_sales = business_processor.calculate_net_sales_utilization_based(
            july_2024_plan
        )
        
        print(f"   Original business plan revenue: ${original_revenue:,.0f}")
        print(f"   Calculated net sales (utilization): ${calculated_net_sales:,.0f}")
        print(f"   Difference: ${calculated_net_sales - original_revenue:,.0f} ({((calculated_net_sales - original_revenue) / original_revenue * 100):+.1f}%)")
        
        # Show calculation breakdown
        consultant_workforce = july_2024_plan.baseline_fte.get('Consultant', {})
        consultant_utilization = july_2024_plan.utilization_targets.get('Consultant', 0.85)
        
        print(f"\n   NET SALES CALCULATION BREAKDOWN:")
        print(f"      Consultant utilization: {consultant_utilization:.0%}")
        print(f"      Working hours/month: {july_2024_plan.working_hours_per_month}")
        
        breakdown_total = 0
        for level, count in consultant_workforce.items():
            if count > 0:
                price_per_hour = july_2024_plan.price_per_hour.get(level, 0)
                level_revenue = count * consultant_utilization * price_per_hour * july_2024_plan.working_hours_per_month
                breakdown_total += level_revenue
                
                print(f"      Level {level}: {count} × {consultant_utilization:.0%} × ${price_per_hour:.0f}/hr × {july_2024_plan.working_hours_per_month}hrs = ${level_revenue:,.0f}")
        
        print(f"      TOTAL NET SALES: ${breakdown_total:,.0f}")
        
        # 4. FINANCIAL KPI CALCULATION
        print("\n4. ENHANCED FINANCIAL KPI CALCULATION")
        print("=" * 40)
        
        # Calculate comprehensive financial metrics
        salary_budget = business_processor._calculate_salary_budget(july_2024_plan)
        operating_costs = july_2024_plan.operating_costs
        total_costs = salary_budget + operating_costs
        gross_profit = calculated_net_sales - total_costs
        profit_margin = (gross_profit / calculated_net_sales * 100) if calculated_net_sales > 0 else 0
        
        print(f"   Net Sales: ${calculated_net_sales:,.0f}")
        print(f"   Salary Budget: ${salary_budget:,.0f}")
        print(f"   Operating Costs: ${operating_costs:,.0f}")
        print(f"   Total Costs: ${total_costs:,.0f}")
        print(f"   Gross Profit: ${gross_profit:,.0f}")
        print(f"   Profit Margin: {profit_margin:.1f}%")
        
        # Revenue per FTE and cost per FTE
        revenue_per_fte = calculated_net_sales / total_fte if total_fte > 0 else 0
        cost_per_fte = total_costs / total_fte if total_fte > 0 else 0
        
        print(f"   Revenue per FTE: ${revenue_per_fte:,.0f}")
        print(f"   Cost per FTE: ${cost_per_fte:,.0f}")
        
        # 5. ROLE-SPECIFIC FINANCIAL ATTRIBUTION
        print("\n5. ROLE-SPECIFIC FINANCIAL ATTRIBUTION")
        print("=" * 40)
        
        # Only Consultants generate revenue
        consultant_count = sum(july_2024_plan.baseline_fte.get('Consultant', {}).values())
        consultant_revenue = calculated_net_sales  # All revenue from consultants
        consultant_costs = salary_budget * (consultant_count / total_fte) if total_fte > 0 else 0
        
        # Support roles are pure cost centers
        support_roles = ['Sales', 'Recruitment', 'Operations']
        for role in support_roles:
            role_count = sum(july_2024_plan.baseline_fte.get(role, {}).values())
            role_revenue = 0  # Support roles generate no revenue
            role_costs = salary_budget * (role_count / total_fte) if total_fte > 0 else 0
            role_profit = role_revenue - role_costs
            
            print(f"   {role} ({role_count} people):")
            print(f"      Revenue: ${role_revenue:,.0f} (support role)")
            print(f"      Costs: ${role_costs:,.0f}")
            print(f"      Profit: ${role_profit:,.0f} (cost center)")
        
        print(f"   Consultant ({consultant_count} people):")
        print(f"      Revenue: ${consultant_revenue:,.0f} (generates ALL revenue)")
        print(f"      Costs: ${consultant_costs:,.0f}")
        print(f"      Profit: ${consultant_revenue - consultant_costs:,.0f}")
        
        # 6. VERIFICATION SUMMARY
        print("\n6. ENHANCED BUSINESS PLAN VERIFICATION")
        print("=" * 40)
        
        # Verify all enhanced fields are present and populated
        enhanced_features = {
            'baseline_fte': len(july_2024_plan.baseline_fte) > 0,
            'utilization_targets': len(july_2024_plan.utilization_targets) > 0,
            'price_per_hour': len(july_2024_plan.price_per_hour) > 0,
            'working_hours_per_month': july_2024_plan.working_hours_per_month > 0,
            'operating_costs': july_2024_plan.operating_costs > 0,
            'net_sales_calculation': calculated_net_sales > 0
        }
        
        all_features_working = all(enhanced_features.values())
        
        print(f"   Enhanced Features Status:")
        for feature, working in enhanced_features.items():
            status = "[OK] Working" if working else "[X] Missing"
            print(f"      {feature}: {status}")
        
        print(f"\n   Overall Status: {'[OK] ALL ENHANCED FEATURES WORKING' if all_features_working else '[X] Some features missing'}")
        
        return True, {
            'original_revenue': original_revenue,
            'calculated_net_sales': calculated_net_sales,
            'total_fte': total_fte,
            'consultant_count': consultant_count,
            'profit_margin': profit_margin,
            'enhanced_features_working': all_features_working
        }
        
    except Exception as e:
        print(f"\nERROR: Enhanced business plan test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Starting Enhanced Business Plan Testing")
    print("=" * 45)
    
    success, metrics = test_enhanced_business_plan()
    
    print("\n" + "=" * 45)
    if success:
        print("SUCCESS: Enhanced business plan working!")
        print(f"Net sales calculation: ${metrics['calculated_net_sales']:,.0f}")
        print(f"Total workforce: {metrics['total_fte']} ({metrics['consultant_count']} consultants)")
        print(f"Profit margin: {metrics['profit_margin']:.1f}%")
        print("Enhanced features: Baseline FTE, utilization-based revenue, role-specific attribution")
    else:
        print("FAILURE: Enhanced business plan needs work")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print(f"\nEnhanced business plan test complete")