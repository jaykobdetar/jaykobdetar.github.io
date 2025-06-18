"""
Database Manager for Influencer News CMS
Handles all database operations with connection pooling and transaction support
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
from datetime import datetime
import logging

class DatabaseManager:
    """Manages SQLite database connections and operations"""
    
    def __init__(self, db_path: str = "data/infnews.db"):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database if needed
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database with schema if it doesn't exist"""
        if not os.path.exists(self.db_path):
            self.logger.info(f"Creating new database at {self.db_path}")
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            with self.get_connection() as conn:
                conn.executescript(schema)
            
            self.logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection with proper cleanup
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dicts
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries representing rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    def execute_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a query and return single result
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Dictionary representing single row or None
        """
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_write(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Last row ID for INSERT, or number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith("INSERT"):
                return cursor.lastrowid
            else:
                return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute multiple queries with different parameters
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    # Article operations
    def get_article(self, article_id: Optional[int] = None, slug: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get article by ID or slug"""
        if article_id:
            query = "SELECT * FROM article_full_view WHERE id = ?"
            params = (article_id,)
        elif slug:
            query = "SELECT * FROM article_full_view WHERE slug = ?"
            params = (slug,)
        else:
            raise ValueError("Either article_id or slug must be provided")
        
        return self.execute_one(query, params)
    
    def get_articles(self, category_id: Optional[int] = None, author_id: Optional[int] = None, 
                    limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get articles with optional filtering"""
        query = "SELECT * FROM article_full_view WHERE 1=1"
        params = []
        
        if category_id:
            query += " AND category_id = ?"
            params.append(category_id)
        
        if author_id:
            query += " AND author_id = ?"
            params.append(author_id)
        
        query += " ORDER BY publish_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        return self.execute_query(query, tuple(params))
    
    def create_article(self, title: str, slug: str, author_id: int, category_id: int,
                      publish_date: str, content: str, **kwargs) -> int:
        """Create new article"""
        query = """
        INSERT INTO articles (title, slug, excerpt, content, author_id, category_id,
                            status, featured, trending, publish_date, image_url, 
                            hero_image_url, thumbnail_url, tags, views, likes, 
                            comments, read_time_minutes, seo_title, seo_description,
                            mobile_title, mobile_excerpt, mobile_hero_image_id, 
                            last_modified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            title, slug, kwargs.get('excerpt'), content, author_id, category_id,
            kwargs.get('status', 'draft'), kwargs.get('featured', False),
            kwargs.get('trending', False), publish_date, kwargs.get('image_url'),
            kwargs.get('hero_image_url'), kwargs.get('thumbnail_url'),
            kwargs.get('tags'), kwargs.get('views', 0), kwargs.get('likes', 0),
            kwargs.get('comments', 0), kwargs.get('read_time_minutes', 5),
            kwargs.get('seo_title'), kwargs.get('seo_description'),
            kwargs.get('mobile_title'), kwargs.get('mobile_excerpt'),
            kwargs.get('mobile_hero_image_id'), kwargs.get('last_modified')
        )
        return self.execute_write(query, params)
    
    # Author operations
    def get_author(self, author_id: Optional[int] = None, slug: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get author by ID or slug"""
        if author_id:
            query = "SELECT * FROM authors WHERE id = ?"
            params = (author_id,)
        elif slug:
            query = "SELECT * FROM authors WHERE slug = ?"
            params = (slug,)
        else:
            raise ValueError("Either author_id or slug must be provided")
        
        return self.execute_one(query, params)
    
    def get_authors(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get authors with pagination"""
        query = "SELECT * FROM authors ORDER BY name LIMIT ? OFFSET ?"
        return self.execute_query(query, (limit, offset))
    
    def create_author(self, name: str, slug: str, **kwargs) -> int:
        """Create new author"""
        query = """
        INSERT INTO authors (name, slug, title, bio, email, location, expertise,
                           twitter, linkedin, image_url, joined_date, article_count,
                           rating, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            name, slug, kwargs.get('title'), kwargs.get('bio'), kwargs.get('email'),
            kwargs.get('location'), kwargs.get('expertise'), kwargs.get('twitter'),
            kwargs.get('linkedin'), kwargs.get('image_url'), 
            kwargs.get('joined_date', datetime.now().isoformat()),
            kwargs.get('article_count', 0), kwargs.get('rating', 0.0),
            kwargs.get('is_active', True)
        )
        return self.execute_write(query, params)
    
    # Category operations
    def get_category(self, category_id: Optional[int] = None, slug: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get category by ID or slug"""
        if category_id:
            query = "SELECT * FROM categories WHERE id = ?"
            params = (category_id,)
        elif slug:
            query = "SELECT * FROM categories WHERE slug = ?"
            params = (slug,)
        else:
            raise ValueError("Either category_id or slug must be provided")
        
        return self.execute_one(query, params)
    
    def get_categories(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get categories with pagination"""
        query = "SELECT * FROM categories ORDER BY name LIMIT ? OFFSET ?"
        return self.execute_query(query, (limit, offset))
    
    def create_category(self, name: str, slug: str, **kwargs) -> int:
        """Create new category"""
        query = """
        INSERT INTO categories (name, slug, description, color, icon, parent_id,
                              sort_order, article_count, is_featured)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            name, slug, kwargs.get('description'), kwargs.get('color', '#6B7280'),
            kwargs.get('icon', '📁'), kwargs.get('parent_id'), 
            kwargs.get('sort_order', 999), kwargs.get('article_count', 0),
            kwargs.get('is_featured', False)
        )
        return self.execute_write(query, params)
    
    # Trending operations
    def get_trending_topic(self, topic_id: Optional[int] = None, slug: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get trending topic by ID or slug"""
        if topic_id:
            query = "SELECT * FROM trending_topics WHERE id = ?"
            params = (topic_id,)
        elif slug:
            query = "SELECT * FROM trending_topics WHERE slug = ?"
            params = (slug,)
        else:
            raise ValueError("Either topic_id or slug must be provided")
        
        return self.execute_one(query, params)
    
    def get_trending_topics(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get trending topics ordered by heat score with pagination"""
        query = "SELECT * FROM trending_topics ORDER BY heat_score DESC LIMIT ? OFFSET ?"
        return self.execute_query(query, (limit, offset))
    
    def create_trending_topic(self, title: str, slug: str, **kwargs) -> int:
        """Create new trending topic"""
        query = """
        INSERT INTO trending_topics (title, slug, description, content, heat_score,
                                   growth_rate, momentum, article_count, related_articles,
                                   hashtag, icon, category_id, start_date, peak_date,
                                   status, mentions_youtube, mentions_tiktok, 
                                   mentions_instagram, mentions_twitter, mentions_twitch,
                                   is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            title, slug, kwargs.get('description'), kwargs.get('content'),
            kwargs.get('heat_score', 0), kwargs.get('growth_rate', 0.0),
            kwargs.get('momentum', 0.0), kwargs.get('article_count', 0),
            json.dumps(kwargs.get('related_articles', [])) if kwargs.get('related_articles') else None,
            kwargs.get('hashtag'), kwargs.get('icon', '🔥'), kwargs.get('category_id'),
            kwargs.get('start_date', datetime.now().isoformat()), kwargs.get('peak_date'),
            kwargs.get('status', 'active'), kwargs.get('mentions_youtube', 0),
            kwargs.get('mentions_tiktok', 0), kwargs.get('mentions_instagram', 0),
            kwargs.get('mentions_twitter', 0), kwargs.get('mentions_twitch', 0),
            kwargs.get('is_active', True)
        )
        return self.execute_write(query, params)
    
    # Image operations
    def get_images(self, content_type: str, content_id: int) -> List[Dict[str, Any]]:
        """Get all images for a content item"""
        query = "SELECT * FROM images WHERE content_type = ? AND content_id = ?"
        return self.execute_query(query, (content_type, content_id))
    
    def get_image(self, content_type: str, content_id: int, image_type: str) -> Optional[Dict[str, Any]]:
        """Get specific image for content"""
        query = """
        SELECT * FROM images 
        WHERE content_type = ? AND content_id = ? AND image_type = ?
        """
        return self.execute_one(query, (content_type, content_id, image_type))
    
    def create_image(self, content_type: str, content_id: int, image_type: str,
                    local_filename: str, **kwargs) -> int:
        """Create new image record"""
        query = """
        INSERT INTO images (content_type, content_id, image_type, original_url,
                          local_filename, alt_text, caption, width, height,
                          file_size, mime_type, is_placeholder)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            content_type, content_id, image_type, kwargs.get('original_url'),
            local_filename, kwargs.get('alt_text'), kwargs.get('caption'),
            kwargs.get('width'), kwargs.get('height'), kwargs.get('file_size'),
            kwargs.get('mime_type'), kwargs.get('is_placeholder', False)
        )
        return self.execute_write(query, params)
    
    def update_image(self, image_id: int, **kwargs) -> int:
        """Update image record"""
        allowed_fields = ['local_filename', 'alt_text', 'caption', 'width', 
                         'height', 'file_size', 'mime_type', 'is_placeholder']
        
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if not fields:
            return 0
        
        values.append(image_id)
        query = f"UPDATE images SET {', '.join(fields)} WHERE id = ?"
        
        return self.execute_write(query, tuple(values))
    
    def update_article(self, article_id: int, **kwargs) -> int:
        """Update article record"""
        allowed_fields = ['title', 'slug', 'excerpt', 'content', 'author_id', 'category_id',
                         'status', 'featured', 'trending', 'publish_date', 'image_url',
                         'hero_image_url', 'thumbnail_url', 'tags', 'views', 'likes',
                         'comments', 'read_time_minutes', 'seo_title', 'seo_description',
                         'mobile_title', 'mobile_excerpt', 'mobile_hero_image_id',
                         'last_modified']
        
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if not fields:
            return 0
        
        values.append(article_id)
        query = f"UPDATE articles SET {', '.join(fields)} WHERE id = ?"
        
        return self.execute_write(query, tuple(values))
    
    def update_author(self, author_id: int, **kwargs) -> int:
        """Update author record"""
        allowed_fields = ['name', 'slug', 'title', 'bio', 'email', 'location',
                         'expertise', 'twitter', 'linkedin', 'image_url',
                         'article_count', 'rating', 'is_active']
        
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if not fields:
            return 0
        
        values.append(author_id)
        query = f"UPDATE authors SET {', '.join(fields)} WHERE id = ?"
        
        return self.execute_write(query, tuple(values))
    
    def update_category(self, category_id: int, **kwargs) -> int:
        """Update category record"""
        allowed_fields = ['name', 'slug', 'description', 'color', 'icon',
                         'parent_id', 'sort_order', 'article_count', 'is_featured']
        
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if not fields:
            return 0
        
        values.append(category_id)
        query = f"UPDATE categories SET {', '.join(fields)} WHERE id = ?"
        
        return self.execute_write(query, tuple(values))
    
    def update_trending_topic(self, topic_id: int, **kwargs) -> int:
        """Update trending topic record"""
        allowed_fields = ['title', 'slug', 'description', 'content', 'heat_score',
                         'growth_rate', 'momentum', 'article_count', 'related_articles',
                         'hashtag', 'icon', 'category_id', 'start_date', 'peak_date',
                         'status', 'mentions_youtube', 'mentions_tiktok',
                         'mentions_instagram', 'mentions_twitter', 'mentions_twitch',
                         'is_active']
        
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                fields.append(f"{field} = ?")
                # Handle JSON encoding for related_articles
                if field == 'related_articles' and value is not None:
                    value = json.dumps(value) if isinstance(value, list) else value
                values.append(value)
        
        if not fields:
            return 0
        
        values.append(topic_id)
        query = f"UPDATE trending_topics SET {', '.join(fields)} WHERE id = ?"
        
        return self.execute_write(query, tuple(values))
    
    # Search operations
    def search_articles(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search articles by title, subtitle, or content"""
        query = """
        SELECT * FROM article_full_view
        WHERE title LIKE ? OR subtitle LIKE ? OR content LIKE ?
        ORDER BY publish_date DESC
        LIMIT ?
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, limit)
        
        return self.execute_query(query, params)
    
    # Related articles operations
    def get_related_articles(self, article_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get related articles for a given article"""
        query = """
        SELECT a.* FROM article_full_view a
        JOIN related_articles ra ON a.id = ra.related_article_id
        WHERE ra.article_id = ?
        LIMIT ?
        """
        return self.execute_query(query, (article_id, limit))
    
    def add_related_article(self, article_id: int, related_article_id: int, 
                          relationship_type: str = 'related') -> int:
        """Add related article relationship"""
        query = """
        INSERT INTO related_articles (article_id, related_article_id, relationship_type) 
        VALUES (?, ?, ?)
        """
        return self.execute_write(query, (article_id, related_article_id, relationship_type))
    
    # Article sections operations
    def create_article_section(self, article_id: int, content: str, **kwargs) -> int:
        """Create article section"""
        query = """
        INSERT INTO article_sections (article_id, heading, content, section_type, order_num)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            article_id, kwargs.get('heading'), content,
            kwargs.get('section_type', 'paragraph'), kwargs.get('order_num', 0)
        )
        return self.execute_write(query, params)
    
    def get_article_sections(self, article_id: int) -> List[Dict[str, Any]]:
        """Get all sections for an article ordered by order_num"""
        query = "SELECT * FROM article_sections WHERE article_id = ? ORDER BY order_num"
        return self.execute_query(query, (article_id,))
    
    def update_article_section(self, section_id: int, **kwargs) -> int:
        """Update article section"""
        allowed_fields = ['heading', 'content', 'section_type', 'order_num']
        
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if not fields:
            return 0
        
        values.append(section_id)
        query = f"UPDATE article_sections SET {', '.join(fields)} WHERE id = ?"
        
        return self.execute_write(query, tuple(values))
    
    def delete_article_section(self, section_id: int) -> int:
        """Delete article section"""
        query = "DELETE FROM article_sections WHERE id = ?"
        return self.execute_write(query, (section_id,))
    
    # Utility methods
    def get_article_count_by_category(self) -> Dict[str, int]:
        """Get article count for each category"""
        query = """
        SELECT c.slug, COUNT(a.id) as count
        FROM categories c
        LEFT JOIN articles a ON c.id = a.category_id
        GROUP BY c.id
        """
        results = self.execute_query(query)
        return {row['slug']: row['count'] for row in results}
    
    def update_category_article_counts(self) -> None:
        """Update article counts for all categories"""
        query = """
        UPDATE categories
        SET article_count = (
            SELECT COUNT(*) FROM articles WHERE category_id = categories.id
        )
        """
        self.execute_write(query)
    
    def vacuum_database(self) -> None:
        """Vacuum database to reclaim space and optimize"""
        with self.get_connection() as conn:
            conn.execute("VACUUM")
    
    # Mobile metrics operations
    def create_mobile_metrics(self, article_id: int, date_recorded: str, **kwargs) -> int:
        """Create mobile metrics record"""
        query = """
        INSERT INTO mobile_metrics (article_id, date_recorded, mobile_views, tablet_views,
                                  desktop_views, avg_load_time_ms, bounce_rate, 
                                  scroll_depth_percent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            article_id, date_recorded, kwargs.get('mobile_views', 0),
            kwargs.get('tablet_views', 0), kwargs.get('desktop_views', 0),
            kwargs.get('avg_load_time_ms', 0), kwargs.get('bounce_rate', 0.0),
            kwargs.get('scroll_depth_percent', 0)
        )
        return self.execute_write(query, params)
    
    def get_mobile_metrics(self, article_id: int, date_recorded: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get mobile metrics for an article"""
        if date_recorded:
            query = "SELECT * FROM mobile_metrics WHERE article_id = ? AND date_recorded = ?"
            params = (article_id, date_recorded)
        else:
            query = "SELECT * FROM mobile_metrics WHERE article_id = ? ORDER BY date_recorded DESC"
            params = (article_id,)
        return self.execute_query(query, params)
    
    def update_mobile_metrics(self, article_id: int, date_recorded: str, **kwargs) -> int:
        """Update mobile metrics record"""
        allowed_fields = ['mobile_views', 'tablet_views', 'desktop_views',
                         'avg_load_time_ms', 'bounce_rate', 'scroll_depth_percent']
        
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if not fields:
            return 0
        
        values.extend([article_id, date_recorded])
        query = f"UPDATE mobile_metrics SET {', '.join(fields)} WHERE article_id = ? AND date_recorded = ?"
        
        return self.execute_write(query, tuple(values))
    
    # Image variants operations
    def create_image_variant(self, image_id: int, variant_type: str, width: int, 
                           height: int, local_filename: str, **kwargs) -> int:
        """Create image variant record"""
        query = """
        INSERT INTO image_variants (image_id, variant_type, width, height, 
                                  local_filename, file_size, quality, format, 
                                  is_optimized)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            image_id, variant_type, width, height, local_filename,
            kwargs.get('file_size', 0), kwargs.get('quality', 80),
            kwargs.get('format', 'webp'), kwargs.get('is_optimized', False)
        )
        return self.execute_write(query, params)
    
    def get_image_variants(self, image_id: int) -> List[Dict[str, Any]]:
        """Get all variants for an image"""
        query = "SELECT * FROM image_variants WHERE image_id = ? ORDER BY width DESC"
        return self.execute_query(query, (image_id,))
    
    def get_image_variant(self, image_id: int, variant_type: str) -> Optional[Dict[str, Any]]:
        """Get specific variant for an image"""
        query = "SELECT * FROM image_variants WHERE image_id = ? AND variant_type = ?"
        return self.execute_one(query, (image_id, variant_type))
    
    def update_image_variant(self, variant_id: int, **kwargs) -> int:
        """Update image variant record"""
        allowed_fields = ['local_filename', 'file_size', 'quality', 'format', 'is_optimized']
        
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if not fields:
            return 0
        
        values.append(variant_id)
        query = f"UPDATE image_variants SET {', '.join(fields)} WHERE id = ?"
        
        return self.execute_write(query, tuple(values))