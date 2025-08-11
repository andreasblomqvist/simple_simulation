import json

with open('backend/data/business_plans/oslo_actual_fte_plan.json') as f:
    plan = json.load(f)

consultant_total = 0
support_total = 0

print('OSLO BUSINESS PLAN RECRUITMENT RATES:')
print('CONSULTANTS:')
for entry in plan['entries']:
    role = entry['role']
    if role == 'Consultant':
        recruitment = entry['recruitment']
        consultant_total += recruitment
        print(f'  {entry["level"]}: {recruitment}')

print(f'CONSULTANT TOTAL: {consultant_total} people/month')

print('\nSUPPORT STAFF:')
for entry in plan['entries']:
    role = entry['role']
    if role != 'Consultant':
        recruitment = entry['recruitment'] 
        support_total += recruitment
        print(f'  {role} {entry["level"]}: {recruitment}')
        
print(f'SUPPORT TOTAL: {support_total} people/month')

total = consultant_total + support_total
print(f'\nPER-MONTH RECRUITMENT BREAKDOWN:')
print(f'  Consultants: {consultant_total} ({(consultant_total/total)*100:.1f}%)')
print(f'  Support: {support_total} ({(support_total/total)*100:.1f}%)')

print(f'\nPER-YEAR RECRUITMENT PROJECTION (x12 months):')
print(f'  Consultants: {consultant_total * 12} people')
print(f'  Support: {support_total * 12} people')
print(f'  Total: {total * 12} people')