#!/usr/bin/env python3

import requests
import json

def delete_all_except_oslo():
    """Delete all business plans except Oslo ones"""
    try:
        # Get all plans
        response = requests.get("http://localhost:8000/business-plans")
        response.raise_for_status()
        plans = response.json()
        
        print(f"Found {len(plans)} total plans")
        
        # Find plans to delete (not Oslo)
        delete_ids = []
        keep_ids = []
        
        for plan in plans:
            office_id = plan.get('office_id', '').lower()
            plan_id = plan.get('id', '')
            
            if office_id == 'oslo' or plan_id == 'oslo_complete_business_plan':
                keep_ids.append(plan_id)
            else:
                delete_ids.append(plan_id)
        
        print(f"Will keep {len(keep_ids)} Oslo plans")
        print(f"Will delete {len(delete_ids)} non-Oslo plans")
        
        # Delete in batches of 10 to avoid timeout
        deleted_count = 0
        for i, plan_id in enumerate(delete_ids):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(delete_ids)}")
            
            try:
                response = requests.delete(f"http://localhost:8000/business-plans/{plan_id}")
                if response.status_code == 200:
                    deleted_count += 1
                else:
                    print(f"Failed to delete {plan_id}")
            except Exception as e:
                print(f"Error deleting {plan_id}: {e}")
        
        print(f"Successfully deleted {deleted_count} plans")
        
        # Check final count
        response = requests.get("http://localhost:8000/business-plans")
        remaining_plans = response.json()
        print(f"Remaining plans: {len(remaining_plans)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    delete_all_except_oslo()