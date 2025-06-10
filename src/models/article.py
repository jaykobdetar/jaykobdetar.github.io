"""Article model for Influencer News CMS"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .author import Author
from .category import Category
from ..utils.sanitizer import model_validator
from ..utils.logger import get_logger, ValidationException

logger = get_logger(__name__)

class Article(BaseModel):
    """Article model representing news articles"""
    
    _table_name = "articles"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Article specific fields
        self.title: str = kwargs.get('title', '')
        self.slug: str = kwargs.get('slug', '')
        self.subtitle: Optional[str] = kwargs.get('subtitle')
        self.author_id: int = kwargs.get('author_id', 0)
        self.category_id: int = kwargs.get('category_id', 0)
        self.publication_date: str = kwargs.get('publication_date', '')
        self.read_time: int = kwargs.get('read_time', 5)
        self.meta_description: Optional[str] = kwargs.get('meta_description')
        self.content: str = kwargs.get('content', '')
        self.view_count: int = kwargs.get('view_count', 0)
        
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
            'subtitle': self.subtitle,
            'content': self.content,
            'author_id': self.author_id,
            'category_id': self.category_id,
            'publication_date': self.publication_date,
            'read_time': self.read_time,
            'tags': self.tags,
            'meta_description': self.meta_description
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
        self.subtitle = cleaned_data.get('subtitle', self.subtitle)
        self.content = cleaned_data.get('content', self.content)
        self.read_time = cleaned_data.get('read_time', self.read_time)
        self.tags = cleaned_data.get('tags', self.tags)
        self.meta_description = cleaned_data.get('meta_description', self.meta_description)
        
        if validation_result.warnings:
            logger.info(f"Article validation warnings: {'; '.join(validation_result.warnings)}")
        
        db = self.get_db()
        
        if self.id:
            # Update existing article
            db.update_article(
                article_id=self.id,
                title=self.title,
                slug=self.slug,
                author_id=self.author_id,
                category_id=self.category_id,
                publication_date=self.publication_date,
                content=self.content,
                subtitle=self.subtitle,
                read_time=self.read_time,
                tags=self.tags,
                meta_description=self.meta_description
            )
        else:
            # Create new article
            self.id = db.create_article(
                title=self.title,
                slug=self.slug,
                author_id=self.author_id,
                category_id=self.category_id,
                publication_date=self.publication_date,
                content=self.content,
                subtitle=self.subtitle,
                read_time=self.read_time,
                tags=self.tags,
                meta_description=self.meta_description
            )
        
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
    
    def increment_view_count(self) -> None:
        """Increment the view count"""
        db = self.get_db()
        query = "UPDATE articles SET view_count = view_count + 1 WHERE id = ?"
        db.execute_write(query, (self.id,))
        self.view_count += 1
    
    def __repr__(self) -> str:
        return f"<Article id={self.id} slug='{self.slug}' title='{self.title}'>"