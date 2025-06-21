#!/usr/bin/env python3
"""
Test script to validate Excel export functionality and cross-check data accuracy
"""

import requests
import json
import pandas as pd
import tempfile
import os
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_simulation_and_export():
    """Test the complete simulation and Excel export flow"""
    
    print("🧪 Testing Simulation and Excel Export Functionality")
    print("=" * 60)
    
    # 1. Test simulation endpoint
    print("\n1. Running simulation...")
    simulation_params = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2027,
        "end_month": 12,
        "price_increase": 0.02,  # 2%
        "salary_increase": 0.02,  # 2%
        "unplanned_absence": 0.05,  # 5%
        "hy_working_hours": 166.4,
        "other_expense": 100000.0
    }
    
    try:
        # Run simulation
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
        
        # 2. Test Excel export endpoint
        print("\n2. Testing Excel export...")
        export_response = requests.post(
            f"{BACKEND_URL}/simulation/export/excel",
            json=simulation_params,
            headers={"Content-Type": "application/json"}
        )
        
        if export_response.status_code != 200:
            print(f"❌ Excel export failed: {export_response.status_code}")
            print(f"Error: {export_response.text}")
            return False
            
        # Save Excel file for analysis
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file.write(export_response.content)
            excel_path = temp_file.name
            
        print(f"✅ Excel file generated: {excel_path}")
        
        # 3. Validate Excel file structure and content
        print("\n3. Validating Excel file structure...")
        if not validate_excel_structure(excel_path):
            return False
            
        # 4. Cross-check data accuracy
        print("\n4. Cross-checking data accuracy...")
        if not cross_check_data_accuracy(excel_path, simulation_results):
            return False
            
        # 5. Clean up
        os.unlink(excel_path)
        print(f"\n✅ All tests passed! Excel file cleaned up.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def validate_excel_structure(excel_path):
    """Validate that the Excel file has the correct structure"""
    
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(excel_path)
        
        # Check required sheets
        required_sheets = [
            'Summary',
            'Financial_KPIs', 
            'Office_Details',
            'Journey_Analysis',
            'Movement_Logs',
            'Baseline_Comparison'
        ]
        
        print(f"📊 Excel file contains {len(excel_file.sheet_names)} sheets")
        print(f"📋 Sheet names: {excel_file.sheet_names}")
        
        missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_file.sheet_names]
        if missing_sheets:
            print(f"❌ Missing required sheets: {missing_sheets}")
            return False
            
        print("✅ All required sheets present")
        
        # Check each sheet for basic structure
        for sheet_name in required_sheets:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"   📄 {sheet_name}: {len(df)} rows, {len(df.columns)} columns")
            
            # Basic validation for each sheet
            if sheet_name == 'Summary':
                if 'Metric' not in df.columns or 'Current' not in df.columns:
                    print(f"❌ Summary sheet missing required columns")
                    return False
                    
            elif sheet_name == 'Financial_KPIs':
                if 'Year' not in df.columns or 'Net Sales' not in df.columns:
                    print(f"❌ Financial_KPIs sheet missing required columns")
                    return False
                    
            elif sheet_name == 'Office_Details':
                if 'Year' not in df.columns or 'Office' not in df.columns:
                    print(f"❌ Office_Details sheet missing required columns")
                    return False
                    
            elif sheet_name == 'Journey_Analysis':
                if 'Year' not in df.columns or 'Journey 1 Total' not in df.columns:
                    print(f"❌ Journey_Analysis sheet missing required columns")
                    return False
                    
            elif sheet_name == 'Movement_Logs':
                if 'Year' not in df.columns or 'Month' not in df.columns:
                    print(f"❌ Movement_Logs sheet missing required columns")
                    return False
                    
            elif sheet_name == 'Baseline_Comparison':
                if 'Year' not in df.columns or 'Net Sales vs Baseline (%)' not in df.columns:
                    print(f"❌ Baseline_Comparison sheet missing required columns")
                    return False
        
        print("✅ All sheets have correct structure")
        return True
        
    except Exception as e:
        print(f"❌ Excel validation failed: {e}")
        return False

