-- Migration: Create Population Snapshot Tables
-- Version: 002
-- Description: Add population snapshot functionality for workforce baseline management

-- ================================================
-- POPULATION SNAPSHOTS TABLE
-- ================================================
CREATE TABLE population_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    office_id UUID NOT NULL REFERENCES offices(id) ON DELETE CASCADE,
    snapshot_date VARCHAR(6) NOT NULL, -- YYYYMM format
    snapshot_name VARCHAR(200) NOT NULL,
    description TEXT,
    total_fte INTEGER NOT NULL CHECK (total_fte >= 0),
    is_default BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    source VARCHAR(50) NOT NULL CHECK (source IN ('manual', 'simulation', 'import', 'business_plan', 'current')),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100) NOT NULL,
    last_used_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    
    -- Ensure unique names per office
    UNIQUE(office_id, snapshot_name)
);

-- ================================================
-- SNAPSHOT WORKFORCE DETAILS
-- ================================================
CREATE TABLE snapshot_workforce (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    level VARCHAR(20), -- NULL for flat roles like Operations
    fte INTEGER NOT NULL CHECK (fte >= 0),
    
    -- Ensure unique role/level combinations per snapshot
    UNIQUE(snapshot_id, role, level)
);

-- ================================================
-- SNAPSHOT TAGS
-- ================================================
CREATE TABLE snapshot_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure unique tags per snapshot
    UNIQUE(snapshot_id, tag)
);

-- ================================================
-- SNAPSHOT COMPARISONS
-- ================================================
CREATE TABLE snapshot_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_1_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    snapshot_2_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    comparison_date TIMESTAMP DEFAULT NOW(),
    compared_by VARCHAR(100),
    delta_data JSONB NOT NULL, -- Differences between snapshots
    insights TEXT, -- AI-generated or manual insights
    
    CHECK (snapshot_1_id != snapshot_2_id)
);

-- ================================================
-- SNAPSHOT AUDIT LOG
-- ================================================
CREATE TABLE snapshot_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES population_snapshots(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL CHECK (action IN (
        'created', 'modified', 'approved', 'set_default',
        'used_in_scenario', 'used_in_plan', 'used_in_simulation'
    )),
    entity_type VARCHAR(50), -- 'scenario', 'business_plan', 'simulation'
    entity_id UUID,
    user_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT NOW(),
    details JSONB DEFAULT '{}'
);

-- ================================================
-- EXTEND EXISTING TABLES
-- ================================================

