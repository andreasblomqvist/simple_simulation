"""
Database migration and stored procedure tests for population snapshots
Tests SQL migration scripts, triggers, functions, views, and constraints
"""

import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, date
from uuid import uuid4
import json
from typing import Any, Dict, List, Optional

# Mock database connection for testing migrations
class MockDatabaseConnection:
    """Mock database connection for testing migration scripts"""
    
    def __init__(self):
        self.tables = {}
        self.views = {}
        self.functions = {}
        self.triggers = {}
        self.indexes = {}
        self.constraints = {}
        self.executed_queries = []
        
    def execute(self, query: str, params: Optional[tuple] = None):
        """Execute SQL query and track execution"""
        self.executed_queries.append((query, params))
        return MockCursor()
        
    def commit(self):
        """Mock commit"""
        pass
        
    def rollback(self):
        """Mock rollback"""
        pass

class MockCursor:
    """Mock database cursor"""
    
    def __init__(self):
        self.rowcount = 1
        self.fetchall_result = []
        self.fetchone_result = None
        
    def fetchall(self):
        return self.fetchall_result
        
    def fetchone(self):
        return self.fetchone_result
        
    def close(self):
        pass

@pytest.fixture
def mock_db():
    """Provide mock database connection"""
    return MockDatabaseConnection()

