#!/usr/bin/env python3
"""
Analyze simulation JSON results and print total FTE for each year.
"""
import json
import os

def main():
    result_file = "simulation_results_20250630_161229.json"
    if not os.path.exists(result_file):
        print(f"❌ File not found: {result_file}")
        return
    with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Try to find yearly FTE totals
    if "years" in data:
        years = data["years"]
    elif "results" in data and "years" in data["results"]:
        years = data["results"]["years"]
    else:
        print("❌ Could not find 'years' in result JSON.")
        return

    print("Yearly FTE Totals:")
    print("==================")
    for year in years:
        year_data = years[year]
        # Try to find total FTE for the year
        total_fte = None
        if isinstance(year_data, dict):
            # Try common keys
            for key in ["total_fte", "fte", "totalFte", "total_FTE", "fte_total"]:
                if key in year_data:
                    total_fte = year_data[key]
                    break
            # Try to sum FTEs from offices if not found
            if total_fte is None and "offices" in year_data:
                total_fte = sum(
                    office.get("total_fte", 0)
                    for office in year_data["offices"].values()
                )
        print(f"{year}: {total_fte if total_fte is not None else 'N/A'}")

if __name__ == "__main__":
    main() 