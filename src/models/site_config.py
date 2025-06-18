#!/usr/bin/env python3
"""
Site Configuration Model
=======================
Model for managing site-wide configuration data
"""

import datetime
from typing import Dict, List, Optional, Any, Union
from .base import BaseModel

class SiteConfig(BaseModel):
    """Site configuration model for managing site-wide settings"""
    
    table_name = 'site_config'
    required_fields = ['config_type', 'config_key', 'config_value']
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_type = kwargs.get('config_type', '')
        self.config_key = kwargs.get('config_key', '')
        self.config_value = kwargs.get('config_value', '')
        self.description = kwargs.get('description', '')
        self.is_active = kwargs.get('is_active', True)
        self.last_modified = kwargs.get('last_modified', None)
        
    def save(self) -> bool:
        """Save site config to database"""
        try:
            if not self.config_type or not self.config_key:
                raise ValueError("config_type and config_key are required")
                
            from ..database import DatabaseManager
            db = DatabaseManager()
            
            if self.id:
                # Update existing
                success = db.execute_write("""
                    UPDATE site_config 
                    SET config_value = ?, description = ?, is_active = ?, 
                        last_modified = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (self.config_value, self.description, self.is_active, 
                     self.last_modified, self.id))
                success = success > 0
            else:
                # Create new
                result = db.execute_write("""
                    INSERT INTO site_config 
                    (config_type, config_key, config_value, description, is_active, last_modified)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (self.config_type, self.config_key, self.config_value, 
                     self.description, self.is_active, self.last_modified))
                
                if result:
                    self.id = result  # execute_write returns lastrowid for INSERT
                success = bool(result)
            
            return success
            
        except Exception as e:
            print(f"Error saving site config: {e}")
            return False
    
    @classmethod
    def find_by_type(cls, config_type: str) -> List['SiteConfig']:
        """Find all config items by type"""
        try:
            from ..database import DatabaseManager
            db = DatabaseManager()
            
            rows = db.execute_query("""
                SELECT * FROM site_config 
                WHERE config_type = ? AND is_active = 1
                ORDER BY config_key
            """, (config_type,))
            
            return [cls(**row) for row in rows]
            
        except Exception as e:
            print(f"Error finding site config by type: {e}")
            return []
    
    @classmethod
    def find_by_key(cls, config_type: str, config_key: str) -> Optional['SiteConfig']:
        """Find specific config item by type and key"""
        try:
            from ..database import DatabaseManager
            db = DatabaseManager()
            
            row = db.execute_one("""
                SELECT * FROM site_config 
                WHERE config_type = ? AND config_key = ? AND is_active = 1
            """, (config_type, config_key))
            
            return cls(**row) if row else None
            
        except Exception as e:
            print(f"Error finding site config by key: {e}")
            return None
    
    @classmethod
    def get_config_dict(cls, config_type: str) -> Dict[str, str]:
        """Get config as dictionary for easy access"""
        configs = cls.find_by_type(config_type)
        return {config.config_key: config.config_value for config in configs}
    
    @classmethod
    def set_config(cls, config_type: str, config_key: str, config_value: str, 
                   description: str = '', last_modified: str = None) -> bool:
        """Set or update a config value"""
        try:
            # Try to find existing
            existing = cls.find_by_key(config_type, config_key)
            
            if existing:
                existing.config_value = config_value
                existing.description = description
                if last_modified:
                    existing.last_modified = last_modified
                return existing.save()
            else:
                # Create new
                new_config = cls(
                    config_type=config_type,
                    config_key=config_key,
                    config_value=config_value,
                    description=description,
                    last_modified=last_modified
                )
                return new_config.save()
                
        except Exception as e:
            print(f"Error setting site config: {e}")
            return False
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Dict[str, str]]:
        """Get all site configuration organized by type"""
        try:
            from ..database import DatabaseManager
            db = DatabaseManager()
            
            rows = db.execute_query("""
                SELECT config_type, config_key, config_value 
                FROM site_config 
                WHERE is_active = 1
                ORDER BY config_type, config_key
            """)
            
            result = {}
            for row in rows:
                config_type = row['config_type']
                if config_type not in result:
                    result[config_type] = {}
                result[config_type][row['config_key']] = row['config_value']
            
            return result
            
        except Exception as e:
            print(f"Error getting all site config: {e}")
            return {}
    
    @classmethod
    def bulk_update(cls, config_data: Dict[str, Dict[str, str]], 
                    last_modified: str = None) -> bool:
        """Bulk update site configuration from parsed content files"""
        try:
            success_count = 0
            total_count = 0
            
            for config_type, configs in config_data.items():
                for config_key, config_value in configs.items():
                    total_count += 1
                    if cls.set_config(config_type, config_key, config_value, 
                                    last_modified=last_modified):
                        success_count += 1
            
            print(f"Site config bulk update: {success_count}/{total_count} successful")
            return success_count == total_count
            
        except Exception as e:
            print(f"Error in bulk update: {e}")
            return False
    
    def __str__(self):
        return f"SiteConfig({self.config_type}.{self.config_key}={self.config_value})"
        
    def __repr__(self):
        return f"SiteConfig(id={self.id}, type='{self.config_type}', key='{self.config_key}', value='{self.config_value[:50]}...')"