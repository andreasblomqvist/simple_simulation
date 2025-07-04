#!/usr/bin/env python3
"""
Test script for JSON export functionality.
This script tests the comprehensive JSON export without modifying existing logic.
"""

import sys
import os
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.json_export_service import JSONExportService
from backend.src.services.kpi import EconomicParameters

def test_json_export():
    """Test the JSON export functionality"""
    print("🧪 Testing JSON Export Functionality")
    print("=" * 50)
    
    try:
        # Initialize simulation engine
        print("1. Initializing simulation engine...")
        engine = SimulationEngine()
        print("✅ Simulation engine initialized")
        
        # Create economic parameters
        print("2. Creating economic parameters...")
        economic_params = EconomicParameters(
            unplanned_absence=0.05,
            working_hours_per_month=166.4,
            other_expense=120000.0,
            employment_cost_rate=0.34,
            utilization=0.85
        )
        print("✅ Economic parameters created")
        
        # Run a simple simulation
        print("3. Running simulation...")
        results = engine.run_simulation(
            start_year=2025,
            start_month=1,
            end_year=2027,
            end_month=12,
            price_increase=0.02,
            salary_increase=0.03,
            economic_params=economic_params
        )
        print("✅ Simulation completed")
        
        # Test JSON export
        print("4. Testing JSON export...")
        json_export_service = JSONExportService()
        
        # Create scenario metadata
        scenario_metadata = {
            "scenario_name": "Test Scenario",
            "scenario_description": "Test scenario for JSON export validation",
            "created_by": "Test Script",
            "test_run": True
        }
        
        # Generate comprehensive JSON
        comprehensive_results = json_export_service.export_simulation_results(
            simulation_results=results,
            scenario_metadata=scenario_metadata,
            output_path="test_comprehensive_export.json"
        )
        print("✅ JSON export completed")
        
        # Validate the structure
        print("5. Validating JSON structure...")
        required_sections = [
            "metadata",
            "simulation_period", 
            "configuration",
            "time_series_data",
            "summary_metrics",
            "event_data",
            "kpi_data",
            "office_analysis",
            "level_analysis",
            "journey_analysis",
            "movement_analysis"
        ]
        
        for section in required_sections:
            if section in comprehensive_results:
                print(f"   ✅ {section}: Present")
            else:
                print(f"   ❌ {section}: Missing")
                return False
        
        # Check specific data points
        print("6. Validating data content...")
        
        # Check metadata
        metadata = comprehensive_results.get("metadata", {})
        if metadata.get("export_timestamp"):
            print("   ✅ Export timestamp: Present")
        else:
            print("   ❌ Export timestamp: Missing")
        
        # Check simulation period
        sim_period = comprehensive_results.get("simulation_period", {})
        if sim_period.get("start") and sim_period.get("end"):
            print("   ✅ Simulation period: Present")
        else:
            print("   ❌ Simulation period: Missing")
        
        # Check time series data
        time_series = comprehensive_results.get("time_series_data", {})
        yearly_data = time_series.get("yearly_data", {})
        if yearly_data:
            print(f"   ✅ Yearly data: {len(yearly_data)} years")
        else:
            print("   ❌ Yearly data: Missing")
        
        # Check summary metrics
        summary = comprehensive_results.get("summary_metrics", {})
        if summary.get("headcount_summary"):
            print("   ✅ Headcount summary: Present")
        else:
            print("   ❌ Headcount summary: Missing")
        
        # Check event data
        event_data = comprehensive_results.get("event_data", {})
        if event_data.get("available") is not None:
            print("   ✅ Event data: Present")
        else:
            print("   ❌ Event data: Missing")
        
        print("\n📊 JSON Export Summary:")
        print(f"   📁 Output file: test_comprehensive_export.json")
        print(f"   📏 File size: {os.path.getsize('test_comprehensive_export.json')} bytes")
        print(f"   📅 Export time: {metadata.get('export_timestamp', 'Unknown')}")
        print(f"   🎯 Scenario: {scenario_metadata.get('scenario_name', 'Unknown')}")
        
        # Show a sample of the data structure
        print("\n📋 Sample Data Structure:")
        print(json.dumps({
            "metadata": comprehensive_results["metadata"],
            "simulation_period": comprehensive_results["simulation_period"],
            "summary_metrics": comprehensive_results["summary_metrics"]
        }, indent=2)[:1000] + "...")
        
        print("\n✅ JSON Export Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ JSON Export Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_export()
    sys.exit(0 if success else 1) 