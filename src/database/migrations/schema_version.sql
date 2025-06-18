-- Schema Version Table for Influencer News CMS
-- This table tracks the current database schema version
-- to enable safe migrations and updates

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    migration_name TEXT NOT NULL,
    checksum TEXT,
    description TEXT
);

-- Insert initial version
INSERT OR IGNORE INTO schema_version (version, migration_name, description) 
VALUES (1, '001_initial_schema.sql', 'Initial database schema with all core tables');