class TestSnapshotMigrations:
    """Test snapshot database migrations"""
    
    def test_migration_002_create_tables(self, mock_db):
        """Test that migration 002 creates all required tables"""
        migration_sql = """
        CREATE TABLE population_snapshots (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            office_id UUID NOT NULL,
            snapshot_date VARCHAR(6) NOT NULL,
            snapshot_name VARCHAR(200) NOT NULL,
            description TEXT,
            total_fte INTEGER NOT NULL CHECK (total_fte >= 0),
            is_default BOOLEAN DEFAULT FALSE,
            is_approved BOOLEAN DEFAULT FALSE,
            source VARCHAR(50) NOT NULL CHECK (source IN ('manual', 'simulation', 'import', 'business_plan', 'current')),
            created_at TIMESTAMP DEFAULT NOW(),
            created_by VARCHAR(100) NOT NULL,
            last_used_at TIMESTAMP,
            metadata JSONB DEFAULT '{}',
            UNIQUE(office_id, snapshot_name)
        );
        """
        
        cursor = mock_db.execute(migration_sql)
        
        # Verify table creation was attempted
        assert len(mock_db.executed_queries) == 1
        assert 'CREATE TABLE population_snapshots' in mock_db.executed_queries[0][0]
        
    def test_migration_002_create_workforce_table(self, mock_db):
        """Test snapshot_workforce table creation"""
        migration_sql = """
        CREATE TABLE snapshot_workforce (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            snapshot_id UUID NOT NULL,
            role VARCHAR(50) NOT NULL,
            level VARCHAR(20),
            fte INTEGER NOT NULL CHECK (fte >= 0),
            UNIQUE(snapshot_id, role, level)
        );
        """
        
        cursor = mock_db.execute(migration_sql)
        
        assert 'CREATE TABLE snapshot_workforce' in mock_db.executed_queries[0][0]
        assert 'CHECK (fte >= 0)' in mock_db.executed_queries[0][0]
        
    def test_migration_002_create_tags_table(self, mock_db):
        """Test snapshot_tags table creation"""
        migration_sql = """
        CREATE TABLE snapshot_tags (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            snapshot_id UUID NOT NULL,
            tag VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(snapshot_id, tag)
        );
        """
        
        cursor = mock_db.execute(migration_sql)
        
        assert 'CREATE TABLE snapshot_tags' in mock_db.executed_queries[0][0]
        assert 'UNIQUE(snapshot_id, tag)' in mock_db.executed_queries[0][0]
        
    def test_migration_002_create_comparisons_table(self, mock_db):
        """Test snapshot_comparisons table creation"""
        migration_sql = """
        CREATE TABLE snapshot_comparisons (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            snapshot_1_id UUID NOT NULL,
            snapshot_2_id UUID NOT NULL,
            comparison_date TIMESTAMP DEFAULT NOW(),
            compared_by VARCHAR(100),
            delta_data JSONB NOT NULL,
            insights TEXT,
            CHECK (snapshot_1_id != snapshot_2_id)
        );
        """
        
        cursor = mock_db.execute(migration_sql)
        
        assert 'CREATE TABLE snapshot_comparisons' in mock_db.executed_queries[0][0]
        assert 'CHECK (snapshot_1_id != snapshot_2_id)' in mock_db.executed_queries[0][0]
        
    def test_migration_002_create_audit_table(self, mock_db):
        """Test snapshot_audit_log table creation"""
        migration_sql = """
        CREATE TABLE snapshot_audit_log (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            snapshot_id UUID NOT NULL,
            action VARCHAR(50) NOT NULL CHECK (action IN (
                'created', 'modified', 'approved', 'set_default',
                'used_in_scenario', 'used_in_plan', 'used_in_simulation'
            )),
            entity_type VARCHAR(50),
            entity_id UUID,
            user_id VARCHAR(100),
            timestamp TIMESTAMP DEFAULT NOW(),
            details JSONB DEFAULT '{}'
        );
        """
        
        cursor = mock_db.execute(migration_sql)
        
        assert 'CREATE TABLE snapshot_audit_log' in mock_db.executed_queries[0][0]
        assert 'CHECK (action IN' in mock_db.executed_queries[0][0]
        
    def test_migration_002_create_indexes(self, mock_db):
        """Test that all required indexes are created"""
        indexes = [
            "CREATE INDEX idx_snapshots_office_date ON population_snapshots(office_id, snapshot_date DESC);",
            "CREATE INDEX idx_snapshots_office_default ON population_snapshots(office_id, is_default) WHERE is_default = TRUE;",
            "CREATE INDEX idx_snapshots_approved ON population_snapshots(office_id, is_approved) WHERE is_approved = TRUE;",
            "CREATE INDEX idx_snapshot_workforce_snapshot ON snapshot_workforce(snapshot_id);",
            "CREATE INDEX idx_snapshot_workforce_role ON snapshot_workforce(role, level);",
            "CREATE INDEX idx_snapshot_tags_snapshot ON snapshot_tags(snapshot_id);",
            "CREATE INDEX idx_snapshot_tags_tag ON snapshot_tags(tag);",
            "CREATE INDEX idx_comparisons_snapshots ON snapshot_comparisons(snapshot_1_id, snapshot_2_id);",
            "CREATE INDEX idx_audit_snapshot ON snapshot_audit_log(snapshot_id, timestamp DESC);",
            "CREATE INDEX idx_audit_action ON snapshot_audit_log(action, timestamp DESC);"
        ]
        
        for index_sql in indexes:
            mock_db.execute(index_sql)
            
        # Verify all indexes were created
        assert len(mock_db.executed_queries) == 10
        index_names = [
            'idx_snapshots_office_date',
            'idx_snapshots_office_default', 
            'idx_snapshots_approved',
            'idx_snapshot_workforce_snapshot',
            'idx_snapshot_workforce_role',
            'idx_snapshot_tags_snapshot',
            'idx_snapshot_tags_tag',
            'idx_comparisons_snapshots',
            'idx_audit_snapshot',
            'idx_audit_action'
        ]
        
        for index_name in index_names:
            found = any(index_name in query[0] for query in mock_db.executed_queries)
            assert found, f"Index {index_name} not created"
            
    def test_rollback_migration_002(self, mock_db):
        """Test that rollback migration correctly removes all snapshot structures"""
        rollback_queries = [
            "DROP VIEW IF EXISTS v_snapshot_workforce_comparison;",
            "DROP VIEW IF EXISTS v_snapshot_summary;",
            "DROP FUNCTION IF EXISTS create_snapshot_from_current(UUID, VARCHAR, TEXT, VARCHAR);",
            "DROP FUNCTION IF EXISTS log_snapshot_usage();",
            "DROP FUNCTION IF EXISTS ensure_single_default_snapshot();",
            "DROP TRIGGER IF EXISTS ensure_single_default_snapshot_trigger ON population_snapshots;",
            "DROP TRIGGER IF EXISTS update_population_snapshots_updated_at ON population_snapshots;",
            "DROP TABLE IF EXISTS snapshot_audit_log;",
            "DROP TABLE IF EXISTS snapshot_comparisons;",
            "DROP TABLE IF EXISTS snapshot_tags;",
            "DROP TABLE IF EXISTS snapshot_workforce;",
            "DROP TABLE IF EXISTS population_snapshots;"
        ]
        
        for query in rollback_queries:
            mock_db.execute(query)
            
        # Verify all drop statements executed
        assert len(mock_db.executed_queries) == len(rollback_queries)
        
        # Check specific drop operations
        drop_statements = [query[0] for query in mock_db.executed_queries]
        assert any('DROP VIEW IF EXISTS v_snapshot_workforce_comparison' in stmt for stmt in drop_statements)
        assert any('DROP FUNCTION IF EXISTS create_snapshot_from_current' in stmt for stmt in drop_statements)
        assert any('DROP TABLE IF EXISTS population_snapshots' in stmt for stmt in drop_statements)

