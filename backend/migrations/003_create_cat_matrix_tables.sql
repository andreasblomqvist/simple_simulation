-- Migration: CAT Matrix Management System
-- Version: 003
-- Description: Complete CAT matrix configurations per office with progression probabilities

-- Create enum types for CAT matrix
CREATE TYPE cat_stage_enum AS ENUM (
    'CAT0', 'CAT6', 'CAT12', 'CAT18', 'CAT24', 'CAT30', 
    'CAT36', 'CAT42', 'CAT48', 'CAT54', 'CAT60'
);

CREATE TYPE level_enum AS ENUM (
    'A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P', 'X', 'OPE'
);

CREATE TYPE journey_stage_enum AS ENUM ('J-1', 'J-2', 'J-3');

-- ================================================
-- CAT MATRIX CONFIGURATIONS (one per office)
-- ================================================
CREATE TABLE cat_matrix_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    office_id UUID NOT NULL REFERENCES offices(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- Audit trail
    last_validated_at TIMESTAMP,
    validation_status VARCHAR(50) DEFAULT 'pending',
    validation_notes TEXT,
    
    UNIQUE(office_id, name),
    CONSTRAINT check_version_positive CHECK (version > 0)
);

-- Add indexes for CAT matrix configurations
CREATE INDEX idx_cat_matrix_office_id ON cat_matrix_configurations(office_id);
CREATE INDEX idx_cat_matrix_active ON cat_matrix_configurations(office_id, is_active);
CREATE INDEX idx_cat_matrix_version ON cat_matrix_configurations(office_id, version);

-- ================================================
-- CAT LEVEL CONFIGURATIONS (progression rules per level per office)
-- ================================================
CREATE TABLE cat_level_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matrix_id UUID NOT NULL REFERENCES cat_matrix_configurations(id) ON DELETE CASCADE,
    level level_enum NOT NULL,
    
    -- Level-specific progression settings
    start_tenure INTEGER NOT NULL DEFAULT 0,
    time_on_level INTEGER NOT NULL DEFAULT 12,
    next_level level_enum,
    journey journey_stage_enum,
    progression_months INTEGER[] NOT NULL DEFAULT '{1}',
    base_progression_rate DECIMAL(5,4) NOT NULL DEFAULT 0.0 CHECK (base_progression_rate >= 0 AND base_progression_rate <= 1),
    
    -- CAT curve configuration
    use_cat_curve BOOLEAN DEFAULT true,
    curve_type progression_curve_enum DEFAULT 'custom',
    custom_curve_data JSONB DEFAULT '{}',
    
    -- Metadata
    notes TEXT,
    is_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(matrix_id, level),
    CONSTRAINT check_start_tenure_positive CHECK (start_tenure >= 0),
    CONSTRAINT check_time_on_level_positive CHECK (time_on_level > 0),
    CONSTRAINT check_progression_months_not_empty CHECK (array_length(progression_months, 1) > 0)
);

-- Add indexes for level configurations
CREATE INDEX idx_cat_levels_matrix_id ON cat_level_configurations(matrix_id);
CREATE INDEX idx_cat_levels_level ON cat_level_configurations(level);
CREATE INDEX idx_cat_levels_enabled ON cat_level_configurations(matrix_id, is_enabled);

-- ================================================
-- CAT PROGRESSION PROBABILITIES (probability matrix per office)
-- ================================================
CREATE TABLE cat_progression_probabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matrix_id UUID NOT NULL REFERENCES cat_matrix_configurations(id) ON DELETE CASCADE,
    level level_enum NOT NULL,
    cat_stage cat_stage_enum NOT NULL,
    probability DECIMAL(6,4) NOT NULL DEFAULT 0.0 CHECK (probability >= 0 AND probability <= 1),
    
    -- Optional overrides
    effective_from_month INTEGER,
    effective_to_month INTEGER,
    seasonal_adjustment DECIMAL(5,4) DEFAULT 0.0,
    
    -- Metadata
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(matrix_id, level, cat_stage),
    CONSTRAINT check_effective_months CHECK (
        (effective_from_month IS NULL AND effective_to_month IS NULL) OR
        (effective_from_month IS NOT NULL AND effective_to_month IS NOT NULL AND 
         effective_from_month >= 1 AND effective_from_month <= 12 AND
         effective_to_month >= 1 AND effective_to_month <= 12)
    )
);

-- Add indexes for progression probabilities
CREATE INDEX idx_cat_probabilities_matrix_id ON cat_progression_probabilities(matrix_id);
CREATE INDEX idx_cat_probabilities_level ON cat_progression_probabilities(level);
CREATE INDEX idx_cat_probabilities_stage ON cat_progression_probabilities(cat_stage);
CREATE INDEX idx_cat_probabilities_active ON cat_progression_probabilities(matrix_id, is_active);
CREATE INDEX idx_cat_probabilities_lookup ON cat_progression_probabilities(matrix_id, level, cat_stage) WHERE is_active = true;

