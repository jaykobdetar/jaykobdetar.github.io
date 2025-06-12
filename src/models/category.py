"""Category model for Influencer News CMS"""

from typing import List, Optional, Dict, Any
try:
    from .base import BaseModel
except ImportError:
    from src.models.base import BaseModel

class Category(BaseModel):
    """Category model representing content categories"""
    
    _table_name = "categories"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Category specific fields (aligned with new schema)
        self.name: str = kwargs.get('name', '')
        self.slug: str = kwargs.get('slug', '')
        self.description: Optional[str] = kwargs.get('description')
        self.icon: Optional[str] = kwargs.get('icon')
        self.color: Optional[str] = kwargs.get('color')  # New field for category color
        self.parent_id: Optional[int] = kwargs.get('parent_id')  # For hierarchical categories
        self.sort_order: int = kwargs.get('sort_order', 0)  # For custom ordering
        self.is_featured: bool = kwargs.get('is_featured', False)  # New field
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
            SET name = ?, slug = ?, description = ?, icon = ?, color = ?, 
                parent_id = ?, sort_order = ?, is_featured = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            params = (self.name, self.slug, self.description, self.icon, self.color,
                     self.parent_id, self.sort_order, self.is_featured, self.id)
            db.execute_write(query, params)
        else:
            # Create new category
            query = """
            INSERT INTO categories (name, slug, description, icon, color, parent_id, 
                                  sort_order, is_featured, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            params = (self.name, self.slug, self.description, self.icon, self.color,
                     self.parent_id, self.sort_order, self.is_featured)
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
    
    def get_parent(self) -> Optional['Category']:
        """Get parent category if this is a subcategory"""
        if self.parent_id:
            return self.find_by_id(self.parent_id)
        return None
    
    def get_children(self) -> List['Category']:
        """Get child categories"""
        db = self.get_db()
        query = "SELECT * FROM categories WHERE parent_id = ? ORDER BY sort_order, name"
        results = db.execute_query(query, (self.id,))
        return [self.__class__.from_dict(data) for data in results]
    
    def get_hierarchy_path(self) -> List[str]:
        """Get full hierarchy path as list of category names"""
        path = []
        current = self
        while current:
            path.insert(0, current.name)
            current = current.get_parent()
        return path
    
    def is_descendant_of(self, category_id: int) -> bool:
        """Check if this category is a descendant of another category"""
        current = self.get_parent()
        while current:
            if current.id == category_id:
                return True
            current = current.get_parent()
        return False
    
    @classmethod
    def find_featured(cls, limit: int = 10) -> List['Category']:
        """Find featured categories"""
        db = cls.get_db()
        query = "SELECT * FROM categories WHERE is_featured = 1 ORDER BY sort_order, name LIMIT ?"
        results = db.execute_query(query, (limit,))
        return [cls.from_dict(data) for data in results]
    
    @classmethod
    def find_root_categories(cls) -> List['Category']:
        """Find all root categories (no parent)"""
        db = cls.get_db()
        query = "SELECT * FROM categories WHERE parent_id IS NULL ORDER BY sort_order, name"
        results = db.execute_query(query)
        return [cls.from_dict(data) for data in results]
    
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