#!/usr/bin/env python3
"""
Patch all Consultant UTRs to 0.85 in office_configuration.json
"""
import json
import os

CONFIG_PATH = os.path.join('backend', 'config', 'office_configuration.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

changed = 0
for office in data.values():
    roles = office.get('roles', {})
    consultant = roles.get('Consultant', {})
    for level in consultant.values():
        for m in range(1, 13):
            key = f'utr_{m}'
            if key in level:
                if level[key] != 0.85:
                    level[key] = 0.85
                    changed += 1
            else:
                level[key] = 0.85
                changed += 1

with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Patched all Consultant UTRs to 0.85 ({changed} fields updated)") 