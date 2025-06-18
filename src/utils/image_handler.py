#!/usr/bin/env python3
"""
Image Handler for Influencer News CMS
Manages author images, article images, and image processing
"""

import os
import hashlib
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import urllib.parse
from urllib.request import urlretrieve
import logging

logger = logging.getLogger(__name__)

class ImageHandler:
    """Handles image management for the CMS"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.assets_dir = self.base_dir / 'assets' / 'images'
        self.authors_dir = self.assets_dir / 'authors'
        self.articles_dir = self.assets_dir / 'articles'
        self.placeholders_dir = self.base_dir / 'assets' / 'placeholders'
        
        # Create directories if they don't exist
        self.authors_dir.mkdir(parents=True, exist_ok=True)
        self.articles_dir.mkdir(parents=True, exist_ok=True)
        self.placeholders_dir.mkdir(parents=True, exist_ok=True)
        
        # Default placeholder URLs
        self.default_placeholders = {
            'author': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face',
            'author_female': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face',
            'article': 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=400&fit=crop',
            'article_tech': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&h=400&fit=crop',
            'article_business': 'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=800&h=400&fit=crop',
            'article_entertainment': 'https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=800&h=400&fit=crop',
            'article_fashion': 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800&h=400&fit=crop',
        }
    
    def get_author_image_path(self, author_name: str, author_id: Optional[int] = None) -> str:
        """Generate consistent path for author image"""
        # Clean author name for filename
        clean_name = self._sanitize_filename(author_name)
        
        # Use ID if provided for uniqueness
        if author_id:
            filename = f"author_{author_id}_{clean_name}.jpg"
        else:
            filename = f"author_{clean_name}.jpg"
        
        return str(self.authors_dir / filename)
    
    def get_article_image_path(self, article_slug: str, article_id: Optional[int] = None) -> str:
        """Generate consistent path for article image"""
        # Clean slug for filename
        clean_slug = self._sanitize_filename(article_slug)
        
        # Use ID if provided for uniqueness
        if article_id:
            filename = f"article_{article_id}_{clean_slug}.jpg"
        else:
            filename = f"article_{clean_slug}.jpg"
        
        return str(self.articles_dir / filename)
    
    def process_author_image(self, author_data: Dict[str, Any]) -> str:
        """Process and return appropriate author image URL"""
        author_name = author_data.get('name', 'Unknown')
        author_id = author_data.get('id')
        image_url = author_data.get('image_url', '')
        
        # Check if local image already exists
        local_path = self.get_author_image_path(author_name, author_id)
        if os.path.exists(local_path):
            # Return relative path from project root
            return os.path.relpath(local_path, self.base_dir)
        
        # If image URL is provided and is external
        if image_url and (image_url.startswith('http://') or image_url.startswith('https://')):
            # For now, return the external URL
            # In production, you might want to download and cache it
            return image_url
        
        # Determine appropriate placeholder based on author info
        placeholder_type = 'author'
        
        # Simple heuristic for gender-appropriate placeholder
        # In production, this should be based on author preference/profile
        female_names = ['sarah', 'jessica', 'maria', 'emma', 'lisa', 'anna', 'emily']
        first_name = author_name.split()[0].lower() if author_name else ''
        if any(name in first_name for name in female_names):
            placeholder_type = 'author_female'
        
        return self.default_placeholders[placeholder_type]
    
    def process_article_image(self, article_data: Dict[str, Any]) -> str:
        """Process and return appropriate article image URL"""
        article_slug = article_data.get('slug', 'unknown')
        article_id = article_data.get('id')
        image_url = article_data.get('image_url', '')
        category = article_data.get('category', '').lower()
        
        # Check if local image already exists
        local_path = self.get_article_image_path(article_slug, article_id)
        if os.path.exists(local_path):
            # Return relative path from project root
            return os.path.relpath(local_path, self.base_dir)
        
        # If image URL is provided and is external
        if image_url and (image_url.startswith('http://') or image_url.startswith('https://')):
            # For now, return the external URL
            # In production, you might want to download and cache it
            return image_url
        
        # Determine appropriate placeholder based on category
        placeholder_type = 'article'
        category_map = {
            'technology': 'article_tech',
            'business': 'article_business',
            'entertainment': 'article_entertainment',
            'fashion': 'article_fashion',
            'beauty': 'article_fashion',
        }
        
        if category in category_map:
            placeholder_type = category_map[category]
        
        return self.default_placeholders[placeholder_type]
    
    def download_image(self, url: str, destination: str) -> bool:
        """Download image from URL to destination"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            # Download the image
            urlretrieve(url, destination)
            logger.info(f"Downloaded image from {url} to {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return False
    
    def copy_placeholder(self, placeholder_key: str, destination: str) -> bool:
        """Copy a placeholder image to destination"""
        try:
            # Get placeholder path
            placeholder_file = self.placeholders_dir / f"{placeholder_key}.jpg"
            
            # If local placeholder doesn't exist, download it
            if not placeholder_file.exists() and placeholder_key in self.default_placeholders:
                self.download_image(self.default_placeholders[placeholder_key], str(placeholder_file))
            
            # Copy to destination
            if placeholder_file.exists():
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy2(placeholder_file, destination)
                logger.info(f"Copied placeholder {placeholder_key} to {destination}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to copy placeholder {placeholder_key}: {e}")
        
        return False
    
    def get_image_dimensions(self, image_path: str) -> Optional[Tuple[int, int]]:
        """Get image dimensions (width, height)"""
        try:
            # This would require PIL/Pillow in production
            # For now, return default dimensions
            if 'author' in image_path:
                return (200, 200)
            else:
                return (800, 400)
        except:
            return None
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use in filename"""
        # Remove special characters and replace spaces
        clean = name.lower()
        clean = clean.replace(' ', '-')
        clean = ''.join(c for c in clean if c.isalnum() or c in '-_')
        return clean[:50]  # Limit length
    
    def ensure_default_images(self):
        """Ensure default placeholder images exist"""
        # Create placeholder files if they don't exist
        placeholder_files = {
            'author_placeholder.svg': self._get_svg_placeholder('person'),
            'article_placeholder.svg': self._get_svg_placeholder('image'),
        }
        
        for filename, content in placeholder_files.items():
            filepath = self.placeholders_dir / filename
            if not filepath.exists():
                with open(filepath, 'w') as f:
                    f.write(content)
                logger.info(f"Created placeholder: {filepath}")
    
    def _get_svg_placeholder(self, icon_type: str) -> str:
        """Generate SVG placeholder"""
        if icon_type == 'person':
            return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
                <rect width="200" height="200" fill="#E5E7EB"/>
                <path d="M100 50 C 70 50, 50 70, 50 100 C 50 120, 60 130, 70 135 C 50 140, 30 155, 30 180 L 170 180 C 170 155, 150 140, 130 135 C 140 130, 150 120, 150 100 C 150 70, 130 50, 100 50" fill="#9CA3AF"/>
            </svg>'''
        else:
            return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
                <rect width="800" height="400" fill="#E5E7EB"/>
                <path d="M 300 150 L 350 200 L 400 175 L 450 225 L 500 200 L 500 250 L 300 250 Z" fill="#9CA3AF"/>
                <circle cx="350" cy="150" r="20" fill="#9CA3AF"/>
            </svg>'''


def main():
    """Test the image handler"""
    handler = ImageHandler()
    
    # Test author image
    author = {
        'id': 1,
        'name': 'Sarah Chen',
        'image_url': ''
    }
    
    author_image = handler.process_author_image(author)
    print(f"Author image: {author_image}")
    
    # Test article image
    article = {
        'id': 1,
        'slug': 'test-article',
        'category': 'technology',
        'image_url': ''
    }
    
    article_image = handler.process_article_image(article)
    print(f"Article image: {article_image}")
    
    # Ensure placeholders exist
    handler.ensure_default_images()


if __name__ == '__main__':
    main()