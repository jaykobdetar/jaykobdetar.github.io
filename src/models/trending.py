"""Trending Topic model for Influencer News CMS"""

import json
from typing import List, Optional, Dict, Any
from .base import BaseModel

class TrendingTopic(BaseModel):
    """Trending Topic model representing hot topics"""
    
    _table_name = "trending_topics"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Trending topic specific fields
        self.title: str = kwargs.get('title', '')
        self.slug: str = kwargs.get('slug', '')
        self.description: Optional[str] = kwargs.get('description')
        self.icon: Optional[str] = kwargs.get('icon')
        self.category_id: Optional[int] = kwargs.get('category_id')
        self.heat_score: int = kwargs.get('heat_score', 0)
        self.article_count: int = kwargs.get('article_count', 0)
        
        # Handle related articles as JSON
        related = kwargs.get('related_articles')
        if isinstance(related, str):
            try:
                self.related_articles = json.loads(related) if related else []
            except json.JSONDecodeError:
                self.related_articles = []
        else:
            self.related_articles = related or []
    
    @classmethod
    def find_by_id(cls, topic_id: int) -> Optional['TrendingTopic']:
        """Find trending topic by ID"""
        db = cls.get_db()
        data = db.get_trending_topic(topic_id=topic_id)
        return cls.from_dict(data) if data else None
    
    @classmethod
    def find_by_slug(cls, slug: str) -> Optional['TrendingTopic']:
        """Find trending topic by slug"""
        db = cls.get_db()
        data = db.get_trending_topic(slug=slug)
        return cls.from_dict(data) if data else None
    
    @classmethod
    def find_all(cls, limit: int = 100, offset: int = 0) -> List['TrendingTopic']:
        """Find all trending topics ordered by heat score with pagination"""
        db = cls.get_db()
        results = db.get_trending_topics(limit=limit, offset=offset)
        return [cls.from_dict(data) for data in results]
    
    @classmethod
    def find_top(cls, limit: int = 5) -> List['TrendingTopic']:
        """Find top trending topics"""
        db = cls.get_db()
        query = "SELECT * FROM trending_topics ORDER BY heat_score DESC LIMIT ?"
        results = db.execute_query(query, (limit,))
        return [cls.from_dict(data) for data in results]
    
    def save(self) -> int:
        """Save trending topic to database"""
        db = self.get_db()
        
        if self.id:
            # Update existing trending topic
            query = """
            UPDATE trending_topics 
            SET title = ?, description = ?, icon = ?, category_id = ?,
                heat_score = ?, article_count = ?, related_articles = ?
            WHERE id = ?
            """
            params = (
                self.title, self.description, self.icon, self.category_id,
                self.heat_score, self.article_count,
                json.dumps(self.related_articles) if self.related_articles else None,
                self.id
            )
            db.execute_write(query, params)
        else:
            # Create new trending topic
            self.id = db.create_trending_topic(
                title=self.title,
                slug=self.slug,
                description=self.description,
                icon=self.icon,
                category_id=self.category_id,
                heat_score=self.heat_score,
                article_count=self.article_count,
                related_articles=self.related_articles
            )
        
        return self.id
    
    def get_category(self):
        """Get the category of this trending topic"""
        if self.category_id:
            from .category import Category
            return Category.find_by_id(self.category_id)
        return None
    
    def get_related_articles(self) -> List:
        """Get related articles for this trending topic"""
        if not self.related_articles:
            return []
        
        from .article import Article
        db = self.get_db()
        
        # Build query for multiple article IDs
        placeholders = ','.join(['?' for _ in self.related_articles])
        query = f"SELECT * FROM article_full_view WHERE id IN ({placeholders})"
        
        results = db.execute_query(query, tuple(self.related_articles))
        return [Article.from_dict(data) for data in results]
    
    def add_related_article(self, article_id: int) -> None:
        """Add a related article to this trending topic"""
        if article_id not in self.related_articles:
            self.related_articles.append(article_id)
            self.article_count = len(self.related_articles)
            self.save()
    
    def remove_related_article(self, article_id: int) -> None:
        """Remove a related article from this trending topic"""
        if article_id in self.related_articles:
            self.related_articles.remove(article_id)
            self.article_count = len(self.related_articles)
            self.save()
    
    def increment_heat_score(self, amount: int = 1) -> None:
        """Increment the heat score"""
        db = self.get_db()
        query = "UPDATE trending_topics SET heat_score = heat_score + ? WHERE id = ?"
        db.execute_write(query, (amount, self.id))
        self.heat_score += amount
    
    def get_images(self) -> List[Dict[str, Any]]:
        """Get all images for this trending topic"""
        db = self.get_db()
        return db.get_images('trending', self.id)
    
    def get_cover_image(self) -> Optional[Dict[str, Any]]:
        """Get cover image for this trending topic"""
        db = self.get_db()
        return db.get_image('trending', self.id, 'cover')
    
    def get_thumbnail_image(self) -> Optional[Dict[str, Any]]:
        """Get thumbnail image for this trending topic"""
        db = self.get_db()
        return db.get_image('trending', self.id, 'thumbnail')
    
    def __repr__(self) -> str:
        return f"<TrendingTopic id={self.id} slug='{self.slug}' heat_score={self.heat_score}>"