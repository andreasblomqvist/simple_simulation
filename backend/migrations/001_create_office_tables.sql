-- Migration: Create Office Management Tables
-- Version: 001
-- Description: Initial schema for office-specific business planning and configuration

-- Create enum types
CREATE TYPE office_journey_enum AS ENUM ('emerging', 'established', 'mature');
CREATE TYPE progression_curve_enum AS ENUM ('linear', 'exponential', 'custom');

-- ================================================
-- OFFICES TABLE
-- ================================================
CREATE TABLE offices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    journey office_journey_enum NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    economic_parameters JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX idx_offices_journey ON offices(journey);
CREATE INDEX idx_offices_name ON offices(name);

-- ================================================
-- OFFICE WORKFORCE DISTRIBUTIONS
-- ================================================
CREATE TABLE office_workforce (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    office_id UUID NOT NULL REFERENCES offices(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    role VARCHAR(50) NOT NULL,
    level VARCHAR(10) NOT NULL,
    fte INTEGER NOT NULL DEFAULT 0 CHECK (fte >= 0),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(office_id, start_date, role, level)
);

-- Add indexes for workforce queries
CREATE INDEX idx_office_workforce_office_id ON office_workforce(office_id);
CREATE INDEX idx_office_workforce_role_level ON office_workforce(role, level);
CREATE INDEX idx_office_workforce_start_date ON office_workforce(start_date);

-- ================================================
-- OFFICE BUSINESS PLANS
-- ================================================
CREATE TABLE office_business_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    office_id UUID NOT NULL REFERENCES offices(id) ON DELETE CASCADE,
    year INTEGER NOT NULL CHECK (year >= 2020 AND year <= 2050),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    role VARCHAR(50) NOT NULL,
    level VARCHAR(10) NOT NULL,
    
    -- Core business plan parameters
    recruitment INTEGER DEFAULT 0 CHECK (recruitment >= 0),
    churn INTEGER DEFAULT 0 CHECK (churn >= 0),
    price DECIMAL(10,2) CHECK (price >= 0),
    utr DECIMAL(3,2) CHECK (utr BETWEEN 0 AND 1),
    salary DECIMAL(10,2) CHECK (salary >= 0),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(office_id, year, month, role, level)
);

-- Add indexes for business plan queries
CREATE INDEX idx_business_plans_office_id ON office_business_plans(office_id);
CREATE INDEX idx_business_plans_year_month ON office_business_plans(year, month);
CREATE INDEX idx_business_plans_role_level ON office_business_plans(role, level);
CREATE INDEX idx_business_plans_office_year ON office_business_plans(office_id, year);

-- ================================================
-- CAT PROGRESSION CONFIGURATIONS
-- ================================================
CREATE TABLE office_progressions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    office_id UUID NOT NULL REFERENCES offices(id) ON DELETE CASCADE,
    level VARCHAR(10) NOT NULL,
    monthly_rate DECIMAL(5,4) CHECK (monthly_rate >= 0 AND monthly_rate <= 1),
    curve_type progression_curve_enum DEFAULT 'linear',
    custom_points JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(office_id, level)
);

-- Add indexes for progression queries
CREATE INDEX idx_office_progressions_office_id ON office_progressions(office_id);
CREATE INDEX idx_office_progressions_level ON office_progressions(level);

-- ================================================
-- TRIGGERS FOR UPDATED_AT
-- ================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers to all tables
CREATE TRIGGER update_offices_updated_at BEFORE UPDATE ON offices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_office_workforce_updated_at BEFORE UPDATE ON office_workforce 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_office_business_plans_updated_at BEFORE UPDATE ON office_business_plans 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_office_progressions_updated_at BEFORE UPDATE ON office_progressions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- SEED DATA
-- ================================================

