from backend.src.services.business_plan_processor_v2 import BusinessPlanProcessorV2
from backend.src.services.business_plan_storage import BusinessPlanStorage

# Load Oslo business plan
bp_storage = BusinessPlanStorage()
oslo_plan = bp_storage.get_plan('oslo_actual_fte_plan')

# Process through business plan processor
processor = BusinessPlanProcessorV2()
processor.load_business_plan('Oslo', oslo_plan)

# Get monthly targets for January 2025
targets = processor.get_monthly_targets('Oslo', 2025, 1)

print('MONTHLY TARGETS FROM BUSINESS PLAN PROCESSOR:')
print('=' * 50)
print('RECRUITMENT TARGETS:')
for role, levels in targets.recruitment_targets.items():
    print(f'  {role}:')
    role_total = 0
    for level, count in levels.items():
        print(f'    {level}: {count} people/month')
        role_total += count
    print(f'    ROLE TOTAL: {role_total} people/month')

total_recruitment = sum(sum(levels.values()) for levels in targets.recruitment_targets.values())
print(f'TOTAL RECRUITMENT: {total_recruitment} people/month')

# Verify vs raw plan
consultant_sum = sum(entry['recruitment'] for entry in oslo_plan['entries'] if entry['role'] == 'Consultant')
support_sum = sum(entry['recruitment'] for entry in oslo_plan['entries'] if entry['role'] != 'Consultant')
print(f'\nVERIFICATION VS RAW PLAN:')
print(f'  Raw consultant recruitment: {consultant_sum}')
print(f'  Raw support recruitment: {support_sum}')
print(f'  Raw total: {consultant_sum + support_sum}')

print(f'\nCHURN TARGETS:')
for role, levels in targets.churn_targets.items():
    role_total = sum(levels.values())
    if role_total > 0:
        print(f'  {role}: {role_total} people/month')