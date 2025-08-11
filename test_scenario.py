#!/usr/bin/env python3
import requests
import json

# Read scenario definition
with open(r'C:\Users\andre\Code\SimpleSim\backend\data\scenarios\definitions\4346a731-90a1-4455-9c19-5994bfcd9b00.json', 'r') as f:
    scenario_def = json.load(f)

# Create request payload
payload = {
    "scenario_definition": scenario_def
}

# Run the scenario
response = requests.post(
    "http://localhost:8000/scenarios/run",
    headers={"Content-Type": "application/json"},
    json=payload
)

if response.status_code == 200:
    results = response.json()
    
    # Check the price and salary values
    try:
        consultant_a = results['results']['years']['2025']['offices']['Oslo']['roles']['Consultant']['levels']['A'][0]
        print(f"✅ SUCCESS! New values:")
        print(f"Price: {consultant_a['price']:,.0f} NOK")
        print(f"Salary: {consultant_a['salary']:,.0f} NOK")
        print(f"FTE: {consultant_a['fte']}")
        
        # Show expected vs actual
        print(f"\n📊 Expected from business plan:")
        print(f"Price: 1,128 NOK (hourly)")
        print(f"Salary: 40,000 NOK (monthly)")
        
        # Check if the values are correct
        if abs(consultant_a['price'] - 1128) < 10:
            print("✅ Price is CORRECT!")
        else:
            print(f"❌ Price is WRONG: {consultant_a['price']} should be 1128")
            
        if abs(consultant_a['salary'] - 40000) < 100:
            print("✅ Salary is CORRECT!")
        else:
            print(f"❌ Salary is WRONG: {consultant_a['salary']} should be 40000")
            
    except KeyError as e:
        print(f"❌ Error accessing results: {e}")
        print("Response:", json.dumps(results, indent=2)[:1000])
        
else:
    print(f"❌ Error {response.status_code}: {response.text}")