-- Add snapshot reference to scenarios (if scenarios table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scenarios') THEN
        ALTER TABLE scenarios 
        ADD COLUMN IF NOT EXISTS baseline_snapshot_id UUID REFERENCES population_snapshots(id),
        ADD COLUMN IF NOT EXISTS baseline_type VARCHAR(20) CHECK (baseline_type IN ('snapshot', 'current', 'custom'));
    END IF;
END $$;

-- Add snapshot reference to office_business_plans
ALTER TABLE office_business_plans 
ADD COLUMN IF NOT EXISTS baseline_snapshot_id UUID REFERENCES population_snapshots(id);

-- ================================================
-- INDEXES FOR PERFORMANCE
-- ================================================
CREATE INDEX idx_snapshots_office_date ON population_snapshots(office_id, snapshot_date DESC);
CREATE INDEX idx_snapshots_office_default ON population_snapshots(office_id, is_default) WHERE is_default = TRUE;
CREATE INDEX idx_snapshots_approved ON population_snapshots(office_id, is_approved) WHERE is_approved = TRUE;
CREATE INDEX idx_snapshot_workforce_snapshot ON snapshot_workforce(snapshot_id);
CREATE INDEX idx_snapshot_workforce_role ON snapshot_workforce(role, level);
CREATE INDEX idx_snapshot_tags_snapshot ON snapshot_tags(snapshot_id);
CREATE INDEX idx_snapshot_tags_tag ON snapshot_tags(tag);
CREATE INDEX idx_comparisons_snapshots ON snapshot_comparisons(snapshot_1_id, snapshot_2_id);
CREATE INDEX idx_audit_snapshot ON snapshot_audit_log(snapshot_id, timestamp DESC);
CREATE INDEX idx_audit_action ON snapshot_audit_log(action, timestamp DESC);

-- ================================================
-- TRIGGERS
-- ================================================

-- Update the updated_at timestamp for snapshots
CREATE TRIGGER update_population_snapshots_updated_at 
    BEFORE UPDATE ON population_snapshots 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to ensure only one default snapshot per office
CREATE OR REPLACE FUNCTION ensure_single_default_snapshot()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = TRUE THEN
        -- Clear other defaults for this office
        UPDATE population_snapshots 
        SET is_default = FALSE 
        WHERE office_id = NEW.office_id 
        AND id != NEW.id 
        AND is_default = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ensure_single_default_snapshot_trigger
    BEFORE INSERT OR UPDATE ON population_snapshots
    FOR EACH ROW
    WHEN (NEW.is_default = TRUE)
    EXECUTE FUNCTION ensure_single_default_snapshot();

-- Function to log snapshot usage
CREATE OR REPLACE FUNCTION log_snapshot_usage()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF OLD.last_used_at IS DISTINCT FROM NEW.last_used_at THEN
            INSERT INTO snapshot_audit_log (
                snapshot_id, 
                action, 
                timestamp,
                details
            ) VALUES (
                NEW.id,
                'used_in_' || TG_ARGV[0],
                NOW(),
                jsonb_build_object('trigger_source', TG_TABLE_NAME)
            );
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- VIEWS FOR EASIER ACCESS
-- ================================================

-- View for snapshot summary with tags
CREATE OR REPLACE VIEW v_snapshot_summary AS
SELECT 
    ps.id,
    ps.office_id,
    o.name as office_name,
    ps.snapshot_date,
    ps.snapshot_name,
    ps.description,
    ps.total_fte,
    ps.is_default,
    ps.is_approved,
    ps.source,
    ps.created_at,
    ps.created_by,
    ps.last_used_at,
    array_agg(DISTINCT st.tag) FILTER (WHERE st.tag IS NOT NULL) as tags,
    COUNT(DISTINCT sw.id) as workforce_entries
FROM population_snapshots ps
JOIN offices o ON ps.office_id = o.id
LEFT JOIN snapshot_tags st ON ps.id = st.snapshot_id
LEFT JOIN snapshot_workforce sw ON ps.id = sw.snapshot_id
GROUP BY ps.id, o.id, o.name;

-- View for workforce comparison between snapshots
CREATE OR REPLACE VIEW v_snapshot_workforce_comparison AS
WITH snapshot_pairs AS (
    SELECT DISTINCT
        sc.id as comparison_id,
        sc.snapshot_1_id,
        sc.snapshot_2_id,
        sw1.role,
        sw1.level
    FROM snapshot_comparisons sc
    LEFT JOIN snapshot_workforce sw1 ON sc.snapshot_1_id = sw1.snapshot_id
    UNION
    SELECT DISTINCT
        sc.id as comparison_id,
        sc.snapshot_1_id,
        sc.snapshot_2_id,
        sw2.role,
        sw2.level
    FROM snapshot_comparisons sc
    LEFT JOIN snapshot_workforce sw2 ON sc.snapshot_2_id = sw2.snapshot_id
)
SELECT 
    sp.comparison_id,
    sp.role,
    sp.level,
    COALESCE(sw1.fte, 0) as snapshot_1_fte,
    COALESCE(sw2.fte, 0) as snapshot_2_fte,
    COALESCE(sw2.fte, 0) - COALESCE(sw1.fte, 0) as delta
FROM snapshot_pairs sp
LEFT JOIN snapshot_workforce sw1 
    ON sp.snapshot_1_id = sw1.snapshot_id 
    AND sp.role = sw1.role 
    AND (sp.level = sw1.level OR (sp.level IS NULL AND sw1.level IS NULL))
LEFT JOIN snapshot_workforce sw2 
    ON sp.snapshot_2_id = sw2.snapshot_id 
    AND sp.role = sw2.role 
    AND (sp.level = sw2.level OR (sp.level IS NULL AND sw2.level IS NULL));

-- ================================================
-- HELPER FUNCTIONS
-- ================================================

-- Function to create snapshot from current office workforce
CREATE OR REPLACE FUNCTION create_snapshot_from_current(
    p_office_id UUID,
    p_snapshot_name VARCHAR,
    p_description TEXT,
    p_created_by VARCHAR
) RETURNS UUID AS $$
DECLARE
    v_snapshot_id UUID;
    v_total_fte INTEGER;
    v_snapshot_date VARCHAR(6);
BEGIN
    -- Generate snapshot date in YYYYMM format
    v_snapshot_date := TO_CHAR(CURRENT_DATE, 'YYYYMM');
    
    -- Calculate total FTE from current workforce
    SELECT COALESCE(SUM(fte), 0) INTO v_total_fte
    FROM office_workforce
    WHERE office_id = p_office_id
    AND start_date = (
        SELECT MAX(start_date) 
        FROM office_workforce 
        WHERE office_id = p_office_id
    );
    
    -- Create the snapshot
    INSERT INTO population_snapshots (
        office_id,
        snapshot_date,
        snapshot_name,
        description,
        total_fte,
        source,
        created_by
    ) VALUES (
        p_office_id,
        v_snapshot_date,
        p_snapshot_name,
        p_description,
        v_total_fte,
        'current',
        p_created_by
    ) RETURNING id INTO v_snapshot_id;
    
    -- Copy workforce data
    INSERT INTO snapshot_workforce (snapshot_id, role, level, fte)
    SELECT 
        v_snapshot_id,
        role,
        level,
        fte
    FROM office_workforce
    WHERE office_id = p_office_id
    AND start_date = (
        SELECT MAX(start_date) 
        FROM office_workforce 
        WHERE office_id = p_office_id
    )
    AND fte > 0;
    
    -- Log the creation
    INSERT INTO snapshot_audit_log (
        snapshot_id,
        action,
        user_id,
        details
    ) VALUES (
        v_snapshot_id,
        'created',
        p_created_by,
        jsonb_build_object('source', 'current_workforce', 'total_fte', v_total_fte)
    );
    
    RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- COMMENTS
-- ================================================

COMMENT ON TABLE population_snapshots IS 'Point-in-time snapshots of office workforce populations used as baselines for scenarios and planning';
COMMENT ON COLUMN population_snapshots.snapshot_date IS 'Snapshot date in YYYYMM format';
COMMENT ON COLUMN population_snapshots.is_default IS 'Whether this is the default baseline for the office';
COMMENT ON COLUMN population_snapshots.is_approved IS 'Whether this snapshot is approved for use in official planning';
COMMENT ON COLUMN population_snapshots.source IS 'Origin of the snapshot data';

COMMENT ON TABLE snapshot_workforce IS 'Detailed workforce composition for each snapshot';
COMMENT ON COLUMN snapshot_workforce.level IS 'Level within role (NULL for flat roles like Operations)';

COMMENT ON TABLE snapshot_tags IS 'Tags for categorizing and filtering snapshots';
COMMENT ON TABLE snapshot_comparisons IS 'Stored comparisons between two snapshots';
COMMENT ON TABLE snapshot_audit_log IS 'Audit trail of snapshot usage across the system';

COMMENT ON VIEW v_snapshot_summary IS 'Summary view of snapshots with aggregated tags and workforce counts';
COMMENT ON VIEW v_snapshot_workforce_comparison IS 'Detailed workforce comparison between snapshot pairs';