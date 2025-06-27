#!/usr/bin/env python3
"""
CAT Progression Probability Matrix Generator

This script creates a comprehensive matrix showing progression probabilities
for each level across different CAT categories and base progression rates.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config.default_config import DEFAULT_RATES

def create_cat_probability_matrix():
    """Create a comprehensive matrix of CAT progression probabilities"""
    
    # Get CAT curves from configuration
    cat_curves = DEFAULT_RATES['progression']['cat_curves']
    
    # Define base progression rates to test (in decimal)
    base_rates = [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30]
    
    # CAT categories and their tenure ranges
    cat_categories = {
        'CAT0': '0-6 months',
        'CAT6': '6-12 months', 
        'CAT12': '12-18 months',
        'CAT18': '18-24 months',
        'CAT24': '24-30 months',
        'CAT30': '30+ months'
    }
    
    print("=" * 120)
    print("CAT PROGRESSION PROBABILITY MATRIX")
    print("=" * 120)
    print()
    print("This matrix shows progression probabilities for each level across different CAT categories")
    print("and base progression rates. Probabilities are calculated as: base_rate × CAT_multiplier")
    print("(capped at 1.0 maximum probability)")
    print()
    
    # Create matrix for each level
    for level_name in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM']:
        print(f"LEVEL: {level_name}")
        print("-" * 120)
        
        # Header row
        header = f"{'Base Rate':<10}"
        for cat in cat_categories.keys():
            header += f"{cat:<15}"
        print(header)
        
        # Subheader with tenure ranges
        subheader = f"{'':<10}"
        for cat, tenure in cat_categories.items():
            subheader += f"{tenure:<15}"
        print(subheader)
        print("-" * 120)
        
        # Data rows
        for base_rate in base_rates:
            row = f"{base_rate*100:>8.1f}% "
            for cat in cat_categories.keys():
                cat_multiplier = cat_curves[level_name].get(cat, 0.0)
                probability = min(base_rate * cat_multiplier, 1.0)
                row += f"{probability*100:>13.1f}% "
            print(row)
        
        print()
        print("CAT Multipliers for this level:")
        for cat, multiplier in cat_curves[level_name].items():
            print(f"  {cat}: {multiplier}x")
        print()
        print("=" * 120)
        print()

def create_tenure_based_matrix():
    """Create a matrix showing probabilities based on actual tenure months"""
    
    print("=" * 100)
    print("TENURE-BASED PROGRESSION PROBABILITY MATRIX")
    print("=" * 100)
    print()
    print("This matrix shows progression probabilities based on actual tenure months")
    print("for different base progression rates.")
    print()
    
    # Define base progression rates to test
    base_rates = [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30]
    
    # Tenure months to test
    tenure_months = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 36, 42, 48]
    
    for level_name in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM']:
        print(f"LEVEL: {level_name}")
        print("-" * 100)
        
        # Header
        header = f"{'Base Rate':<10}"
        for months in tenure_months:
            header += f"{months:>6}mo "
        print(header)
        print("-" * 100)
        
        # Data rows
        for base_rate in base_rates:
            row = f"{base_rate*100:>8.1f}% "
            for months in tenure_months:
                # Calculate CAT category
                if months < 6:
                    cat = 'CAT0'
                else:
                    cat_number = min(30, 6 * ((months // 6)))
                    cat = f'CAT{cat_number}'
                
                # Get multiplier
                cat_multiplier = DEFAULT_RATES['progression']['cat_curves'][level_name].get(cat, 0.0)
                probability = min(base_rate * cat_multiplier, 1.0)
                row += f"{probability*100:>5.1f}% "
            print(row)
        
        print()
        print("CAT Category Mapping:")
        print("  CAT0: 0-6 months (no progression)")
        print("  CAT6: 6-12 months")
        print("  CAT12: 12-18 months") 
        print("  CAT18: 18-24 months")
        print("  CAT24: 24-30 months")
        print("  CAT30: 30+ months")
        print()
        print("=" * 100)
        print()

def create_summary_table():
    """Create a summary table showing CAT multipliers for all levels"""
    
    print("=" * 80)
    print("CAT CURVE MULTIPLIERS SUMMARY")
    print("=" * 80)
    print()
    print("This table shows the CAT curve multipliers for each level and tenure category.")
    print("These multipliers are applied to the base progression rate.")
    print()
    
    cat_curves = DEFAULT_RATES['progression']['cat_curves']
    cat_categories = ['CAT0', 'CAT6', 'CAT12', 'CAT18', 'CAT24', 'CAT30']
    
    # Header
    header = f"{'Level':<8}"
    for cat in cat_categories:
        header += f"{cat:<12}"
    print(header)
    print("-" * 80)
    
    # Data rows
    for level_name in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM']:
        row = f"{level_name:<8}"
        for cat in cat_categories:
            multiplier = cat_curves[level_name].get(cat, 0.0)
            row += f"{multiplier:<12.2f}"
        print(row)
    
    print()
    print("Interpretation:")
    print("- CAT0 (0-6 months): No progression allowed")
    print("- Higher multipliers = higher progression probability")
    print("- Multipliers are applied to base progression rate")
    print("- Final probability = base_rate × multiplier (capped at 1.0)")
    print()
    print("=" * 80)

if __name__ == "__main__":
    print("CAT Progression Probability Analysis")
    print("=" * 50)
    print()
    
    # Generate all matrices
    create_summary_table()
    print()
    create_cat_probability_matrix()
    print()
    create_tenure_based_matrix() 