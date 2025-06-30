import csv
from collections import defaultdict, Counter

# Read the event log
events = []
with open('logs/person_events_8a579f59-cee4-441c-a62c-e07b9db54d20.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        events.append(row)

print("=== EVENT LOG ANALYSIS ===")
print(f"Total events: {len(events)}")

# Get unique people
unique_people = set(event['person_id'] for event in events)
print(f"Unique people: {len(unique_people)}")

# Get date range
dates = [event['date'] for event in events]
print(f"Date range: {min(dates)} to {max(dates)}")

# Unique months
months = sorted(set(dates))
print(f"Months covered: {months}")

# Unique offices
offices = set(event['office'] for event in events)
print(f"Unique offices: {sorted(offices)} (total: {len(offices)})")

# Count event types
event_types = Counter(event['event_type'] for event in events)
print("\nEvent types:")
for event_type, count in event_types.items():
    print(f"  {event_type}: {count}")

# Count roles
roles = Counter(event['role'] for event in events)
print("\nRoles (all events):")
for role, count in roles.items():
    print(f"  {role}: {count}")

# Get final state for each person
final_states = {}
for event in events:
    person_id = event['person_id']
    final_states[person_id] = event

# Count final roles
final_roles = Counter(final_states[person_id]['role'] for person_id in final_states)
print("\n=== FINAL EMPLOYEE COUNT BY ROLE ===")
for role, count in final_roles.items():
    print(f"  {role}: {count}")

print(f"\nTotal employees at end: {len(final_states)}")

# Check churned people
churned_people = set()
for event in events:
    if event['event_type'] == 'churn':
        churned_people.add(event['person_id'])

print(f"\nPeople who churned: {len(churned_people)}")

# People still employed (not in churned list)
still_employed = set(final_states.keys()) - churned_people
print(f"People still employed: {len(still_employed)}")

# Count by role for still employed
still_employed_by_role = Counter()
for person_id in still_employed:
    role = final_states[person_id]['role']
    still_employed_by_role[role] += 1

print("\n=== STILL EMPLOYED BY ROLE ===")
for role, count in still_employed_by_role.items():
    print(f"  {role}: {count}") 