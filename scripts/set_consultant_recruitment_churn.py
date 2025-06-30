#!/usr/bin/env python3
"""
Set Consultant recruitment and churn rates for all offices in office_configuration.json
"""
import json
from pathlib import Path

# New rates (monthly, decimals from screenshot)
recruitment_rates = {
    'A': 0.1730,
    'AC': 0.0530,
    'C': 0.0129,
    'SrC': 0.0027,
    'AM': 0.0009,
    'M': 0.0000,
    'SrM': 0.0000,
    'PiP': 0.0000,
    'Pi': 0.0000,
    'P': 0.0000
}
churn_rates = {
    'A': 0.0198,
    'AC': 0.0265,
    'C': 0.0230,
    'SrC': 0.0172,
    'AM': 0.0140,
    'M': 0.0112,
    'SrM': 0.0082,
    'PiP': 0.0000,
    'Pi': 0.0000,
    'P': 0.0000
}

config_path = Path('backend/config/office_configuration.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

for office, office_data in config.items():
    roles = office_data.get('roles', {})
    consultant = roles.get('Consultant', {})
    for level, level_data in consultant.items():
        if level in recruitment_rates:
            for i in range(1, 13):
                level_data[f'recruitment_{i}'] = recruitment_rates[level]
                level_data[f'churn_{i}'] = churn_rates[level]

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print('✅ Consultant recruitment and churn rates updated for all offices (screenshot rates).') 