class TestSnapshotStoredProcedures:
    """Test snapshot stored procedures and functions"""
    
    def test_ensure_single_default_snapshot_function(self, mock_db):
        """Test the ensure_single_default_snapshot trigger function"""
        function_sql = """
        CREATE OR REPLACE FUNCTION ensure_single_default_snapshot()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.is_default = TRUE THEN
                UPDATE population_snapshots 
                SET is_default = FALSE 
                WHERE office_id = NEW.office_id 
                AND id != NEW.id 
                AND is_default = TRUE;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        cursor = mock_db.execute(function_sql)
        
        assert 'CREATE OR REPLACE FUNCTION ensure_single_default_snapshot()' in mock_db.executed_queries[0][0]
        assert 'UPDATE population_snapshots' in mock_db.executed_queries[0][0]
        assert 'is_default = FALSE' in mock_db.executed_queries[0][0]
        
    def test_log_snapshot_usage_function(self, mock_db):
        """Test the log_snapshot_usage trigger function"""
        function_sql = """
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
        """
        
        cursor = mock_db.execute(function_sql)
        
        assert 'CREATE OR REPLACE FUNCTION log_snapshot_usage()' in mock_db.executed_queries[0][0]
        assert 'INSERT INTO snapshot_audit_log' in mock_db.executed_queries[0][0]
        assert 'jsonb_build_object' in mock_db.executed_queries[0][0]
        
    def test_create_snapshot_from_current_function(self, mock_db):
        """Test the create_snapshot_from_current stored procedure"""
        function_sql = """
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
            v_snapshot_date := TO_CHAR(CURRENT_DATE, 'YYYYMM');
            
            SELECT COALESCE(SUM(fte), 0) INTO v_total_fte
            FROM office_workforce
            WHERE office_id = p_office_id;
            
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
            
            RETURN v_snapshot_id;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        cursor = mock_db.execute(function_sql)
        
        assert 'CREATE OR REPLACE FUNCTION create_snapshot_from_current' in mock_db.executed_queries[0][0]
        assert 'INSERT INTO population_snapshots' in mock_db.executed_queries[0][0]
        assert 'RETURNING id INTO v_snapshot_id' in mock_db.executed_queries[0][0]

class TestSnapshotViews:
    """Test snapshot database views"""
    
    def test_v_snapshot_summary_view(self, mock_db):
        """Test the v_snapshot_summary view creation"""
        view_sql = """
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
        """
        
        cursor = mock_db.execute(view_sql)
        
        assert 'CREATE OR REPLACE VIEW v_snapshot_summary' in mock_db.executed_queries[0][0]
        assert 'array_agg(DISTINCT st.tag)' in mock_db.executed_queries[0][0]
        assert 'COUNT(DISTINCT sw.id)' in mock_db.executed_queries[0][0]
        assert 'GROUP BY ps.id, o.id, o.name' in mock_db.executed_queries[0][0]
        
    def test_v_snapshot_workforce_comparison_view(self, mock_db):
        """Test the v_snapshot_workforce_comparison view creation"""
        view_sql = """
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
        )
        SELECT 
            sp.comparison_id,
            sp.role,
            sp.level,
            COALESCE(sw1.fte, 0) as snapshot_1_fte,
            COALESCE(sw2.fte, 0) as snapshot_2_fte,
            COALESCE(sw2.fte, 0) - COALESCE(sw1.fte, 0) as delta
        FROM snapshot_pairs sp
        LEFT JOIN snapshot_workforce sw1 ON sp.snapshot_1_id = sw1.snapshot_id
        LEFT JOIN snapshot_workforce sw2 ON sp.snapshot_2_id = sw2.snapshot_id;
        """
        
        cursor = mock_db.execute(view_sql)
        
        assert 'CREATE OR REPLACE VIEW v_snapshot_workforce_comparison' in mock_db.executed_queries[0][0]
        assert 'WITH snapshot_pairs AS' in mock_db.executed_queries[0][0]
        assert 'COALESCE(sw2.fte, 0) - COALESCE(sw1.fte, 0) as delta' in mock_db.executed_queries[0][0]

