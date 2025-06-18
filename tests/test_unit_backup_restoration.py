#!/usr/bin/env python3
"""
Comprehensive tests for backup and restoration functionality
Tests for database backups, file backups, and restoration procedures
"""

import pytest
import sys
import tempfile
import shutil
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.backup import BackupManager, BackupError
from database.migrate_schema import SchemaMigrator


class TestBackupManager:
    """Test the BackupManager class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.test_dir / 'data'
        self.backup_dir = self.test_dir / 'backups'
        self.content_dir = self.test_dir / 'content'
        self.integrated_dir = self.test_dir / 'integrated'
        
        # Create directories
        self.data_dir.mkdir(parents=True)
        self.backup_dir.mkdir(parents=True)
        self.content_dir.mkdir(parents=True)
        self.integrated_dir.mkdir(parents=True)
        
        # Create test database
        self.db_path = self.data_dir / 'test.db'
        self.create_test_database()
        
        # Initialize backup manager
        self.backup_manager = BackupManager(
            db_path=str(self.db_path),
            backup_dir=str(self.backup_dir),
            content_dir=str(self.content_dir),
            integrated_dir=str(self.integrated_dir)
        )
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.test_dir)
    
    def create_test_database(self):
        """Create a test database with sample data"""
        conn = sqlite3.connect(self.db_path)
        
        # Create simple tables for testing
        conn.executescript('''
            CREATE TABLE authors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                bio TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE articles (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT,
                author_id INTEGER,
                category_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES authors(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );
            
            INSERT INTO authors (name, slug, bio) VALUES
            ('John Doe', 'john-doe', 'Test author bio'),
            ('Jane Smith', 'jane-smith', 'Another test author');
            
            INSERT INTO categories (name, slug, description) VALUES
            ('Technology', 'technology', 'Tech news and updates'),
            ('Business', 'business', 'Business and finance news');
            
            INSERT INTO articles (title, slug, content, author_id, category_id) VALUES
            ('Test Article 1', 'test-article-1', 'Content of test article 1', 1, 1),
            ('Test Article 2', 'test-article-2', 'Content of test article 2', 2, 2);
        ''')
        
        conn.close()
    
    def create_test_content_files(self):
        """Create test content files"""
        # Create author files
        author_dir = self.content_dir / 'authors'
        author_dir.mkdir(exist_ok=True)
        
        (author_dir / 'john-doe.txt').write_text('''name: John Doe
slug: john-doe
title: Senior Writer
---
John is an experienced writer with 10 years of experience.''')
        
        (author_dir / 'jane-smith.txt').write_text('''name: Jane Smith
slug: jane-smith
title: Tech Editor
---
Jane specializes in technology and business coverage.''')
        
        # Create category files
        category_dir = self.content_dir / 'categories'
        category_dir.mkdir(exist_ok=True)
        
        (category_dir / 'technology.txt').write_text('''name: Technology
slug: technology
color: blue
---
Latest technology news and innovations.''')
        
        # Create article files
        article_dir = self.content_dir / 'articles'
        article_dir.mkdir(exist_ok=True)
        
        (article_dir / 'test-article.txt').write_text('''title: Test Article
slug: test-article
author: john-doe
category: technology
---
# Test Article

This is the content of the test article.''')
    
    def create_test_integrated_files(self):
        """Create test integrated files"""
        # Create integrated HTML files
        (self.integrated_dir / 'article_1.html').write_text('''<!DOCTYPE html>
<html><head><title>Test Article 1</title></head>
<body><h1>Test Article 1</h1><p>Article content</p></body></html>''')
        
        (self.integrated_dir / 'authors.html').write_text('''<!DOCTYPE html>
<html><head><title>Authors</title></head>
<body><h1>Authors</h1><div>Author listings</div></body></html>''')
    
    def test_initialization(self):
        """Test BackupManager initialization"""
        assert self.backup_manager.db_path == str(self.db_path)
        assert self.backup_manager.backup_dir == str(self.backup_dir)
        assert self.backup_manager.content_dir == str(self.content_dir)
        assert self.backup_manager.integrated_dir == str(self.integrated_dir)
    
    def test_database_backup_creation(self):
        """Test creating database backups"""
        backup_path = self.backup_manager.backup_database()
        
        assert backup_path.exists()
        assert backup_path.suffix == '.db'
        assert 'backup' in backup_path.name
        
        # Verify backup contains data
        conn = sqlite3.connect(backup_path)
        cursor = conn.execute("SELECT COUNT(*) FROM authors")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 2  # Should have our test authors
    
    def test_database_backup_with_custom_suffix(self):
        """Test database backup with custom suffix"""
        backup_path = self.backup_manager.backup_database(suffix='custom_test')
        
        assert 'custom_test' in backup_path.name
        assert backup_path.exists()
    
    def test_database_backup_failure(self):
        """Test database backup failure handling"""
        # Test with non-existent database
        backup_manager = BackupManager(
            db_path='/nonexistent/database.db',
            backup_dir=str(self.backup_dir)
        )
        
        with pytest.raises(BackupError, match="Database backup failed"):
            backup_manager.backup_database()
    
    def test_content_backup_creation(self):
        """Test creating content file backups"""
        self.create_test_content_files()
        
        backup_path = self.backup_manager.backup_content_files()
        
        assert backup_path.exists()
        assert backup_path.suffix == '.tar.gz'
        assert 'content_backup' in backup_path.name
        
        # Verify backup contains files (basic check)
        import tarfile
        with tarfile.open(backup_path, 'r:gz') as tar:
            files = tar.getnames()
            assert any('john-doe.txt' in f for f in files)
            assert any('technology.txt' in f for f in files)
    
    def test_integrated_backup_creation(self):
        """Test creating integrated files backup"""
        self.create_test_integrated_files()
        
        backup_path = self.backup_manager.backup_integrated_files()
        
        assert backup_path.exists()
        assert backup_path.suffix == '.tar.gz'
        assert 'integrated_backup' in backup_path.name
        
        # Verify backup contains files
        import tarfile
        with tarfile.open(backup_path, 'r:gz') as tar:
            files = tar.getnames()
            assert any('article_1.html' in f for f in files)
            assert any('authors.html' in f for f in files)
    
    def test_full_system_backup(self):
        """Test complete system backup"""
        self.create_test_content_files()
        self.create_test_integrated_files()
        
        backup_info = self.backup_manager.create_full_backup()
        
        assert 'database' in backup_info
        assert 'content' in backup_info
        assert 'integrated' in backup_info
        assert 'timestamp' in backup_info
        
        # Verify all backup files exist
        for backup_type, backup_path in backup_info.items():
            if backup_type != 'timestamp':
                assert Path(backup_path).exists()
    
    def test_backup_listing(self):
        """Test listing available backups"""
        # Create multiple backups
        self.backup_manager.backup_database(suffix='test1')
        self.backup_manager.backup_database(suffix='test2')
        
        backups = self.backup_manager.list_backups()
        
        assert len(backups) >= 2
        assert any('test1' in backup['filename'] for backup in backups)
        assert any('test2' in backup['filename'] for backup in backups)
        
        # Check backup info structure
        for backup in backups:
            assert 'filename' in backup
            assert 'path' in backup
            assert 'size' in backup
            assert 'created' in backup
            assert 'type' in backup
    
    def test_backup_cleanup(self):
        """Test backup cleanup functionality"""
        # Create multiple backups
        backup_paths = []
        for i in range(5):
            path = self.backup_manager.backup_database(suffix=f'test{i}')
            backup_paths.append(path)
        
        # Test cleanup (keep only 3 most recent)
        self.backup_manager.cleanup_old_backups(keep_count=3, backup_type='database')
        
        # Count remaining backups
        remaining_backups = list(self.backup_dir.glob('*backup*.db'))
        assert len(remaining_backups) <= 3
    
    def test_database_restoration(self):
        """Test database restoration"""
        # Create backup
        backup_path = self.backup_manager.backup_database()
        
        # Modify original database
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM authors WHERE id = 1")
        conn.commit()
        conn.close()
        
        # Verify modification
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM authors")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 1  # Should have one less author
        
        # Restore from backup
        self.backup_manager.restore_database(backup_path)
        
        # Verify restoration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM authors")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 2  # Should be restored to original
    
    def test_content_restoration(self):
        """Test content files restoration"""
        self.create_test_content_files()
        
        # Create backup
        backup_path = self.backup_manager.backup_content_files()
        
        # Delete original content
        shutil.rmtree(self.content_dir)
        self.content_dir.mkdir()
        
        # Verify deletion
        assert len(list(self.content_dir.glob('**/*.txt'))) == 0
        
        # Restore from backup
        self.backup_manager.restore_content_files(backup_path)
        
        # Verify restoration
        txt_files = list(self.content_dir.glob('**/*.txt'))
        assert len(txt_files) > 0
        
        # Check specific files were restored
        assert (self.content_dir / 'authors' / 'john-doe.txt').exists()
        assert (self.content_dir / 'categories' / 'technology.txt').exists()
    
    def test_integrated_restoration(self):
        """Test integrated files restoration"""
        self.create_test_integrated_files()
        
        # Create backup
        backup_path = self.backup_manager.backup_integrated_files()
        
        # Delete original integrated files
        shutil.rmtree(self.integrated_dir)
        self.integrated_dir.mkdir()
        
        # Verify deletion
        assert len(list(self.integrated_dir.glob('*.html'))) == 0
        
        # Restore from backup
        self.backup_manager.restore_integrated_files(backup_path)
        
        # Verify restoration
        html_files = list(self.integrated_dir.glob('*.html'))
        assert len(html_files) > 0
        
        # Check specific files were restored
        assert (self.integrated_dir / 'article_1.html').exists()
        assert (self.integrated_dir / 'authors.html').exists()
    
    def test_backup_verification(self):
        """Test backup file verification"""
        # Create valid backup
        backup_path = self.backup_manager.backup_database()
        
        # Test valid backup
        assert self.backup_manager.verify_backup(backup_path)
        
        # Test invalid backup (corrupt file)
        corrupt_backup = self.backup_dir / 'corrupt_backup.db'
        corrupt_backup.write_text('This is not a valid SQLite database')
        
        assert not self.backup_manager.verify_backup(corrupt_backup)
        
        # Test non-existent backup
        assert not self.backup_manager.verify_backup(Path('/nonexistent/backup.db'))
    
    def test_backup_metadata(self):
        """Test backup metadata creation and reading"""
        backup_info = self.backup_manager.create_full_backup()
        
        # Should create metadata file
        metadata_files = list(self.backup_dir.glob('backup_metadata_*.json'))
        assert len(metadata_files) > 0
        
        # Verify metadata content
        metadata_file = metadata_files[0]
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        assert 'timestamp' in metadata
        assert 'database_backup' in metadata
        assert 'content_backup' in metadata
        assert 'integrated_backup' in metadata
        assert 'system_info' in metadata
    
    def test_incremental_backup(self):
        """Test incremental backup functionality"""
        # Create initial backup
        initial_backup = self.backup_manager.create_full_backup()
        
        # Add new content
        new_article = self.content_dir / 'articles' / 'new-article.txt'
        new_article.parent.mkdir(parents=True, exist_ok=True)
        new_article.write_text('''title: New Article
slug: new-article
---
This is a new article added after the initial backup.''')
        
        # Create incremental backup
        incremental_backup = self.backup_manager.create_incremental_backup(
            since_timestamp=initial_backup['timestamp']
        )
        
        # Should have detected the new file
        assert incremental_backup is not None
        if 'changed_files' in incremental_backup:
            assert len(incremental_backup['changed_files']) > 0
    
    def test_backup_compression(self):
        """Test backup compression"""
        self.create_test_content_files()
        
        # Create uncompressed backup
        uncompressed_path = self.backup_manager.backup_content_files(compress=False)
        
        # Create compressed backup
        compressed_path = self.backup_manager.backup_content_files(compress=True)
        
        # Compressed should be smaller (or at least exist)
        assert compressed_path.exists()
        assert uncompressed_path.exists()
        
        # Compressed file should have .gz extension
        assert compressed_path.suffix == '.gz' or '.tar.gz' in compressed_path.name


class TestSchemaMigrator:
    """Test the SchemaMigrator class for backup and restoration scenarios"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / 'test.db'
        self.backup_path = self.test_dir / 'backup.db'
        
        # Create test database with old schema
        self.create_old_schema_database()
        
        self.migrator = SchemaMigrator(db_path=str(self.db_path))
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.test_dir)
    
    def create_old_schema_database(self):
        """Create database with old schema for migration testing"""
        conn = sqlite3.connect(self.db_path)
        
        # Create old schema (simplified version)
        conn.executescript('''
            CREATE TABLE authors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                bio TEXT,
                expertise TEXT,
                twitter_handle TEXT,
                linkedin_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT,
                article_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            INSERT INTO authors (name, slug, bio) VALUES
            ('Test Author', 'test-author', 'Test bio');
            
            INSERT INTO categories (name, slug, description) VALUES
            ('Technology', 'technology', 'Tech category');
        ''')
        
        conn.close()
    
    def test_backup_creation_before_migration(self):
        """Test that backup is created before migration"""
        migrator = SchemaMigrator(db_path=str(self.db_path))
        
        # Mock the migration process to just test backup
        with patch.object(migrator, 'create_new_database'), \
             patch.object(migrator, 'migrate_data'), \
             patch.object(migrator, 'verify_migration'):
            
            migrator.backup_database()
            
            # Should create backup file
            assert migrator.backup_path.exists()
    
    def test_data_extraction_before_migration(self):
        """Test data extraction from old database"""
        migrator = SchemaMigrator(db_path=str(self.db_path))
        
        data = migrator.extract_existing_data()
        
        assert 'authors' in data
        assert 'categories' in data
        assert len(data['authors']) == 1
        assert len(data['categories']) == 1
        
        # Check author data
        author = data['authors'][0]
        assert author['name'] == 'Test Author'
        assert author['slug'] == 'test-author'
    
    def test_migration_rollback_on_failure(self):
        """Test rollback capability when migration fails"""
        migrator = SchemaMigrator(db_path=str(self.db_path))
        
        # Create backup first
        migrator.backup_database()
        original_backup = migrator.backup_path
        
        # Verify original data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM authors")
        original_count = cursor.fetchone()[0]
        conn.close()
        
        # Simulate migration failure
        with patch.object(migrator, 'migrate_data', side_effect=Exception("Migration failed")):
            with pytest.raises(Exception, match="Migration failed"):
                migrator.migrate()
        
        # Restore from backup should be possible
        if original_backup.exists():
            shutil.copy2(original_backup, self.db_path)
            
            # Verify restoration
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM authors")
            restored_count = cursor.fetchone()[0]
            conn.close()
            
            assert restored_count == original_count
    
    def test_verification_after_migration(self):
        """Test migration verification"""
        migrator = SchemaMigrator(db_path=str(self.db_path))
        
        # Create a simple new database to test verification
        conn = sqlite3.connect(self.db_path)
        conn.execute("DROP TABLE IF EXISTS authors")
        conn.execute('''CREATE TABLE authors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            title TEXT,
            email TEXT,
            rating REAL DEFAULT 0.0,
            is_active BOOLEAN DEFAULT 1
        )''')
        conn.close()
        
        # Run verification
        migrator.verify_migration()
        
        # Should complete without errors (basic test)
        # In real scenarios, this would check for specific schema elements