-- ================================================
-- CAT MATRIX AUDIT LOG
-- ================================================
CREATE TABLE cat_matrix_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matrix_id UUID NOT NULL REFERENCES cat_matrix_configurations(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'matrix', 'level', 'probability'
    entity_id UUID,
    old_values JSONB DEFAULT '{}',
    new_values JSONB DEFAULT '{}',
    user_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    
    CONSTRAINT check_action_valid CHECK (action IN (
        'created', 'updated', 'deleted', 'activated', 'deactivated',
        'copied_from', 'reset_to_default', 'validated', 'bulk_updated'
    ))
);

-- Add indexes for audit log
CREATE INDEX idx_cat_audit_matrix_id ON cat_matrix_audit_log(matrix_id, timestamp DESC);
CREATE INDEX idx_cat_audit_action ON cat_matrix_audit_log(action, timestamp DESC);
CREATE INDEX idx_cat_audit_user ON cat_matrix_audit_log(user_id, timestamp DESC);

-- ================================================
-- TRIGGERS FOR UPDATED_AT
-- ================================================

-- Add triggers to CAT matrix tables
CREATE TRIGGER update_cat_matrix_configurations_updated_at 
    BEFORE UPDATE ON cat_matrix_configurations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cat_level_configurations_updated_at 
    BEFORE UPDATE ON cat_level_configurations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cat_progression_probabilities_updated_at 
    BEFORE UPDATE ON cat_progression_probabilities 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- SEED DEFAULT CAT MATRICES FOR ALL OFFICES
-- ================================================

-- Create default CAT matrix for each office
INSERT INTO cat_matrix_configurations (office_id, name, description, created_by)
SELECT 
    id,
    'Default CAT Matrix',
    'Default CAT progression matrix based on global configuration',
    'system'
FROM offices;

-- Create level configurations based on global progression config
INSERT INTO cat_level_configurations (
    matrix_id, level, start_tenure, time_on_level, next_level, journey, 
    progression_months, base_progression_rate, use_cat_curve
)
SELECT 
    cmc.id as matrix_id,
    level_data.level::level_enum,
    level_data.start_tenure,
    level_data.time_on_level,
    CASE 
        WHEN level_data.next_level != level_data.level THEN level_data.next_level::level_enum 
        ELSE NULL 
    END as next_level,
    CASE 
        WHEN level_data.journey IS NOT NULL THEN level_data.journey::journey_stage_enum 
        ELSE NULL 
    END as journey,
    level_data.progression_months,
    level_data.progression_rate,
    true as use_cat_curve
FROM cat_matrix_configurations cmc
CROSS JOIN (
    VALUES 
        ('A', 0, 6, 'AC', 'J-1', ARRAY[1,4,7,10], 0.15),
        ('AC', 6, 9, 'C', 'J-1', ARRAY[1,4,7,10], 0.12),
        ('C', 15, 12, 'SrC', 'J-1', ARRAY[1,7], 0.10),
        ('SrC', 27, 18, 'AM', 'J-2', ARRAY[1,7], 0.08),
        ('AM', 45, 30, 'M', 'J-2', ARRAY[1,7], 0.06),
        ('M', 75, 24, 'SrM', 'J-3', ARRAY[1], 0.04),
        ('SrM', 99, 120, 'Pi', 'J-3', ARRAY[1], 0.03),
        ('Pi', 219, 12, 'P', 'J-3', ARRAY[1], 0.02),
        ('P', 231, 1000, 'X', 'J-3', ARRAY[1], 0.01),
        ('X', 1231, 1000, 'X', 'J-3', ARRAY[1], 0.005),
        ('OPE', 1279, 1000, 'OPE', NULL, ARRAY[1], 0.0)
) AS level_data(level, start_tenure, time_on_level, next_level, journey, progression_months, progression_rate);

-- Create CAT progression probabilities based on global CAT curves
INSERT INTO cat_progression_probabilities (matrix_id, level, cat_stage, probability)
SELECT 
    cmc.id as matrix_id,
    prob_data.level::level_enum,
    prob_data.cat_stage::cat_stage_enum,
    prob_data.probability
