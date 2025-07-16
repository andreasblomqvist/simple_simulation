#!/usr/bin/env python3
"""
Test script to verify churn fix
"""
from src.services.simulation_engine import SimulationEngine
from src.services.kpi import EconomicParameters
import json

# Load a test scenario
with open('data/scenarios/definitions/a11c022f-efb2-4284-8093-a104722e41d7.json', 'r') as f:
    scenario_data = json.load(f)

# Run simulation
engine = SimulationEngine()
economic_params = EconomicParameters()

# Extract time range from scenario
time_range = scenario_data.get('time_range', {
    'start_year': 2025,
    'start_month': 1,
    'end_year': 2025,
    'end_month': 8
})

results = engine.run_simulation(
    start_year=time_range['start_year'],
    start_month=time_range['start_month'],
    end_year=time_range['end_year'],
    end_month=time_range['end_month'],
    economic_params=economic_params
)

# Check first few months of churn data
print('Testing churn fix:')
print('=================')
offices = results['years']['2025']['offices']
for office_name, office_data in offices.items():
    print(f'{office_name}:')
    consultant_a = office_data['levels']['Consultant']['A']
    for i, month_data in enumerate(consultant_a[:5]):  # First 5 months
        fte = month_data['fte']
        churn_rate = month_data['churn_rate']
        churn_count = month_data['churn_count']
        expected_churn = churn_rate * fte
        print(f'  Month {i+1}: FTE={fte}, churn_rate={churn_rate:.4f}, churn_count={churn_count} (expected ~{expected_churn:.2f})')
    break  # Just show first office