-- Financial Planning Database Schema
-- Comprehensive expense structure for SimpleSim

-- Currency and configuration tables
CREATE TABLE IF NOT EXISTS currencies (
    code VARCHAR(3) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10),
    decimal_places INTEGER DEFAULT 2,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO currencies (code, name, symbol) VALUES 
('EUR', 'Euro', '€'),
('USD', 'US Dollar', '$'),
('SEK', 'Swedish Krona', 'kr'),
('NOK', 'Norwegian Krone', 'kr'),
('DKK', 'Danish Krone', 'kr'),
('GBP', 'British Pound', '£'),
('CHF', 'Swiss Franc', 'CHF');

-- Financial models (top-level container)
CREATE TABLE IF NOT EXISTS financial_models (
    id VARCHAR(100) PRIMARY KEY,
    office_id VARCHAR(50) NOT NULL,
    office_name VARCHAR(200) NOT NULL,
    currency_code VARCHAR(3) REFERENCES currencies(code),
    fiscal_year INTEGER NOT NULL,
    model_version VARCHAR(20) DEFAULT '1.0',
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    
    UNIQUE(office_id, fiscal_year, model_version)
);

-- Financial time series data (stores all monthly values)
CREATE TABLE IF NOT EXISTS financial_time_series (
    id SERIAL PRIMARY KEY,
    series_id VARCHAR(100) NOT NULL,
    model_id VARCHAR(100) REFERENCES financial_models(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,  -- staff_costs, office_expenses, revenue, etc.
    subcategory VARCHAR(100),       -- base_salary, office_rent, etc.
    item_name VARCHAR(200),         -- specific item description
    month_key VARCHAR(6) NOT NULL,  -- YYYYMM format
    amount DECIMAL(15,2) NOT NULL,
    currency_code VARCHAR(3) REFERENCES currencies(code),
    allocation_method VARCHAR(50) DEFAULT 'direct',
    is_fixed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_series_month (series_id, month_key),
    INDEX idx_model_category (model_id, category),
    INDEX idx_month_key (month_key)
);

-- Staff costs detailed breakdown
CREATE TABLE IF NOT EXISTS staff_costs (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) REFERENCES financial_models(id) ON DELETE CASCADE,
    role_name VARCHAR(100) NOT NULL,
    level_name VARCHAR(50),
    month_key VARCHAR(6) NOT NULL,
    
    -- Headcount
    headcount DECIMAL(8,2) DEFAULT 0,
    
    -- Salary components
    base_salary DECIMAL(12,2) DEFAULT 0,
    variable_salary DECIMAL(12,2) DEFAULT 0,
    social_security DECIMAL(12,2) DEFAULT 0,
    pension_contribution DECIMAL(12,2) DEFAULT 0,
    insurance_benefits DECIMAL(12,2) DEFAULT 0,
    overtime_allowance DECIMAL(12,2) DEFAULT 0,
    bonus_payments DECIMAL(12,2) DEFAULT 0,
    stock_options DECIMAL(12,2) DEFAULT 0,
    other_benefits DECIMAL(12,2) DEFAULT 0,
    
    -- Additional costs
    recruitment_costs DECIMAL(12,2) DEFAULT 0,
    training_costs DECIMAL(12,2) DEFAULT 0,
    equipment_costs DECIMAL(12,2) DEFAULT 0,
    
    currency_code VARCHAR(3) REFERENCES currencies(code),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(model_id, role_name, level_name, month_key),
    INDEX idx_staff_role_month (model_id, role_name, month_key)
);

-- Office expenses detailed breakdown
CREATE TABLE IF NOT EXISTS office_expenses (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) REFERENCES financial_models(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    expense_description VARCHAR(300) NOT NULL,
    month_key VARCHAR(6) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency_code VARCHAR(3) REFERENCES currencies(code),
    is_fixed BOOLEAN DEFAULT TRUE,
    allocation_method VARCHAR(50) DEFAULT 'direct',
    supplier_name VARCHAR(200),
    contract_reference VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_office_category_month (model_id, category, month_key),
    INDEX idx_office_month (model_id, month_key)
);

