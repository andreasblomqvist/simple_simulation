#!/usr/bin/env python3

import requests
import json
import time

def keep_only_two_oslo_plans():
    """Keep only 2 specific Oslo plans: one original and oslo_complete_business_plan"""
    try:
        # Get all plans
        response = requests.get("http://localhost:8000/business-plans")
        response.raise_for_status()
        plans = response.json()
        
        print(f"Found {len(plans)} total plans")
        
        # Find the plans to keep
        oslo_complete = None
        first_oslo = None
        delete_ids = []
        
        for plan in plans:
            office_id = plan.get('office_id', '')
            plan_id = plan.get('id', '')
            
            if plan_id == 'oslo_complete_business_plan':
                oslo_complete = plan
                print(f"KEEP: oslo_complete_business_plan")
            elif office_id.lower() == 'oslo' and first_oslo is None:
                first_oslo = plan
                print(f"KEEP: First Oslo plan {plan_id[:12]}...")
            else:
                delete_ids.append(plan_id)
        
        print(f"Will keep 2 plans: oslo_complete_business_plan + 1 Oslo plan")
        print(f"Will delete {len(delete_ids)} other plans")
        
        # Delete in small batches to avoid timeout
        deleted_count = 0
        batch_size = 5
        
        for i in range(0, len(delete_ids), batch_size):
            batch = delete_ids[i:i+batch_size]
            print(f"Deleting batch {i//batch_size + 1}/{(len(delete_ids) + batch_size - 1)//batch_size}")
            
            for plan_id in batch:
                try:
                    response = requests.delete(f"http://localhost:8000/business-plans/{plan_id}")
                    if response.status_code == 200:
                        deleted_count += 1
                    time.sleep(0.1)  # Small delay to prevent overwhelming the server
                except Exception as e:
                    print(f"Error deleting {plan_id}: {e}")
        
        print(f"Deleted {deleted_count} plans")
        
        # Check final result
        response = requests.get("http://localhost:8000/business-plans")
        remaining = response.json()
        print(f"Final count: {len(remaining)} plans remaining")
        
        for plan in remaining:
            office_id = plan.get('office_id', '')
            plan_id = plan.get('id', '')
            print(f"  - {office_id}: {plan_id[:20]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    keep_only_two_oslo_plans()