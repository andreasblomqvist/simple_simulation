#!/usr/bin/env python3
"""
Test script for CSV logging functionality
"""

import sys
import os
sys.path.append('.')

from backend.src.services.simulation.utils import generate_csv_logs
from backend.src.services.kpi.kpi_models import EconomicParameters
from datetime import datetime

def create_test_data():
    """Create test simulation data"""
    # Mock economic parameters
    economic_params = EconomicParameters(
        unplanned_absence=0.16,
        other_expense=19000000.0,
        employment_cost_rate=0.4,
        working_hours_per_month=166.4,
        utilization=0.85
    )
    
    # Mock yearly snapshots
    yearly_snapshots = {
        '2025': {
            'Stockholm': {
                'total_fte': 821,
                'levels': {
                    'Consultant': {
                        'A': [
                            {'total': 69, 'salary': 45000, 'price': 1200}
                        ],
                        'AC': [
                            {'total': 45, 'salary': 55000, 'price': 1300}
                        ]
                    },
                    'Operations': [
                        {'total': 12, 'salary': 40000}
                    ]
                }
            },
            'Gothenburg': {
                'total_fte': 156,
                'levels': {
                    'Consultant': {
                        'A': [
                            {'total': 23, 'salary': 45000, 'price': 1200}
                        ]
                    },
                    'Operations': [
                        {'total': 8, 'salary': 40000}
                    ]
                }
            }
        }
    }
    
    # Mock monthly office metrics
    monthly_office_metrics = {
        'Stockholm': {
            '2025-1': {'total_fte': 821, 'consultants': 114, 'operations': 12, 'sales': 0, 'recruitment': 0},
            '2025-2': {'total_fte': 845, 'consultants': 118, 'operations': 12, 'sales': 0, 'recruitment': 0}
        },
        'Gothenburg': {
            '2025-1': {'total_fte': 156, 'consultants': 23, 'operations': 8, 'sales': 0, 'recruitment': 0},
            '2025-2': {'total_fte': 162, 'consultants': 25, 'operations': 8, 'sales': 0, 'recruitment': 0}
        }
    }
    
    return yearly_snapshots, monthly_office_metrics, economic_params

def test_csv_logging():
    """Test CSV logging functionality"""
    print("Testing CSV logging functionality...")
    
    # Create test data
    yearly_snapshots, monthly_office_metrics, economic_params = create_test_data()
    
    # Generate CSV logs
    generate_csv_logs(yearly_snapshots, monthly_office_metrics, economic_params, "test_logs")
    
    # Check if files were created
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    expected_filename = f"test_logs/simulation_results_{timestamp}.csv"
    
    if os.path.exists(expected_filename):
        print("✅ CSV logs generated successfully!")
        print(f"📄 Generated file: {expected_filename}")
        
        # Show file content
        with open(expected_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"📊 File size: {len(content)} characters")
            print("📋 File content preview:")
            print("-" * 50)
            lines = content.split('\n')
            for i, line in enumerate(lines[:20]):  # Show first 20 lines
                print(line)
            if len(lines) > 20:
                print(f"... and {len(lines) - 20} more lines")
            print("-" * 50)
    else:
        print("❌ CSV logs generation failed!")
        print(f"Expected file: {expected_filename}")
        return False
    
    print("🎉 CSV logging test completed successfully!")
    return True

if __name__ == "__main__":
    test_csv_logging() 