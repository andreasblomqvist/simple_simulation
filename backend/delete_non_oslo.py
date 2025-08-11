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
            print(f"OK Deleted: {plan_id} - {result.get('message', 'Success')}")
            return True
        else:
            print(f"FAIL Failed to delete {plan_id}: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR Error deleting {plan_id}: {e}")
        return False

def main():
    print("=== Deleting Non-Oslo Business Plans ===\n")
    
    # Get all plans
    plans = get_all_business_plans()
    if not plans:
        print("No business plans found or error occurred")
        return
    
    print(f"Found {len(plans)} business plans")
    
    # Keep only Oslo plans and oslo_complete_business_plan
    plans_to_keep = []
    plans_to_delete = []
    
    for plan in plans:
        office_id = plan.get('office_id', '').lower()
        plan_id = plan.get('id', '')
        
        # Keep Oslo plans and the complete one we created
        if office_id == 'oslo' or plan_id == 'oslo_complete_business_plan':
            plans_to_keep.append(plan)
            print(f"KEEP: {office_id} | {plan_id[:12]}...")
        else:
            plans_to_delete.append(plan)
    
    print(f"\nKeeping {len(plans_to_keep)} plans")
    print(f"Deleting {len(plans_to_delete)} plans")
    
    if plans_to_delete:
        print(f"\nDeleting {len(plans_to_delete)} business plans...")
        
        deleted_count = 0
        for plan in plans_to_delete:
            plan_id = plan.get('id')
            office_id = plan.get('office_id', 'Unknown')
            if delete_business_plan(plan_id):
                deleted_count += 1
        
        print(f"\nOK Successfully deleted {deleted_count} out of {len(plans_to_delete)} business plans")
    else:
        print("No plans to delete")

if __name__ == "__main__":
    main()