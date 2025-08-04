-- Rollback Migration: Drop Office Management Tables
-- Version: 001
-- Description: Rollback initial schema for office-specific business planning

-- Drop triggers first
DROP TRIGGER IF EXISTS update_offices_updated_at ON offices;
DROP TRIGGER IF EXISTS update_office_workforce_updated_at ON office_workforce;
DROP TRIGGER IF EXISTS update_office_business_plans_updated_at ON office_business_plans;
DROP TRIGGER IF EXISTS update_office_progressions_updated_at ON office_progressions;

-- Drop the update function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS office_progressions;
DROP TABLE IF EXISTS office_business_plans;
DROP TABLE IF EXISTS office_workforce;
DROP TABLE IF EXISTS offices;

-- Drop enum types
DROP TYPE IF EXISTS progression_curve_enum;
DROP TYPE IF EXISTS office_journey_enum;