"""
Image Manager for Influencer News CMS
Handles image path generation, URL extraction, and procurement tracking
"""

import os
import re
import csv
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import logging

# Import configuration
try:
    from .config import config
except ImportError:
    from src.utils.config import config

class ImageManager:
    """Manages image paths and conversions from URLs to local files"""
    
    def __init__(self, base_path: str = None):
        """
        Initialize image manager
        
        Args:
            base_path: Base path for image storage (defaults to config value)
        """
        # Use config value if no path provided
        self.base_path = base_path or config.get('paths.images_dir', 'assets/images')
        self.logger = logging.getLogger(__name__)
        
        # Image type mappings
        self.content_subdirs = {
            'article': 'articles',
            'author': 'authors',
            'category': 'categories',
            'trending': 'trending'
        }
        
        # Placeholder mappings
        self.placeholders = {
            'article': 'article_placeholder.jpg',
            'author': 'author_placeholder.jpg',
            'category': 'category_placeholder.jpg',
            'trending': 'trending_placeholder.jpg',
            'default': 'default_placeholder.jpg'
        }
        
        # Initialize procurement tracking
        self.procurement_list: List[Dict[str, str]] = []
    
    def generate_image_filename(self, content_type: str, content_id: int, 
                              image_type: str, slug: Optional[str] = None) -> str:
        """
        Generate standardized image filename
        
        Args:
            content_type: Type of content (article, author, category, trending)
            content_id: ID of the content
            image_type: Type of image (hero, thumbnail, profile, etc.)
            slug: Optional slug for readable filenames
            
        Returns:
            Generated filename
        """
        # Use slug if provided for better readability
        if slug and content_type in ['author', 'category', 'trending']:
            base = f"{content_type}_{slug}"
        else:
            base = f"{content_type}_{content_id}"
        
        # Add image type
        filename = f"{base}_{image_type}.jpg"
        
        # Sanitize filename
        filename = re.sub(r'[^a-zA-Z0-9_\-.]', '_', filename)
        filename = re.sub(r'_+', '_', filename)
        
        return filename.lower()
    
    def get_image_path(self, content_type: str, filename: str) -> str:
        """
        Get full relative path for an image
        
        Args:
            content_type: Type of content
            filename: Image filename
            
        Returns:
            Full relative path
        """
        subdir = self.content_subdirs.get(content_type, content_type)
        return os.path.join(self.base_path, subdir, filename)
    
    def get_placeholder_path(self, content_type: str) -> str:
        """
        Get placeholder image path for content type
        
        Args:
            content_type: Type of content
            
        Returns:
            Placeholder image path
        """
        placeholder = self.placeholders.get(content_type, self.placeholders['default'])
        return os.path.join("assets/placeholders", placeholder)
    
    def extract_image_url(self, text: str) -> Optional[str]:
        """
        Extract image URL from text content
        
        Args:
            text: Text to search for image URLs
            
        Returns:
            First found image URL or None
        """
        # Common image URL patterns
        patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:jpg|jpeg|png|gif|webp)',
            r'https?://images\.unsplash\.com/[^\s<>"{}|\\^`\[\]]+',
            r'https?://[^\s<>"{}|\\^`\[\]]+/photo-[^\s<>"{}|\\^`\[\]]+'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def extract_all_image_urls(self, text: str) -> List[str]:
        """
        Extract all image URLs from text content
        
        Args:
            text: Text to search for image URLs
            
        Returns:
            List of found image URLs
        """
        urls = []
        patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:jpg|jpeg|png|gif|webp)',
            r'https?://images\.unsplash\.com/[^\s<>"{}|\\^`\[\]]+',
            r'https?://[^\s<>"{}|\\^`\[\]]+/photo-[^\s<>"{}|\\^`\[\]]+'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    def track_image_for_procurement(self, content_type: str, content_id: int,
                                  original_url: str, local_filename: str,
                                  alt_text: str, image_type: str,
                                  dimensions: Optional[str] = None) -> None:
        """
        Add image to procurement tracking list
        
        Args:
            content_type: Type of content
            content_id: ID of content
            original_url: Original external URL
            local_filename: Generated local filename
            alt_text: Alt text for image
            image_type: Type of image
            dimensions: Optional dimensions string
        """
        self.procurement_list.append({
            'content_type': content_type,
            'content_id': str(content_id),
            'original_url': original_url,
            'local_filename': local_filename,
            'alt_text': alt_text,
            'image_type': image_type,
            'dimensions': dimensions or ''
        })
    
    def save_procurement_list(self, filepath: str = None) -> None:
        """
        Save procurement list to CSV file
        
        Args:
            filepath: Path to save CSV file (defaults to config value)
        """
        # Use config value if no path provided
        if filepath is None:
            filepath = config.get('images.procurement_file', 'data/image_procurement_list.csv')
        
        if not self.procurement_list:
            self.logger.warning("No images to save in procurement list")
            return
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['content_type', 'content_id', 'original_url', 
                         'local_filename', 'alt_text', 'image_type', 'dimensions']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(self.procurement_list)
        
        self.logger.info(f"Saved {len(self.procurement_list)} images to procurement list")
    
    def validate_image_file(self, file_path: str, file_size_bytes: int = None) -> bool:
        """
        Validate image file against configuration rules
        
        Args:
            file_path: Path to image file
            file_size_bytes: File size in bytes (optional)
            
        Returns:
            True if valid, False otherwise
        """
        # Check file extension
        allowed_extensions = config.get('images.allowed_extensions', ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in allowed_extensions:
            self.logger.warning(f"Invalid image extension {file_ext}. Allowed: {allowed_extensions}")
            return False
        
        # Check file size if provided
        if file_size_bytes is not None:
            max_size_mb = config.get('images.max_file_size_mb', 10)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size_bytes > max_size_bytes:
                self.logger.warning(f"Image file too large: {file_size_bytes} bytes (max: {max_size_bytes} bytes)")
                return False
        
        return True
    
    def get_thumbnail_size(self) -> Tuple[int, int]:
        """
        Get thumbnail size from configuration
        
        Returns:
            Tuple of (width, height)
        """
        size_config = config.get('images.thumbnail_size', [300, 200])
        return tuple(size_config) if isinstance(size_config, list) else (300, 200)
    
    def should_generate_thumbnails(self) -> bool:
        """
        Check if thumbnails should be generated based on configuration
        
        Returns:
            True if thumbnails should be generated
        """
        return config.get('images.generate_thumbnails', True)
    
    def create_directory_structure(self) -> None:
        """Create necessary directory structure for images"""
        # Create main directories
        dirs = [
            self.base_path,
            "assets/placeholders"
        ]
        
        # Add content type subdirectories
        for subdir in self.content_subdirs.values():
            dirs.append(os.path.join(self.base_path, subdir))
        
        # Create all directories
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {dir_path}")
    
    def generate_img_tag(self, local_filename: str, alt_text: str,
                        content_type: str, css_class: str = "",
                        base_path: str = "../") -> str:
        """
        Generate complete HTML img tag with fallback
        
        Args:
            local_filename: Local image filename
            alt_text: Alt text for accessibility
            content_type: Type of content for proper path
            css_class: Optional CSS class
            base_path: Base path prefix (varies by page depth)
            
        Returns:
            Complete HTML img tag
        """
        # Get full paths
        img_path = self.get_image_path(content_type, local_filename)
        placeholder_path = self.get_placeholder_path(content_type)
        
        # Build attributes
        attrs = [
            f'src="{base_path}{img_path}"',
            f'alt="{alt_text}"',
            f'onerror="this.src=\'{base_path}{placeholder_path}\'"',
            'loading="lazy"'
        ]
        
        if css_class:
            attrs.append(f'class="{css_class}"')
        
        return f'<img {" ".join(attrs)}>'
    
    def convert_url_to_local(self, image_url: str, content_type: str,
                           content_id: int, image_type: str,
                           slug: Optional[str] = None,
                           alt_text: Optional[str] = None) -> Tuple[str, str]:
        """
        Convert external URL to local filename and track for procurement
        
        Args:
            image_url: External image URL
            content_type: Type of content
            content_id: ID of content
            image_type: Type of image
            slug: Optional slug for filename
            alt_text: Alt text for image
            
        Returns:
            Tuple of (local_filename, img_tag)
        """
        # Generate local filename
        local_filename = self.generate_image_filename(
            content_type, content_id, image_type, slug
        )
        
        # Generate alt text if not provided
        if not alt_text:
            alt_text = f"{content_type.title()} {image_type} image"
        
        # Track for procurement
        self.track_image_for_procurement(
            content_type=content_type,
            content_id=content_id,
            original_url=image_url,
            local_filename=local_filename,
            alt_text=alt_text,
            image_type=image_type
        )
        
        # Generate img tag
        img_tag = self.generate_img_tag(
            local_filename=local_filename,
            alt_text=alt_text,
            content_type=content_type
        )
        
        return local_filename, img_tag
    
    def get_procurement_summary(self) -> Dict[str, int]:
        """
        Get summary of images tracked for procurement
        
        Returns:
            Dictionary with counts by content type
        """
        summary = {}
        for item in self.procurement_list:
            content_type = item['content_type']
            summary[content_type] = summary.get(content_type, 0) + 1
        
        return summary