def cross_check_data_accuracy(excel_path, simulation_results):
    """Cross-check data between Excel export and simulation results"""
    
    try:
        print("🔍 Cross-checking data accuracy...")
        
        # Read Excel sheets
        summary_df = pd.read_excel(excel_path, 'Summary')
        financial_df = pd.read_excel(excel_path, 'Financial_KPIs')
        office_df = pd.read_excel(excel_path, 'Office_Details')
        journey_df = pd.read_excel(excel_path, 'Journey_Analysis')
        
        # Check Summary sheet data
        print("\n   📊 Checking Summary sheet...")
        total_fte_row = summary_df[summary_df['Metric'] == 'Total FTE']
        if not total_fte_row.empty:
            excel_total_fte = total_fte_row['Current'].iloc[0]
            print(f"      Excel Total FTE: {excel_total_fte}")
            
            # Compare with simulation results
            if 'kpis' in simulation_results and 'growth' in simulation_results['kpis']:
                sim_total_fte = simulation_results['kpis']['growth'].get('current_total_fte', 0)
                print(f"      Simulation Total FTE: {sim_total_fte}")
                
                if abs(excel_total_fte - sim_total_fte) < 1:  # Allow small rounding differences
                    print("      ✅ Total FTE matches")
                else:
                    print(f"      ❌ Total FTE mismatch: {excel_total_fte} vs {sim_total_fte}")
                    return False
        
        # Check Financial KPIs
        print("\n   💰 Checking Financial KPIs...")
        if not financial_df.empty:
            latest_year = financial_df['Year'].max()
            year_data = financial_df[financial_df['Year'] == latest_year]
            
            if not year_data.empty:
                excel_net_sales = year_data['Net Sales'].iloc[0]
                excel_ebitda = year_data['EBITDA'].iloc[0]
                print(f"      Excel Net Sales ({latest_year}): {excel_net_sales:,.0f}")
                print(f"      Excel EBITDA ({latest_year}): {excel_ebitda:,.0f}")
                
                # Compare with simulation results
                if 'years' in simulation_results and str(latest_year) in simulation_results['years']:
                    year_kpis = simulation_results['years'][str(latest_year)].get('kpis', {})
                    if 'financial' in year_kpis:
                        sim_net_sales = year_kpis['financial'].get('net_sales', 0)
                        sim_ebitda = year_kpis['financial'].get('ebitda', 0)
                        print(f"      Simulation Net Sales: {sim_net_sales:,.0f}")
                        print(f"      Simulation EBITDA: {sim_ebitda:,.0f}")
                        
                        # Check for reasonable agreement (within 1%)
                        if abs(excel_net_sales - sim_net_sales) / max(sim_net_sales, 1) < 0.01:
                            print("      ✅ Net Sales matches")
                        else:
                            print(f"      ❌ Net Sales mismatch: {excel_net_sales:,.0f} vs {sim_net_sales:,.0f}")
                            return False
                            
                        if abs(excel_ebitda - sim_ebitda) / max(sim_ebitda, 1) < 0.01:
                            print("      ✅ EBITDA matches")
                        else:
                            print(f"      ❌ EBITDA mismatch: {excel_ebitda:,.0f} vs {sim_ebitda:,.0f}")
                            return False
        
        # Check Office Details
        print("\n   🏢 Checking Office Details...")
        if not office_df.empty:
            office_count = office_df['Office'].nunique()
            print(f"      Excel Office Count: {office_count}")
            
            # Compare with simulation results
            if 'years' in simulation_results:
                first_year = list(simulation_results['years'].keys())[0]
                sim_office_count = len(simulation_results['years'][first_year].get('offices', {}))
                print(f"      Simulation Office Count: {sim_office_count}")
                
                if office_count == sim_office_count:
                    print("      ✅ Office count matches")
                else:
                    print(f"      ❌ Office count mismatch: {office_count} vs {sim_office_count}")
                    return False
        
        # Check Journey Analysis
        print("\n   📈 Checking Journey Analysis...")
        if not journey_df.empty:
            latest_year = journey_df['Year'].max()
            year_data = journey_df[journey_df['Year'] == latest_year]
            
            if not year_data.empty:
                journey1_total = year_data['Journey 1 Total'].iloc[0]
                journey2_total = year_data['Journey 2 Total'].iloc[0]
                print(f"      Excel Journey 1 ({latest_year}): {journey1_total}")
                print(f"      Excel Journey 2 ({latest_year}): {journey2_total}")
                
                # Basic validation - journey totals should be reasonable
                if journey1_total >= 0 and journey2_total >= 0:
                    print("      ✅ Journey totals are reasonable")
                else:
                    print(f"      ❌ Invalid journey totals: {journey1_total}, {journey2_total}")
                    return False
        
        print("✅ All data cross-checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Data cross-check failed: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    
    print("\n🧪 Testing Error Handling")
    print("=" * 40)
    
    # Test 1: Export without running simulation first
    print("\n1. Testing export without simulation...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/simulation/export/excel",
            json={"start_year": 2025, "end_year": 2025},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 500:
            print("✅ Correctly handled export without simulation")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    # Test 2: Invalid parameters
    print("\n2. Testing invalid parameters...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/simulation/export/excel",
            json={"invalid": "parameters"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [400, 422, 500]:
            print("✅ Correctly handled invalid parameters")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting Excel Export Validation Tests")
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run main test
    success = test_simulation_and_export()
    
    # Run error handling tests
    test_error_handling()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 ALL TESTS PASSED! Excel export functionality is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! Please check the implementation.")
    
    print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 