class TestBackupIntegration:
    """Integration tests for backup system"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.setup_complete_environment()
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.test_dir)
    
    def setup_complete_environment(self):
        """Setup complete test environment"""
        # Create directory structure
        self.data_dir = self.test_dir / 'data'
        self.content_dir = self.test_dir / 'content'
        self.integrated_dir = self.test_dir / 'integrated'
        self.backup_dir = self.test_dir / 'backups'
        
        for dir_path in [self.data_dir, self.content_dir, self.integrated_dir, self.backup_dir]:
            dir_path.mkdir(parents=True)
        
        # Create database
        self.db_path = self.data_dir / 'cms.db'
        conn = sqlite3.connect(self.db_path)
        conn.executescript('''
            CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT, slug TEXT UNIQUE);
            CREATE TABLE articles (id INTEGER PRIMARY KEY, title TEXT, content TEXT);
            INSERT INTO authors (name, slug) VALUES ('John Doe', 'john-doe');
            INSERT INTO articles (title, content) VALUES ('Test Article', 'Test content');
        ''')
        conn.close()
        
        # Create content files
        (self.content_dir / 'test.txt').write_text('Test content file')
        
        # Create integrated files
        (self.integrated_dir / 'test.html').write_text('<html><body>Test</body></html>')
        
        # Initialize backup manager
        self.backup_manager = BackupManager(
            db_path=str(self.db_path),
            backup_dir=str(self.backup_dir),
            content_dir=str(self.content_dir),
            integrated_dir=str(self.integrated_dir)
        )
    
    def test_disaster_recovery_simulation(self):
        """Test complete disaster recovery scenario"""
        # Step 1: Create full backup
        backup_info = self.backup_manager.create_full_backup()
        
        # Step 2: Simulate disaster (delete everything)
        shutil.rmtree(self.data_dir)
        shutil.rmtree(self.content_dir)
        shutil.rmtree(self.integrated_dir)
        
        # Step 3: Recreate directories
        for dir_path in [self.data_dir, self.content_dir, self.integrated_dir]:
            dir_path.mkdir(parents=True)
        
        # Step 4: Restore from backups
        self.backup_manager.restore_database(Path(backup_info['database']))
        self.backup_manager.restore_content_files(Path(backup_info['content']))
        self.backup_manager.restore_integrated_files(Path(backup_info['integrated']))
        
        # Step 5: Verify complete restoration
        # Check database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM authors")
        author_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM articles")
        article_count = cursor.fetchone()[0]
        conn.close()
        
        assert author_count == 1
        assert article_count == 1
        
        # Check content files
        assert (self.content_dir / 'test.txt').exists()
        
        # Check integrated files
        assert (self.integrated_dir / 'test.html').exists()
    
    def test_backup_automation_workflow(self):
        """Test automated backup workflow"""
        # Simulate automated daily backup
        for day in range(7):
            # Create some changes
            conn = sqlite3.connect(self.db_path)
            conn.execute(f"INSERT INTO articles (title, content) VALUES ('Article {day}', 'Content {day}')")
            conn.commit()
            conn.close()
            
            # Create backup
            backup_info = self.backup_manager.create_full_backup()
            assert backup_info is not None
        
        # Verify multiple backups exist
        backups = self.backup_manager.list_backups()
        assert len(backups) >= 7
        
        # Test cleanup (keep only 5 most recent)
        self.backup_manager.cleanup_old_backups(keep_count=5)
        
        remaining_backups = self.backup_manager.list_backups()
        assert len(remaining_backups) <= 5
    
    def test_partial_restoration_scenario(self):
        """Test partial restoration (only database or only files)"""
        # Create full backup
        backup_info = self.backup_manager.create_full_backup()
        
        # Corrupt only database
        self.db_path.write_text('corrupted data')
        
        # Restore only database
        self.backup_manager.restore_database(Path(backup_info['database']))
        
        # Verify database is restored but files are unchanged
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM authors")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1  # Database restored
        assert (self.content_dir / 'test.txt').exists()  # Files unchanged


if __name__ == "__main__":
    pytest.main([__file__, "-v"])