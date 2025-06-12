"""Trending Topic model for Influencer News CMS"""

import json
from typing import List, Optional, Dict, Any
try:
    from .base import BaseModel
except ImportError:
    from src.models.base import BaseModel

class TrendingTopic(BaseModel):
    """Trending Topic model representing hot topics"""
    
    _table_name = "trending_topics"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Trending topic specific fields (aligned with new schema)
        self.title: str = kwargs.get('title', '')
        self.slug: str = kwargs.get('slug', '')
        self.description: Optional[str] = kwargs.get('description')
        self.icon: Optional[str] = kwargs.get('icon')
        self.category_id: Optional[int] = kwargs.get('category_id')
        self.heat_score: int = kwargs.get('heat_score', 0)
        self.article_count: int = kwargs.get('article_count', 0)
        self.peak_date: Optional[str] = kwargs.get('peak_date')  # When topic peaked
        self.is_active: bool = kwargs.get('is_active', True)  # Whether topic is active
        self.momentum: float = kwargs.get('momentum', 0.0)  # Rate of heat score change
        
        # Additional rich data fields for trending topics
        self.analysis: Optional[str] = kwargs.get('analysis')  # Rich analysis content
        self.growth_rate: float = kwargs.get('growth_rate', 0.0)  # Growth rate percentage
        self.hashtag: Optional[str] = kwargs.get('hashtag')  # Associated hashtag
        self.status: str = kwargs.get('status', 'active')  # Topic status
        
        # Platform-specific data
        self.platform_data: Dict[str, Any] = kwargs.get('platform_data', {})
        self.mentions_youtube: int = kwargs.get('mentions_youtube', 0)
        self.mentions_tiktok: int = kwargs.get('mentions_tiktok', 0)
        self.mentions_instagram: int = kwargs.get('mentions_instagram', 0)
        self.mentions_twitter: int = kwargs.get('mentions_twitter', 0)
        self.mentions_twitch: int = kwargs.get('mentions_twitch', 0)
        
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
            SET title = ?, slug = ?, description = ?, icon = ?, category_id = ?,
                heat_score = ?, article_count = ?, related_articles = ?, 
                peak_date = ?, is_active = ?, momentum = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            params = (
                self.title, self.slug, self.description, self.icon, self.category_id,
                self.heat_score, self.article_count,
                json.dumps(self.related_articles) if self.related_articles else None,
                self.peak_date, self.is_active, self.momentum, self.id
            )
            db.execute_write(query, params)
        else:
            # Create new trending topic
            query = """
            INSERT INTO trending_topics (title, slug, description, icon, category_id,
                                       heat_score, article_count, related_articles,
                                       peak_date, is_active, momentum, 
                                       created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            params = (
                self.title, self.slug, self.description, self.icon, self.category_id,
                self.heat_score, self.article_count,
                json.dumps(self.related_articles) if self.related_articles else None,
                self.peak_date, self.is_active, self.momentum
            )
            self.id = db.execute_write(query, params)
        
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
        """Increment the heat score and update momentum"""
        db = self.get_db()
        
        # Calculate momentum (rate of change)
        old_heat = self.heat_score
        new_heat = old_heat + amount
        
        # Update momentum based on change rate
        if old_heat > 0:
            self.momentum = (new_heat - old_heat) / old_heat
        else:
            self.momentum = 1.0 if amount > 0 else 0.0
            
        # Update peak date if this is a new peak
        update_peak = new_heat > old_heat
        
        if update_peak:
            from datetime import datetime
            peak_date = datetime.now().isoformat()
            query = """
            UPDATE trending_topics 
            SET heat_score = heat_score + ?, momentum = ?, peak_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            db.execute_write(query, (amount, self.momentum, peak_date, self.id))
            self.peak_date = peak_date
        else:
            query = """
            UPDATE trending_topics 
            SET heat_score = heat_score + ?, momentum = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            db.execute_write(query, (amount, self.momentum, self.id))
            
        self.heat_score = new_heat
    
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
    
    def activate(self) -> None:
        """Activate this trending topic"""
        self.is_active = True
        db = self.get_db()
        query = "UPDATE trending_topics SET is_active = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_write(query, (self.id,))
    
    def deactivate(self) -> None:
        """Deactivate this trending topic"""
        self.is_active = False
        db = self.get_db()
        query = "UPDATE trending_topics SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_write(query, (self.id,))
    
    @classmethod
    def find_active(cls, limit: int = 20, offset: int = 0) -> List['TrendingTopic']:
        """Find active trending topics"""
        db = cls.get_db()
        query = """
        SELECT * FROM trending_topics 
        WHERE is_active = 1 
        ORDER BY heat_score DESC, momentum DESC 
        LIMIT ? OFFSET ?
        """
        results = db.execute_query(query, (limit, offset))
        return [cls.from_dict(data) for data in results]
    
    @classmethod
    def find_by_momentum(cls, limit: int = 10) -> List['TrendingTopic']:
        """Find trending topics with highest momentum"""
        db = cls.get_db()
        query = """
        SELECT * FROM trending_topics 
        WHERE is_active = 1 AND momentum > 0
        ORDER BY momentum DESC, heat_score DESC 
        LIMIT ?
        """
        results = db.execute_query(query, (limit,))
        return [cls.from_dict(data) for data in results]
    
    def calculate_trend_strength(self) -> str:
        """Calculate trend strength based on heat score and momentum"""
        if self.heat_score >= 100 and self.momentum >= 0.5:
            return "viral"
        elif self.heat_score >= 50 and self.momentum >= 0.25:
            return "hot"
        elif self.heat_score >= 20 and self.momentum >= 0.1:
            return "trending"
        elif self.heat_score >= 5:
            return "emerging"
        else:
            return "cool"
    
    def get_trend_metrics(self) -> Dict[str, Any]:
        """Get comprehensive trend metrics"""
        return {
            'heat_score': self.heat_score,
            'momentum': self.momentum,
            'trend_strength': self.calculate_trend_strength(),
            'peak_date': self.peak_date,
            'article_count': self.article_count,
            'is_active': self.is_active,
            'category': self.get_category().name if self.get_category() else None
        }
    
    def __repr__(self) -> str:
        return f"<TrendingTopic id={self.id} slug='{self.slug}' heat_score={self.heat_score} active={self.is_active}>"