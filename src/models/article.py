"""Article model for Influencer News CMS"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
try:
    from .base import BaseModel
    from .author import Author
    from .category import Category
    from ..utils.sanitizer import model_validator
    from ..utils.logger import get_logger, ValidationException
except ImportError:
    # Fallback for when run as script
    from src.models.base import BaseModel
    from src.models.author import Author
    from src.models.category import Category
    from src.utils.sanitizer import model_validator
    from src.utils.logger import get_logger, ValidationException

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
        self.status: str = kwargs.get('status', 'draft')  # draft, published, archived
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
        
        # Handle backward compatibility
        if not self.excerpt and kwargs.get('subtitle'):
            self.excerpt = kwargs.get('subtitle')
        if not self.publish_date and kwargs.get('publication_date'):
            self.publish_date = kwargs.get('publication_date')
        if not self.views and kwargs.get('view_count'):
            self.views = kwargs.get('view_count')
        if not self.read_time_minutes and kwargs.get('read_time'):
            self.read_time_minutes = kwargs.get('read_time')
        if not self.seo_description and kwargs.get('meta_description'):
            self.seo_description = kwargs.get('meta_description')
        
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
            'status': self.status,
            'publish_date': self.publish_date,
            'read_time_minutes': self.read_time_minutes,
            'tags': self.tags,
            'seo_title': self.seo_title,
            'seo_description': self.seo_description
        }
        
        validation_result = model_validator.validate_article(article_data)
        
        if not validation_result.is_valid:
            logger.warning(f"Article validation failed: {'; '.join(validation_result.errors)}")
            raise ValidationException(
                f"Article validation failed: {'; '.join(validation_result.errors)}",
                user_message="Please check your article data and try again."
            )
        
        # Update instance with cleaned data
        cleaned_data = validation_result.cleaned_content
        self.title = cleaned_data.get('title', self.title)
        self.slug = cleaned_data.get('slug', self.slug)
        self.excerpt = cleaned_data.get('excerpt', self.excerpt)
        self.content = cleaned_data.get('content', self.content)
        self.read_time_minutes = cleaned_data.get('read_time_minutes', self.read_time_minutes)
        self.tags = cleaned_data.get('tags', self.tags)
        self.seo_title = cleaned_data.get('seo_title', self.seo_title)
        self.seo_description = cleaned_data.get('seo_description', self.seo_description)
        
        if validation_result.warnings:
            logger.info(f"Article validation warnings: {'; '.join(validation_result.warnings)}")
        
        db = self.get_db()
        
        if self.id:
            # Update existing article
            query = """
            UPDATE articles 
            SET title = ?, slug = ?, excerpt = ?, content = ?, author_id = ?, category_id = ?,
                status = ?, featured = ?, trending = ?, publish_date = ?, image_url = ?,
                hero_image_url = ?, thumbnail_url = ?, tags = ?, views = ?, likes = ?,
                comments = ?, read_time_minutes = ?, seo_title = ?, seo_description = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            tags_json = json.dumps(self.tags) if self.tags else None
            params = (self.title, self.slug, self.excerpt, self.content, self.author_id,
                     self.category_id, self.status, self.featured, self.trending,
                     self.publish_date, self.image_url, self.hero_image_url,
                     self.thumbnail_url, tags_json, self.views, self.likes,
                     self.comments, self.read_time_minutes, self.seo_title,
                     self.seo_description, self.id)
            db.execute_write(query, params)
        else:
            # Create new article
            query = """
            INSERT INTO articles (title, slug, excerpt, content, author_id, category_id,
                                status, featured, trending, publish_date, image_url,
                                hero_image_url, thumbnail_url, tags, views, likes,
                                comments, read_time_minutes, seo_title, seo_description,
                                created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            tags_json = json.dumps(self.tags) if self.tags else None
            params = (self.title, self.slug, self.excerpt, self.content, self.author_id,
                     self.category_id, self.status, self.featured, self.trending,
                     self.publish_date, self.image_url, self.hero_image_url,
                     self.thumbnail_url, tags_json, self.views, self.likes,
                     self.comments, self.read_time_minutes, self.seo_title,
                     self.seo_description)
            self.id = db.execute_write(query, params)
        
        logger.info(f"Article saved successfully: {self.title} (ID: {self.id})")
        return self.id
    
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
        
        # Update or insert mobile metrics
        query = """
        INSERT INTO mobile_metrics (article_id, mobile_views, tablet_views, desktop_views, date_recorded)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(article_id, date_recorded) DO UPDATE SET
            mobile_views = mobile_views + CASE WHEN ? = 'mobile' THEN 1 ELSE 0 END,
            tablet_views = tablet_views + CASE WHEN ? = 'tablet' THEN 1 ELSE 0 END,
            desktop_views = desktop_views + CASE WHEN ? = 'desktop' THEN 1 ELSE 0 END
        """
        
        mobile_inc = 1 if device_type == 'mobile' else 0
        tablet_inc = 1 if device_type == 'tablet' else 0
        desktop_inc = 1 if device_type == 'desktop' else 0
        
        try:
            db.execute_write(query, (
                self.id, mobile_inc, tablet_inc, desktop_inc, today,
                device_type, device_type, device_type
            ))
        except Exception:
            # Fallback for SQLite without UPSERT support
            fallback_query = """
            INSERT OR IGNORE INTO mobile_metrics (article_id, date_recorded) VALUES (?, ?);
            UPDATE mobile_metrics SET 
                mobile_views = mobile_views + ?,
                tablet_views = tablet_views + ?,
                desktop_views = desktop_views + ?
            WHERE article_id = ? AND date_recorded = ?
            """
            db.execute_write(fallback_query, (
                self.id, today, mobile_inc, tablet_inc, desktop_inc, self.id, today
            ))
    
    def get_mobile_title(self) -> str:
        """Get mobile-optimized title"""
        return self.mobile_title or self.title
    
    def get_mobile_excerpt(self) -> str:
        """Get mobile-optimized excerpt"""
        if self.mobile_excerpt:
            return self.mobile_excerpt
        elif self.subtitle:
            return self.subtitle
        else:
            # Generate excerpt from content (first 150 chars)
            import re
            clean_content = re.sub(r'<[^>]+>', '', self.content)
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
                'name': self.author_name,
                'slug': self.author_slug
            },
            'category': {
                'name': self.category_name,
                'slug': self.category_slug,
                'icon': self.category_icon
            },
            'publication_date': self.publication_date,
            'read_time': self.read_time,
            'view_count': self.view_count,
            'hero_image': self.get_mobile_hero_image(),
            'responsive_images': self.get_responsive_images()
        }
    
    def publish(self) -> None:
        """Publish the article"""
        if self.status != 'published':
            self.status = 'published'
            if not self.publish_date:
                from datetime import datetime
                self.publish_date = datetime.now().isoformat()
            self.save()
    
    def unpublish(self) -> None:
        """Unpublish the article (set to draft)"""
        self.status = 'draft'
        self.save()
    
    def archive(self) -> None:
        """Archive the article"""
        self.status = 'archived'
        self.save()
    
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
        
        where_clauses = ["status = 'published'"]
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
        WHERE featured = 1 AND status = 'published'
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
        WHERE trending = 1 AND status = 'published'
        ORDER BY views DESC, publish_date DESC 
        LIMIT ?
        """
        results = db.execute_query(query, (limit,))
        return [cls.from_dict(data) for data in results]
    
    @classmethod
    def search_fts(cls, search_term: str, limit: int = 20) -> List['Article']:
        """Search articles using full-text search"""
        db = cls.get_db()
        query = """
        SELECT a.* FROM articles a
        JOIN articles_fts fts ON a.id = fts.rowid
        WHERE articles_fts MATCH ? AND a.status = 'published'
        ORDER BY rank
        LIMIT ?
        """
        results = db.execute_query(query, (search_term, limit))
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
    
    @property
    def publication_date(self) -> Optional[str]:
        """Backward compatibility property for publication_date"""
        return self.publish_date
    
    @property
    def read_time(self) -> int:
        """Backward compatibility property for read_time"""
        return self.read_time_minutes
    
    @property
    def view_count(self) -> int:
        """Backward compatibility property for view_count"""
        return self.views
    
    @property
    def subtitle(self) -> Optional[str]:
        """Backward compatibility property for subtitle"""
        return self.excerpt

    def __repr__(self) -> str:
        return f"<Article id={self.id} slug='{self.slug}' status='{self.status}' title='{self.title}'>"