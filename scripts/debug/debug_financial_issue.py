#!/usr/bin/env python3
"""
Debug script to identify why simulation financial results are 26x higher than baseline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi_service import KPIService
import random

def debug_financial_calculation():
    """Debug the financial calculation discrepancy"""
    
    print("🔍 Debugging Financial Calculation Issue")
    print("=" * 60)
    
    # Seed for reproducible results
    random.seed(42)
    
    # Create engine
    engine = SimulationEngine()
    kpi_service = KPIService()
    
    print("📊 Step 1: Check Baseline Financial Calculation")
    print("-" * 40)
    
    # Calculate baseline manually using KPI service
    baseline_data = kpi_service._get_baseline_data()
    baseline_metrics = kpi_service._calculate_baseline_financial_metrics(
        baseline_data, 
        unplanned_absence=0.05, 
        other_expense=19000000.0,  # 19M SEK per month
        duration_months=12
    )
    
    print(f"Baseline Net Sales: {baseline_metrics['net_sales']:,.0f} SEK")
    print(f"Baseline EBITDA: {baseline_metrics['ebitda']:,.0f} SEK")
    print(f"Baseline Margin: {baseline_metrics['margin']:.1f}%")
    print(f"Baseline Consultants: {baseline_metrics['total_consultants']:,}")
    print("")
    
    print("📊 Step 2: Run 12-Month Simulation")
    print("-" * 40)
    
    # Run 12-month simulation with no levers
    results = engine.run_simulation(
        start_year=2025, start_month=1,
        end_year=2025, end_month=12,
        lever_plan={}  # No levers applied
    )
    
    # Calculate KPIs for simulation
    all_kpis = kpi_service.calculate_all_kpis(
        results,
        simulation_duration_months=12,
        unplanned_absence=0.05,
        other_expense=19000000.0
    )
    
    print(f"Simulation Net Sales: {all_kpis.financial.net_sales:,.0f} SEK")
    print(f"Simulation EBITDA: {all_kpis.financial.ebitda:,.0f} SEK")
    print(f"Simulation Margin: {all_kpis.financial.margin:.1f}%")
    print(f"Simulation Consultants: {all_kpis.financial.total_consultants:,}")
    print("")
    
    print("📊 Step 3: Compare Results")
    print("-" * 40)
    
    revenue_ratio = all_kpis.financial.net_sales / baseline_metrics['net_sales'] if baseline_metrics['net_sales'] > 0 else 0
    ebitda_ratio = all_kpis.financial.ebitda / baseline_metrics['ebitda'] if baseline_metrics['ebitda'] > 0 else 0
    consultant_ratio = all_kpis.financial.total_consultants / baseline_metrics['total_consultants'] if baseline_metrics['total_consultants'] > 0 else 0
    
    print(f"Revenue Ratio (Simulation/Baseline): {revenue_ratio:.1f}x")
    print(f"EBITDA Ratio (Simulation/Baseline): {ebitda_ratio:.1f}x")
    print(f"Consultant Ratio (Simulation/Baseline): {consultant_ratio:.1f}x")
    print("")
    
    if revenue_ratio > 2.0:
        print("❌ ISSUE IDENTIFIED: Simulation revenue is significantly higher than baseline!")
        print("   This suggests a calculation error in the simulation financial logic.")
    else:
        print("✅ Results look reasonable")
    
    print("📊 Step 4: Analyze Simulation Data Structure")
    print("-" * 40)
    
    # Look at the raw simulation data structure
    print(f"Simulation years: {list(results.get('years', {}).keys())}")
    
    if 'years' in results:
        for year, year_data in results['years'].items():
            print(f"\nYear {year}:")
            print(f"  Total FTE: {year_data.get('summary', {}).get('total_fte', 'N/A')}")
            print(f"  Total Consultants: {year_data.get('summary', {}).get('total_consultants', 'N/A')}")
            
            # Check if there are multiple months being counted
            offices = year_data.get('offices', {})
            print(f"  Number of offices: {len(offices)}")
            
            # Sample one office to see data structure
            if offices:
                sample_office = list(offices.keys())[0]
                office_data = offices[sample_office]
                print(f"  Sample office ({sample_office}) data keys: {list(office_data.keys())}")
                
                if 'levels' in office_data:
                    consultant_data = office_data['levels'].get('Consultant', {})
                    if consultant_data:
                        sample_level = list(consultant_data.keys())[0]
                        level_data = consultant_data[sample_level]
                        print(f"    Sample level ({sample_level}) data type: {type(level_data)}")
                        if isinstance(level_data, list):
                            print(f"    Sample level data length: {len(level_data)} (this might be the issue!)")
                            print(f"    First entry: {level_data[0] if level_data else 'Empty'}")
                            print(f"    Last entry: {level_data[-1] if level_data else 'Empty'}")

if __name__ == "__main__":
    debug_financial_calculation() 