-- Standard office expense categories for consistency
CREATE TABLE IF NOT EXISTS expense_categories (
    id SERIAL PRIMARY KEY,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(200) NOT NULL,
    parent_category VARCHAR(50),
    description TEXT,
    default_allocation_method VARCHAR(50) DEFAULT 'direct',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0
);

INSERT INTO expense_categories (category_code, category_name, parent_category, description, sort_order) VALUES
-- Facilities & Infrastructure
('facilities', 'Facilities & Infrastructure', NULL, 'Office space and infrastructure costs', 1),
('office_rent', 'Office Rent', 'facilities', 'Monthly office rent and lease payments', 101),
('office_utilities', 'Office Utilities', 'facilities', 'Electricity, heating, water, internet', 102),
('cleaning_services', 'Cleaning Services', 'facilities', 'Cleaning and maintenance services', 103),
('security_services', 'Security Services', 'facilities', 'Security and access control', 104),

-- IT & Equipment
('it_equipment', 'IT & Equipment', NULL, 'Technology and equipment costs', 2),
('it_infrastructure', 'IT Infrastructure', 'it_equipment', 'Servers, network equipment', 201),
('software_licenses', 'Software Licenses', 'it_equipment', 'Software and SaaS subscriptions', 202),
('hardware_depreciation', 'Hardware Depreciation', 'it_equipment', 'Computer and equipment depreciation', 203),

-- Operations
('operations', 'Operations', NULL, 'Day-to-day operational expenses', 3),
('office_supplies', 'Office Supplies', 'operations', 'General office supplies', 301),
('phone_communications', 'Phone & Communications', 'operations', 'Phone and communication costs', 302),
('mail_shipping', 'Mail & Shipping', 'operations', 'Mail and shipping costs', 303),

-- People & Culture
('people_culture', 'People & Culture', NULL, 'Employee development and culture', 4),
('conference_costs', 'Conference Costs', 'people_culture', 'Conferences and events', 401),
('education_training', 'Education & Training', 'people_culture', 'Education and training', 402),
('team_events', 'Team Events', 'people_culture', 'Team building and social events', 403),
('external_representation', 'External Representation', 'people_culture', 'Client entertainment', 404),

-- Professional Services
('professional_services', 'Professional Services', NULL, 'External professional services', 5),
('legal_services', 'Legal Services', 'professional_services', 'Legal and compliance costs', 501),
('accounting_audit', 'Accounting & Audit', 'professional_services', 'Accounting and audit fees', 502),
('consulting_services', 'Consulting Services', 'professional_services', 'External consulting', 503),

-- Travel & Transport
('travel_transport', 'Travel & Transport', NULL, 'Travel and transportation', 6),
('travel_expenses', 'Travel Expenses', 'travel_transport', 'Business travel costs', 601),
('local_transport', 'Local Transport', 'travel_transport', 'Local transportation', 602);

-- Revenue streams
CREATE TABLE IF NOT EXISTS revenue_streams (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) REFERENCES financial_models(id) ON DELETE CASCADE,
    stream_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    client_type VARCHAR(100),
    service_type VARCHAR(100),
    month_key VARCHAR(6) NOT NULL,
    revenue_amount DECIMAL(15,2) NOT NULL,
    currency_code VARCHAR(3) REFERENCES currencies(code),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_revenue_stream_month (model_id, stream_name, month_key),
    INDEX idx_revenue_category (model_id, category, month_key)
);

-- Project costs
CREATE TABLE IF NOT EXISTS project_costs (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) REFERENCES financial_models(id) ON DELETE CASCADE,
    project_reference VARCHAR(200),
    cost_category VARCHAR(100) NOT NULL,
    month_key VARCHAR(6) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency_code VARCHAR(3) REFERENCES currencies(code),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_project_category_month (model_id, cost_category, month_key)
);

