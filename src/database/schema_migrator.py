#!/usr/bin/env python3
"""
Schema Migration System for Influencer News CMS
Provides version control and safe upgrades for database schema
"""

import sqlite3
import hashlib
import os
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SchemaMigrator:
    """Manages database schema versions and migrations"""
    
    def __init__(self, db_path: str, migrations_dir: str = None):
        self.db_path = db_path
        self.migrations_dir = migrations_dir or os.path.join(
            os.path.dirname(__file__), 'migrations'
        )
        self._ensure_version_table()
    
    def _ensure_version_table(self):
        """Create schema_version table if it doesn't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    migration_name TEXT NOT NULL,
                    checksum TEXT,
                    description TEXT
                )
            """)
            conn.commit()
    
    def get_current_version(self) -> int:
        """Get the current schema version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT MAX(version) FROM schema_version"
            )
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
    
    def get_pending_migrations(self) -> List[Tuple[int, str, str]]:
        """Get list of migrations that haven't been applied yet"""
        current_version = self.get_current_version()
        pending = []
        
        # Get all SQL files in migrations directory
        migration_files = sorted([
            f for f in os.listdir(self.migrations_dir) 
            if f.endswith('.sql') and f[0:3].isdigit()
        ])
        
        for filename in migration_files:
            # Extract version number from filename (e.g., "002_add_mobile_fields.sql")
            try:
                version = int(filename.split('_')[0])
                if version > current_version:
                    filepath = os.path.join(self.migrations_dir, filename)
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    # Extract description from first comment line
                    description = "No description"
                    for line in content.split('\n'):
                        if line.strip().startswith('--') and not line.strip().startswith('---'):
                            description = line.strip()[2:].strip()
                            break
                    
                    pending.append((version, filename, description))
            except (ValueError, IndexError):
                logger.warning(f"Skipping invalid migration filename: {filename}")
        
        return pending
    
    def apply_migration(self, version: int, filename: str, dry_run: bool = False) -> bool:
        """Apply a single migration"""
        filepath = os.path.join(self.migrations_dir, filename)
        
        if not os.path.exists(filepath):
            logger.error(f"Migration file not found: {filepath}")
            return False
        
        with open(filepath, 'r') as f:
            sql_content = f.read()
        
        # Calculate checksum
        checksum = hashlib.md5(sql_content.encode()).hexdigest()
        
        if dry_run:
            logger.info(f"[DRY RUN] Would apply migration {version}: {filename}")
            return True
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Begin transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Execute migration SQL
                conn.executescript(sql_content)
                
                # Record migration
                conn.execute("""
                    INSERT INTO schema_version (version, migration_name, checksum, description)
                    VALUES (?, ?, ?, ?)
                """, (version, filename, checksum, f"Migration {version}"))
                
                conn.commit()
                logger.info(f"Successfully applied migration {version}: {filename}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            return False
    
    def migrate_to_latest(self, dry_run: bool = False) -> bool:
        """Apply all pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("Database is already at the latest version")
            return True
        
        logger.info(f"Found {len(pending)} pending migrations")
        
        for version, filename, description in pending:
            logger.info(f"Applying migration {version}: {description}")
            if not self.apply_migration(version, filename, dry_run):
                logger.error(f"Migration failed at version {version}")
                return False
        
        if not dry_run:
            logger.info(f"Successfully migrated to version {self.get_current_version()}")
        
        return True
    
    def rollback_to_version(self, target_version: int) -> bool:
        """Rollback to a specific version (if rollback scripts exist)"""
        current = self.get_current_version()
        
        if target_version >= current:
            logger.error(f"Cannot rollback to version {target_version} (current: {current})")
            return False
        
        # Look for rollback scripts
        for version in range(current, target_version, -1):
            rollback_file = os.path.join(
                self.migrations_dir, 
                f"rollback_{version:03d}.sql"
            )
            
            if not os.path.exists(rollback_file):
                logger.error(f"Rollback script not found for version {version}")
                return False
            
            try:
                with open(rollback_file, 'r') as f:
                    sql_content = f.read()
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.executescript(sql_content)
                    conn.execute(
                        "DELETE FROM schema_version WHERE version = ?",
                        (version,)
                    )
                    conn.commit()
                    
                logger.info(f"Rolled back version {version}")
                
            except Exception as e:
                logger.error(f"Rollback failed for version {version}: {e}")
                return False
        
        return True
    
    def get_migration_history(self) -> List[dict]:
        """Get the history of applied migrations"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT version, applied_at, migration_name, checksum, description
                FROM schema_version
                ORDER BY version DESC
            """)
            return [dict(row) for row in cursor.fetchall()]


def main():
    """Command line interface for schema migrations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Schema Migration Tool')
    parser.add_argument('command', choices=['status', 'migrate', 'history', 'rollback'],
                        help='Command to execute')
    parser.add_argument('--db', default='data/infnews.db',
                        help='Path to database file')
    parser.add_argument('--migrations-dir', 
                        help='Path to migrations directory')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without executing')
    parser.add_argument('--target-version', type=int,
                        help='Target version for rollback')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    migrator = SchemaMigrator(args.db, args.migrations_dir)
    
    if args.command == 'status':
        current = migrator.get_current_version()
        pending = migrator.get_pending_migrations()
        
        print(f"Current schema version: {current}")
        print(f"Pending migrations: {len(pending)}")
        
        if pending:
            print("\nPending migrations:")
            for version, filename, description in pending:
                print(f"  {version}: {filename} - {description}")
    
    elif args.command == 'migrate':
        success = migrator.migrate_to_latest(dry_run=args.dry_run)
        if not success:
            exit(1)
    
    elif args.command == 'history':
        history = migrator.get_migration_history()
        if not history:
            print("No migrations have been applied")
        else:
            print("Migration History:")
            for entry in history:
                print(f"  Version {entry['version']}: {entry['migration_name']}")
                print(f"    Applied: {entry['applied_at']}")
                print(f"    Checksum: {entry['checksum']}")
                print()
    
    elif args.command == 'rollback':
        if not args.target_version:
            print("Error: --target-version is required for rollback")
            exit(1)
        
        success = migrator.rollback_to_version(args.target_version)
        if not success:
            exit(1)


if __name__ == '__main__':
    main()