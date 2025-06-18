#!/usr/bin/env python3
"""
Base Integrator Class
====================
Shared functionality for all content integrators using SQLite database
"""

import os
import sys
import json
import datetime
import html
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod

try:
    from ..database import DatabaseManager
except ImportError:
    from src.database import DatabaseManager
try:
    from ..models import Article, Author, Category, TrendingTopic, Image
    from ..utils import ImageManager, PathManager
    from ..utils.trusted_security import trusted_sanitizer, trusted_validator
    from ..utils.security_middleware import security_middleware
except ImportError:
    from src.models import Article, Author, Category, TrendingTopic, Image
    from src.utils import ImageManager, PathManager
    from src.utils.trusted_security import trusted_sanitizer, trusted_validator
    from src.utils.security_middleware import security_middleware


class BaseIntegrator(ABC):
    """Base class for all content integrators using SQLite database"""
    
    def __init__(self, content_type: str, content_dir: str):
        self.content_type = content_type
        self.content_dir = Path("content") / content_dir
        self.content_dir.mkdir(parents=True, exist_ok=True)
        
        # Integrated output directory for generated content
        self.integrated_dir = Path("integrated") / content_dir
        self.integrated_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database and image managers
        self.db = DatabaseManager()
        self.image_manager = ImageManager()
        
        # Initialize site integrator for site-wide configuration
        self._site_integrator = None
        
        # Progress callback for GUI updates
        self.progress_callback: Optional[Callable] = None
        
        # Common category colors
        self.category_colors = {
            'business': 'green',
            'entertainment': 'orange', 
            'tech': 'blue',
            'technology': 'blue',
            'fashion': 'pink',
            'charity': 'purple',
            'beauty': 'pink',
            'lifestyle': 'indigo',
            'sports': 'red',
            'gaming': 'purple',
            'food': 'yellow',
            'travel': 'teal',
            'creator-economy': 'purple'
        }
    
    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def update_progress(self, message: str, progress: float = None):
        """Update progress via callback if set"""
        if self.progress_callback:
            self.progress_callback(self.content_type, message, progress)
    
    @abstractmethod
    def parse_content_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a content file - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def create_content_page(self, content: Any):
        """Create individual content page - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def update_listing_page(self, content_list: List[Any]):
        """Update the main listing page - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def create_sample_file(self):
        """Create a sample file for reference - must be implemented by subclasses"""
        pass
    
    def validate_required_fields(self, content: Dict[str, Any], required_fields: List[str], file_path: Path):
        """Validate that all required fields are present"""
        missing_fields = [field for field in required_fields if field not in content or not content[field]]
        if missing_fields:
            raise ValueError(f"Missing required fields in {file_path}: {', '.join(missing_fields)}")
    
    def format_date_relative(self, date_str: str) -> str:
        """Format date as relative time"""
        try:
            if isinstance(date_str, datetime.datetime):
                date_obj = date_str
            else:
                date_obj = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            now = datetime.datetime.now()
            if date_obj.tzinfo:
                now = now.replace(tzinfo=date_obj.tzinfo)
                
            diff = now - date_obj
            
            if diff.days > 365:
                years = diff.days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
            elif diff.days > 30:
                months = diff.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            elif diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                minutes = max(1, diff.seconds // 60)
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        except:
            return "Recently"
    
    def parse_metadata_section(self, metadata_text: str) -> Dict[str, str]:
        """Parse metadata section with key: value pairs"""
        metadata = {}
        for line in metadata_text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip().lower().replace(' ', '_')] = value.strip()
        return metadata
    
    def sanitize_html(self, text: str, allow_html: bool = False) -> str:
        """Sanitize HTML using most secure trusted sanitizer - always validates against whitelist"""
        if text is None:
            return ""
        # Always use secure sanitization with trusted whitelist of tags
        return trusted_sanitizer.sanitize_html(str(text), allow_tags=allow_html)
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text content (no HTML allowed)"""
        if text is None:
            return ""
        return trusted_sanitizer.sanitize_text(str(text))
    
    def escape_js_string(self, text: str) -> str:
        """Safely escape string for JavaScript using trusted sanitization"""
        if text is None:
            return ""
        # First sanitize, then escape for JavaScript
        sanitized = trusted_sanitizer.sanitize_text(str(text))
        return sanitized.replace('"', '\\"').replace('\n', '\\n').replace('\r', '').replace("'", "\\'")
    
    def escape_html(self, text: str) -> str:
        """Safely escape text for HTML using most secure trusted sanitization"""
        if text is None:
            return ""
        return trusted_sanitizer.sanitize_text(str(text))
    
    def validate_and_sanitize_content(self, content: str, content_type: str = 'general') -> str:
        """Validate and sanitize content using most secure trusted validator with strict validation"""
        try:
            if content_type == 'html':
                # Even for HTML content, use strict validation with trusted whitelist only
                return trusted_validator.validate_and_sanitize_text(
                    content, content_type, allow_html=True, required=False
                )
            else:
                # For non-HTML content, strip all HTML tags
                return trusted_validator.validate_and_sanitize_text(
                    content, content_type, allow_html=False, required=False
                )
        except ValueError as e:
            self.update_progress(f"Content validation failed with strict security: {e}")
            # Always return secure fallback with no HTML
            return trusted_sanitizer.sanitize_text(content or "")
    
    def get_category_color(self, category: str) -> str:
        """Get color for category"""
        return self.category_colors.get(category.lower(), 'gray')
    
    def get_security_meta_tags(self) -> str:
        """Get security meta tags for HTML pages"""
        return security_middleware.get_meta_tags()
    
    def get_current_nonce(self) -> str:
        """Get current nonce for inline scripts"""
        return security_middleware.get_current_nonce()
    
    def get_secure_html_head(self, title: str, description: str = "", additional_meta: str = "") -> str:
        """Generate secure HTML head section"""
        sanitized_title = self.sanitize_text(title)
        sanitized_description = self.sanitize_text(description)
        nonce = self.get_current_nonce()
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{sanitized_title}</title>
    {f'<meta name="description" content="{sanitized_description}">' if description else ''}
    
    {self.get_security_meta_tags()}
    
    <link rel="stylesheet" href="../assets/css/styles.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    
    <!-- PWA Configuration -->
    <link rel="manifest" href="../manifest.json">
    <meta name="theme-color" content="#4f46e5">
    
    {additional_meta}
</head>'''
    
    def get_secure_html_scripts(self) -> str:
        """Get secure script section for HTML pages"""
        nonce = self.get_current_nonce()
        return f'''
    <!-- Security: DOMPurify for HTML sanitization -->
    <script src="https://cdn.jsdelivr.net/npm/dompurify@3.1.7/dist/purify.min.js" integrity="sha384-LW1Q2+3pcx1jz7WDNJ6X4LWq7l5D7Lrf7K8V9Vq0T6kl5o9S1R7B8tLqGZhcQ2E" crossorigin="anonymous"></script>
    
    <!-- Trusted Sanitization -->
    <script src="../assets/js/trusted-sanitizer.js" nonce="{nonce}"></script>
    
    <!-- Mobile Touch Enhancements -->
    <script src="../assets/js/mobile-touch.js" nonce="{nonce}"></script>'''
    
    def get_path_manager(self, current_location: str) -> PathManager:
        """Get path manager for current page location"""
        return PathManager.from_page_location(current_location)
    
    def get_site_integrator(self):
        """Get site integrator instance (lazy loading)"""
        if self._site_integrator is None:
            # Import here to avoid circular imports
            try:
                from .site_integrator import SiteIntegrator
            except ImportError:
                from src.integrators.site_integrator import SiteIntegrator
            self._site_integrator = SiteIntegrator()
        return self._site_integrator
    
    def get_site_config(self, config_type: str = None) -> Dict[str, Any]:
        """Get site configuration"""
        site_integrator = self.get_site_integrator()
        if config_type:
            return site_integrator.get_config_by_type(config_type)
        return site_integrator.get_site_config()
    
    def generate_site_header(self, current_page: str = '', page_title: str = None, path_prefix: str = '') -> str:
        """Generate standardized site header"""
        site_integrator = self.get_site_integrator()
        return site_integrator.generate_header_html(current_page, path_prefix)
    
    def generate_site_footer(self, path_prefix: str = '') -> str:
        """Generate standardized site footer"""
        site_integrator = self.get_site_integrator()
        return site_integrator.generate_footer_html(path_prefix)
    
    def generate_site_meta_tags(self, page_title: str = None, page_description: str = None) -> str:
        """Generate site meta tags"""
        site_integrator = self.get_site_integrator()
        return site_integrator.generate_site_meta_tags(page_title, page_description)
    
    def generate_navigation_html(self, current_location: str, active_page: str = '') -> str:
        """Generate navigation HTML with proper paths"""
        path_manager = self.get_path_manager(current_location)
        nav_links = path_manager.generate_navigation_links()
        
        nav_items = []
        for page, link in nav_links.items():
            active_class = 'active' if page == active_page else ''
            nav_items.append(f'<a href="{link}" class="nav-link {active_class}">{page.title()}</a>')
        
        return ' | '.join(nav_items)
    
    def convert_image_urls(self, content: Dict[str, Any], content_type: str, 
                          content_id: int, slug: Optional[str] = None) -> Dict[str, Any]:
        """Convert external image URLs to local references"""
        # Extract image URLs from content
        image_fields = ['image', 'image_url', 'hero_image', 'thumbnail']
        
        for field in image_fields:
            if field in content and content[field]:
                # Determine image type based on field
                if field in ['hero_image', 'image_url']:
                    image_type = 'hero'
                elif field == 'thumbnail':
                    image_type = 'thumbnail'
                elif field == 'image':
                    image_type = 'profile' if content_type == 'author' else 'hero'
                else:
                    image_type = 'image'
                
                # Convert URL to local reference
                local_filename, img_tag = self.image_manager.convert_url_to_local(
                    image_url=content[field],
                    content_type=content_type,
                    content_id=content_id,
                    image_type=image_type,
                    slug=slug,
                    alt_text=content.get('title', content.get('name', ''))
                )
                
                # Store in database
                self.db.create_image(
                    content_type=content_type,
                    content_id=content_id,
                    image_type=image_type,
                    local_filename=local_filename,
                    original_url=content[field],
                    alt_text=content.get('title', content.get('name', '')),
                    is_placeholder=True
                )
                
                # Update content with local reference
                content[f'{field}_local'] = local_filename
                content[f'{field}_tag'] = img_tag
        
        return content
    
    def process_new_content(self) -> int:
        """Process all new content files"""
        self.update_progress("Starting content processing...", 0)
        processed_count = 0
        
        # Get all .txt files in content directory
        txt_files = list(self.content_dir.glob("*.txt"))
        total_files = len(txt_files)
        
        if total_files == 0:
            self.update_progress("No content files found. Creating sample...", 100)
            self.create_sample_file()
            return 0
        
        # Process each .txt file
        for idx, file_path in enumerate(txt_files):
            progress = (idx / total_files) * 100
            
            try:
                self.update_progress(f"Processing: {file_path.name}", progress)
                
                # Parse content file
                content_data = self.parse_content_file(file_path)
                content_data['filename'] = file_path.name
                
                # Process based on content type
                if self.content_type == 'articles':
                    processed = self.process_article(content_data)
                elif self.content_type == 'authors':
                    processed = self.process_author(content_data)
                elif self.content_type == 'categories':
                    processed = self.process_category(content_data)
                elif self.content_type == 'trending':
                    processed = self.process_trending(content_data)
                else:
                    raise ValueError(f"Unknown content type: {self.content_type}")
                
                if processed:
                    processed_count += 1
                    self.update_progress(f"Successfully processed: {content_data.get('name', content_data.get('title', 'Unknown'))}", progress)
                
            except Exception as e:
                self.update_progress(f"Error processing {file_path.name}: {str(e)}", progress)
                continue
        
        if processed_count > 0:
            # Update listing pages
            self.update_all_listing_pages()
            
            # Save image procurement list
            self.image_manager.save_procurement_list()
            
            self.update_progress(f"Successfully integrated {processed_count} new {self.content_type}!", 100)
        else:
            self.update_progress(f"No new {self.content_type} to process.", 100)
        
        return processed_count
    
    def sync_with_files(self) -> Dict[str, int]:
        """Sync database content with content files (bidirectional)"""
        self.update_progress("Starting bidirectional content sync...", 0)
        
        # Get all .txt files in content directory
        txt_files = list(self.content_dir.glob("*.txt"))
        file_names = {f.stem for f in txt_files}  # Remove .txt extension
        
        # Get existing content from database based on content type
        existing_content = self.get_existing_content()
        existing_slugs = {item.slug for item in existing_content}
        existing_by_slug = {item.slug: item for item in existing_content}
        
        stats = {'added': 0, 'removed': 0, 'updated': 0, 'skipped': 0}
        
        # Process files (add new, update existing)
        for idx, file_path in enumerate(txt_files):
            progress = (idx / len(txt_files)) * 50  # First half of progress
            
            try:
                self.update_progress(f"Processing file: {file_path.name}", progress)
                
                # Parse content file
                content_data = self.parse_content_file(file_path)
                content_data['filename'] = file_path.name
                
                # Generate slug from filename or content
                file_slug = file_path.stem
                content_slug = self.generate_slug_from_content(content_data)
                
                # Check if content exists (by slug or filename)
                existing_item = existing_by_slug.get(content_slug) or existing_by_slug.get(file_slug)
                
                if existing_item:
                    # Content exists - check if it needs updating
                    if self.content_has_changed(existing_item, content_data, file_path):
                        # Content has changed - update it
                        updated = self.update_existing_content(existing_item, content_data)
                        if updated:
                            stats['updated'] += 1
                            self.update_progress(f"Updated: {content_data.get('name', content_data.get('title', file_slug))}", progress)
                        else:
                            stats['skipped'] += 1
                            self.update_progress(f"Update failed: {content_data.get('name', content_data.get('title', file_slug))}", progress)
                    else:
                        stats['skipped'] += 1
                        self.update_progress(f"No changes: {content_data.get('name', content_data.get('title', file_slug))}", progress)
                else:
                    # New content - add it
                    processed = self.process_content_by_type(content_data)
                    if processed:
                        stats['added'] += 1
                        self.update_progress(f"Added: {content_data.get('name', content_data.get('title', file_slug))}", progress)
                
            except Exception as e:
                self.update_progress(f"Error processing {file_path.name}: {str(e)}", progress)
                continue
        
        # Remove content that no longer has files
        for idx, item in enumerate(existing_content):
            progress = 50 + (idx / len(existing_content)) * 50  # Second half of progress
            
            # Check if this item has a corresponding file
            item_has_file = (item.slug in file_names or 
                           any(f.stem == item.slug for f in txt_files) or
                           self.content_has_source_file(item, txt_files))
            
            if not item_has_file:
                try:
                    self.update_progress(f"Removing orphaned: {getattr(item, 'name', getattr(item, 'title', item.slug))}", progress)
                    
                    # Remove generated HTML files first
                    self.remove_generated_files(item)
                    
                    # Then remove from database
                    success = item.delete()
                    if success:
                        stats['removed'] += 1
                        self.update_progress(f"Removed: {getattr(item, 'name', getattr(item, 'title', item.slug))}", progress)
                except Exception as e:
                    if "FOREIGN KEY constraint failed" in str(e):
                        # Show what's preventing deletion
                        references = self.find_foreign_key_references(item)
                        ref_info = ", ".join([f"{ref['count']} {ref['table']}" for ref in references])
                        self.update_progress(f"Cannot remove {getattr(item, 'name', getattr(item, 'title', item.slug))} - referenced by: {ref_info}", progress)
                    else:
                        self.update_progress(f"Error removing {item.slug}: {str(e)}", progress)
        
        # Clean up any orphaned HTML files that don't have database entries
        self.update_progress("Cleaning up orphaned files...", 90)
        orphaned_count = self.clean_orphaned_html_files()
        if orphaned_count > 0:
            stats['removed'] += orphaned_count
            self.update_progress(f"Removed {orphaned_count} orphaned HTML files", 90)
        
        # Update listing pages if there were any changes
        if stats['added'] > 0 or stats['removed'] > 0:
            self.update_progress("Updating listing pages...", 95)
            self.update_all_listing_pages()
        
        self.update_progress(f"Sync complete: +{stats['added']} -{stats['removed']} ={stats['skipped']}", 100)
        return stats
    
    def find_foreign_key_references(self, item):
        """Find what database records reference this item, preventing deletion"""
        references = []
        table_name = self.content_type  # e.g., 'categories', 'authors'
        record_id = item.id
        
        try:
            from ..database.db_manager import DatabaseManager
            db = DatabaseManager()
            
            with db.get_connection() as conn:
                # Get all tables
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                tables = [row['name'] for row in cursor.fetchall()]
                
                # For each table, check its foreign key constraints
                for target_table in tables:
                    if target_table == table_name:
                        continue  # Skip the source table
                        
                    try:
                        # Get foreign key info for this table
                        cursor = conn.execute(f'PRAGMA foreign_key_list({target_table})')
                        fks = cursor.fetchall()
                        
                        for fk in fks:
                            fk_dict = dict(fk)
                            if fk_dict['table'] == table_name:  # This FK points to our table
                                fk_column = fk_dict['from']
                                
                                # Check if any records reference our ID
                                query = f'SELECT COUNT(*) as count FROM {target_table} WHERE {fk_column} = ?'
                                cursor = conn.execute(query, (record_id,))
                                count = cursor.fetchone()['count']
                                
                                if count > 0:
                                    references.append({
                                        'table': target_table,
                                        'fk_column': fk_column,
                                        'count': count
                                    })
                    except Exception:
                        continue  # Skip tables with issues
                        
        except Exception:
            pass  # If we can't determine references, just return empty list
            
        return references
    
    def get_existing_content(self, limit: int = 1000):
        """Get existing content from database with limit (to be implemented by subclasses)"""
        if self.content_type == 'articles':
            from ..models.article import Article
            return Article.find_all(limit=limit)
        elif self.content_type == 'authors':
            from ..models.author import Author
            return Author.find_all(limit=limit)
        elif self.content_type == 'categories':
            from ..models.category import Category
            return Category.find_all(limit=limit)
        elif self.content_type == 'trending':
            from ..models.trending import TrendingTopic
            return TrendingTopic.find_all(limit=limit)
        else:
            return []
    
    def generate_slug_from_content(self, content_data: Dict[str, Any]) -> str:
        """Generate slug from content data"""
        if 'slug' in content_data and content_data['slug']:
            return content_data['slug']
        
        # Try different fields for slug generation
        title = content_data.get('title') or content_data.get('name') or content_data.get('topic', '')
        if title:
            slug = title.lower().replace(' ', '-').replace(',', '').replace(':', '').replace('?', '').replace('!', '')
            return ''.join(c for c in slug if c.isalnum() or c == '-')
        
        # Fallback to filename
        return content_data.get('filename', '').replace('.txt', '')
    
    def content_has_source_file(self, item, txt_files) -> bool:
        """Check if content item has a corresponding source file"""
        # Check by slug
        for file_path in txt_files:
            if file_path.stem == item.slug:
                return True
                
        # Check by parsing each file to see if it matches this content
        for file_path in txt_files:
            try:
                content_data = self.parse_content_file(file_path)
                content_slug = self.generate_slug_from_content(content_data)
                if content_slug == item.slug:
                    return True
            except:
                continue
                
        return False
    
    def process_content_by_type(self, content_data: Dict[str, Any]) -> bool:
        """Process content based on content type"""
        if self.content_type == 'articles':
            return self.process_article(content_data)
        elif self.content_type == 'authors':
            return self.process_author(content_data)
        elif self.content_type == 'categories':
            return self.process_category(content_data)
        elif self.content_type == 'trending':
            return self.process_trending(content_data)
        else:
            return False
    
    def process_article(self, content_data: Dict[str, Any]) -> bool:
        """Process article content - to be implemented by ArticleIntegrator"""
        return False
    
    def process_author(self, content_data: Dict[str, Any]) -> bool:
        """Process author content - to be implemented by AuthorIntegrator"""
        return False
    
    def process_category(self, content_data: Dict[str, Any]) -> bool:
        """Process category content - to be implemented by CategoryIntegrator"""
        return False
    
    def process_trending(self, content_data: Dict[str, Any]) -> bool:
        """Process trending content - to be implemented by TrendingIntegrator"""
        return False
    
    def content_has_changed(self, existing_item, content_data: Dict[str, Any], file_path: Path) -> bool:
        """Check if content has changed compared to existing database item"""
        import os
        
        try:
            # Compare file modification time with database last_modified if available
            file_mtime = os.path.getmtime(file_path)
            if hasattr(existing_item, 'last_modified') and existing_item.last_modified:
                try:
                    from datetime import datetime
                    # Parse database timestamp
                    if isinstance(existing_item.last_modified, str):
                        db_time = datetime.fromisoformat(existing_item.last_modified.replace('Z', '+00:00'))
                    else:
                        db_time = existing_item.last_modified
                    
                    db_timestamp = db_time.timestamp()
                    
                    # If file is newer than database record, consider it changed
                    if file_mtime > db_timestamp + 1:  # 1 second tolerance
                        return True
                except:
                    pass  # If timestamp comparison fails, fall back to content comparison
            
            # Compare key content fields
            content_fields = self.get_comparable_fields(existing_item, content_data)
            
            for field_name, (db_value, file_value) in content_fields.items():
                # Normalize values for comparison
                db_str = str(db_value or '').strip()
                file_str = str(file_value or '').strip()
                
                if db_str != file_str:
                    self.update_progress(f"Field '{field_name}' changed in {file_path.name}")
                    return True
            
            return False
            
        except Exception as e:
            self.update_progress(f"Error checking changes for {file_path.name}: {str(e)}")
            # If we can't determine, assume it has changed to be safe
            return True
    
    def get_comparable_fields(self, existing_item, content_data: Dict[str, Any]) -> Dict[str, tuple]:
        """Get fields to compare between database item and file content"""
        fields = {}
        
        # Common fields for all content types
        if hasattr(existing_item, 'title') and 'title' in content_data:
            fields['title'] = (existing_item.title, content_data['title'])
        elif hasattr(existing_item, 'name') and 'name' in content_data:
            fields['name'] = (existing_item.name, content_data['name'])
        
        if hasattr(existing_item, 'description') and 'description' in content_data:
            fields['description'] = (existing_item.description, content_data['description'])
        
        # Content-specific fields
        if self.content_type == 'articles':
            if hasattr(existing_item, 'content') and 'content' in content_data:
                fields['content'] = (existing_item.content, content_data['content'])
            if hasattr(existing_item, 'excerpt') and 'excerpt' in content_data:
                fields['excerpt'] = (existing_item.excerpt, content_data['excerpt'])
        elif self.content_type == 'authors':
            if hasattr(existing_item, 'bio') and 'bio' in content_data:
                fields['bio'] = (existing_item.bio, content_data['bio'])
            if hasattr(existing_item, 'expertise') and 'expertise' in content_data:
                fields['expertise'] = (existing_item.expertise, content_data['expertise'])
        elif self.content_type == 'categories':
            if hasattr(existing_item, 'icon') and 'icon' in content_data:
                fields['icon'] = (existing_item.icon, content_data['icon'])
        elif self.content_type == 'trending':
            if hasattr(existing_item, 'heat_score') and 'heat_score' in content_data:
                fields['heat_score'] = (existing_item.heat_score, content_data['heat_score'])
        
        return fields
    
    def update_existing_content(self, existing_item, content_data: Dict[str, Any]) -> bool:
        """Update existing content with new data from file"""
        try:
            # Update the item with new data
            updated = False
            
            if self.content_type == 'articles':
                updated = self.update_article(existing_item, content_data)
            elif self.content_type == 'authors':
                updated = self.update_author(existing_item, content_data)
            elif self.content_type == 'categories':
                updated = self.update_category(existing_item, content_data)
            elif self.content_type == 'trending':
                updated = self.update_trending(existing_item, content_data)
            
            if updated:
                # Regenerate the individual page for this content
                self.create_content_page(existing_item)
                self.update_progress(f"Regenerated page for {getattr(existing_item, 'title', getattr(existing_item, 'name', existing_item.slug))}")
            
            return updated
            
        except Exception as e:
            self.update_progress(f"Error updating content: {str(e)}")
            return False
    
    def update_article(self, article, content_data: Dict[str, Any]) -> bool:
        """Update article - to be implemented by ArticleIntegrator"""
        return False
    
    def update_author(self, author, content_data: Dict[str, Any]) -> bool:
        """Update author - to be implemented by AuthorIntegrator"""
        return False
    
    def update_category(self, category, content_data: Dict[str, Any]) -> bool:
        """Update category - to be implemented by CategoryIntegrator"""
        return False
    
    def update_trending(self, trending, content_data: Dict[str, Any]) -> bool:
        """Update trending - to be implemented by TrendingIntegrator"""
        return False
    
    def update_all_listing_pages(self):
        """Update all listing pages with current database content"""
        # This will be called after processing to regenerate listing pages
        pass
    
    def remove_generated_files(self, item):
        """Remove generated HTML files for a content item"""
        try:
            if self.content_type == 'articles':
                # Remove article page
                article_file = Path("integrated/articles") / f"article_{item.id}.html"
                if article_file.exists():
                    article_file.unlink()
                    self.update_progress(f"Removed {article_file}")
                    
            elif self.content_type == 'authors':
                # Remove author page
                author_file = Path("integrated/authors") / f"author_{item.slug}.html"
                if author_file.exists():
                    author_file.unlink()
                    self.update_progress(f"Removed {author_file}")
                    
            elif self.content_type == 'categories':
                # Remove category page
                category_file = Path("integrated/categories") / f"category_{item.slug}.html"
                if category_file.exists():
                    category_file.unlink()
                    self.update_progress(f"Removed {category_file}")
                    
            elif self.content_type == 'trending':
                # Remove trending page
                trend_file = Path("integrated/trending") / f"trend_{item.slug}.html"
                if trend_file.exists():
                    trend_file.unlink()
                    self.update_progress(f"Removed {trend_file}")
                    
        except Exception as e:
            self.update_progress(f"Error removing generated files for {item.slug}: {str(e)}")
    
    def clean_orphaned_html_files(self) -> int:
        """Remove HTML files that don't have corresponding database entries"""
        try:
            # Get existing content from database
            existing_content = self.get_existing_content()
            
            # Create set of valid file names
            valid_files = set()
            for item in existing_content:
                if self.content_type == 'articles':
                    valid_files.add(f"article_{item.id}.html")
                elif self.content_type == 'authors':
                    valid_files.add(f"author_{item.slug}.html")
                elif self.content_type == 'categories':
                    valid_files.add(f"category_{item.slug}.html")
                elif self.content_type == 'trending':
                    valid_files.add(f"trend_{item.slug}.html")
            
            # Check integrated directory for orphaned files
            integrated_path = Path("integrated") / self.content_type
            if not integrated_path.exists():
                return 0
            
            removed_count = 0
            for html_file in integrated_path.glob("*.html"):
                if html_file.name not in valid_files:
                    html_file.unlink()
                    self.update_progress(f"Removed orphaned file: {html_file}")
                    removed_count += 1
            
            return removed_count
            
        except Exception as e:
            self.update_progress(f"Error cleaning orphaned files: {str(e)}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about integrated content"""
        stats = {}
        
        if self.content_type == 'articles':
            stats['total_count'] = self.db.execute_one("SELECT COUNT(*) as count FROM articles")['count']
        elif self.content_type == 'authors':
            stats['total_count'] = self.db.execute_one("SELECT COUNT(*) as count FROM authors")['count']
        elif self.content_type == 'categories':
            stats['total_count'] = self.db.execute_one("SELECT COUNT(*) as count FROM categories")['count']
        elif self.content_type == 'trending':
            stats['total_count'] = self.db.execute_one("SELECT COUNT(*) as count FROM trending_topics")['count']
        
        return stats