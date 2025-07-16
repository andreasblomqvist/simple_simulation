#!/usr/bin/env python3
"""
Test KPI Calculation
====================

Script to test the KPI calculation directly with the data structure.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.services.kpi import KPIService
from src.services.kpi.kpi_models import EconomicParameters
from test_scenarios import get_scenario_by_name

def test_kpi_calculation():
    """Test KPI calculation directly."""
    
    print("🧮 TESTING KPI CALCULATION DIRECTLY")
    print("=" * 60)
    
    # Get the scenario
    scenario_definition = get_scenario_by_name("minimal")
    
    # Create economic parameters
    economic_params = EconomicParameters(
        unplanned_absence=0.05,
        other_expense=1000000.0,
        employment_cost_rate=0.3,
        working_hours_per_month=160.0
    )
    
    # Create KPI service
    kpi_service = KPIService(economic_params)
    
    # Create test data structure (simulating what the simulation engine produces)
    test_year_data = {
        'offices': {
            'Stockholm': {
                'total_fte': 1000,
                'roles': {
                    'Consultant': {
                        'A': [
                            {
                                'fte': 31,
                                'price': 1200.0,
                                'salary': 45000.0,
                                'utr': 0.85
                            }
                        ],
                        'AC': [
                            {
                                'fte': 213,
                                'price': 1300.0,
                                'salary': 55000.0,
                                'utr': 0.85
                            }
                        ]
                    },
                    'Operations': [
                        {
                            'fte': 50,
                            'price': 0.0,
                            'salary': 40000.0,
                            'utr': 0.85
                        }
                    ]
                }
            }
        }
    }
    
    # Test the KPI calculation
    print("📊 Testing KPI calculation...")
    
    try:
        # Create a simulation results structure
        simulation_results = {
            'years': {
                '2025': test_year_data
            }
        }
        
        # Calculate KPIs
        all_kpis = kpi_service.calculate_all_kpis(
            simulation_results,
            simulation_duration_months=12,
            economic_params=economic_params
        )
        
        print("✅ KPI calculation successful!")
        print(f"\n💰 FINANCIAL KPIs:")
        print(f"  Net Sales: ${all_kpis.financial.net_sales:,.0f}")
        print(f"  Net Sales Baseline: ${all_kpis.financial.net_sales_baseline:,.0f}")
        print(f"  Total Salary Costs: ${all_kpis.financial.total_salary_costs:,.0f}")
        print(f"  Total Salary Costs Baseline: ${all_kpis.financial.total_salary_costs_baseline:,.0f}")
        print(f"  EBITDA: ${all_kpis.financial.ebitda:,.0f}")
        print(f"  EBITDA Baseline: ${all_kpis.financial.ebitda_baseline:,.0f}")
        print(f"  Margin: {all_kpis.financial.margin:.2%}")
        print(f"  Margin Baseline: {all_kpis.financial.margin_baseline:.2%}")
        print(f"  Total Consultants: {all_kpis.financial.total_consultants}")
        print(f"  Total Consultants Baseline: {all_kpis.financial.total_consultants_baseline}")
        print(f"  Avg Hourly Rate: ${all_kpis.financial.avg_hourly_rate:,.0f}")
        print(f"  Avg Hourly Rate Baseline: ${all_kpis.financial.avg_hourly_rate_baseline:,.0f}")
        
        # Calculate expected values manually
        print(f"\n🧮 MANUAL CALCULATION:")
        
        # Consultant A
        fte_a = 31
        price_a = 1200.0
        salary_a = 45000.0
        utr_a = 0.85
        
        # Consultant AC
        fte_ac = 213
        price_ac = 1300.0
        salary_ac = 55000.0
        utr_ac = 0.85
        
        # Operations
        fte_ops = 50
        salary_ops = 40000.0
        
        # Revenue calculation
        working_hours = 160.0
        unplanned_absence = 0.05
        available_hours = working_hours * (1 - unplanned_absence)
        
        # Consultant A revenue
        billable_hours_a = available_hours * utr_a
        monthly_revenue_a = fte_a * price_a * billable_hours_a
        annual_revenue_a = monthly_revenue_a * 12
        
        # Consultant AC revenue
        billable_hours_ac = available_hours * utr_ac
        monthly_revenue_ac = fte_ac * price_ac * billable_hours_ac
        annual_revenue_ac = monthly_revenue_ac * 12
        
        total_revenue = annual_revenue_a + annual_revenue_ac
        
        # Cost calculation
        employment_cost_rate = 0.3
        
        # Consultant A cost
        monthly_cost_a = fte_a * salary_a * (1 + employment_cost_rate)
        annual_cost_a = monthly_cost_a * 12
        
        # Consultant AC cost
        monthly_cost_ac = fte_ac * salary_ac * (1 + employment_cost_rate)
        annual_cost_ac = monthly_cost_ac * 12
        
        # Operations cost
        monthly_cost_ops = fte_ops * salary_ops * (1 + employment_cost_rate)
        annual_cost_ops = monthly_cost_ops * 12
        
        total_cost = annual_cost_a + annual_cost_ac + annual_cost_ops
        
        # Other expense allocation
        total_fte = fte_a + fte_ac + fte_ops
        other_expense = 1000000.0
        stockholm_share = (total_fte / total_fte) * other_expense * 12  # Assuming total system FTE = Stockholm FTE
        
        total_cost_with_expense = total_cost + stockholm_share
        
        # Profit calculation
        profit = total_revenue - total_cost_with_expense
        
        print(f"  Expected Annual Revenue: ${total_revenue:,.0f}")
        print(f"  Expected Annual Cost: ${total_cost_with_expense:,.0f}")
        print(f"  Expected Annual Profit: ${profit:,.0f}")
        print(f"  Expected Margin: {(profit / total_revenue * 100):.1f}%" if total_revenue > 0 else "  Expected Margin: N/A")
        
        # Compare
        print(f"\n📈 COMPARISON:")
        print(f"  Revenue - KPI: ${all_kpis.financial.net_sales:,.0f}, Manual: ${total_revenue:,.0f}")
        print(f"  Cost - KPI: ${all_kpis.financial.total_salary_costs:,.0f}, Manual: ${total_cost:,.0f}")
        print(f"  Profit - KPI: ${all_kpis.financial.ebitda:,.0f}, Manual: ${profit:,.0f}")
        
    except Exception as e:
        print(f"❌ KPI calculation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_kpi_calculation() 