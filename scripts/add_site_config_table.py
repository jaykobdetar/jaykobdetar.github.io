#!/usr/bin/env python3
"""
Add site_config table to existing database
"""

import sqlite3
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.database import DatabaseManager
except ImportError:
    # Fallback import
    import os
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(script_dir, '..', 'src')
    sys.path.insert(0, src_dir)
    from database import DatabaseManager

def add_site_config_table():
    """Add site_config table and indexes to database"""
    db = DatabaseManager()
    
    print("Adding site_config table to database...")
    
    try:
        with db.get_connection() as conn:
            # Check if table already exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='site_config'
            """)
            
            if cursor.fetchone():
                print("✓ site_config table already exists")
                return True
            
            # Create site_config table
            conn.execute("""
                CREATE TABLE site_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_type TEXT NOT NULL,        -- 'branding', 'contact', 'navigation', 'content'
                    config_key TEXT NOT NULL,         -- specific setting name
                    config_value TEXT,                -- setting value
                    description TEXT,                 -- human-readable description
                    is_active BOOLEAN DEFAULT 1,
                    last_modified TEXT,               -- track source file modifications
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(config_type, config_key)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX idx_site_config_type ON site_config(config_type)")
            conn.execute("CREATE INDEX idx_site_config_key ON site_config(config_key)")
            conn.execute("CREATE INDEX idx_site_config_active ON site_config(is_active)")
            
            # Create trigger for updating timestamps
            conn.execute("""
                CREATE TRIGGER update_site_config_timestamp 
                AFTER UPDATE ON site_config
                BEGIN
                    UPDATE site_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """)
            
            conn.commit()
            print("✓ Successfully added site_config table with indexes and triggers")
            return True
            
    except Exception as e:
        print(f"✗ Error adding site_config table: {e}")
        return False

if __name__ == "__main__":
    success = add_site_config_table()
    sys.exit(0 if success else 1)