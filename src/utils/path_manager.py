"""
Path Manager for Influencer News CMS
Handles dynamic URL resolution and path generation for cross-directory navigation
"""

import os
from typing import Optional

class PathManager:
    """Manages path resolution for consistent navigation across all pages"""
    
    def __init__(self, current_path: str = ""):
        """
        Initialize path manager
        
        Args:
            current_path: Current page path relative to root
        """
        self.current_path = current_path
        self.depth = self._calculate_depth()
    
    def _calculate_depth(self) -> int:
        """Calculate directory depth from root"""
        if not self.current_path:
            return 0
        
        # Count directory separators
        path_parts = self.current_path.strip('/').split('/')
        return len(path_parts) - 1 if path_parts[0] else 0
    
    def get_base_path(self) -> str:
        """
        Get base path prefix for current location
        
        Returns:
            Path prefix (e.g., '../' or '../../')
        """
        if self.depth == 0:
            return ""
        
        return "../" * self.depth
    
    def get_root_path(self) -> str:
        """Get path to root directory"""
        return self.get_base_path() if self.depth > 0 else "./"
    
    def get_asset_path(self, asset: str) -> str:
        """
        Get path to asset file
        
        Args:
            asset: Asset path relative to root
            
        Returns:
            Full path to asset
        """
        base = self.get_base_path()
        return f"{base}{asset}"
    
    def get_page_path(self, page: str) -> str:
        """
        Get path to another page
        
        Args:
            page: Page path relative to root
            
        Returns:
            Full path to page
        """
        return self.get_asset_path(page)
    
    def get_integrated_path(self, category: str, filename: str) -> str:
        """
        Get path to integrated content
        
        Args:
            category: Content category (articles, authors, etc.)
            filename: Filename within category
            
        Returns:
            Full path to integrated content
        """
        return self.get_page_path(f"integrated/{category}/{filename}")
    
    def get_image_path(self, image_path: str) -> str:
        """
        Get path to image asset
        
        Args:
            image_path: Image path relative to assets/images
            
        Returns:
            Full path to image
        """
        return self.get_asset_path(f"assets/images/{image_path}")
    
    def get_css_path(self, css_file: str = "style.css") -> str:
        """
        Get path to CSS file
        
        Args:
            css_file: CSS filename
            
        Returns:
            Full path to CSS
        """
        return self.get_asset_path(f"assets/css/{css_file}")
    
    def get_js_path(self, js_file: str) -> str:
        """
        Get path to JavaScript file
        
        Args:
            js_file: JS filename
            
        Returns:
            Full path to JS
        """
        return self.get_asset_path(f"assets/js/{js_file}")
    
    @classmethod
    def from_page_location(cls, page_location: str) -> 'PathManager':
        """
        Create PathManager from page location
        
        Args:
            page_location: Page location (e.g., 'integrated/articles/article_1.html')
            
        Returns:
            PathManager instance
        """
        return cls(page_location)
    
    def generate_navigation_links(self) -> dict:
        """
        Generate standard navigation links
        
        Returns:
            Dictionary of navigation links
        """
        return {
            'home': self.get_page_path('index.html'),
            'articles': self.get_integrated_path('', 'articles.html'),
            'authors': self.get_page_path('authors.html'),
            'categories': self.get_integrated_path('', 'categories.html'),
            'trending': self.get_integrated_path('', 'trending.html'),
            'search': self.get_page_path('search.html')
        }
    
    def __repr__(self) -> str:
        return f"<PathManager depth={self.depth} base='{self.get_base_path()}'>"