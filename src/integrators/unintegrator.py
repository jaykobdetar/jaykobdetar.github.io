#!/usr/bin/env python3
"""
Content Unintegrator
====================
Removes integrated content and cleans up references
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable


class ContentUnintegrator:
    """Handles removal of integrated content"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.integrated_dir = Path("integrated")
        self.progress_callback: Optional[Callable] = None
        
    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def update_progress(self, message: str, progress: float = None):
        """Update progress via callback if set"""
        if self.progress_callback:
            self.progress_callback("unintegrator", message, progress)
    
    def remove_content_by_id(self, content_type: str, content_id: int) -> bool:
        """Remove a specific piece of content by ID"""
        try:
            # Load database
            db_file = self.data_dir / f"{content_type}_db.json"
            if not db_file.exists():
                self.update_progress(f"No database found for {content_type}")
                return False
                
            with open(db_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
            
            # Find content item
            content_items = db.get(content_type, [])
            item_to_remove = None
            for item in content_items:
                if item.get('id') == content_id:
                    item_to_remove = item
                    break
            
            if not item_to_remove:
                self.update_progress(f"Content ID {content_id} not found in {content_type}")
                return False
            
            # Remove files
            self._remove_content_files(content_type, item_to_remove)
            
            # Remove from database
            content_items.remove(item_to_remove)
            
            # Save updated database
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            
            # Update listing pages
            self._update_listing_pages(content_type, content_items)
            
            self.update_progress(f"Successfully removed {content_type} ID {content_id}")
            return True
            
        except Exception as e:
            self.update_progress(f"Error removing {content_type} ID {content_id}: {str(e)}")
            return False
    
    def remove_content_by_filename(self, content_type: str, filename: str) -> bool:
        """Remove content by source filename"""
        try:
            # Load database
            db_file = self.data_dir / f"{content_type}_db.json"
            if not db_file.exists():
                self.update_progress(f"No database found for {content_type}")
                return False
                
            with open(db_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
            
            # Find content item
            content_items = db.get(content_type, [])
            item_to_remove = None
            for item in content_items:
                if item.get('filename') == filename:
                    item_to_remove = item
                    break
            
            if not item_to_remove:
                self.update_progress(f"Content with filename {filename} not found in {content_type}")
                return False
            
            # Remove files
            self._remove_content_files(content_type, item_to_remove)
            
            # Remove from database
            content_items.remove(item_to_remove)
            
            # Save updated database
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            
            # Update listing pages
            self._update_listing_pages(content_type, content_items)
            
            self.update_progress(f"Successfully removed {content_type} with filename {filename}")
            return True
            
        except Exception as e:
            self.update_progress(f"Error removing {content_type} with filename {filename}: {str(e)}")
            return False
    
    def _remove_content_files(self, content_type: str, item: Dict[str, Any]):
        """Remove the generated files for a content item"""
        content_dir = self.integrated_dir / content_type
        
        if content_type == 'articles':
            # Remove article page
            article_file = content_dir / f"article_{item['id']}.html"
            if article_file.exists():
                article_file.unlink()
                self.update_progress(f"Removed {article_file}")
                
        elif content_type == 'authors':
            # Remove author page
            author_slug = item['name'].lower().replace(' ', '-')
            author_file = content_dir / f"author_{author_slug}.html"
            if author_file.exists():
                author_file.unlink()
                self.update_progress(f"Removed {author_file}")
                
        elif content_type == 'categories':
            # Remove category page
            category_file = content_dir / f"category_{item['slug']}.html"
            if category_file.exists():
                category_file.unlink()
                self.update_progress(f"Removed {category_file}")
                
        elif content_type == 'trending':
            # Remove trending page
            trend_slug = item['topic'].lower().replace(' ', '-')
            trend_file = content_dir / f"trend_{trend_slug}.html"
            if trend_file.exists():
                trend_file.unlink()
                self.update_progress(f"Removed {trend_file}")
    
    def clean_orphaned_files(self, content_type: str) -> int:
        """Remove files that don't have corresponding database entries"""
        try:
            # Load database
            db_file = self.data_dir / f"{content_type}_db.json"
            if not db_file.exists():
                self.update_progress(f"No database found for {content_type}")
                return 0
                
            with open(db_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
            
            content_items = db.get(content_type, [])
            content_dir = self.integrated_dir / content_type
            
            if not content_dir.exists():
                return 0
            
            # Get valid filenames from database
            valid_files = set()
            for item in content_items:
                if content_type == 'articles':
                    valid_files.add(f"article_{item['id']}.html")
                elif content_type == 'authors':
                    author_slug = item['name'].lower().replace(' ', '-')
                    valid_files.add(f"author_{author_slug}.html")
                elif content_type == 'categories':
                    valid_files.add(f"category_{item['slug']}.html")
                elif content_type == 'trending':
                    trend_slug = item['topic'].lower().replace(' ', '-')
                    valid_files.add(f"trend_{trend_slug}.html")
            
            # Remove orphaned files
            removed_count = 0
            for file_path in content_dir.glob("*.html"):
                if file_path.name not in valid_files:
                    file_path.unlink()
                    self.update_progress(f"Removed orphaned file: {file_path}")
                    removed_count += 1
            
            return removed_count
            
        except Exception as e:
            self.update_progress(f"Error cleaning orphaned {content_type} files: {str(e)}")
            return 0
    
    def remove_all_content(self, content_type: str) -> bool:
        """Remove all content of a specific type"""
        try:
            # Load database
            db_file = self.data_dir / f"{content_type}_db.json"
            if not db_file.exists():
                self.update_progress(f"No database found for {content_type}")
                return True  # Nothing to remove
                
            with open(db_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
            
            content_items = db.get(content_type, [])
            total_items = len(content_items)
            
            if total_items == 0:
                self.update_progress(f"No {content_type} to remove")
                return True
            
            # Remove all files
            for i, item in enumerate(content_items):
                progress = (i / total_items) * 100
                self.update_progress(f"Removing {content_type} {i+1}/{total_items}", progress)
                self._remove_content_files(content_type, item)
            
            # Clear database but keep structure
            db[content_type] = []
            db['next_id'] = 1
            db['last_integration'] = None
            
            # Save updated database
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            
            # Update listing pages with empty content to clear them
            self._update_listing_pages(content_type, [])
            
            self.update_progress(f"Successfully removed all {total_items} {content_type}", 100)
            return True
            
        except Exception as e:
            self.update_progress(f"Error removing all {content_type}: {str(e)}")
            return False
    
    def _remove_listing_pages(self, content_type: str):
        """Remove listing pages for content type"""
        if content_type == 'categories':
            categories_file = self.integrated_dir / "categories.html"
            if categories_file.exists():
                categories_file.unlink()
                self.update_progress(f"Removed {categories_file}")
                
        elif content_type == 'trending':
            trending_file = self.integrated_dir / "trending.html"
            if trending_file.exists():
                trending_file.unlink()
                self.update_progress(f"Removed {trending_file}")
    
    def _update_listing_pages(self, content_type: str, content_items: List[Dict[str, Any]]):
        """Update listing pages after content removal"""
        try:
            # Import the appropriate integrator
            if content_type == 'articles':
                from .article_integrator import ArticleIntegrator
                integrator = ArticleIntegrator()
            elif content_type == 'authors':
                from .author_integrator import AuthorIntegrator
                integrator = AuthorIntegrator()
            elif content_type == 'categories':
                from .category_integrator import CategoryIntegrator
                integrator = CategoryIntegrator()
            elif content_type == 'trending':
                from .trending_integrator import TrendingIntegrator
                integrator = TrendingIntegrator()
            else:
                return
            
            # Load current database state to ensure consistency
            integrator.load_content_db()
            
            # Update listing pages with remaining content
            integrator.update_listing_page(content_items)
            self.update_progress(f"Updated listing pages for {content_type}")
            
            # For articles, also update search page with remaining content
            if content_type == 'articles':
                integrator.update_search_page(content_items)
                self.update_progress(f"Updated search page for {content_type}")
            
        except Exception as e:
            self.update_progress(f"Error updating listing pages for {content_type}: {str(e)}")
    
    def get_content_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all integrated content"""
        summary = {}
        content_types = ['articles', 'authors', 'categories', 'trending']
        
        for content_type in content_types:
            db_file = self.data_dir / f"{content_type}_db.json"
            if db_file.exists():
                with open(db_file, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                content_items = db.get(content_type, [])
                summary[content_type] = {
                    'count': len(content_items),
                    'last_integration': db.get('last_integration', 'Never'),
                    'items': [{'id': item.get('id'), 'name': self._get_item_name(content_type, item), 'filename': item.get('filename')} for item in content_items]
                }
            else:
                summary[content_type] = {
                    'count': 0,
                    'last_integration': 'Never',
                    'items': []
                }
        
        return summary
    
    def _get_item_name(self, content_type: str, item: Dict[str, Any]) -> str:
        """Get display name for content item"""
        if content_type == 'articles':
            return item.get('title', 'Unknown Article')
        elif content_type == 'authors':
            return item.get('name', 'Unknown Author')
        elif content_type == 'categories':
            return item.get('name', 'Unknown Category')
        elif content_type == 'trending':
            return item.get('topic', 'Unknown Topic')
        return 'Unknown'