FROM cat_matrix_configurations cmc
CROSS JOIN (
    VALUES 
        -- Level A
        ('A', 'CAT0', 0.0), ('A', 'CAT6', 0.919), ('A', 'CAT12', 0.85),
        ('A', 'CAT18', 0.0), ('A', 'CAT24', 0.0), ('A', 'CAT30', 0.0),
        
        -- Level AC
        ('AC', 'CAT0', 0.0), ('AC', 'CAT6', 0.054), ('AC', 'CAT12', 0.759),
        ('AC', 'CAT18', 0.400), ('AC', 'CAT24', 0.0), ('AC', 'CAT30', 0.0),
        
        -- Level C
        ('C', 'CAT0', 0.0), ('C', 'CAT6', 0.050), ('C', 'CAT12', 0.442),
        ('C', 'CAT18', 0.597), ('C', 'CAT24', 0.278), ('C', 'CAT30', 0.643),
        ('C', 'CAT36', 0.200), ('C', 'CAT42', 0.0),
        
        -- Level SrC
        ('SrC', 'CAT0', 0.0), ('SrC', 'CAT6', 0.206), ('SrC', 'CAT12', 0.438),
        ('SrC', 'CAT18', 0.317), ('SrC', 'CAT24', 0.211), ('SrC', 'CAT30', 0.206),
        ('SrC', 'CAT36', 0.167), ('SrC', 'CAT42', 0.0), ('SrC', 'CAT48', 0.0),
        ('SrC', 'CAT54', 0.0), ('SrC', 'CAT60', 0.0),
        
        -- Level AM
        ('AM', 'CAT0', 0.0), ('AM', 'CAT6', 0.0), ('AM', 'CAT12', 0.0),
        ('AM', 'CAT18', 0.189), ('AM', 'CAT24', 0.197), ('AM', 'CAT30', 0.234),
        ('AM', 'CAT36', 0.048), ('AM', 'CAT42', 0.0), ('AM', 'CAT48', 0.0),
        ('AM', 'CAT54', 0.0), ('AM', 'CAT60', 0.0),
        
        -- Level M
        ('M', 'CAT0', 0.0), ('M', 'CAT6', 0.00), ('M', 'CAT12', 0.01),
        ('M', 'CAT18', 0.02), ('M', 'CAT24', 0.03), ('M', 'CAT30', 0.04),
        ('M', 'CAT36', 0.05), ('M', 'CAT42', 0.06), ('M', 'CAT48', 0.07),
        ('M', 'CAT54', 0.08), ('M', 'CAT60', 0.10),
        
        -- Level SrM
        ('SrM', 'CAT0', 0.0), ('SrM', 'CAT6', 0.00), ('SrM', 'CAT12', 0.005),
        ('SrM', 'CAT18', 0.01), ('SrM', 'CAT24', 0.015), ('SrM', 'CAT30', 0.02),
        ('SrM', 'CAT36', 0.025), ('SrM', 'CAT42', 0.03), ('SrM', 'CAT48', 0.04),
        ('SrM', 'CAT54', 0.05), ('SrM', 'CAT60', 0.06),
        
        -- Level Pi, P, X, OPE (all have CAT0 = 0.0)
        ('Pi', 'CAT0', 0.0), ('P', 'CAT0', 0.0), ('X', 'CAT0', 0.0), ('OPE', 'CAT0', 0.0)
) AS prob_data(level, cat_stage, probability);

-- ================================================
-- VALIDATION FUNCTIONS
-- ================================================

-- Function to validate CAT matrix consistency
CREATE OR REPLACE FUNCTION validate_cat_matrix(matrix_uuid UUID)
RETURNS TABLE (
    is_valid BOOLEAN,
    issues TEXT[],
    warnings TEXT[]
) AS $$
DECLARE
    issue_list TEXT[] := '{}';
    warning_list TEXT[] := '{}';
    level_count INTEGER;
    prob_count INTEGER;
    missing_levels TEXT[];
BEGIN
    -- Check if matrix exists
    IF NOT EXISTS (SELECT 1 FROM cat_matrix_configurations WHERE id = matrix_uuid) THEN
        issue_list := array_append(issue_list, 'Matrix does not exist');
        RETURN QUERY SELECT false, issue_list, warning_list;
        RETURN;
    END IF;
    
    -- Check level configurations exist
    SELECT COUNT(*) INTO level_count
    FROM cat_level_configurations
    WHERE matrix_id = matrix_uuid AND is_enabled = true;
    
    IF level_count = 0 THEN
        issue_list := array_append(issue_list, 'No enabled level configurations found');
    END IF;
    
    -- Check progression probabilities exist
    SELECT COUNT(*) INTO prob_count
    FROM cat_progression_probabilities
    WHERE matrix_id = matrix_uuid AND is_active = true;
    
    IF prob_count = 0 THEN
        issue_list := array_append(issue_list, 'No active progression probabilities found');
    END IF;
    
    -- Check for levels with no CAT probabilities
    SELECT array_agg(level::TEXT) INTO missing_levels
    FROM cat_level_configurations clc
    WHERE clc.matrix_id = matrix_uuid 
      AND clc.is_enabled = true
      AND clc.use_cat_curve = true
      AND NOT EXISTS (
          SELECT 1 FROM cat_progression_probabilities cpp
          WHERE cpp.matrix_id = matrix_uuid 
            AND cpp.level = clc.level 
            AND cpp.is_active = true
      );
    
    IF missing_levels IS NOT NULL AND array_length(missing_levels, 1) > 0 THEN
        warning_list := array_append(warning_list, 
            'Levels missing CAT probabilities: ' || array_to_string(missing_levels, ', '));
    END IF;
    
    -- Return validation results
    RETURN QUERY SELECT 
        array_length(issue_list, 1) = 0 OR issue_list = '{}',
        issue_list,
        warning_list;