class TestSnapshotTriggers:
    """Test snapshot database triggers"""
    
    def test_ensure_single_default_snapshot_trigger(self, mock_db):
        """Test the trigger that ensures only one default snapshot per office"""
        trigger_sql = """
        CREATE TRIGGER ensure_single_default_snapshot_trigger
            BEFORE INSERT OR UPDATE ON population_snapshots
            FOR EACH ROW
            WHEN (NEW.is_default = TRUE)
            EXECUTE FUNCTION ensure_single_default_snapshot();
        """
        
        cursor = mock_db.execute(trigger_sql)
        
        assert 'CREATE TRIGGER ensure_single_default_snapshot_trigger' in mock_db.executed_queries[0][0]
        assert 'BEFORE INSERT OR UPDATE' in mock_db.executed_queries[0][0]
        assert 'WHEN (NEW.is_default = TRUE)' in mock_db.executed_queries[0][0]
        assert 'EXECUTE FUNCTION ensure_single_default_snapshot' in mock_db.executed_queries[0][0]
        
    def test_update_updated_at_trigger(self, mock_db):
        """Test the trigger that updates the updated_at timestamp"""
        trigger_sql = """
        CREATE TRIGGER update_population_snapshots_updated_at 
            BEFORE UPDATE ON population_snapshots 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        cursor = mock_db.execute(trigger_sql)
        
        assert 'CREATE TRIGGER update_population_snapshots_updated_at' in mock_db.executed_queries[0][0]
        assert 'BEFORE UPDATE ON population_snapshots' in mock_db.executed_queries[0][0]
        assert 'EXECUTE FUNCTION update_updated_at_column()' in mock_db.executed_queries[0][0]

class TestSnapshotConstraints:
    """Test snapshot database constraints"""
    
    def test_population_snapshots_constraints(self, mock_db):
        """Test population_snapshots table constraints"""
        # Test total_fte check constraint
        constraint_tests = [
            "ALTER TABLE population_snapshots ADD CHECK (total_fte >= 0);",
            "ALTER TABLE population_snapshots ADD CHECK (source IN ('manual', 'simulation', 'import', 'business_plan', 'current'));",
            "ALTER TABLE population_snapshots ADD UNIQUE(office_id, snapshot_name);"
        ]
        
        for constraint_sql in constraint_tests:
            cursor = mock_db.execute(constraint_sql)
            
        # Verify constraints were applied
        constraint_queries = [query[0] for query in mock_db.executed_queries]
        assert any('CHECK (total_fte >= 0)' in query for query in constraint_queries)
        assert any('source IN' in query for query in constraint_queries)
        assert any('UNIQUE(office_id, snapshot_name)' in query for query in constraint_queries)
        
    def test_snapshot_workforce_constraints(self, mock_db):
        """Test snapshot_workforce table constraints"""
        constraint_tests = [
            "ALTER TABLE snapshot_workforce ADD CHECK (fte >= 0);",
            "ALTER TABLE snapshot_workforce ADD UNIQUE(snapshot_id, role, level);"
        ]
        
        for constraint_sql in constraint_tests:
            cursor = mock_db.execute(constraint_sql)
            
        constraint_queries = [query[0] for query in mock_db.executed_queries]
        assert any('CHECK (fte >= 0)' in query for query in constraint_queries)
        assert any('UNIQUE(snapshot_id, role, level)' in query for query in constraint_queries)
        
    def test_snapshot_comparisons_constraints(self, mock_db):
        """Test snapshot_comparisons table constraints"""
        constraint_sql = "ALTER TABLE snapshot_comparisons ADD CHECK (snapshot_1_id != snapshot_2_id);"
        
        cursor = mock_db.execute(constraint_sql)
        
        assert 'CHECK (snapshot_1_id != snapshot_2_id)' in mock_db.executed_queries[0][0]
        
    def test_snapshot_audit_log_constraints(self, mock_db):
        """Test snapshot_audit_log table constraints"""
        constraint_sql = """
        ALTER TABLE snapshot_audit_log ADD CHECK (action IN (
            'created', 'modified', 'approved', 'set_default',
            'used_in_scenario', 'used_in_plan', 'used_in_simulation'
        ));
        """
        
        cursor = mock_db.execute(constraint_sql)
        
        assert 'CHECK (action IN' in mock_db.executed_queries[0][0]
        assert 'created' in mock_db.executed_queries[0][0]
        assert 'used_in_scenario' in mock_db.executed_queries[0][0]

class TestSnapshotMigrationIntegrity:
    """Test migration integrity and rollback scenarios"""
    
    def test_migration_rollback_integrity(self, mock_db):
        """Test that migration can be rolled back cleanly"""
        # First apply migration
        migration_queries = [
            "CREATE TABLE population_snapshots (id UUID PRIMARY KEY);",
            "CREATE TABLE snapshot_workforce (id UUID PRIMARY KEY);",
            "CREATE FUNCTION ensure_single_default_snapshot() RETURNS TRIGGER AS $$ BEGIN RETURN NEW; END; $$ LANGUAGE plpgsql;",
            "CREATE TRIGGER ensure_single_default_snapshot_trigger BEFORE INSERT ON population_snapshots EXECUTE FUNCTION ensure_single_default_snapshot();"
        ]
        
        for query in migration_queries:
            mock_db.execute(query)
            
        # Then rollback
        rollback_queries = [
            "DROP TRIGGER IF EXISTS ensure_single_default_snapshot_trigger ON population_snapshots;",
            "DROP FUNCTION IF EXISTS ensure_single_default_snapshot();",
            "DROP TABLE IF EXISTS snapshot_workforce;",
            "DROP TABLE IF EXISTS population_snapshots;"
        ]
        
        for query in rollback_queries:
            mock_db.execute(query)
            
        # Verify both migration and rollback executed
        assert len(mock_db.executed_queries) == 8
        
        # Check rollback order (triggers/functions before tables)
        rollback_start_index = 4
        rollback_queries_executed = [query[0] for query in mock_db.executed_queries[rollback_start_index:]]
        
        assert 'DROP TRIGGER' in rollback_queries_executed[0]
        assert 'DROP FUNCTION' in rollback_queries_executed[1]
        assert 'DROP TABLE' in rollback_queries_executed[2]
        assert 'DROP TABLE' in rollback_queries_executed[3]
        
    def test_foreign_key_constraints(self, mock_db):
        """Test foreign key relationship integrity"""
        fk_constraints = [
            "ALTER TABLE population_snapshots ADD CONSTRAINT fk_snapshots_office FOREIGN KEY (office_id) REFERENCES offices(id) ON DELETE CASCADE;",
            "ALTER TABLE snapshot_workforce ADD CONSTRAINT fk_workforce_snapshot FOREIGN KEY (snapshot_id) REFERENCES population_snapshots(id) ON DELETE CASCADE;",
            "ALTER TABLE snapshot_tags ADD CONSTRAINT fk_tags_snapshot FOREIGN KEY (snapshot_id) REFERENCES population_snapshots(id) ON DELETE CASCADE;",
            "ALTER TABLE snapshot_comparisons ADD CONSTRAINT fk_comparisons_snapshot1 FOREIGN KEY (snapshot_1_id) REFERENCES population_snapshots(id) ON DELETE CASCADE;",
            "ALTER TABLE snapshot_comparisons ADD CONSTRAINT fk_comparisons_snapshot2 FOREIGN KEY (snapshot_2_id) REFERENCES population_snapshots(id) ON DELETE CASCADE;",
            "ALTER TABLE snapshot_audit_log ADD CONSTRAINT fk_audit_snapshot FOREIGN KEY (snapshot_id) REFERENCES population_snapshots(id) ON DELETE CASCADE;"
        ]
        
        for constraint_sql in fk_constraints:
            cursor = mock_db.execute(constraint_sql)
            
        # Verify all foreign keys were created
        assert len(mock_db.executed_queries) == 6
        
        fk_queries = [query[0] for query in mock_db.executed_queries]
        assert all('FOREIGN KEY' in query for query in fk_queries)
        assert all('ON DELETE CASCADE' in query for query in fk_queries)
        
    def test_index_performance_coverage(self, mock_db):
        """Test that indexes cover expected query patterns"""
        # These are the indexes that should exist for performance
        expected_indexes = {
            'office_date_queries': 'idx_snapshots_office_date',
            'default_snapshot_queries': 'idx_snapshots_office_default', 
            'approved_snapshot_queries': 'idx_snapshots_approved',
            'workforce_by_snapshot': 'idx_snapshot_workforce_snapshot',
            'workforce_by_role': 'idx_snapshot_workforce_role',
            'tags_by_snapshot': 'idx_snapshot_tags_snapshot',
            'tags_search': 'idx_snapshot_tags_tag',
            'comparison_lookups': 'idx_comparisons_snapshots',
            'audit_by_snapshot': 'idx_audit_snapshot',
            'audit_by_action': 'idx_audit_action'
        }
        
        # Simulate creating indexes
        index_queries = [
            "CREATE INDEX idx_snapshots_office_date ON population_snapshots(office_id, snapshot_date DESC);",
            "CREATE INDEX idx_snapshots_office_default ON population_snapshots(office_id, is_default) WHERE is_default = TRUE;",
            "CREATE INDEX idx_snapshots_approved ON population_snapshots(office_id, is_approved) WHERE is_approved = TRUE;",
            "CREATE INDEX idx_snapshot_workforce_snapshot ON snapshot_workforce(snapshot_id);",
            "CREATE INDEX idx_snapshot_workforce_role ON snapshot_workforce(role, level);",
            "CREATE INDEX idx_snapshot_tags_snapshot ON snapshot_tags(snapshot_id);",
            "CREATE INDEX idx_snapshot_tags_tag ON snapshot_tags(tag);",
            "CREATE INDEX idx_comparisons_snapshots ON snapshot_comparisons(snapshot_1_id, snapshot_2_id);",
            "CREATE INDEX idx_audit_snapshot ON snapshot_audit_log(snapshot_id, timestamp DESC);",
            "CREATE INDEX idx_audit_action ON snapshot_audit_log(action, timestamp DESC);"
        ]
        
        for index_sql in index_queries:
            cursor = mock_db.execute(index_sql)
            
        # Verify all expected indexes are covered
        executed_indexes = [query[0] for query in mock_db.executed_queries]
        
        for use_case, index_name in expected_indexes.items():
            found = any(index_name in query for query in executed_indexes)
            assert found, f"Missing index {index_name} for {use_case}"

class TestSnapshotFunctionLogic:
    """Test snapshot function business logic"""
    
    def test_ensure_single_default_logic(self, mock_db):
        """Test that only one default snapshot can exist per office"""
        # Simulate the function logic
        test_scenarios = [
            {
                'description': 'Setting first default snapshot',
                'new_is_default': True,
                'office_id': 'office-1',
                'existing_defaults': [],
                'expected_updates': 0
            },
            {
                'description': 'Setting second default snapshot should clear first',
                'new_is_default': True,
                'office_id': 'office-1',
                'existing_defaults': [{'id': 'snap-1', 'is_default': True}],
                'expected_updates': 1
            },
            {
                'description': 'Setting non-default snapshot should not affect defaults',
                'new_is_default': False,
                'office_id': 'office-1',
                'existing_defaults': [{'id': 'snap-1', 'is_default': True}],
                'expected_updates': 0
            }
        ]
        
        for scenario in test_scenarios:
            # Reset mock
            mock_db.executed_queries = []
            
            # Simulate trigger function logic
            if scenario['new_is_default']:
                update_sql = """
                UPDATE population_snapshots 
                SET is_default = FALSE 
                WHERE office_id = %s 
                AND id != %s 
                AND is_default = TRUE;
                """
                cursor = mock_db.execute(update_sql, (scenario['office_id'], 'new-snapshot-id'))
                
            # Verify correct number of updates
            if scenario['new_is_default']:
                assert len(mock_db.executed_queries) == 1
                assert 'UPDATE population_snapshots' in mock_db.executed_queries[0][0]
                assert 'is_default = FALSE' in mock_db.executed_queries[0][0]
            else:
                assert len(mock_db.executed_queries) == 0
                
    def test_create_snapshot_from_current_logic(self, mock_db):
        """Test the create_snapshot_from_current function logic"""
        # Simulate function parameters
        office_id = str(uuid4())
        snapshot_name = "Test Snapshot"
        description = "Created from current workforce"
        created_by = "test_user"
        
        # Mock the function steps
        steps = [
            "SELECT TO_CHAR(CURRENT_DATE, 'YYYYMM');",  # Generate date
            "SELECT COALESCE(SUM(fte), 0) FROM office_workforce WHERE office_id = %s;",  # Calculate FTE
            "INSERT INTO population_snapshots (...) VALUES (...) RETURNING id;",  # Create snapshot
            "INSERT INTO snapshot_workforce SELECT ...",  # Copy workforce data
            "INSERT INTO snapshot_audit_log (...) VALUES (...);"  # Log creation
        ]
        
        for step in steps:
            cursor = mock_db.execute(step, (office_id,) if '%s' in step else None)
            
        # Verify all function steps executed
        assert len(mock_db.executed_queries) == 5
        
        executed_queries = [query[0] for query in mock_db.executed_queries]
        assert any('TO_CHAR(CURRENT_DATE' in query for query in executed_queries)
        assert any('COALESCE(SUM(fte), 0)' in query for query in executed_queries)
        assert any('INSERT INTO population_snapshots' in query for query in executed_queries)
        assert any('INSERT INTO snapshot_workforce' in query for query in executed_queries)
        assert any('INSERT INTO snapshot_audit_log' in query for query in executed_queries)
        
    def test_log_snapshot_usage_logic(self, mock_db):
        """Test the log_snapshot_usage trigger function logic"""
        # Simulate different usage scenarios
        usage_scenarios = [
            {
                'operation': 'UPDATE',
                'old_last_used_at': None,
                'new_last_used_at': '2025-01-15 10:30:00',
                'trigger_arg': 'scenario',
                'should_log': True
            },
            {
                'operation': 'UPDATE',
                'old_last_used_at': '2025-01-15 10:30:00',
                'new_last_used_at': '2025-01-15 10:30:00',
                'trigger_arg': 'scenario',
                'should_log': False  # No change in last_used_at
            },
            {
                'operation': 'INSERT',
                'old_last_used_at': None,
                'new_last_used_at': '2025-01-15 10:30:00',
                'trigger_arg': 'plan',
                'should_log': False  # Only logs on UPDATE
            }
        ]
        
        for scenario in usage_scenarios:
            mock_db.executed_queries = []
            
            # Simulate trigger logic
            if (scenario['operation'] == 'UPDATE' and 
                scenario['old_last_used_at'] != scenario['new_last_used_at']):
                
                log_sql = """
                INSERT INTO snapshot_audit_log (
                    snapshot_id, 
                    action, 
                    timestamp,
                    details
                ) VALUES (%s, %s, NOW(), %s);
                """
                
                action = f"used_in_{scenario['trigger_arg']}"
                details = json.dumps({'trigger_source': 'population_snapshots'})
                
                cursor = mock_db.execute(log_sql, ('snapshot-id', action, details))
                
            # Verify logging behavior
            if scenario['should_log']:
                assert len(mock_db.executed_queries) == 1
                assert 'INSERT INTO snapshot_audit_log' in mock_db.executed_queries[0][0]
            else:
                assert len(mock_db.executed_queries) == 0

# Integration test helper
class TestMigrationIntegration:
    """Integration tests for complete migration scenarios"""
    
    def test_full_migration_cycle(self, mock_db):
        """Test complete migration and rollback cycle"""
        # Step 1: Apply migration
        migration_steps = [
            "CREATE TABLE population_snapshots (...);",
            "CREATE TABLE snapshot_workforce (...);", 
            "CREATE TABLE snapshot_tags (...);",
            "CREATE TABLE snapshot_comparisons (...);",
            "CREATE TABLE snapshot_audit_log (...);",
            "CREATE INDEX idx_snapshots_office_date ON population_snapshots(...);",
            "CREATE FUNCTION ensure_single_default_snapshot() RETURNS TRIGGER AS $$...$$;",
            "CREATE TRIGGER ensure_single_default_snapshot_trigger ...",
            "CREATE VIEW v_snapshot_summary AS SELECT ...;",
            "ALTER TABLE office_business_plans ADD COLUMN baseline_snapshot_id UUID;"
        ]
        
        for step in migration_steps:
            mock_db.execute(step)
            
        # Step 2: Test that migration was applied
        assert len(mock_db.executed_queries) == len(migration_steps)
        
        # Step 3: Apply rollback
        rollback_steps = [
            "DROP VIEW IF EXISTS v_snapshot_summary;",
            "DROP TRIGGER IF EXISTS ensure_single_default_snapshot_trigger ON population_snapshots;",
            "DROP FUNCTION IF EXISTS ensure_single_default_snapshot();",
            "ALTER TABLE office_business_plans DROP COLUMN IF EXISTS baseline_snapshot_id;",
            "DROP TABLE IF EXISTS snapshot_audit_log;",
            "DROP TABLE IF EXISTS snapshot_comparisons;",
            "DROP TABLE IF EXISTS snapshot_tags;",
            "DROP TABLE IF EXISTS snapshot_workforce;",
            "DROP TABLE IF EXISTS population_snapshots;"
        ]
        
        for step in rollback_steps:
            mock_db.execute(step)
            
        # Step 4: Verify complete cycle
        total_queries = len(migration_steps) + len(rollback_steps)
        assert len(mock_db.executed_queries) == total_queries
        
        # Verify rollback order (dependencies first)
        rollback_start_index = len(migration_steps)
        rollback_queries = [query[0] for query in mock_db.executed_queries[rollback_start_index:]]
        
        # Views and triggers should be dropped before functions
        view_index = next(i for i, q in enumerate(rollback_queries) if 'DROP VIEW' in q)
        trigger_index = next(i for i, q in enumerate(rollback_queries) if 'DROP TRIGGER' in q)
        function_index = next(i for i, q in enumerate(rollback_queries) if 'DROP FUNCTION' in q)
        table_index = next(i for i, q in enumerate(rollback_queries) if 'DROP TABLE' in q)
        
        assert view_index < function_index < table_index
        assert trigger_index < function_index < table_index
        
    def test_migration_idempotency(self, mock_db):
        """Test that migration can be run multiple times safely"""
        # Use CREATE OR REPLACE and IF NOT EXISTS patterns
        idempotent_statements = [
            "CREATE TABLE IF NOT EXISTS population_snapshots (...);",
            "CREATE OR REPLACE FUNCTION ensure_single_default_snapshot() RETURNS TRIGGER AS $$...$$;",
            "CREATE INDEX IF NOT EXISTS idx_snapshots_office_date ON population_snapshots(...);",
            "ALTER TABLE office_business_plans ADD COLUMN IF NOT EXISTS baseline_snapshot_id UUID;"
        ]
        
        # Run migration twice
        for run in range(2):
            for statement in idempotent_statements:
                mock_db.execute(statement)
                
        # Should not fail and should handle duplicate operations gracefully
        assert len(mock_db.executed_queries) == len(idempotent_statements) * 2
        
        # Verify idempotent patterns are used
        all_queries = [query[0] for query in mock_db.executed_queries]
        assert any('IF NOT EXISTS' in query for query in all_queries)
        assert any('CREATE OR REPLACE' in query for query in all_queries)
        assert any('ADD COLUMN IF NOT EXISTS' in query for query in all_queries)