#!/usr/bin/env python3
"""
Migration utility for converting existing data to unified data structures.

This script migrates all existing scenario files and configuration data
to use the new unified data structure format.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
import sys
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.services.data_transformation_service import DataTransformationService
from backend.src.services.data_validation_service import DataValidationService
from backend.src.services.unified_data_models import ScenarioDefinition


class MigrationUtility:
    """Utility for migrating existing data to unified structures"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.transformation_service = DataTransformationService()
        self.validation_service = DataValidationService()
        self.migration_log = []
        self.backup_dir = project_root / "data" / "backups" / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created backup directory: {self.backup_dir}")
    
    def log_migration(self, operation: str, file_path: str, status: str, details: str = ""):
        """Log a migration operation"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'file_path': file_path,
            'status': status,
            'details': details
        }
        self.migration_log.append(log_entry)
        logger.info(f"Migration: {operation} - {file_path} - {status}")
        if details:
            logger.info(f"  Details: {details}")
    
    def backup_file(self, file_path: Path) -> Path:
        """Create a backup of the file before migration"""
        try:
            relative_path = file_path.relative_to(self.project_root)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            self.log_migration("backup", str(file_path), "success", f"Backed up to {backup_path}")
            return backup_path
        except Exception as e:
            self.log_migration("backup", str(file_path), "failed", f"Error: {e}")
            raise
    
    def migrate_scenario_file(self, file_path: Path) -> bool:
        """Migrate a single scenario file to unified structure"""
        try:
            # Backup original file
            self.backup_file(file_path)
            
            # Load original data
            with open(file_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            # Check if already migrated
            if self.is_already_migrated(original_data):
                self.log_migration("migrate_scenario", str(file_path), "skipped", "Already in unified format")
                return True
            
            # Transform to unified structure
            try:
                unified_scenario = self.transformation_service.transform_legacy_scenario(original_data)
                unified_data = unified_scenario.model_dump()
            except Exception as e:
                self.log_migration("migrate_scenario", str(file_path), "failed", f"Transformation error: {e}")
                return False
            
            # Validate the transformed data
            is_valid, errors = self.validation_service.validate_complete_scenario(unified_data)
            if not is_valid:
                self.log_migration("migrate_scenario", str(file_path), "failed", f"Validation errors: {errors}")
                return False
            
            # Write the migrated data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(unified_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.log_migration("migrate_scenario", str(file_path), "success", "Migrated to unified structure")
            return True
            
        except Exception as e:
            self.log_migration("migrate_scenario", str(file_path), "error", f"Unexpected error: {e}")
            return False
    
    def is_already_migrated(self, data: Dict[str, Any]) -> bool:
        """Check if data is already in unified format"""
        # Check for unified structure indicators
        unified_indicators = [
            # Has proper baseline_input structure
            data.get('baseline_input', {}).get('global') is not None,
            # No deprecated fields
            'progression_rate' not in json.dumps(data),
            # Has proper time_range structure
            isinstance(data.get('time_range'), dict) and all(
                key in data['time_range'] 
                for key in ['start_year', 'start_month', 'end_year', 'end_month']
            ),
            # Has proper economic_params structure
            isinstance(data.get('economic_params'), dict)
        ]
        
        # If most indicators are present, consider it migrated
        return sum(unified_indicators) >= 3
    
    def migrate_all_scenario_files(self) -> Dict[str, int]:
        """Migrate all scenario files in the project"""
        scenarios_dir = self.project_root / "data" / "scenarios" / "definitions"
        
        if not scenarios_dir.exists():
            logger.warning(f"Scenarios directory not found: {scenarios_dir}")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
        
        scenario_files = list(scenarios_dir.glob("*.json"))
        logger.info(f"Found {len(scenario_files)} scenario files to migrate")
        
        results = {"total": len(scenario_files), "success": 0, "failed": 0, "skipped": 0}
        
        for file_path in scenario_files:
            success = self.migrate_scenario_file(file_path)
            if success:
                # Check if it was actually migrated or skipped
                last_log = self.migration_log[-1] if self.migration_log else {}
                if last_log.get('status') == 'skipped':
                    results["skipped"] += 1
                else:
                    results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def migrate_configuration_files(self) -> Dict[str, int]:
        """Migrate configuration files to unified structure"""
        config_dir = self.project_root / "backend" / "config"
        
        if not config_dir.exists():
            logger.warning(f"Config directory not found: {config_dir}")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
        
        config_files = list(config_dir.glob("*.json"))
        logger.info(f"Found {len(config_files)} configuration files to migrate")
        
        results = {"total": len(config_files), "success": 0, "failed": 0, "skipped": 0}
        
        for file_path in config_files:
            success = self.migrate_config_file(file_path)
            if success:
                last_log = self.migration_log[-1] if self.migration_log else {}
                if last_log.get('status') == 'skipped':
                    results["skipped"] += 1
                else:
                    results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def migrate_config_file(self, file_path: Path) -> bool:
        """Migrate a single configuration file"""
        try:
            # Backup original file
            self.backup_file(file_path)
            
            # Load original data
            with open(file_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            # Remove deprecated fields
            modified = False
            
            # Remove progression_rate fields
            if self.remove_progression_rate_recursive(original_data):
                modified = True
            
            # Standardize field names
            if self.standardize_config_field_names(original_data):
                modified = True
            
            if not modified:
                self.log_migration("migrate_config", str(file_path), "skipped", "No changes needed")
                return True
            
            # Write the modified data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(original_data, f, indent=2, ensure_ascii=False)
            
            self.log_migration("migrate_config", str(file_path), "success", "Updated configuration")
            return True
            
        except Exception as e:
            self.log_migration("migrate_config", str(file_path), "error", f"Unexpected error: {e}")
            return False
    
    def remove_progression_rate_recursive(self, data: Any) -> bool:
        """Recursively remove progression_rate fields"""
        modified = False
        
        if isinstance(data, dict):
            if 'progression_rate' in data:
                del data['progression_rate']
                modified = True
            
            for key, value in data.items():
                if self.remove_progression_rate_recursive(value):
                    modified = True
        
        elif isinstance(data, list):
            for item in data:
                if self.remove_progression_rate_recursive(item):
                    modified = True
        
        return modified
    
    def standardize_config_field_names(self, data: Any) -> bool:
        """Standardize field names in configuration data"""
        modified = False
        
        if isinstance(data, dict):
            # Field name mappings
            field_mappings = {
                'Price_1': 'price_1',
                'Price_2': 'price_2',
                'Price_3': 'price_3',
                'Price_4': 'price_4',
                'Price_5': 'price_5',
                'Price_6': 'price_6',
                'Price_7': 'price_7',
                'Price_8': 'price_8',
                'Price_9': 'price_9',
                'Price_10': 'price_10',
                'Price_11': 'price_11',
                'Price_12': 'price_12',
            }
            
            # Apply field mappings
            for old_name, new_name in field_mappings.items():
                if old_name in data:
                    data[new_name] = data.pop(old_name)
                    modified = True
            
            # Recursively process nested structures
            for key, value in data.items():
                if self.standardize_config_field_names(value):
                    modified = True
        
        elif isinstance(data, list):
            for item in data:
                if self.standardize_config_field_names(item):
                    modified = True
        
        return modified
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate a comprehensive migration report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'backup_directory': str(self.backup_dir),
            'migration_summary': {
                'total_operations': len(self.migration_log),
                'successful_operations': len([log for log in self.migration_log if log['status'] == 'success']),
                'failed_operations': len([log for log in self.migration_log if log['status'] == 'failed']),
                'skipped_operations': len([log for log in self.migration_log if log['status'] == 'skipped'])
            },
            'operations_by_type': {},
            'failed_operations': [log for log in self.migration_log if log['status'] == 'failed'],
            'detailed_log': self.migration_log
        }
        
        # Group operations by type
        operation_types = {}
        for log in self.migration_log:
            op_type = log['operation']
            if op_type not in operation_types:
                operation_types[op_type] = {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}
            operation_types[op_type]['total'] += 1
            operation_types[op_type][log['status']] += 1
        
        report['operations_by_type'] = operation_types
        
        return report
    
    def save_migration_report(self, report: Dict[str, Any]):
        """Save migration report to file"""
        report_path = self.backup_dir / "migration_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Migration report saved to: {report_path}")
    
    def run_full_migration(self) -> Dict[str, Any]:
        """Run complete migration process"""
        logger.info("Starting full migration to unified data structures...")
        
        # Migrate scenario files
        logger.info("Migrating scenario files...")
        scenario_results = self.migrate_all_scenario_files()
        
        # Migrate configuration files
        logger.info("Migrating configuration files...")
        config_results = self.migrate_configuration_files()
        
        # Generate and save report
        report = self.generate_migration_report()
        self.save_migration_report(report)
        
        # Print summary
        logger.info("Migration completed!")
        logger.info(f"Scenario files: {scenario_results['success']} success, {scenario_results['failed']} failed, {scenario_results['skipped']} skipped")
        logger.info(f"Config files: {config_results['success']} success, {config_results['failed']} failed, {config_results['skipped']} skipped")
        logger.info(f"Backup directory: {self.backup_dir}")
        
        return report


def main():
    """Main function to run the migration"""
    print("🚀 Starting migration to unified data structures...")
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Create migration utility
    migration_util = MigrationUtility(project_root)
    
    # Run migration
    try:
        report = migration_util.run_full_migration()
        
        # Print final summary
        print("\n✅ Migration completed successfully!")
        print(f"📊 Summary:")
        print(f"  Total operations: {report['migration_summary']['total_operations']}")
        print(f"  Successful: {report['migration_summary']['successful_operations']}")
        print(f"  Failed: {report['migration_summary']['failed_operations']}")
        print(f"  Skipped: {report['migration_summary']['skipped_operations']}")
        print(f"📁 Backup directory: {report['backup_directory']}")
        
        if report['migration_summary']['failed_operations'] > 0:
            print("\n⚠️  Some operations failed. Check the migration report for details.")
            for failed_op in report['failed_operations']:
                print(f"  - {failed_op['operation']}: {failed_op['file_path']} - {failed_op['details']}")
        
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        logger.error(f"Migration failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())