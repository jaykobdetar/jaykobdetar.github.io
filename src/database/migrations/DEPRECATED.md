# Deprecated Migration Files

## schema_upgrade.sql - REMOVED
This file contained an incomplete upgrade script that could not perform all necessary schema changes (column renames, etc.). 

**Replacement**: Use the full migration script `migrate_schema.py` which performs a complete data migration from any existing schema to the current `schema.sql`.

## Schema Standardization
As of January 2025, `schema.sql` is the single source of truth for the database schema. All other schema files have been consolidated to match this file.

### Migration Process
1. **For new installations**: Run `python scripts/sync_content.py` - this will automatically create the database with the correct schema
2. **For existing installations**: Run `python scripts/database/migrate_schema.py` - this will backup existing data and migrate to the new schema

### Files Removed
- `schema_upgrade.sql` - Incomplete upgrade script
- No other files removed, but `schema_new.sql` has been updated to match `schema.sql`