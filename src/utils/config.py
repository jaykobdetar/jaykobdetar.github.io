"""
Configuration Manager for Influencer News CMS
Handles loading and managing configuration from YAML files
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
import logging

class ConfigManager:
    """Manages application configuration from YAML files"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Singleton pattern to ensure single config instance"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager"""
        if self._config is None:
            self.load_config()
    
    def load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Optional path to config file, defaults to config.yaml
        """
        if config_path is None:
            # Look for config file in project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            
            # Ensure required directories exist
            self._ensure_directories()
            
        except FileNotFoundError:
            # Create default config if file doesn't exist
            self._create_default_config(config_path)
            self.load_config(config_path)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
    
    def _create_default_config(self, config_path: str) -> None:
        """Create default configuration file"""
        default_config = {
            'database': {
                'path': 'data/infnews.db',
                'backup_dir': 'data/backups',
                'max_backups': 10,
                'auto_backup': True
            },
            'paths': {
                'content_dir': 'content',
                'integrated_dir': 'integrated',
                'assets_dir': 'assets',
                'images_dir': 'assets/images',
                'placeholders_dir': 'assets/placeholders',
                'docs_dir': 'docs'
            },
            'limits': {
                'articles_per_page': 6,
                'search_results_per_page': 20,
                'max_articles_sync': 50,
                'max_authors_sync': 100,
                'max_categories_sync': 100,
                'max_trending_sync': 100
            },
            'security': {
                'sanitize_html': True,
                'max_content_length': 50000,
                'max_title_length': 200,
                'allowed_html_tags': ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/cms.log',
                'max_file_size_mb': 10,
                'backup_count': 5,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
        
        # Create config directory if needed
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(default_config, f, default_flow_style=False, indent=2)
    
    def _ensure_directories(self) -> None:
        """Ensure all configured directories exist"""
        dirs_to_create = [
            self.get('database.backup_dir', 'data/backups'),
            self.get('paths.content_dir', 'content'),
            self.get('paths.integrated_dir', 'integrated'),
            self.get('paths.assets_dir', 'assets'),
            self.get('paths.images_dir', 'assets/images'),
            self.get('paths.placeholders_dir', 'assets/placeholders'),
            os.path.dirname(self.get('logging.file', 'logs/cms.log'))
        ]
        
        for dir_path in dirs_to_create:
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key in dot notation (e.g., 'database.path')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if self._config is None:
            return default
        
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        if self._config is None:
            self._config = {}
        
        keys = key.split('.')
        config_ref = self._config
        
        # Navigate to parent of target key
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        # Set the final value
        config_ref[keys[-1]] = value
    
    def get_database_path(self) -> str:
        """Get database file path"""
        return self.get('database.path', 'data/infnews.db')
    
    def get_backup_dir(self) -> str:
        """Get backup directory path"""
        return self.get('database.backup_dir', 'data/backups')
    
    def get_content_dir(self, content_type: str = '') -> str:
        """Get content directory path"""
        base_dir = self.get('paths.content_dir', 'content')
        if content_type:
            return os.path.join(base_dir, content_type)
        return base_dir
    
    def get_integrated_dir(self, content_type: str = '') -> str:
        """Get integrated directory path"""
        base_dir = self.get('paths.integrated_dir', 'integrated')
        if content_type:
            return os.path.join(base_dir, content_type)
        return base_dir
    
    def get_images_dir(self, content_type: str = '') -> str:
        """Get images directory path"""
        base_dir = self.get('paths.images_dir', 'assets/images')
        if content_type:
            return os.path.join(base_dir, content_type)
        return base_dir
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'level': self.get('logging.level', 'INFO'),
            'filename': self.get('logging.file', 'logs/cms.log'),
            'format': self.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'maxBytes': self.get('logging.max_file_size_mb', 10) * 1024 * 1024,
            'backupCount': self.get('logging.backup_count', 5)
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            'sanitize_html': self.get('security.sanitize_html', True),
            'max_content_length': self.get('security.max_content_length', 50000),
            'max_title_length': self.get('security.max_title_length', 200),
            'allowed_html_tags': self.get('security.allowed_html_tags', ['p', 'br', 'strong', 'em', 'u', 'a'])
        }
    
    def get_limits(self) -> Dict[str, int]:
        """Get content limits configuration"""
        return {
            'articles_per_page': self.get('limits.articles_per_page', 6),
            'search_results_per_page': self.get('limits.search_results_per_page', 20),
            'max_articles_sync': self.get('limits.max_articles_sync', 50),
            'max_authors_sync': self.get('limits.max_authors_sync', 100),
            'max_categories_sync': self.get('limits.max_categories_sync', 100),
            'max_trending_sync': self.get('limits.max_trending_sync', 100)
        }
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode"""
        return self.get('development.debug', False)
    
    def reload_config(self, config_path: Optional[str] = None) -> None:
        """Reload configuration from file"""
        self._config = None
        self.load_config(config_path)

# Global config instance
config = ConfigManager()