-- Insert existing offices with their journeys
INSERT INTO offices (name, journey, timezone, economic_parameters) VALUES
    ('Stockholm', 'mature', 'Europe/Stockholm', '{"cost_of_living": 1.2, "market_multiplier": 1.1, "tax_rate": 0.25}'),
    ('Munich', 'mature', 'Europe/Berlin', '{"cost_of_living": 1.15, "market_multiplier": 1.05, "tax_rate": 0.22}'),
    ('Hamburg', 'established', 'Europe/Berlin', '{"cost_of_living": 1.1, "market_multiplier": 1.0, "tax_rate": 0.22}'),
    ('Berlin', 'established', 'Europe/Berlin', '{"cost_of_living": 1.05, "market_multiplier": 0.95, "tax_rate": 0.22}'),
    ('Helsinki', 'established', 'Europe/Helsinki', '{"cost_of_living": 1.1, "market_multiplier": 1.0, "tax_rate": 0.20}'),
    ('Oslo', 'established', 'Europe/Oslo', '{"cost_of_living": 1.25, "market_multiplier": 1.1, "tax_rate": 0.24}'),
    ('Copenhagen', 'emerging', 'Europe/Copenhagen', '{"cost_of_living": 1.2, "market_multiplier": 1.05, "tax_rate": 0.25}'),
    ('Zurich', 'emerging', 'Europe/Zurich', '{"cost_of_living": 1.4, "market_multiplier": 1.2, "tax_rate": 0.18}'),
    ('Frankfurt', 'emerging', 'Europe/Berlin', '{"cost_of_living": 1.1, "market_multiplier": 1.0, "tax_rate": 0.22}'),
    ('Amsterdam', 'emerging', 'Europe/Amsterdam', '{"cost_of_living": 1.15, "market_multiplier": 1.05, "tax_rate": 0.25}'),
    ('Cologne', 'emerging', 'Europe/Berlin', '{"cost_of_living": 1.05, "market_multiplier": 0.95, "tax_rate": 0.22}'),
    ('Toronto', 'emerging', 'America/Toronto', '{"cost_of_living": 1.0, "market_multiplier": 0.9, "tax_rate": 0.28}');

-- Add default CAT progression rates for all offices and levels
INSERT INTO office_progressions (office_id, level, monthly_rate, curve_type)
SELECT 
    o.id as office_id,
    level_data.level,
    level_data.rate,
    'linear'::progression_curve_enum
FROM offices o
CROSS JOIN (
    VALUES 
        ('A', 0.15),
        ('AC', 0.12),
        ('C', 0.08),
        ('SrC', 0.05),
        ('AM', 0.04),
        ('M', 0.03),
        ('SrM', 0.02),
        ('PiP', 0.01)
) AS level_data(level, rate);

-- ================================================
-- COMMENTS
-- ================================================

COMMENT ON TABLE offices IS 'Office configurations and basic information';
COMMENT ON COLUMN offices.journey IS 'Office maturity level: emerging, established, or mature';
COMMENT ON COLUMN offices.economic_parameters IS 'JSON object containing cost_of_living, market_multiplier, tax_rate';

COMMENT ON TABLE office_workforce IS 'Initial workforce distribution for each office';
COMMENT ON COLUMN office_workforce.fte IS 'Full-time equivalent count for this role/level combination';

COMMENT ON TABLE office_business_plans IS 'Monthly business planning data for each office, role, and level';
COMMENT ON COLUMN office_business_plans.recruitment IS 'Number of new hires planned for this month';
COMMENT ON COLUMN office_business_plans.churn IS 'Number of departures planned for this month';
COMMENT ON COLUMN office_business_plans.price IS 'Hourly billing rate for this role/level';
COMMENT ON COLUMN office_business_plans.utr IS 'Utilization rate (0.0 to 1.0)';
COMMENT ON COLUMN office_business_plans.salary IS 'Monthly salary for this role/level';

COMMENT ON TABLE office_progressions IS 'CAT progression configuration for each office and level';
COMMENT ON COLUMN office_progressions.monthly_rate IS 'Monthly progression rate (0.0 to 1.0)';
COMMENT ON COLUMN office_progressions.custom_points IS 'JSON array of custom progression curve points';