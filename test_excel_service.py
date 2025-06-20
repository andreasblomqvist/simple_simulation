#!/usr/bin/env python3
import requests
import json

def test_excel_service_directly():
    print("🧪 Testing ExcelExportService Directly")
    print("=" * 50)
    
    try:
        # Test if we can create the service
        from backend.src.services.excel_export_service import ExcelExportService
        service = ExcelExportService()
        print("✅ ExcelExportService created successfully")
        
        # Test if we can import pandas and openpyxl
        import pandas as pd
        import openpyxl
        print("✅ Pandas and OpenPyXL imported successfully")
        
        # Test basic Excel creation
        with pd.ExcelWriter('test_simple.xlsx', engine='openpyxl') as writer:
            df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            df.to_excel(writer, sheet_name='Test', index=False)
        print("✅ Basic Excel file creation works")
        
        # Clean up
        import os
        os.unlink('test_simple.xlsx')
        print("✅ Test file cleaned up")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_service_directly() 