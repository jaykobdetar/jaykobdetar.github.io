"""Article model for Influencer News CMS"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .author import Author
from .category import Category
from ..utils.trusted_security import trusted_validator
from ..utils.logger import get_logger, ValidationException

logger = get_logger(__name__)

class Article(BaseModel):
    """Article model representing news articles"""
    
    _table_name = "articles"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Article specific fields (aligned with new schema)
        self.title: str = kwargs.get('title', '')
        self.slug: str = kwargs.get('slug', '')
        self.excerpt: Optional[str] = kwargs.get('excerpt')  # Brief summary
        self.content: str = kwargs.get('content', '')  # Full article content
        self.author_id: int = kwargs.get('author_id', 0)
        self.category_id: int = kwargs.get('category_id', 0)
        self.featured: bool = kwargs.get('featured', False)
        self.trending: bool = kwargs.get('trending', False)
        self.publish_date: Optional[str] = kwargs.get('publish_date')  # When article was published
        self.image_url: Optional[str] = kwargs.get('image_url')  # Featured image
        self.hero_image_url: Optional[str] = kwargs.get('hero_image_url')  # Large hero image
        self.thumbnail_url: Optional[str] = kwargs.get('thumbnail_url')  # Small thumbnail
        self.views: int = kwargs.get('views', 0)  # Updated field name
        self.likes: int = kwargs.get('likes', 0)
        self.comments: int = kwargs.get('comments', 0)
        self.read_time_minutes: int = kwargs.get('read_time_minutes', 0)  # Updated field name
        self.seo_title: Optional[str] = kwargs.get('seo_title')
        self.seo_description: Optional[str] = kwargs.get('seo_description')
        
        # Handle backward compatibility (simplified)
        self.excerpt = self.excerpt or kwargs.get('subtitle')
        self.publish_date = self.publish_date or kwargs.get('publication_date')
        self.views = self.views or kwargs.get('view_count', 0)
        self.read_time_minutes = self.read_time_minutes or kwargs.get('read_time', 0)
        self.seo_description = self.seo_description or kwargs.get('meta_description')
        
        # Mobile-specific fields
        self.mobile_title: Optional[str] = kwargs.get('mobile_title')
        self.mobile_excerpt: Optional[str] = kwargs.get('mobile_excerpt')
        self.mobile_hero_image_id: Optional[int] = kwargs.get('mobile_hero_image_id')
        
        # Handle tags as JSON
        tags = kwargs.get('tags')
        if isinstance(tags, str):
            try:
                self.tags = json.loads(tags) if tags else []
            except json.JSONDecodeError:
                self.tags = []
        else:
            self.tags = tags or []
        
        # Extended fields from view
        self.author_name: Optional[str] = kwargs.get('author_name')
        self.author_slug: Optional[str] = kwargs.get('author_slug')
        self.category_name: Optional[str] = kwargs.get('category_name')
        self.category_slug: Optional[str] = kwargs.get('category_slug')
        self.category_icon: Optional[str] = kwargs.get('category_icon')
    
    @classmethod
    def find_by_id(cls, article_id: int) -> Optional['Article']:
        """Find article by ID"""
        db = cls.get_db()
        data = db.get_article(article_id=article_id)
        return cls.from_dict(data) if data else None
    
    @classmethod
    def find_by_slug(cls, slug: str) -> Optional['Article']:
        """Find article by slug"""
        db = cls.get_db()
        data = db.get_article(slug=slug)
        return cls.from_dict(data) if data else None
    
    @classmethod
    def find_all(cls, category_id: Optional[int] = None, author_id: Optional[int] = None,
                 limit: int = 20, offset: int = 0) -> List['Article']:
        """Find all articles with optional filtering"""
        db = cls.get_db()
        results = db.get_articles(category_id=category_id, author_id=author_id,
                                 limit=limit, offset=offset)
        return [cls.from_dict(data) for data in results]
    
    @classmethod
    def search(cls, search_term: str, limit: int = 20) -> List['Article']:
        """Search articles by term"""
        db = cls.get_db()
        results = db.search_articles(search_term, limit)
        return [cls.from_dict(data) for data in results]
    
    def save(self) -> int:
        """Save article to database with validation and sanitization"""
        # Validate and sanitize article data
        article_data = {
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'content': self.content,
            'author_id': self.author_id,
            'category_id': self.category_id,
            'publish_date': self.publish_date,
            'read_time_minutes': self.read_time_minutes,
            'tags': self.tags,
            'seo_title': self.seo_title,
            'seo_description': self.seo_description
        }
        
        # Validate and sanitize article data using trusted validator
        article_data['title'] = trusted_validator.validate_and_sanitize_text(
            article_data.get('title', ''), 'title', max_length=300, required=True)
        article_data['excerpt'] = trusted_validator.validate_and_sanitize_text(
            article_data.get('excerpt', ''), 'excerpt', max_length=500, required=True)
        article_data['content'] = trusted_validator.validate_and_sanitize_text(
            article_data.get('content', ''), 'content', allow_html=True, required=True)
        
        validation_result = {'is_valid': True, 'sanitized_data': article_data}
        
        if not validation_result['is_valid']:
            errors = validation_result.get('errors', ['Unknown validation error'])
            logger.warning(f"Article validation failed: {'; '.join(errors)}")
            raise ValidationException(
                f"Article validation failed: {'; '.join(errors)}",
                user_message="Please check your article data and try again."
            )
        
        # Update instance with cleaned data
        cleaned_data = validation_result['sanitized_data']
        self.title = cleaned_data.get('title', self.title)
        self.slug = cleaned_data.get('slug', self.slug)
        self.excerpt = cleaned_data.get('excerpt', self.excerpt)
        self.content = cleaned_data.get('content', self.content)
        self.read_time_minutes = cleaned_data.get('read_time_minutes', self.read_time_minutes)
        self.tags = cleaned_data.get('tags', self.tags)
        self.seo_title = cleaned_data.get('seo_title', self.seo_title)
        self.seo_description = cleaned_data.get('seo_description', self.seo_description)
        
        if validation_result.get('warnings'):
            logger.info(f"Article validation warnings: {'; '.join(validation_result['warnings'])}")
        
        db = self.get_db()
        
        try:
            if self.id:
                # Update existing article
                query = """
                UPDATE articles 
                SET title = ?, slug = ?, excerpt = ?, content = ?, author_id = ?, category_id = ?,
                    featured = ?, trending = ?, publish_date = ?, image_url = ?,
                    hero_image_url = ?, thumbnail_url = ?, tags = ?, views = ?, likes = ?,
                    comments = ?, read_time_minutes = ?, seo_title = ?, seo_description = ?,
                    mobile_title = ?, mobile_excerpt = ?, mobile_hero_image_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """
                tags_json = json.dumps(self.tags) if self.tags else None
                params = (self.title, self.slug, self.excerpt, self.content, self.author_id,
                         self.category_id, self.featured, self.trending,
                         self.publish_date, self.image_url, self.hero_image_url,
                         self.thumbnail_url, tags_json, self.views, self.likes,
                         self.comments, self.read_time_minutes, self.seo_title,
                         self.seo_description, self.mobile_title, self.mobile_excerpt,
                         self.mobile_hero_image_id, self.id)
                db.execute_write(query, params)
            else:
                # Create new article
                query = """
                INSERT INTO articles (title, slug, excerpt, content, author_id, category_id,
                                    featured, trending, publish_date, image_url,
                                    hero_image_url, thumbnail_url, tags, views, likes,
                                    comments, read_time_minutes, seo_title, seo_description,
                                    mobile_title, mobile_excerpt, mobile_hero_image_id,
                                    created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
                tags_json = json.dumps(self.tags) if self.tags else None
                params = (self.title, self.slug, self.excerpt, self.content, self.author_id,
                         self.category_id, self.featured, self.trending,
                         self.publish_date, self.image_url, self.hero_image_url,
                         self.thumbnail_url, tags_json, self.views, self.likes,
                         self.comments, self.read_time_minutes, self.seo_title,
                         self.seo_description, self.mobile_title, self.mobile_excerpt,
                         self.mobile_hero_image_id)
                self.id = db.execute_write(query, params)
        
            logger.info(f"Article saved successfully: {self.title} (ID: {self.id})")
            return self.id
            
        except Exception as e:
            logger.error(f"Failed to save article '{self.title}': {str(e)}")
            # Check for common database constraint violations
            error_message = str(e).lower()
            if 'foreign key constraint' in error_message:
                if 'author_id' in error_message:
                    raise ValueError(f"Invalid author ID {self.author_id}. Please ensure the author exists.")
                elif 'category_id' in error_message:
                    raise ValueError(f"Invalid category ID {self.category_id}. Please ensure the category exists.")
                else:
                    raise ValueError("Database relationship error. Please check your data references.")
            elif 'unique constraint' in error_message:
                if 'slug' in error_message:
                    raise ValueError(f"Article slug '{self.slug}' already exists. Please use a different slug.")
                else:
                    raise ValueError("Duplicate data found. Please check for existing records.")
            else:
                raise ValueError(f"Database error: {str(e)}")
    
    def get_author(self) -> Optional[Author]:
        """Get the author of this article"""
        if self.author_id:
            return Author.find_by_id(self.author_id)
        return None
    
    def get_category(self) -> Optional[Category]:
        """Get the category of this article"""
        if self.category_id:
            return Category.find_by_id(self.category_id)
        return None
    
    def get_related_articles(self, limit: int = 3) -> List['Article']:
        """Get related articles"""
        db = self.get_db()
        results = db.get_related_articles(self.id)[:limit]
        return [self.__class__.from_dict(data) for data in results]
    
    def add_related_article(self, related_article_id: int) -> None:
        """Add a related article"""
        db = self.get_db()
        db.add_related_article(self.id, related_article_id)
    
    def get_sections(self) -> List[Dict[str, Any]]:
        """Get article sections"""
        db = self.get_db()
        query = """
        SELECT * FROM article_sections 
        WHERE article_id = ? 
        ORDER BY section_order
        """
        return db.execute_query(query, (self.id,))
    
    def get_images(self) -> List[Dict[str, Any]]:
        """Get all images for this article"""
        db = self.get_db()
        return db.get_images('article', self.id)
    
    def get_hero_image(self) -> Optional[Dict[str, Any]]:
        """Get hero image for this article"""
        db = self.get_db()
        return db.get_image('article', self.id, 'hero')
    
    def get_thumbnail_image(self) -> Optional[Dict[str, Any]]:
        """Get thumbnail image for this article"""
        db = self.get_db()
        return db.get_image('article', self.id, 'thumbnail')
    
    def increment_view_count(self, device_type: str = 'desktop') -> None:
        """Increment the view count and track mobile metrics"""
        db = self.get_db()
        query = "UPDATE articles SET views = views + 1 WHERE id = ?"
        db.execute_write(query, (self.id,))
        self.views += 1
        
        # Track mobile-specific metrics
        self.track_mobile_view(device_type)
    
    def track_mobile_view(self, device_type: str) -> None:
        """Track mobile-specific view metrics"""
        db = self.get_db()
        
        # Get today's date
        from datetime import date
        today = date.today().isoformat()
        
        # Prepare values for different device types
        mobile_inc = 1 if device_type == 'mobile' else 0
        tablet_inc = 1 if device_type == 'tablet' else 0
        desktop_inc = 1 if device_type == 'desktop' else 0
        
        try:
            # Use SQLite upsert equivalent with INSERT OR REPLACE
            fallback_query = """
            INSERT OR IGNORE INTO mobile_metrics (article_id, date_recorded, mobile_views, tablet_views, desktop_views) 
            VALUES (?, ?, 0, 0, 0);
            UPDATE mobile_metrics SET 
                mobile_views = mobile_views + ?,
                tablet_views = tablet_views + ?,
                desktop_views = desktop_views + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE article_id = ? AND date_recorded = ?
            """
            db.execute_write(fallback_query, (
                self.id, today, mobile_inc, tablet_inc, desktop_inc, self.id, today
            ))
        except Exception as e:
            logger.warning(f"Failed to track mobile view for article {self.id}: {e}")
    
    def get_mobile_title(self) -> str:
        """Get mobile-optimized title"""
        return self.mobile_title or self.title
    
    def get_mobile_excerpt(self) -> str:
        """Get mobile-optimized excerpt"""
        if self.mobile_excerpt:
            return self.mobile_excerpt
        elif self.excerpt:
            return self.excerpt
        else:
            # Generate excerpt from content (first 150 chars)
            import re
            clean_content = re.sub(r'<[^>]+>', '', self.content or '')
            return clean_content[:150] + '...' if len(clean_content) > 150 else clean_content
    
    def get_mobile_hero_image(self) -> Optional[Dict[str, Any]]:
        """Get mobile-specific hero image"""
        db = self.get_db()
        if self.mobile_hero_image_id:
            query = "SELECT * FROM images WHERE id = ?"
            result = db.execute_query(query, (self.mobile_hero_image_id,))
            return result[0] if result else None
        else:
            return self.get_hero_image()
    
    def get_responsive_images(self, image_type: str = 'hero') -> Dict[str, List[Dict[str, Any]]]:
        """Get responsive image variants for different screen sizes"""
        db = self.get_db()
        
        # Get the base image
        base_image = db.get_image('article', self.id, image_type)
        if not base_image:
            return {}
        
        # Get all variants for this image
        query = """
        SELECT * FROM image_variants 
        WHERE image_id = ? 
        ORDER BY variant_type, width
        """
        variants = db.execute_query(query, (base_image['id'],))
        
        # Group by variant type
        grouped_variants = {}
        for variant in variants:
            variant_type = variant['variant_type']
            if variant_type not in grouped_variants:
                grouped_variants[variant_type] = []
            grouped_variants[variant_type].append(variant)
        
        return grouped_variants
    
    def get_mobile_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get mobile metrics for this article"""
        db = self.get_db()
        query = """
        SELECT 
            SUM(mobile_views) as total_mobile_views,
            SUM(tablet_views) as total_tablet_views,
            SUM(desktop_views) as total_desktop_views,
            AVG(avg_load_time_ms) as avg_load_time,
            AVG(bounce_rate) as avg_bounce_rate,
            AVG(scroll_depth_percent) as avg_scroll_depth
        FROM mobile_metrics 
        WHERE article_id = ? AND date_recorded >= date('now', '-{} days')
        """.format(days)
        
        result = db.execute_query(query, (self.id,))
        return result[0] if result else {}
    
    @classmethod
    def find_mobile_optimized(cls, limit: int = 20, offset: int = 0) -> List['Article']:
        """Find articles optimized for mobile using mobile view"""
        db = cls.get_db()
        query = """
        SELECT * FROM article_full_view 
        ORDER BY publish_date DESC 
        LIMIT ? OFFSET ?
        """
        results = db.execute_query(query, (limit, offset))
        return [cls.from_dict(data) for data in results]
    
    def to_mobile_dict(self) -> Dict[str, Any]:
        """Convert to dictionary optimized for mobile API responses"""
        return {
            'id': self.id,
            'title': self.get_mobile_title(),
            'slug': self.slug,
            'excerpt': self.get_mobile_excerpt(),
            'author': {
                'name': self.author_name or 'Unknown',
                'slug': self.author_slug or ''
            },
            'category': {
                'name': self.category_name or 'General',
                'slug': self.category_slug or '',
                'icon': self.category_icon or '📁'
            },
            'publish_date': self.publish_date,
            'read_time_minutes': self.read_time_minutes,
            'views': self.views,
            'hero_image': self.get_mobile_hero_image(),
            'responsive_images': self.get_responsive_images()
        }
    
    def feature(self) -> None:
        """Mark article as featured"""
        self.featured = True
        self.save()
    
    def unfeature(self) -> None:
        """Remove featured status"""
        self.featured = False
        self.save()
    
    def mark_trending(self) -> None:
        """Mark article as trending"""
        self.trending = True
        self.save()
    
    def unmark_trending(self) -> None:
        """Remove trending status"""
        self.trending = False
        self.save()
    
    def increment_likes(self) -> None:
        """Increment like count"""
        db = self.get_db()
        query = "UPDATE articles SET likes = likes + 1 WHERE id = ?"
        db.execute_write(query, (self.id,))
        self.likes += 1
    
    def increment_comments(self) -> None:
        """Increment comment count"""
        db = self.get_db()
        query = "UPDATE articles SET comments = comments + 1 WHERE id = ?"
        db.execute_write(query, (self.id,))
        self.comments += 1
    
    @classmethod
    def find_published(cls, category_id: Optional[int] = None, author_id: Optional[int] = None,
                      limit: int = 20, offset: int = 0) -> List['Article']:
        """Find published articles"""
        db = cls.get_db()
        
        where_clauses = []
        params = []
        
        if category_id:
            where_clauses.append("category_id = ?")
            params.append(category_id)
        
        if author_id:
            where_clauses.append("author_id = ?")
            params.append(author_id)
        
        where_sql = " AND ".join(where_clauses)
        params.extend([limit, offset])
        
        query = f"""
        SELECT * FROM article_full_view 
        WHERE {where_sql}
        ORDER BY publish_date DESC 
        LIMIT ? OFFSET ?
        """
        
        results = db.execute_query(query, tuple(params))
        return [cls.from_dict(data) for data in results]
    
    @classmethod
    def find_featured(cls, limit: int = 5) -> List['Article']:
        """Find featured articles"""
        db = cls.get_db()
        query = """
        SELECT * FROM article_full_view 
        WHERE featured = 1
        ORDER BY publish_date DESC 
        LIMIT ?
        """
        results = db.execute_query(query, (limit,))
        return [cls.from_dict(data) for data in results]
    
    @classmethod
    def find_trending(cls, limit: int = 5) -> List['Article']:
        """Find trending articles"""
        db = cls.get_db()
        query = """
        SELECT * FROM article_full_view 
        WHERE trending = 1
        ORDER BY views DESC, publish_date DESC 
        LIMIT ?
        """
        results = db.execute_query(query, (limit,))
        return [cls.from_dict(data) for data in results]
    
    
    def get_word_count(self) -> int:
        """Get estimated word count of content"""
        if self.content:
            import re
            # Remove HTML tags and count words
            clean_content = re.sub(r'<[^>]+>', '', self.content)
            words = clean_content.split()
            return len(words)
        return 0
    
    def estimate_reading_time(self) -> int:
        """Estimate reading time based on word count (200 words per minute)"""
        word_count = self.get_word_count()
        return max(1, round(word_count / 200))
    
    def update_reading_time(self) -> None:
        """Update reading time based on content"""
        self.read_time_minutes = self.estimate_reading_time()
        self.save()
    
    def to_dict_with_relations(self) -> Dict[str, Any]:
        """Convert to dictionary with related data included"""
        base_dict = self.to_dict()
        
        # Add author info
        if hasattr(self, 'author_name'):
            base_dict['author'] = {
                'id': self.author_id,
                'name': self.author_name,
                'slug': self.author_slug
            }
        
        # Add category info
        if hasattr(self, 'category_name'):
            base_dict['category'] = {
                'id': self.category_id,
                'name': self.category_name,
                'slug': self.category_slug,
                'icon': self.category_icon
            }
        
        return base_dict
    
    # Backward compatibility properties (simplified)
    publication_date = property(lambda self: self.publish_date)
    read_time = property(lambda self: self.read_time_minutes)
    view_count = property(lambda self: self.views)
    subtitle = property(lambda self: self.excerpt)

    def __repr__(self) -> str:
        return f"<Article id={self.id} slug='{self.slug}' title='{self.title}'>"