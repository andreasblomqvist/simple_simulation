#!/usr/bin/env python3
"""
Generate a recruitment/churn summary table from simulation results JSON.
Each level has five columns: recruitment, churn, total FTE (population), % recruitment, and % churn.
Totals are also separated.
"""
import json
import csv
import os
from collections import defaultdict

RESULT_FILE = "simulation_results_20250630_161229.json"
OUTPUT_FILE = "rec_churn_summary.csv"

LEVEL_ORDER = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "Pi", "P"]


def main():
    if not os.path.exists(RESULT_FILE):
        print(f"❌ File not found: {RESULT_FILE}")
        return
    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Find the years dict
    if "years" not in data or not isinstance(data["years"], dict):
        print("❌ Could not find expected 'years' dict in result JSON.")
        return
    years = data["years"]

    # Table: {date: {level: [recruited, churned, total_fte]}}
    table = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    level_totals = defaultdict(lambda: [0, 0, 0])
    grand_total = [0, 0, 0]

    for year, year_data in years.items():
        offices = year_data.get("offices", {})
        for office_name, office in offices.items():
            levels = office.get("levels", {})
            for role_name, role_levels in levels.items():
                if isinstance(role_levels, dict):
                    for level_name, months in role_levels.items():
                        if level_name not in LEVEL_ORDER:
                            continue
                        for i, month_data in enumerate(months):
                            # Calculate correct year and month
                            base_year = int(year)
                            month_num = (i % 12) + 1
                            year_num = base_year + (i // 12)
                            date = f"{year_num}{str(month_num).zfill(2)}"
                            recruited = month_data.get("recruited", 0)
                            churned = month_data.get("churned", 0)
                            total_fte = month_data.get("total", 0)
                            table[date][level_name][0] += recruited
                            table[date][level_name][1] += churned
                            table[date][level_name][2] += total_fte
                            level_totals[level_name][0] += recruited
                            level_totals[level_name][1] += churned
                            level_totals[level_name][2] = total_fte  # Last value for totals row
                            grand_total[0] += recruited
                            grand_total[1] += churned
                            grand_total[2] += total_fte
                elif isinstance(role_levels, list):
                    # Flat role (e.g., Operations)
                    level_name = role_name if role_name in LEVEL_ORDER else None
                    if not level_name:
                        continue
                    for i, month_data in enumerate(role_levels):
                        base_year = int(year)
                        month_num = (i % 12) + 1
                        year_num = base_year + (i // 12)
                        date = f"{year_num}{str(month_num).zfill(2)}"
                        recruited = month_data.get("recruited", 0)
                        churned = month_data.get("churned", 0)
                        total_fte = month_data.get("total", 0)
                        table[date][level_name][0] += recruited
                        table[date][level_name][1] += churned
                        table[date][level_name][2] += total_fte
                        level_totals[level_name][0] += recruited
                        level_totals[level_name][1] += churned
                        level_totals[level_name][2] = total_fte  # Last value for totals row
                        grand_total[0] += recruited
                        grand_total[1] += churned
                        grand_total[2] += total_fte

    # Sort dates
    sorted_dates = sorted(table.keys())

    # Write CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["DATE"]
        for level in LEVEL_ORDER:
            header.append(f"{level}_rec")
            header.append(f"{level}_churn")
            header.append(f"{level}_fte")
            header.append(f"{level}_rec_%")
            header.append(f"{level}_churn_%")
        header += ["Total_rec", "Total_churn", "Total_fte", "Total_rec_%", "Total_churn_%"]
        writer.writerow(header)
        for date in sorted_dates:
            row = [date]
            total_rec = 0
            total_churn = 0
            total_fte = 0
            for level in LEVEL_ORDER:
                rec, churn, fte = table[date][level]
                row.append(rec)
                row.append(churn)
                row.append(fte)
                rec_pct = (rec / fte * 100) if fte else 0
                churn_pct = (churn / fte * 100) if fte else 0
                row.append(f"{rec_pct:.2f}")
                row.append(f"{churn_pct:.2f}")
                total_rec += rec
                total_churn += churn
                total_fte += fte
            total_rec_pct = (total_rec / total_fte * 100) if total_fte else 0
            total_churn_pct = (total_churn / total_fte * 100) if total_fte else 0
            row += [total_rec, total_churn, total_fte, f"{total_rec_pct:.2f}", f"{total_churn_pct:.2f}"]
            writer.writerow(row)
        # Totals row
        total_row = ["Total"]
        for level in LEVEL_ORDER:
            total_row.append(level_totals[level][0])
            total_row.append(level_totals[level][1])
            total_row.append(level_totals[level][2])
            total_row.append("")  # Leave % columns blank for totals
            total_row.append("")
        total_row += [grand_total[0], grand_total[1], grand_total[2], "", ""]
        writer.writerow(total_row)

    print(f"✅ Recruitment/churn/population summary table written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main() 