-- Financial KPIs (calculated metrics)
CREATE TABLE IF NOT EXISTS financial_kpis (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) REFERENCES financial_models(id) ON DELETE CASCADE,
    kpi_name VARCHAR(100) NOT NULL,
    kpi_category VARCHAR(50) NOT NULL,
    month_key VARCHAR(6) NOT NULL,
    value DECIMAL(15,4) NOT NULL,
    unit VARCHAR(20),  -- currency, percentage, ratio, etc.
    calculation_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(model_id, kpi_name, month_key),
    INDEX idx_kpi_category_month (model_id, kpi_category, month_key)
);

-- Budget plans (top-level budget containers)
CREATE TABLE IF NOT EXISTS budget_plans (
    plan_id VARCHAR(100) PRIMARY KEY,
    office_id VARCHAR(50) NOT NULL,
    plan_name VARCHAR(300) NOT NULL,
    fiscal_year INTEGER NOT NULL,
    currency_code VARCHAR(3) REFERENCES currencies(code),
    financial_model_id VARCHAR(100) REFERENCES financial_models(id),
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    
    INDEX idx_budget_office_year (office_id, fiscal_year)
);

-- Budget vs actual tracking
CREATE TABLE IF NOT EXISTS budget_variance_tracking (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(100) REFERENCES budget_plans(plan_id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    month_key VARCHAR(6) NOT NULL,
    budget_amount DECIMAL(15,2) NOT NULL,
    actual_amount DECIMAL(15,2),
    variance_amount DECIMAL(15,2),
    variance_percentage DECIMAL(8,4),
    variance_explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(plan_id, category, subcategory, month_key),
    INDEX idx_variance_plan_month (plan_id, month_key),
    INDEX idx_variance_category (plan_id, category, month_key)
);

-- Budget assumptions and scenarios
CREATE TABLE IF NOT EXISTS budget_assumptions (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(100) REFERENCES budget_plans(plan_id) ON DELETE CASCADE,
    assumption_key VARCHAR(100) NOT NULL,
    assumption_value TEXT NOT NULL,
    assumption_category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(plan_id, assumption_key)
);

-- Multi-year projections
CREATE TABLE IF NOT EXISTS financial_projections (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) REFERENCES financial_models(id) ON DELETE CASCADE,
    projection_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    year_1 DECIMAL(15,2),
    year_2 DECIMAL(15,2),
    year_3 DECIMAL(15,2),
    year_4 DECIMAL(15,2),
    year_5 DECIMAL(15,2),
    growth_assumptions TEXT,
    methodology TEXT,
    confidence_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_projection_category (model_id, category)
);

-- Currency exchange rates (for multi-currency support)
CREATE TABLE IF NOT EXISTS exchange_rates (
    id SERIAL PRIMARY KEY,
    from_currency VARCHAR(3) REFERENCES currencies(code),
    to_currency VARCHAR(3) REFERENCES currencies(code),
    rate DECIMAL(12,6) NOT NULL,
    effective_date DATE NOT NULL,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(from_currency, to_currency, effective_date),
    INDEX idx_exchange_rate_date (from_currency, to_currency, effective_date)
);

-- Audit log for all financial changes
CREATE TABLE IF NOT EXISTS financial_audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL,  -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_reason TEXT,
    
    INDEX idx_audit_table_record (table_name, record_id),
    INDEX idx_audit_user_date (changed_by, changed_at)
);

-- Views for common reporting queries

-- Consolidated monthly expenses by category
CREATE OR REPLACE VIEW monthly_expense_summary AS
SELECT 
    fm.office_id,
    fm.office_name,
    fm.fiscal_year,
    oe.month_key,
    oe.category,
    SUM(oe.amount) as total_amount,
    fm.currency_code,
    COUNT(*) as expense_items
FROM financial_models fm
JOIN office_expenses oe ON fm.id = oe.model_id
GROUP BY fm.office_id, fm.office_name, fm.fiscal_year, oe.month_key, oe.category, fm.currency_code;

-- Staff costs rollup by role
CREATE OR REPLACE VIEW staff_costs_summary AS
SELECT 
    fm.office_id,
    fm.office_name,
    fm.fiscal_year,
    sc.month_key,
    sc.role_name,
    sc.level_name,
    SUM(sc.headcount) as total_headcount,
    SUM(sc.base_salary + sc.variable_salary + sc.social_security + 
        sc.pension_contribution + sc.insurance_benefits + sc.overtime_allowance + 
        sc.bonus_payments + sc.stock_options + sc.other_benefits) as total_compensation,
    SUM(sc.recruitment_costs + sc.training_costs + sc.equipment_costs) as additional_costs,
    fm.currency_code
