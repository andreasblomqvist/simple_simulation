import json

# Load the simulation data
with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
    data = json.load(f)

print("Top level keys:", list(data.keys()))

for year, year_data in data['years'].items():
    print(f"\nYear: {year}")
    print("Year data keys:", list(year_data.keys()))
    
    for office, office_data in year_data['offices'].items():
        print(f"\nOffice: {office}")
        print("Office data keys:", list(office_data.keys()))
        
        print(f"\nLevels structure:")
        for role, role_data in office_data['levels'].items():
            print(f"Role: {role}, Type: {type(role_data)}")
            if isinstance(role_data, dict):
                print(f"  Keys: {list(role_data.keys())}")
            elif isinstance(role_data, list):
                print(f"  List length: {len(role_data)}")
                if len(role_data) > 0:
                    print(f"  First item keys: {list(role_data[0].keys()) if isinstance(role_data[0], dict) else 'Not a dict'}")
        break  # Only check first office
    break  # Only check first year

