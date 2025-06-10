"""
Backup and Restore System for Influencer News CMS
Provides comprehensive backup, restore, and disaster recovery capabilities
"""

import os
import shutil
import sqlite3
import json
import tarfile
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .config import config
from .logger import get_logger, handle_exception, CMSException

logger = get_logger(__name__)

@dataclass
class BackupInfo:
    """Information about a backup"""
    filename: str
    created_at: datetime
    size_bytes: int
    backup_type: str  # 'full', 'incremental', 'database_only'
    description: str
    checksum: str

class BackupManager:
    """Manages backup and restore operations"""
    
    def __init__(self):
        self.backup_dir = Path(config.get_backup_dir())
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.database_path = Path(config.get_database_path())
        self.content_dirs = [
            Path(config.get_content_dir()),
            Path(config.get_integrated_dir()),
            Path(config.get('paths.assets_dir', 'assets')),
            Path(config.get('paths.docs_dir', 'docs'))
        ]
        
        self.max_backups = config.get('database.max_backups', 10)
        self.auto_backup = config.get('database.auto_backup', True)
    
    def create_full_backup(self, description: str = None) -> BackupInfo:
        """
        Create a full backup including database and all content
        
        Args:
            description: Optional description for the backup
            
        Returns:
            BackupInfo object with backup details
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"full_backup_{timestamp}.tar.gz"
            backup_path = self.backup_dir / backup_filename
            
            logger.info(f"Starting full backup: {backup_filename}")
            
            # Create compressed tar archive
            with tarfile.open(backup_path, 'w:gz') as tar:
                # Add database
                if self.database_path.exists():
                    tar.add(self.database_path, arcname='database/infnews.db')
                    logger.debug(f"Added database to backup: {self.database_path}")
                
                # Add content directories
                for content_dir in self.content_dirs:
                    if content_dir.exists():
                        tar.add(content_dir, arcname=f"content/{content_dir.name}")
                        logger.debug(f"Added directory to backup: {content_dir}")
                
                # Add configuration
                config_path = Path('config.yaml')
                if config_path.exists():
                    tar.add(config_path, arcname='config/config.yaml')
                    logger.debug("Added configuration to backup")
                
                # Add backup metadata
                metadata = {
                    'backup_type': 'full',
                    'created_at': datetime.now().isoformat(),
                    'description': description or f"Full backup created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    'cms_version': '1.0.0',
                    'python_version': os.sys.version,
                }
                
                # Write metadata to temporary file and add to archive
                metadata_path = self.backup_dir / 'temp_metadata.json'
                try:
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    tar.add(metadata_path, arcname='metadata.json')
                finally:
                    if metadata_path.exists():
                        metadata_path.unlink()
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)
            
            # Create backup info
            backup_info = BackupInfo(
                filename=backup_filename,
                created_at=datetime.now(),
                size_bytes=backup_path.stat().st_size,
                backup_type='full',
                description=metadata['description'],
                checksum=checksum
            )
            
            # Save backup registry
            self._save_backup_info(backup_info)
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            logger.info(f"Full backup completed successfully: {backup_filename} ({backup_info.size_bytes} bytes)")
            return backup_info
            
        except Exception as e:
            raise handle_exception(logger, e, 'create_full_backup')
    
    def create_database_backup(self, description: str = None) -> BackupInfo:
        """
        Create a database-only backup
        
        Args:
            description: Optional description for the backup
            
        Returns:
            BackupInfo object with backup details
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"db_backup_{timestamp}.db.gz"
            backup_path = self.backup_dir / backup_filename
            
            logger.info(f"Starting database backup: {backup_filename}")
            
            if not self.database_path.exists():
                raise CMSException("Database file not found", user_message="Database file not found for backup")
            
            # Create compressed database backup
            with open(self.database_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)
            
            # Create backup info
            backup_info = BackupInfo(
                filename=backup_filename,
                created_at=datetime.now(),
                size_bytes=backup_path.stat().st_size,
                backup_type='database_only',
                description=description or f"Database backup created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                checksum=checksum
            )
            
            # Save backup registry
            self._save_backup_info(backup_info)
            
            logger.info(f"Database backup completed successfully: {backup_filename} ({backup_info.size_bytes} bytes)")
            return backup_info
            
        except Exception as e:
            raise handle_exception(logger, e, 'create_database_backup')
    
    def restore_full_backup(self, backup_filename: str, 
                           confirm_overwrite: bool = False) -> bool:
        """
        Restore from a full backup
        
        Args:
            backup_filename: Name of backup file to restore
            confirm_overwrite: Confirm that overwriting existing data is OK
            
        Returns:
            True if restore was successful
        """
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                raise CMSException(f"Backup file not found: {backup_filename}")
            
            if not confirm_overwrite:
                raise CMSException(
                    "Restore requires confirmation to overwrite existing data",
                    user_message="Please confirm that you want to overwrite existing data"
                )
            
            logger.info(f"Starting full restore from: {backup_filename}")
            
            # Create backup of current state before restore
            pre_restore_backup = self.create_full_backup("Pre-restore backup")
            logger.info(f"Created pre-restore backup: {pre_restore_backup.filename}")
            
            # Extract backup
            with tarfile.open(backup_path, 'r:gz') as tar:
                # Verify backup integrity
                metadata = self._extract_backup_metadata(tar)
                if not metadata:
                    raise CMSException("Invalid backup file: missing metadata")
                
                logger.info(f"Restoring backup: {metadata.get('description', 'Unknown')}")
                
                # Extract database
                try:
                    tar.extract('database/infnews.db', path=self.backup_dir / 'temp_restore')
                    restored_db = self.backup_dir / 'temp_restore' / 'database' / 'infnews.db'
                    
                    # Verify database integrity
                    if self._verify_database_integrity(restored_db):
                        # Replace current database
                        if self.database_path.exists():
                            self.database_path.unlink()
                        shutil.move(str(restored_db), str(self.database_path))
                        logger.info("Database restored successfully")
                    else:
                        raise CMSException("Restored database failed integrity check")
                        
                except KeyError:
                    logger.warning("No database found in backup")
                
                # Extract content directories
                for member in tar.getmembers():
                    if member.path.startswith('content/'):
                        # Determine target directory
                        content_type = member.path.split('/')[1]
                        target_dir = None
                        
                        for dir_path in self.content_dirs:
                            if dir_path.name == content_type:
                                target_dir = dir_path.parent
                                break
                        
                        if target_dir:
                            # Remove existing directory if it exists
                            existing_dir = target_dir / content_type
                            if existing_dir.exists():
                                shutil.rmtree(existing_dir)
                            
                            # Extract to target location
                            tar.extract(member, path=target_dir)
                            logger.debug(f"Restored directory: {content_type}")
                
                # Extract configuration if present
                try:
                    tar.extract('config/config.yaml', path=self.backup_dir / 'temp_restore')
                    restored_config = self.backup_dir / 'temp_restore' / 'config' / 'config.yaml'
                    if restored_config.exists():
                        shutil.copy2(restored_config, 'config.yaml')
                        logger.info("Configuration restored")
                except KeyError:
                    logger.warning("No configuration found in backup")
            
            # Clean up temporary files
            temp_restore_dir = self.backup_dir / 'temp_restore'
            if temp_restore_dir.exists():
                shutil.rmtree(temp_restore_dir)
            
            logger.info("Full restore completed successfully")
            return True
            
        except Exception as e:
            logger.error("Restore failed, original data may be corrupted")
            raise handle_exception(logger, e, 'restore_full_backup')
    
    def restore_database_backup(self, backup_filename: str, 
                               confirm_overwrite: bool = False) -> bool:
        """
        Restore database from a database backup
        
        Args:
            backup_filename: Name of database backup file
            confirm_overwrite: Confirm that overwriting existing database is OK
            
        Returns:
            True if restore was successful
        """
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                raise CMSException(f"Backup file not found: {backup_filename}")
            
            if not confirm_overwrite:
                raise CMSException(
                    "Database restore requires confirmation to overwrite existing database",
                    user_message="Please confirm that you want to overwrite existing database"
                )
            
            logger.info(f"Starting database restore from: {backup_filename}")
            
            # Create backup of current database
            if self.database_path.exists():
                current_backup = self.create_database_backup("Pre-restore database backup")
                logger.info(f"Created pre-restore database backup: {current_backup.filename}")
            
            # Decompress and restore database
            temp_db_path = self.backup_dir / 'temp_restored.db'
            
            with gzip.open(backup_path, 'rb') as f_in:
                with open(temp_db_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Verify database integrity
            if self._verify_database_integrity(temp_db_path):
                # Replace current database
                if self.database_path.exists():
                    self.database_path.unlink()
                shutil.move(str(temp_db_path), str(self.database_path))
                logger.info("Database restore completed successfully")
                return True
            else:
                # Clean up failed restore
                if temp_db_path.exists():
                    temp_db_path.unlink()
                raise CMSException("Restored database failed integrity check")
                
        except Exception as e:
            raise handle_exception(logger, e, 'restore_database_backup')
    
    def list_backups(self) -> List[BackupInfo]:
        """
        List all available backups
        
        Returns:
            List of BackupInfo objects
        """
        try:
            backups = []
            registry_path = self.backup_dir / 'backup_registry.json'
            
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
                
                for backup_data in registry.get('backups', []):
                    # Verify backup file still exists
                    backup_path = self.backup_dir / backup_data['filename']
                    if backup_path.exists():
                        backups.append(BackupInfo(
                            filename=backup_data['filename'],
                            created_at=datetime.fromisoformat(backup_data['created_at']),
                            size_bytes=backup_data['size_bytes'],
                            backup_type=backup_data['backup_type'],
                            description=backup_data['description'],
                            checksum=backup_data['checksum']
                        ))
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x.created_at, reverse=True)
            return backups
            
        except Exception as e:
            logger.warning(f"Failed to list backups: {e}")
            return []
    
    def delete_backup(self, backup_filename: str) -> bool:
        """
        Delete a backup file
        
        Args:
            backup_filename: Name of backup file to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                raise CMSException(f"Backup file not found: {backup_filename}")
            
            # Remove from registry
            registry_path = self.backup_dir / 'backup_registry.json'
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
                
                registry['backups'] = [
                    b for b in registry.get('backups', [])
                    if b['filename'] != backup_filename
                ]
                
                with open(registry_path, 'w') as f:
                    json.dump(registry, f, indent=2)
            
            # Delete backup file
            backup_path.unlink()
            
            logger.info(f"Backup deleted: {backup_filename}")
            return True
            
        except Exception as e:
            raise handle_exception(logger, e, 'delete_backup')
    
    def verify_backup(self, backup_filename: str) -> bool:
        """
        Verify backup integrity
        
        Args:
            backup_filename: Name of backup file to verify
            
        Returns:
            True if backup is valid
        """
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                return False
            
            # Calculate current checksum
            current_checksum = self._calculate_checksum(backup_path)
            
            # Get stored checksum from registry
            registry_path = self.backup_dir / 'backup_registry.json'
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
                
                for backup_data in registry.get('backups', []):
                    if backup_data['filename'] == backup_filename:
                        stored_checksum = backup_data['checksum']
                        return current_checksum == stored_checksum
            
            return False
            
        except Exception as e:
            logger.warning(f"Failed to verify backup {backup_filename}: {e}")
            return False
    
    def auto_backup_if_enabled(self) -> Optional[BackupInfo]:
        """
        Create automatic backup if enabled and needed
        
        Returns:
            BackupInfo if backup was created, None otherwise
        """
        try:
            if not self.auto_backup:
                return None
            
            # Check if we need a backup (daily)
            backups = self.list_backups()
            if backups:
                latest_backup = backups[0]
                if latest_backup.created_at.date() == datetime.now().date():
                    return None  # Already have a backup today
            
            # Create automatic backup
            return self.create_database_backup("Automatic daily backup")
            
        except Exception as e:
            logger.warning(f"Auto backup failed: {e}")
            return None
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file"""
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _save_backup_info(self, backup_info: BackupInfo):
        """Save backup information to registry"""
        registry_path = self.backup_dir / 'backup_registry.json'
        
        # Load existing registry
        registry = {'backups': []}
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
            except:
                pass  # Use default if file is corrupted
        
        # Add new backup info
        backup_data = {
            'filename': backup_info.filename,
            'created_at': backup_info.created_at.isoformat(),
            'size_bytes': backup_info.size_bytes,
            'backup_type': backup_info.backup_type,
            'description': backup_info.description,
            'checksum': backup_info.checksum
        }
        
        registry['backups'].append(backup_data)
        
        # Save registry
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def _cleanup_old_backups(self):
        """Remove old backups exceeding max_backups limit"""
        backups = self.list_backups()
        
        if len(backups) > self.max_backups:
            backups_to_delete = backups[self.max_backups:]
            for backup in backups_to_delete:
                try:
                    self.delete_backup(backup.filename)
                    logger.info(f"Cleaned up old backup: {backup.filename}")
                except Exception as e:
                    logger.warning(f"Failed to clean up backup {backup.filename}: {e}")
    
    def _verify_database_integrity(self, db_path: Path) -> bool:
        """Verify SQLite database integrity"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Run integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()
            
            return result and result[0] == 'ok'
            
        except Exception as e:
            logger.warning(f"Database integrity check failed: {e}")
            return False
    
    def _extract_backup_metadata(self, tar: tarfile.TarFile) -> Optional[Dict[str, Any]]:
        """Extract metadata from backup archive"""
        try:
            metadata_member = tar.getmember('metadata.json')
            metadata_file = tar.extractfile(metadata_member)
            if metadata_file:
                return json.load(metadata_file)
        except:
            pass
        return None

# Global backup manager instance
backup_manager = BackupManager()