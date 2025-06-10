"""Category model for Influencer News CMS"""

from typing import List, Optional, Dict, Any
from .base import BaseModel

class Category(BaseModel):
    """Category model representing content categories"""
    
    _table_name = "categories"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Category specific fields
        self.name: str = kwargs.get('name', '')
        self.slug: str = kwargs.get('slug', '')
        self.description: Optional[str] = kwargs.get('description')
        self.icon: Optional[str] = kwargs.get('icon')
        self.article_count: int = kwargs.get('article_count', 0)
    
    @classmethod
    def find_by_id(cls, category_id: int) -> Optional['Category']:
        """Find category by ID"""
        db = cls.get_db()
        data = db.get_category(category_id=category_id)
        return cls.from_dict(data) if data else None
    
    @classmethod
    def find_by_slug(cls, slug: str) -> Optional['Category']:
        """Find category by slug"""
        db = cls.get_db()
        data = db.get_category(slug=slug)
        return cls.from_dict(data) if data else None
    
    @classmethod
    def find_all(cls, limit: int = 100, offset: int = 0) -> List['Category']:
        """Find all categories with optional pagination"""
        db = cls.get_db()
        results = db.get_categories(limit=limit, offset=offset)
        return [cls.from_dict(data) for data in results]
    
    def save(self) -> int:
        """Save category to database"""
        db = self.get_db()
        
        if self.id:
            # Update existing category
            query = """
            UPDATE categories 
            SET name = ?, description = ?, icon = ?
            WHERE id = ?
            """
            params = (self.name, self.description, self.icon, self.id)
            db.execute_write(query, params)
        else:
            # Create new category
            query = """
            INSERT INTO categories (name, slug, description, icon)
            VALUES (?, ?, ?, ?)
            """
            params = (self.name, self.slug, self.description, self.icon)
            self.id = db.execute_write(query, params)
        
        return self.id
    
    def get_articles(self, limit: int = 20, offset: int = 0) -> List:
        """Get articles in this category"""
        from .article import Article
        return Article.find_all(category_id=self.id, limit=limit, offset=offset)
    
    def update_article_count(self) -> None:
        """Update the article count for this category"""
        db = self.get_db()
        query = """
        UPDATE categories 
        SET article_count = (
            SELECT COUNT(*) FROM articles WHERE category_id = ?
        )
        WHERE id = ?
        """
        db.execute_write(query, (self.id, self.id))
        
        # Refresh the count
        result = db.execute_one("SELECT article_count FROM categories WHERE id = ?", (self.id,))
        if result:
            self.article_count = result['article_count']
    
    def get_trending_topics(self) -> List:
        """Get trending topics in this category"""
        from .trending import TrendingTopic
        db = self.get_db()
        query = "SELECT * FROM trending_topics WHERE category_id = ? ORDER BY heat_score DESC"
        results = db.execute_query(query, (self.id,))
        return [TrendingTopic.from_dict(data) for data in results]
    
    def get_images(self) -> List[Dict[str, Any]]:
        """Get all images for this category"""
        db = self.get_db()
        return db.get_images('category', self.id)
    
    def get_banner_image(self) -> Optional[Dict[str, Any]]:
        """Get banner image for this category"""
        db = self.get_db()
        return db.get_image('category', self.id, 'banner')
    
    def get_icon_image(self) -> Optional[Dict[str, Any]]:
        """Get icon image for this category"""
        db = self.get_db()
        return db.get_image('category', self.id, 'icon')
    
    @classmethod
    def merge_duplicates(cls, keep_id: int, remove_id: int) -> None:
        """Merge duplicate categories by updating references"""
        db = cls.get_db()
        
        # Update articles to use the keep_id
        query = "UPDATE articles SET category_id = ? WHERE category_id = ?"
        db.execute_write(query, (keep_id, remove_id))
        
        # Update trending topics to use the keep_id
        query = "UPDATE trending_topics SET category_id = ? WHERE category_id = ?"
        db.execute_write(query, (keep_id, remove_id))
        
        # Delete the duplicate category
        query = "DELETE FROM categories WHERE id = ?"
        db.execute_write(query, (remove_id,))
        
        # Update article count for the kept category
        kept_category = cls.find_by_id(keep_id)
        if kept_category:
            kept_category.update_article_count()
    
    def __repr__(self) -> str:
        return f"<Category id={self.id} slug='{self.slug}' name='{self.name}'>"