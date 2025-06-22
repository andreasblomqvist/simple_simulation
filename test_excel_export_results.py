#!/usr/bin/env python3
"""
Test script to run a simulation and export results to Excel for examination
"""

import sys
import os
import requests
import tempfile
import pandas as pd
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Backend URL
BACKEND_URL = "http://localhost:8000"

def test_simulation_and_excel_export():
    """Run a simulation and export to Excel for examination"""
    
    print("🚀 Testing Simulation and Excel Export")
    print("=" * 50)
    
    # 1. Test simulation parameters
    simulation_params = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2027,
        "end_month": 12,
        "price_increase": 0.025,  # 2.5% annual
        "salary_increase": 0.03,  # 3% annual
        "unplanned_absence": 0.05,  # 5%
        "hy_working_hours": 166.4,
        "other_expense": 100000.0
    }
    
    print(f"📊 Simulation Parameters:")
    for key, value in simulation_params.items():
        print(f"   {key}: {value}")
    
    try:
        # 2. Run simulation
        print(f"\n1. Running simulation...")
        response = requests.post(
            f"{BACKEND_URL}/simulation/run",
            json=simulation_params,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ Simulation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
        simulation_results = response.json()
        print("✅ Simulation completed successfully")
        
        # 3. Test Excel export
        print(f"\n2. Testing Excel export...")
        export_response = requests.post(
            f"{BACKEND_URL}/simulation/export/excel",
            json=simulation_params,
            headers={"Content-Type": "application/json"}
        )
        
        if export_response.status_code != 200:
            print(f"❌ Excel export failed: {export_response.status_code}")
            print(f"Error: {export_response.text}")
            return False
            
        # 4. Save Excel file for analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"simulation_export_{timestamp}.xlsx"
        
        with open(excel_filename, 'wb') as f:
            f.write(export_response.content)
            
        print(f"✅ Excel file generated: {excel_filename}")
        print(f"📊 File size: {len(export_response.content)} bytes")
        
        # 5. Analyze Excel file structure
        print(f"\n3. Analyzing Excel file structure...")
        analyze_excel_file(excel_filename)
        
        # 6. Show sample data from each sheet
        print(f"\n4. Sample data from each sheet:")
        show_sample_data(excel_filename)
        
        print(f"\n✅ Analysis complete! Excel file saved as: {excel_filename}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_excel_file(filename):
    """Analyze the structure of the Excel file"""
    try:
        with pd.ExcelFile(filename) as excel_file:
            print(f"📋 Excel file contains {len(excel_file.sheet_names)} sheets:")
            
            for i, sheet_name in enumerate(excel_file.sheet_names, 1):
                df = pd.read_excel(excel_file, sheet_name)
                print(f"   {i}. {sheet_name}: {len(df)} rows × {len(df.columns)} columns")
                
                # Show column names for first few sheets
                if i <= 3:
                    print(f"      Columns: {list(df.columns)}")
                    
    except Exception as e:
        print(f"❌ Error analyzing Excel file: {e}")

def show_sample_data(filename):
    """Show sample data from each sheet"""
    try:
        with pd.ExcelFile(filename) as excel_file:
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name)
                
                print(f"\n📊 {sheet_name} Sheet:")
                print(f"   Shape: {df.shape}")
                
                if not df.empty:
                    print(f"   First 3 rows:")
                    print(df.head(3).to_string(index=False))
                else:
                    print(f"   (Empty sheet)")
                    
                print("-" * 40)
                
    except Exception as e:
        print(f"❌ Error showing sample data: {e}")

if __name__ == "__main__":
    test_simulation_and_excel_export() 