FROM financial_models fm
JOIN staff_costs sc ON fm.id = sc.model_id
GROUP BY fm.office_id, fm.office_name, fm.fiscal_year, sc.month_key, 
         sc.role_name, sc.level_name, fm.currency_code;

-- Budget variance summary
CREATE OR REPLACE VIEW budget_variance_summary AS
SELECT 
    bp.plan_id,
    bp.office_id,
    bp.plan_name,
    bp.fiscal_year,
    bvt.month_key,
    bvt.category,
    SUM(bvt.budget_amount) as total_budget,
    SUM(bvt.actual_amount) as total_actual,
    SUM(bvt.variance_amount) as total_variance,
    CASE 
        WHEN SUM(bvt.budget_amount) > 0 
        THEN (SUM(bvt.variance_amount) / SUM(bvt.budget_amount) * 100)
        ELSE 0 
    END as variance_percentage,
    bp.currency_code
FROM budget_plans bp
JOIN budget_variance_tracking bvt ON bp.plan_id = bvt.plan_id
WHERE bvt.actual_amount IS NOT NULL
GROUP BY bp.plan_id, bp.office_id, bp.plan_name, bp.fiscal_year, 
         bvt.month_key, bvt.category, bp.currency_code;

-- Comprehensive financial dashboard view
CREATE OR REPLACE VIEW financial_dashboard AS
SELECT 
    fm.office_id,
    fm.office_name,
    fm.fiscal_year,
    fm.currency_code,
    
    -- Revenue metrics
    COALESCE(SUM(rs.revenue_amount), 0) as total_revenue,
    
    -- Cost metrics
    COALESCE(SUM(CASE WHEN oe.category = 'facilities' THEN oe.amount ELSE 0 END), 0) as facilities_costs,
    COALESCE(SUM(CASE WHEN oe.category = 'it_equipment' THEN oe.amount ELSE 0 END), 0) as it_costs,
    COALESCE(SUM(CASE WHEN oe.category = 'people_culture' THEN oe.amount ELSE 0 END), 0) as people_costs,
    COALESCE(SUM(oe.amount), 0) as total_office_expenses,
    
    -- Staff metrics
    COALESCE(SUM(sc.headcount), 0) as total_headcount,
    COALESCE(SUM(sc.base_salary + sc.variable_salary + sc.social_security + 
        sc.pension_contribution + sc.insurance_benefits + sc.overtime_allowance + 
        sc.bonus_payments + sc.stock_options + sc.other_benefits), 0) as total_staff_costs,
    
    -- Project costs
    COALESCE(SUM(pc.amount), 0) as total_project_costs,
    
    -- KPIs
    CASE 
        WHEN SUM(rs.revenue_amount) > 0 AND SUM(sc.headcount) > 0
        THEN SUM(rs.revenue_amount) / SUM(sc.headcount)
        ELSE 0 
    END as revenue_per_fte,
    
    CASE 
        WHEN SUM(rs.revenue_amount) > 0 
        THEN ((SUM(rs.revenue_amount) - SUM(oe.amount) - SUM(sc.base_salary + sc.variable_salary + sc.social_security + 
            sc.pension_contribution + sc.insurance_benefits + sc.overtime_allowance + 
            sc.bonus_payments + sc.stock_options + sc.other_benefits) - SUM(pc.amount)) / SUM(rs.revenue_amount) * 100)
        ELSE 0 
    END as ebitda_margin_percent

FROM financial_models fm
LEFT JOIN revenue_streams rs ON fm.id = rs.model_id
LEFT JOIN office_expenses oe ON fm.id = oe.model_id
LEFT JOIN staff_costs sc ON fm.id = sc.model_id
LEFT JOIN project_costs pc ON fm.id = pc.model_id
GROUP BY fm.office_id, fm.office_name, fm.fiscal_year, fm.currency_code;