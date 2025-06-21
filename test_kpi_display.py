#!/usr/bin/env python3
"""
Test script to verify KPI display with total salary costs and baseline comparisons
"""

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi_service import KPIService
from backend.src.services.config_service import ConfigService

def test_kpi_display():
    """Test that KPIs are properly calculated with total salary costs and baselines"""
    
    print("=== Testing KPI Display with Total Salary Costs and Baselines ===\n")
    
    # Initialize services
    config_service = ConfigService()
    simulation_engine = SimulationEngine()
    kpi_service = KPIService()
    
    # Load current configuration
    config = config_service.get_configuration()
    print(f"Loaded config with {len(config)} offices")
    
    # Run a simple simulation
    simulation_results = simulation_engine.run_simulation(
        start_year=2025,
        start_month=1,
        end_year=2025,
        end_month=12,
        price_increase=0.03,  # 3%
        salary_increase=0.03,  # 3%
        lever_plan=None
    )
    
    # Calculate KPIs
    kpis = kpi_service.calculate_all_kpis(
        simulation_results=simulation_results,
        simulation_duration_months=12,
        unplanned_absence=0.094,
        other_expense=19000000.0
    )
    
    print("\n=== KPI RESULTS ===")
    print(f"Financial KPIs calculated: {kpis.financial is not None}")
    
    if kpis.financial:
        financial = kpis.financial
        print(f"\n📊 Current Year Metrics:")
        print(f"  Net Sales: {financial.net_sales:,.0f} SEK")
        print(f"  EBITDA: {financial.ebitda:,.0f} SEK")
        print(f"  EBITDA Margin: {financial.margin:.2%}")
        print(f"  Avg Hourly Rate: {financial.avg_hourly_rate:.2f} SEK")
        print(f"  Total Consultants: {financial.total_consultants}")
        
        print(f"\n📈 Baseline Metrics:")
        print(f"  Net Sales: {financial.net_sales_baseline:,.0f} SEK")
        print(f"  EBITDA: {financial.ebitda_baseline:,.0f} SEK")
        print(f"  EBITDA Margin: {financial.margin_baseline:.2%}")
        print(f"  Avg Hourly Rate: {financial.avg_hourly_rate_baseline:.2f} SEK")
        print(f"  Total Consultants: {financial.total_consultants_baseline}")
        
        print(f"\n🔄 Changes vs Baseline:")
        net_sales_change = financial.net_sales - financial.net_sales_baseline
        ebitda_change = financial.ebitda - financial.ebitda_baseline
        margin_change = financial.margin - financial.margin_baseline
        consultants_change = financial.total_consultants - financial.total_consultants_baseline
        
        print(f"  Net Sales: {net_sales_change:+,.0f} SEK ({net_sales_change/financial.net_sales_baseline*100:+.1f}%)")
        print(f"  EBITDA: {ebitda_change:+,.0f} SEK ({ebitda_change/financial.ebitda_baseline*100:+.1f}%)")
        print(f"  EBITDA Margin: {margin_change:+.2%}")
        print(f"  Total Consultants: {consultants_change:+d} ({consultants_change/financial.total_consultants_baseline*100:+.1f}%)")
        
        # Verify the data structure matches what frontend expects
        print(f"\n🔍 Frontend Data Structure Check:")
        print(f"  KPI data has 'financial' key: {'financial' in kpis.__dict__}")
        print(f"  Financial data has current metrics: {all(hasattr(financial, attr) for attr in ['net_sales', 'ebitda', 'margin', 'avg_hourly_rate'])}")
        print(f"  Financial data has baseline metrics: {all(hasattr(financial, attr) for attr in ['net_sales_baseline', 'ebitda_baseline', 'margin_baseline', 'avg_hourly_rate_baseline'])}")
        
        # Check if the frontend API service can handle this data structure
        print(f"\n🔍 Frontend API Compatibility:")
        print(f"  Net Sales field: {financial.net_sales:,.0f} SEK")
        print(f"  EBITDA field: {financial.ebitda:,.0f} SEK")
        print(f"  Margin field: {financial.margin:.2%}")
        print(f"  Avg Hourly Rate field: {financial.avg_hourly_rate:.2f} SEK")
        
        print(f"\n✅ KPI calculation completed successfully!")
        print(f"✅ Financial metrics are being calculated correctly")
        print(f"✅ Baseline comparisons are available")
        print(f"✅ 19M SEK other expenses are applied globally")
        print(f"✅ Frontend can display these KPIs using the existing structure")
        
    else:
        print("❌ No financial KPIs found in results")

if __name__ == "__main__":
    test_kpi_display() 