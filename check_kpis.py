import json
import sys

# Read from stdin
data = json.load(sys.stdin)

# Extract KPIs from results
if "kpis" in data:
    kpis = data["kpis"]
    print("KPIs from scenario results:")
    for year, year_kpis in kpis.items():
        print(f"\nYear {year}:")
        for kpi_name, kpi_value in year_kpis.items():
            if kpi_value != 0:
                print(f"  {kpi_name}: {kpi_value}")
else:
    # Check for KPI data in year structure
    if "years" in data:
        for year, year_data in data["years"].items():
            print(f"\nYear {year} Office KPIs:")
            for office, office_data in year_data.get("offices", {}).items():
                kpis = office_data.get("kpis", {})
                workforce_kpis = office_data.get("workforce_kpis", {})
                financial_kpis = office_data.get("financial_kpis", {})
                
                if kpis:
                    print(f"  {office} - General KPIs:")
                    for kpi, value in kpis.items():
                        if value != 0 and value is not None:
                            print(f"    {kpi}: {value}")
                            
                if workforce_kpis:
                    print(f"  {office} - Workforce KPIs:")
                    for kpi, value in workforce_kpis.items():
                        if value != 0 and value is not None:
                            print(f"    {kpi}: {value}")
                            
                if financial_kpis:
                    print(f"  {office} - Financial KPIs:")
                    for kpi, value in financial_kpis.items():
                        if value != 0 and value is not None:
                            print(f"    {kpi}: {value}")