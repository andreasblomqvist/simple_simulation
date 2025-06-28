#!/usr/bin/env python3
"""
Verify the new configuration file with currency data
"""

import pandas as pd

# Load the configuration
df = pd.read_excel('default_office_config_20250615_210146.xlsx', sheet_name='Configuration')

print("📊 New Configuration Summary:")
print("=" * 50)
print(f"📋 Total rows: {len(df)}")
print(f"🏢 Offices: {df['Office'].nunique()}")
print(f"💰 Base Currency: {df['Base_Currency'].iloc[0]}")

print("\n🌍 Currency Distribution:")
currency_counts = df['Original_Currency'].value_counts()
for currency, count in currency_counts.items():
    print(f"  {currency}: {count} rows")

print("\n💵 Sample Pricing (A Level):")
sample = df[df['Level'] == 'A'][['Office', 'price_1', 'Original_Currency']].head(6)
for _, row in sample.iterrows():
    print(f"  {row['Office']:12} {row['price_1']:8.2f} SEK (from {row['Original_Currency']})")

print("\n📊 Price Range (price_1):")
print(f"  Min: {df['price_1'].min():.2f} SEK")
print(f"  Max: {df['price_1'].max():.2f} SEK")

# Check currency info sheet exists
try:
    currency_df = pd.read_excel('default_office_config_20250615_210146.xlsx', sheet_name='Currency_Info')
    print(f"\n✅ Currency Info sheet: {len(currency_df)} rows")
    
    summary_df = pd.read_excel('default_office_config_20250615_210146.xlsx', sheet_name='Summary')
    print(f"✅ Summary sheet: {len(summary_df)} rows")
    
except Exception as e:
    print(f"❌ Error reading additional sheets: {e}")

print("\n🎉 Configuration generated successfully with multi-currency support!") 