import json

# Load Oslo business plan
with open('backend/data/business_plans/oslo_actual_fte_plan.json') as f:
    plan = json.load(f)

print('FIXING OSLO BUSINESS PLAN TO INTEGER RECRUITMENT/CHURN:')
print('=' * 60)

# Convert fractional rates to proper monthly integers
# The oslo plan should recruit ~115 consultants and ~15 support per year
# That's ~10 consultants and ~1 support per month

consultant_monthly = 10  # Target: 120/year
support_monthly_total = 1  # Target: 12/year

print(f'Target: {consultant_monthly} consultants/month, {support_monthly_total} support/month')

# Fix consultant recruitment - distribute 10 across levels
consultant_distribution = {
    'A': 2,    # Entry level gets most
    'AC': 3,   # 
    'C': 3,    # Mid-levels get decent amounts  
    'SrC': 2,  #
    'AM': 0,   # Senior levels get very few
    'M': 0,    #
    'SrM': 0,  #
    'Pi': 0    # Partner level gets none
}

# Fix support recruitment - very minimal
support_distribution = {
    ('Sales', 'A'): 0,
    ('Sales', 'AC'): 0, 
    ('Sales', 'C'): 1,  # 1 every few months
    ('Recruitment', 'A'): 0,
    ('Recruitment', 'AC'): 0,
    ('Recruitment', 'C'): 0,
    ('Operations', 'General'): 0  # Very rare
}

print('\nFIXED RECRUITMENT RATES:')
print('Consultants:')
for level, count in consultant_distribution.items():
    print(f'  {level}: {count} people/month')

print('Support:')
for (role, level), count in support_distribution.items():
    print(f'  {role} {level}: {count} people/month')

total_consultant = sum(consultant_distribution.values()) 
total_support = sum(support_distribution.values())
print(f'\nTOTAL: {total_consultant} consultants + {total_support} support = {total_consultant + total_support} people/month')
print(f'ANNUAL: {total_consultant * 12} consultants + {total_support * 12} support = {(total_consultant + total_support) * 12} people/year')
print(f'RATIO: {(total_consultant/(total_consultant + total_support))*100:.1f}% consultants')