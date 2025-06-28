#!/usr/bin/env python3
"""
Debug the actual financial data from the simulation to understand the negative values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi_service import KPIService
import random

def debug_simulation_financials():
    """Debug the actual simulation financial calculations"""
    
    print("🔧 Debugging Actual Simulation Financials")
    print("=" * 60)
    
    # Seed for reproducible results
    random.seed(42)
    
    # Create engine and run a simple 1-year simulation
    engine = SimulationEngine()
    
    print("📊 Running baseline simulation (no levers)...")
    
    # Run simulation for 1 year
    results = engine.run_simulation(
        start_year=2025, start_month=1,
        end_year=2025, end_month=12,
        lever_plan=None  # No levers
    )
    
    print("✅ Simulation completed")
    print("")
    
    # Create KPI service and calculate KPIs
    kpi_service = KPIService()
    kpis = kpi_service.calculate_all_kpis(
        simulation_results=results,
        simulation_duration_months=12,
        unplanned_absence=0.05,
        other_expense=100000.0
    )
    
    print("📈 Financial Results:")
    print(f"   Net Sales: {kpis.financial.net_sales:,.0f} SEK")
    print(f"   Net Sales Baseline: {kpis.financial.net_sales_baseline:,.0f} SEK")
    print(f"   EBITDA: {kpis.financial.ebitda:,.0f} SEK")
    print(f"   EBITDA Baseline: {kpis.financial.ebitda_baseline:,.0f} SEK")
    print(f"   Margin: {kpis.financial.margin:.1f}%")
    print(f"   Margin Baseline: {kpis.financial.margin_baseline:.1f}%")
    print("")
    
    print("👥 Headcount Results:")
    print(f"   Total Consultants: {kpis.financial.total_consultants:,}")
    print(f"   Total Consultants Baseline: {kpis.financial.total_consultants_baseline:,}")
    print(f"   Total FTE: {kpis.growth.current_total_fte:,}")
    print(f"   Total FTE Baseline: {kpis.growth.baseline_total_fte:,}")
    print(f"   Growth: {kpis.growth.total_growth_percent:.1f}%")
    print("")
    
    # Check if the issue is in the data structure
    print("🔍 Examining Raw Data Structure...")
    years = sorted(results['years'].keys())
    last_year = years[-1]
    last_year_data = results['years'][last_year]
    
    print(f"   Last year: {last_year}")
    print(f"   Available offices: {list(last_year_data['offices'].keys())}")
    
    # Look at Stockholm data specifically
    if 'Stockholm' in last_year_data['offices']:
        stockholm_data = last_year_data['offices']['Stockholm']
        print(f"   Stockholm data keys: {list(stockholm_data.keys())}")
        
        if 'levels' in stockholm_data:
            print(f"   Stockholm roles: {list(stockholm_data['levels'].keys())}")
            
            if 'Consultant' in stockholm_data['levels']:
                consultant_data = stockholm_data['levels']['Consultant']
                print(f"   Consultant levels: {list(consultant_data.keys())}")
                
                # Check A level data structure
                if 'A' in consultant_data:
                    a_data = consultant_data['A']
                    print(f"   A level data type: {type(a_data)}")
                    print(f"   A level length: {len(a_data) if isinstance(a_data, list) else 'N/A'}")
                    
                    if isinstance(a_data, list) and len(a_data) > 0:
                        print(f"   A level first entry: {a_data[0]}")
                        print(f"   A level last entry: {a_data[-1]}")
                    else:
                        print(f"   A level data: {a_data}")
    
    # Now test with aggressive levers to see what breaks
    print("\n🚨 Testing with Aggressive Levers...")
    
    # Create aggressive levers similar to what was causing problems
    aggressive_levers = {
        'Stockholm': {
            'Consultant': {
                'A': {
                    'recruitment_1': 0.08,  # 8% recruitment
                    'recruitment_2': 0.08,
                    'recruitment_3': 0.08,
                    'recruitment_4': 0.08,
                    'recruitment_5': 0.08,
                    'recruitment_6': 0.08,
                    'recruitment_7': 0.08,
                    'recruitment_8': 0.08,
                    'recruitment_9': 0.08,
                    'recruitment_10': 0.08,
                    'recruitment_11': 0.08,
                    'recruitment_12': 0.08,
                    'churn_1': 0.015,  # 1.5% churn
                    'churn_2': 0.015,
                    'churn_3': 0.015,
                    'churn_4': 0.015,
                    'churn_5': 0.015,
                    'churn_6': 0.015,
                    'churn_7': 0.015,
                    'churn_8': 0.015,
                    'churn_9': 0.015,
                    'churn_10': 0.015,
                    'churn_11': 0.015,
                    'churn_12': 0.015
                }
            }
        }
    }
    
    # Run aggressive simulation
    aggressive_results = engine.run_simulation(
        start_year=2025, start_month=1,
        end_year=2025, end_month=12,
        lever_plan=aggressive_levers
    )
    
    # Calculate KPIs for aggressive scenario
    aggressive_kpis = kpi_service.calculate_all_kpis(
        simulation_results=aggressive_results,
        simulation_duration_months=12,
        unplanned_absence=0.05,
        other_expense=100000.0
    )
    
    print("🚨 Aggressive Scenario Results:")
    print(f"   Net Sales: {aggressive_kpis.financial.net_sales:,.0f} SEK")
    print(f"   EBITDA: {aggressive_kpis.financial.ebitda:,.0f} SEK")
    print(f"   Margin: {aggressive_kpis.financial.margin:.1f}%")
    print(f"   Total Consultants: {aggressive_kpis.financial.total_consultants:,}")
    print(f"   Total FTE: {aggressive_kpis.growth.current_total_fte:,}")
    print(f"   Growth: {aggressive_kpis.growth.total_growth_percent:.1f}%")
    print("")
    
    # Compare the two scenarios
    print("🔍 Comparison Analysis:")
    print(f"   Revenue change: {aggressive_kpis.financial.net_sales - kpis.financial.net_sales:,.0f} SEK")
    print(f"   Consultant change: {aggressive_kpis.financial.total_consultants - kpis.financial.total_consultants:,}")
    print(f"   Revenue per consultant (baseline): {kpis.financial.net_sales / kpis.financial.total_consultants:,.0f} SEK")
    if aggressive_kpis.financial.total_consultants > 0:
        print(f"   Revenue per consultant (aggressive): {aggressive_kpis.financial.net_sales / aggressive_kpis.financial.total_consultants:,.0f} SEK")
    
    # Check if the issue is with data structure in aggressive scenario
    aggressive_years = sorted(aggressive_results['years'].keys())
    aggressive_last_year = aggressive_years[-1]
    aggressive_last_year_data = aggressive_results['years'][aggressive_last_year]
    
    if 'Stockholm' in aggressive_last_year_data['offices']:
        stockholm_aggressive = aggressive_last_year_data['offices']['Stockholm']
        if 'levels' in stockholm_aggressive and 'Consultant' in stockholm_aggressive['levels']:
            consultant_aggressive = stockholm_aggressive['levels']['Consultant']
            if 'A' in consultant_aggressive:
                a_aggressive = consultant_aggressive['A']
                print(f"   Aggressive A level data type: {type(a_aggressive)}")
                if isinstance(a_aggressive, list) and len(a_aggressive) > 0:
                    print(f"   Aggressive A level last entry: {a_aggressive[-1]}")

if __name__ == "__main__":
    debug_simulation_financials() 