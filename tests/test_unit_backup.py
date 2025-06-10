"""
Unit tests for backup and restore functionality
Tests backup system components
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.utils.backup import BackupManager, BackupInfo
from datetime import datetime


@pytest.mark.unit
class TestBackupManager:
    """Test BackupManager functionality"""
    
    def test_backup_manager_initialization(self):
        """Test BackupManager can be initialized"""
        with patch('src.utils.backup.config') as mock_config:
            mock_config.get_backup_dir.return_value = 'test_backups'
            mock_config.get_database_path.return_value = 'test.db'
            mock_config.get_content_dir.return_value = 'content'
            mock_config.get_integrated_dir.return_value = 'integrated'
            mock_config.get.return_value = 'assets'
            
            manager = BackupManager()
            
            assert manager.backup_dir == Path('test_backups')
            assert manager.database_path == Path('test.db')
    
    def test_backup_info_creation(self):
        """Test BackupInfo dataclass creation"""
        now = datetime.now()
        backup_info = BackupInfo(
            filename='test_backup.tar.gz',
            created_at=now,
            size_bytes=1024,
            backup_type='full',
            description='Test backup',
            checksum='abc123'
        )
        
        assert backup_info.filename == 'test_backup.tar.gz'
        assert backup_info.created_at == now
        assert backup_info.size_bytes == 1024
        assert backup_info.backup_type == 'full'
        assert backup_info.description == 'Test backup'
        assert backup_info.checksum == 'abc123'
    
    @patch('src.utils.backup.tarfile')
    @patch('src.utils.backup.config')
    def test_create_full_backup_structure(self, mock_config, mock_tarfile):
        """Test full backup creation structure"""
        # Mock configuration
        mock_config.get_backup_dir.return_value = 'test_backups'
        mock_config.get_database_path.return_value = 'test.db'
        mock_config.get_content_dir.return_value = 'content'
        mock_config.get_integrated_dir.return_value = 'integrated'
        mock_config.get.return_value = 'assets'
        
        # Mock tar file
        mock_tar = MagicMock()
        mock_tarfile.open.return_value.__enter__.return_value = mock_tar
        
        # Mock file system
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.stat', return_value=Mock(st_size=1024)), \
             patch('builtins.open', create=True):
            
            manager = BackupManager()
            
            # Mock internal methods
            manager._calculate_checksum = Mock(return_value='test_checksum')
            manager._save_backup_info = Mock()
            manager._cleanup_old_backups = Mock()
            
            result = manager.create_full_backup('Test backup')
            
            assert isinstance(result, BackupInfo)
            assert result.backup_type == 'full'
            assert result.description == 'Test backup'
            assert result.checksum == 'test_checksum'
            
            # Verify tar operations were called
            mock_tar.add.assert_called()
            manager._save_backup_info.assert_called_once()
            manager._cleanup_old_backups.assert_called_once()
    
    @patch('src.utils.backup.gzip')
    @patch('src.utils.backup.config')
    def test_create_database_backup_structure(self, mock_config, mock_gzip):
        """Test database backup creation structure"""
        # Mock configuration
        mock_config.get_backup_dir.return_value = 'test_backups'
        mock_config.get_database_path.return_value = 'test.db'
        
        # Mock gzip operations
        mock_gzip_file = MagicMock()
        mock_gzip.open.return_value.__enter__.return_value = mock_gzip_file
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.stat', return_value=Mock(st_size=512)), \
             patch('builtins.open', create=True), \
             patch('shutil.copyfileobj'):
            
            manager = BackupManager()
            
            # Mock internal methods
            manager._calculate_checksum = Mock(return_value='db_checksum')
            manager._save_backup_info = Mock()
            
            result = manager.create_database_backup('DB test backup')
            
            assert isinstance(result, BackupInfo)
            assert result.backup_type == 'database_only'
            assert result.description == 'DB test backup'
            assert result.checksum == 'db_checksum'
            
            manager._save_backup_info.assert_called_once()
    
    def test_calculate_checksum(self):
        """Test checksum calculation"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test content')
            tmp.flush()
            
            try:
                with patch('src.utils.backup.config') as mock_config:
                    mock_config.get_backup_dir.return_value = 'test_backups'
                    mock_config.get_database_path.return_value = 'test.db'
                    mock_config.get_content_dir.return_value = 'content'
                    mock_config.get_integrated_dir.return_value = 'integrated'
                    mock_config.get.return_value = 'assets'
                    
                    manager = BackupManager()
                    checksum = manager._calculate_checksum(Path(tmp.name))
                    
                    assert isinstance(checksum, str)
                    assert len(checksum) == 32  # MD5 hash length
            finally:
                os.unlink(tmp.name)
    
    @patch('src.utils.backup.config')
    def test_save_backup_info(self, mock_config):
        """Test saving backup information to registry"""
        mock_config.get_backup_dir.return_value = 'test_backups'
        mock_config.get_database_path.return_value = 'test.db'
        mock_config.get_content_dir.return_value = 'content'
        mock_config.get_integrated_dir.return_value = 'integrated'
        mock_config.get.return_value = 'assets'
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.exists', return_value=False), \
             patch('builtins.open', create=True) as mock_open:
            
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            manager = BackupManager()
            
            backup_info = BackupInfo(
                filename='test.tar.gz',
                created_at=datetime(2024, 12, 10, 10, 0, 0),
                size_bytes=1024,
                backup_type='full',
                description='Test',
                checksum='abc123'
            )
            
            manager._save_backup_info(backup_info)
            
            # Verify file operations
            mock_file.write.assert_called()
            
            # Get the written content
            written_calls = mock_file.write.call_args_list
            written_content = ''.join(call[0][0] for call in written_calls)
            
            # Should contain backup information
            assert 'test.tar.gz' in written_content
            assert 'full' in written_content
    
    @patch('src.utils.backup.config')
    def test_list_backups(self, mock_config):
        """Test listing available backups"""
        mock_config.get_backup_dir.return_value = 'test_backups'
        mock_config.get_database_path.return_value = 'test.db'
        mock_config.get_content_dir.return_value = 'content'
        mock_config.get_integrated_dir.return_value = 'integrated'
        mock_config.get.return_value = 'assets'
        
        # Mock registry file content
        registry_data = {
            'backups': [
                {
                    'filename': 'backup1.tar.gz',
                    'created_at': '2024-12-10T10:00:00',
                    'size_bytes': 1024,
                    'backup_type': 'full',
                    'description': 'First backup',
                    'checksum': 'abc123'
                },
                {
                    'filename': 'backup2.db.gz',
                    'created_at': '2024-12-11T10:00:00',
                    'size_bytes': 512,
                    'backup_type': 'database_only',
                    'description': 'Second backup',
                    'checksum': 'def456'
                }
            ]
        }
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', create=True) as mock_open:
            
            mock_file = MagicMock()
            mock_file.read.return_value = json.dumps(registry_data)
            mock_open.return_value.__enter__.return_value = mock_file
            
            manager = BackupManager()
            backups = manager.list_backups()
            
            assert len(backups) == 2
            assert backups[0].filename == 'backup2.db.gz'  # Newest first
            assert backups[1].filename == 'backup1.tar.gz'
            assert backups[0].backup_type == 'database_only'
            assert backups[1].backup_type == 'full'
    
    @patch('src.utils.backup.sqlite3')
    @patch('src.utils.backup.config')
    def test_verify_database_integrity(self, mock_config, mock_sqlite3):
        """Test database integrity verification"""
        mock_config.get_backup_dir.return_value = 'test_backups'
        mock_config.get_database_path.return_value = 'test.db'
        mock_config.get_content_dir.return_value = 'content'
        mock_config.get_integrated_dir.return_value = 'integrated'
        mock_config.get.return_value = 'assets'
        
        # Mock successful integrity check
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('ok',)
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite3.connect.return_value = mock_conn
        
        with patch('pathlib.Path.mkdir'):
            manager = BackupManager()
            result = manager._verify_database_integrity(Path('test.db'))
            
            assert result is True
            mock_cursor.execute.assert_called_with("PRAGMA integrity_check")
        
        # Mock failed integrity check
        mock_cursor.fetchone.return_value = ('error: corruption detected',)
        result = manager._verify_database_integrity(Path('test.db'))
        assert result is False
    
    @patch('src.utils.backup.config')
    def test_cleanup_old_backups(self, mock_config):
        """Test cleanup of old backups"""
        mock_config.get_backup_dir.return_value = 'test_backups'
        mock_config.get_database_path.return_value = 'test.db'
        mock_config.get_content_dir.return_value = 'content'
        mock_config.get_integrated_dir.return_value = 'integrated'
        mock_config.get.return_value = 'assets'
        mock_config.get.side_effect = lambda key, default=None: {'database.max_backups': 2}.get(key, default)
        
        with patch('pathlib.Path.mkdir'):
            manager = BackupManager()
            
            # Mock list_backups to return more than max_backups
            old_backups = [
                BackupInfo('old1.tar.gz', datetime.now(), 1024, 'full', 'Old 1', 'abc'),
                BackupInfo('old2.tar.gz', datetime.now(), 1024, 'full', 'Old 2', 'def')
            ]
            
            manager.list_backups = Mock(return_value=[
                BackupInfo('new1.tar.gz', datetime.now(), 1024, 'full', 'New 1', 'ghi'),
                BackupInfo('new2.tar.gz', datetime.now(), 1024, 'full', 'New 2', 'jkl')
            ] + old_backups)
            
            manager.delete_backup = Mock(return_value=True)
            
            manager._cleanup_old_backups()
            
            # Should delete the 2 oldest backups
            assert manager.delete_backup.call_count == 2