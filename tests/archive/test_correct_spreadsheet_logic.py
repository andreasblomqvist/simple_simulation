#!/usr/bin/env python3
"""
Corrected test based on the user's spreadsheet that shows positive gains
I need to understand the correct interpretation of their calculation
"""

def test_correct_spreadsheet_logic():
    """Test using the correct interpretation of the user's spreadsheet"""
    
    print("📋 CORRECTED SPREADSHEET INTERPRETATION")
    print("=" * 60)
    
    # From the user's spreadsheet, I can see these values:
    # Price per hour: 1098, 1116, 1124, etc.
    # Total time: 166.4
    # Ascense: 15.7  
    # Consultant time: 150.7
    # UTR: 0.85
    # Invoiced time: 128.095
    # Revenue: 140,648.31, 142,954.02, etc. (all POSITIVE)
    # Salary base: 42,000, 46,000, 51,000, etc.
    # Social: 1.25 -> 52,500, 57,500, 63,750
    # Pension: 1.15 -> 60,375, 66,125, 73,312.50
    # Final values: 80,273.31, 76,829.02, 70,666.28 (all POSITIVE)
    
    # Let me re-examine the structure...
    # It looks like the final column shows POSITIVE values, not costs
    
    print("🔍 Looking at the user's spreadsheet more carefully:")
    print("The final column shows POSITIVE values, suggesting profit/contribution")
    print()
    
    # Test cases from what I can see in the spreadsheet
    test_cases = [
        {"price": 1098, "revenue": 140648.31, "final_value": 80273.31, "level": "A"},
        {"price": 1116, "revenue": 142954.02, "final_value": 76829.02, "level": "AC"},
        {"price": 1124, "revenue": 143978.78, "final_value": 70666.28, "level": "C"},
        {"price": 1153, "revenue": 147693.54, "final_value": 64318.54, "level": "SrC"},
        {"price": 1226, "revenue": 157044.47, "final_value": 62169.47, "level": "AM"},
        {"price": 1328, "revenue": 170110.16, "final_value": 57985.16, "level": "M"},
        {"price": 1480, "revenue": 189580.60, "final_value": 51580.60, "level": "SrM"},
        {"price": 1427, "revenue": 182791.57, "final_value": 17479.07, "level": "SrM2"},
        {"price": 1807, "revenue": 231467.67, "final_value": 53217.67, "level": "PiP"}
    ]
    
    print("📊 User's actual spreadsheet results:")
    for case in test_cases:
        level = case["level"]
        revenue = case["revenue"]
        final_value = case["final_value"]
        margin = (final_value / revenue) * 100 if revenue > 0 else 0
        
        print(f"{level:4}: {revenue:8.0f} SEK revenue -> {final_value:8.0f} SEK final ({margin:5.1f}%)")
    
    print()
    print("🎯 KEY INSIGHT: User's spreadsheet shows ALL POSITIVE results!")
    print("This means the simulation must be calculating something differently.")
    print("The issue is likely in:")
    print("1. How employment costs are calculated")
    print("2. How the revenue calculation works") 
    print("3. Some other fundamental difference in the logic")

if __name__ == "__main__":
    test_correct_spreadsheet_logic() 