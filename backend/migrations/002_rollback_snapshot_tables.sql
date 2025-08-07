-- Rollback Migration: Remove Population Snapshot Tables
-- Version: 002
-- Description: Rollback snapshot functionality

-- Drop views first
DROP VIEW IF EXISTS v_snapshot_workforce_comparison;
DROP VIEW IF EXISTS v_snapshot_summary;

-- Drop functions
DROP FUNCTION IF EXISTS create_snapshot_from_current(UUID, VARCHAR, TEXT, VARCHAR);
DROP FUNCTION IF EXISTS log_snapshot_usage();
DROP FUNCTION IF EXISTS ensure_single_default_snapshot();

-- Drop triggers
DROP TRIGGER IF EXISTS ensure_single_default_snapshot_trigger ON population_snapshots;
DROP TRIGGER IF EXISTS update_population_snapshots_updated_at ON population_snapshots;

-- Remove columns from existing tables
ALTER TABLE office_business_plans 
DROP COLUMN IF EXISTS baseline_snapshot_id;

-- Remove columns from scenarios if exists
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scenarios') THEN
        ALTER TABLE scenarios 
        DROP COLUMN IF EXISTS baseline_snapshot_id,
        DROP COLUMN IF EXISTS baseline_type;
    END IF;
END $$;

-- Drop tables (in reverse order of dependencies)
DROP TABLE IF EXISTS snapshot_audit_log;
DROP TABLE IF EXISTS snapshot_comparisons;
DROP TABLE IF EXISTS snapshot_tags;
DROP TABLE IF EXISTS snapshot_workforce;
DROP TABLE IF EXISTS population_snapshots;