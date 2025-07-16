#!/usr/bin/env python3
"""
Script to remove progression_rate field from all configuration files
as part of the unified data structures implementation.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List


def remove_progression_rate_from_dict(data: Dict[str, Any]) -> bool:
    """
    Recursively remove progression_rate field from dictionary.
    Returns True if any changes were made.
    """
    changes_made = False
    
    if isinstance(data, dict):
        # Remove progression_rate if it exists
        if 'progression_rate' in data:
            del data['progression_rate']
            changes_made = True
            print(f"  Removed progression_rate field")
        
        # Recursively process nested dictionaries
        for key, value in data.items():
            if isinstance(value, dict):
                if remove_progression_rate_from_dict(value):
                    changes_made = True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        if remove_progression_rate_from_dict(item):
                            changes_made = True
    
    return changes_made


def process_json_file(file_path: Path) -> bool:
    """
    Process a single JSON file to remove progression_rate fields.
    Returns True if file was modified.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Processing: {file_path}")
        
        changes_made = remove_progression_rate_from_dict(data)
        
        if changes_made:
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Updated {file_path}")
            return True
        else:
            print(f"  - No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error processing {file_path}: {e}")
        return False


def find_files_with_progression_rate(root_dir: Path) -> List[Path]:
    """
    Find all JSON files that contain progression_rate field.
    """
    files_with_progression_rate = []
    
    for file_path in root_dir.rglob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'progression_rate' in content:
                    files_with_progression_rate.append(file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return files_with_progression_rate


def main():
    """Main function to process all files."""
    print("🔧 Removing progression_rate fields from configuration files...")
    
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Find all JSON files with progression_rate
    files_to_process = find_files_with_progression_rate(project_root)
    
    print(f"\nFound {len(files_to_process)} files with progression_rate field:")
    for file_path in files_to_process:
        print(f"  - {file_path.relative_to(project_root)}")
    
    if not files_to_process:
        print("No files found with progression_rate field.")
        return
    
    print(f"\nProcessing {len(files_to_process)} files...")
    
    modified_count = 0
    
    for file_path in files_to_process:
        if process_json_file(file_path):
            modified_count += 1
    
    print(f"\n✅ Completed! Modified {modified_count} out of {len(files_to_process)} files.")
    
    # Also check Python files for progression_rate references
    print("\n🔍 Checking Python files for progression_rate references...")
    
    python_files_with_progression_rate = []
    for file_path in project_root.rglob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'progression_rate' in content:
                    python_files_with_progression_rate.append(file_path)
        except Exception:
            pass
    
    if python_files_with_progression_rate:
        print(f"\nFound {len(python_files_with_progression_rate)} Python files with progression_rate references:")
        for file_path in python_files_with_progression_rate:
            print(f"  - {file_path.relative_to(project_root)}")
        print("\n⚠️  These files may need manual review to remove progression_rate usage.")
    else:
        print("No Python files found with progression_rate references.")


if __name__ == "__main__":
    main()