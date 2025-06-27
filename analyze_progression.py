import pandas as pd

# Load the Excel file
def analyze_progression_excel(filename='progression_simulation.xlsx'):
    xls = pd.ExcelFile(filename)
    print(f"Sheets: {xls.sheet_names}")

    # Promotion History
    df_promos = pd.read_excel(xls, 'Promotion History')
    print(f"\nTotal promotions: {len(df_promos)}")
    print(df_promos.head())

    # Level Summary
    df_level = pd.read_excel(xls, 'Level Summary')
    print("\nLevel Summary:")
    print(df_level)

    # CAT Analysis
    if 'CAT Analysis' in xls.sheet_names:
        df_cat = pd.read_excel(xls, 'CAT Analysis')
        print("\nCAT Analysis:")
        print(df_cat)

    # Check for promotions from terminal levels
    terminal_levels = {'P', 'Pi', 'X', 'OPE'}
    terminal_promos = df_promos[df_promos['from_level'].isin(terminal_levels)]
    if not terminal_promos.empty:
        print("\nWARNING: Promotions from terminal levels detected:")
        print(terminal_promos)
    else:
        print("\nNo promotions from terminal levels detected.")

    # Quick summary table
    print("\nQuick Summary Table:")
    summary = df_promos.groupby('from_level').agg(
        promotions=('fte_id', 'count'),
        avg_months_on_level=('months_on_level', 'mean'),
        avg_probability=('probability', 'mean')
    ).reset_index()
    print(summary)

if __name__ == "__main__":
    analyze_progression_excel() 