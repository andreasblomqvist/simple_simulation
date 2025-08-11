#!/usr/bin/env python3

import requests
import json

def get_all_business_plans():
    """Get all business plans from API"""
    try:
        response = requests.get("http://localhost:8000/business-plans")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting business plans: {e}")
        return []

def delete_business_plan(plan_id):
    """Delete a business plan by ID"""
    try:
        response = requests.delete(f"http://localhost:8000/business-plans/{plan_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Deleted: {plan_id} - {result.get('message', 'Success')}")
            return True
        else:
            print(f"✗ Failed to delete {plan_id}: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error deleting {plan_id}: {e}")
        return False

def main():
    print("=== Business Plan Deletion Tool ===\n")
    
    # Get all plans
    plans = get_all_business_plans()
    if not plans:
        print("No business plans found or error occurred")
        return
    
    print(f"Found {len(plans)} business plans:\n")
    
    # List all plans
    for i, plan in enumerate(plans, 1):
        office_id = plan.get('office_id', 'Unknown')
        plan_id = plan.get('id', 'Unknown')
        created_at = plan.get('created_at', 'Unknown')[:19]  # Just date/time part
        entries_count = len(plan.get('entries', []))
        
        print(f"{i:2d}. {office_id:12s} | {plan_id[:8]}... | {created_at} | {entries_count:2d} entries")
    
    print(f"\nOptions:")
    print(f"  'all' - Delete ALL business plans")
    print(f"  '1,3,5' - Delete specific numbers (comma-separated)")
    print(f"  'oslo' - Delete all Oslo plans")
    print(f"  'test' - Delete plans with 'test' in office_id")
    print(f"  'quit' - Exit without deleting")
    
    choice = input(f"\nWhat would you like to delete? ").strip().lower()
    
    if choice == 'quit':
        print("Exiting...")
        return
    
    plans_to_delete = []
    
    if choice == 'all':
        plans_to_delete = plans
        confirm = input(f"Are you sure you want to delete ALL {len(plans)} plans? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled.")
            return
    
    elif choice == 'oslo':
        plans_to_delete = [plan for plan in plans if plan.get('office_id', '').lower() == 'oslo']
        print(f"Found {len(plans_to_delete)} Oslo plans")
    
    elif choice == 'test':
        plans_to_delete = [plan for plan in plans if 'test' in plan.get('office_id', '').lower()]
        print(f"Found {len(plans_to_delete)} test plans")
    
    elif ',' in choice:
        # Specific numbers
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]  # Convert to 0-based
            plans_to_delete = [plans[i] for i in indices if 0 <= i < len(plans)]
            print(f"Selected {len(plans_to_delete)} plans")
        except (ValueError, IndexError) as e:
            print(f"Invalid selection: {e}")
            return
    
    else:
        print("Invalid choice")
        return
    
    if not plans_to_delete:
        print("No plans selected for deletion")
        return
    
    print(f"\nDeleting {len(plans_to_delete)} business plans...")
    
    deleted_count = 0
    for plan in plans_to_delete:
        plan_id = plan.get('id')
        office_id = plan.get('office_id', 'Unknown')
        if delete_business_plan(plan_id):
            deleted_count += 1
    
    print(f"\n✓ Successfully deleted {deleted_count} out of {len(plans_to_delete)} business plans")

if __name__ == "__main__":
    main()