END;
$$ LANGUAGE plpgsql;

-- Function to copy CAT matrix between offices
CREATE OR REPLACE FUNCTION copy_cat_matrix(
    source_matrix_uuid UUID,
    target_office_uuid UUID,
    new_matrix_name TEXT,
    user_id TEXT DEFAULT 'system'
)
RETURNS UUID AS $$
DECLARE
    new_matrix_id UUID;
    source_office_id UUID;
BEGIN
    -- Get source office for audit
    SELECT cmc.office_id INTO source_office_id
    FROM cat_matrix_configurations cmc
    WHERE cmc.id = source_matrix_uuid;
    
    IF source_office_id IS NULL THEN
        RAISE EXCEPTION 'Source matrix not found';
    END IF;
    
    -- Create new matrix configuration
    INSERT INTO cat_matrix_configurations (
        office_id, name, description, created_by, version
    )
    SELECT 
        target_office_uuid,
        new_matrix_name,
        'Copied from ' || cmc.name || ' (Office: ' || o.name || ')',
        user_id,
        1
    FROM cat_matrix_configurations cmc
    JOIN offices o ON o.id = cmc.office_id
    WHERE cmc.id = source_matrix_uuid
    RETURNING id INTO new_matrix_id;
    
    -- Copy level configurations
    INSERT INTO cat_level_configurations (
        matrix_id, level, start_tenure, time_on_level, next_level, journey,
        progression_months, base_progression_rate, use_cat_curve, curve_type,
        custom_curve_data, notes, is_enabled
    )
    SELECT 
        new_matrix_id, level, start_tenure, time_on_level, next_level, journey,
        progression_months, base_progression_rate, use_cat_curve, curve_type,
        custom_curve_data, notes, is_enabled
    FROM cat_level_configurations
    WHERE matrix_id = source_matrix_uuid;
    
    -- Copy progression probabilities
    INSERT INTO cat_progression_probabilities (
        matrix_id, level, cat_stage, probability, effective_from_month,
        effective_to_month, seasonal_adjustment, notes, is_active
    )
    SELECT 
        new_matrix_id, level, cat_stage, probability, effective_from_month,
        effective_to_month, seasonal_adjustment, notes, is_active
    FROM cat_progression_probabilities
    WHERE matrix_id = source_matrix_uuid;
    
    -- Log the copy operation
    INSERT INTO cat_matrix_audit_log (
        matrix_id, action, entity_type, user_id, notes, new_values
    ) VALUES (
        new_matrix_id,
        'copied_from',
        'matrix',
        user_id,
        'Matrix copied from ' || source_matrix_uuid,
        jsonb_build_object('source_matrix_id', source_matrix_uuid, 'source_office_id', source_office_id)
    );
    
    RETURN new_matrix_id;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- COMMENTS
-- ================================================

COMMENT ON TABLE cat_matrix_configurations IS 'CAT matrix configurations - one per office with versioning';
COMMENT ON COLUMN cat_matrix_configurations.version IS 'Version number for matrix evolution tracking';
COMMENT ON COLUMN cat_matrix_configurations.validation_status IS 'Validation status: pending, valid, invalid';

COMMENT ON TABLE cat_level_configurations IS 'Level-specific CAT progression rules and settings';
COMMENT ON COLUMN cat_level_configurations.progression_months IS 'Array of months when progression can occur (1-12)';
COMMENT ON COLUMN cat_level_configurations.use_cat_curve IS 'Whether to use CAT curve probabilities for this level';

COMMENT ON TABLE cat_progression_probabilities IS 'CAT stage progression probabilities per level';
COMMENT ON COLUMN cat_progression_probabilities.seasonal_adjustment IS 'Seasonal adjustment to base probability (-1.0 to +1.0)';
COMMENT ON COLUMN cat_progression_probabilities.effective_from_month IS 'Month when this probability becomes effective (1-12)';

COMMENT ON FUNCTION validate_cat_matrix(UUID) IS 'Validates CAT matrix configuration and returns issues/warnings';
COMMENT ON FUNCTION copy_cat_matrix(UUID, UUID, TEXT, TEXT) IS 'Copies complete CAT matrix from one office to another';