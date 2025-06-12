"""Author model for Influencer News CMS"""

from typing import List, Optional, Dict, Any
try:
    from .base import BaseModel
except ImportError:
    from src.models.base import BaseModel

class Author(BaseModel):
    """Author model representing content creators"""
    
    _table_name = "authors"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Author specific fields (aligned with new schema)
        self.name: str = kwargs.get('name', '')
        self.slug: str = kwargs.get('slug', '')
        self.title: Optional[str] = kwargs.get('title')  # Professional title
        self.bio: Optional[str] = kwargs.get('bio')
        self.email: Optional[str] = kwargs.get('email')
        self.location: Optional[str] = kwargs.get('location')
        self.expertise: Optional[str] = kwargs.get('expertise')  # Comma-separated
        self.twitter: Optional[str] = kwargs.get('twitter')  # Updated field name
        self.linkedin: Optional[str] = kwargs.get('linkedin')  # Updated field name
        self.image_url: Optional[str] = kwargs.get('image_url')
        self.joined_date: str = kwargs.get('joined_date', '')
        self.article_count: int = kwargs.get('article_count', 0)
        self.rating: float = kwargs.get('rating', 0.0)
        self.is_active: bool = kwargs.get('is_active', True)
        
        # Handle backward compatibility
        if not self.twitter and kwargs.get('twitter_handle'):
            self.twitter = kwargs.get('twitter_handle')
        if not self.linkedin and kwargs.get('linkedin_url'):
            self.linkedin = kwargs.get('linkedin_url')
    
    @classmethod
    def find_by_id(cls, author_id: int) -> Optional['Author']:
        """Find author by ID"""
        db = cls.get_db()
        data = db.get_author(author_id=author_id)
        return cls.from_dict(data) if data else None
    
    @classmethod
    def find_by_slug(cls, slug: str) -> Optional['Author']:
        """Find author by slug"""
        db = cls.get_db()
        data = db.get_author(slug=slug)
        return cls.from_dict(data) if data else None
    
    @classmethod
    def find_all(cls, limit: int = 100, offset: int = 0) -> List['Author']:
        """Find all authors with optional pagination"""
        db = cls.get_db()
        results = db.get_authors(limit=limit, offset=offset)
        return [cls.from_dict(data) for data in results]
    
    def save(self) -> int:
        """Save author to database"""
        db = self.get_db()
        
        if self.id:
            # Update existing author
            query = """
            UPDATE authors 
            SET name = ?, slug = ?, title = ?, bio = ?, email = ?, location = ?,
                expertise = ?, twitter = ?, linkedin = ?, image_url = ?, 
                rating = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            params = (self.name, self.slug, self.title, self.bio, self.email, 
                     self.location, self.expertise, self.twitter, self.linkedin, 
                     self.image_url, self.rating, self.is_active, self.id)
            db.execute_write(query, params)
        else:
            # Create new author
            query = """
            INSERT INTO authors (name, slug, title, bio, email, location, expertise, 
                               twitter, linkedin, image_url, joined_date, article_count, 
                               rating, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, 
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            params = (self.name, self.slug, self.title, self.bio, self.email,
                     self.location, self.expertise, self.twitter, self.linkedin,
                     self.image_url, self.article_count, self.rating, self.is_active)
            self.id = db.execute_write(query, params)
        
        return self.id
    
    def get_articles(self, limit: int = 20, offset: int = 0) -> List:
        """Get articles by this author"""
        from .article import Article
        return Article.find_all(author_id=self.id, limit=limit, offset=offset)
    
    def get_article_count(self) -> int:
        """Get total article count for this author"""
        # Return cached count from schema triggers, or query if needed
        if hasattr(self, 'article_count') and self.article_count is not None:
            return self.article_count
            
        db = self.get_db()
        query = "SELECT COUNT(*) as count FROM articles WHERE author_id = ? AND status = 'published'"
        result = db.execute_one(query, (self.id,))
        count = result['count'] if result else 0
        
        # Update the cached count
        self.article_count = count
        return count
    
    def get_images(self) -> List[Dict[str, Any]]:
        """Get all images for this author"""
        db = self.get_db()
        return db.get_images('author', self.id)
    
    def get_profile_image(self) -> Optional[Dict[str, Any]]:
        """Get profile image for this author"""
        db = self.get_db()
        return db.get_image('author', self.id, 'profile')
    
    def get_thumbnail_image(self) -> Optional[Dict[str, Any]]:
        """Get thumbnail image for this author"""
        db = self.get_db()
        return db.get_image('author', self.id, 'thumbnail')
    
    def get_full_linkedin_url(self) -> Optional[str]:
        """Get full LinkedIn URL with protocol"""
        if self.linkedin:
            if not self.linkedin.startswith(('http://', 'https://')):
                return f"https://{self.linkedin}"
            return self.linkedin
        return None
    
    def get_twitter_url(self) -> Optional[str]:
        """Get full Twitter URL"""
        if self.twitter:
            handle = self.twitter.lstrip('@')
            return f"https://twitter.com/{handle}"
        return None
    
    def update_rating(self, new_rating: float) -> None:
        """Update author rating (0.0 - 5.0)"""
        if 0.0 <= new_rating <= 5.0:
            self.rating = new_rating
            db = self.get_db()
            query = "UPDATE authors SET rating = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            db.execute_write(query, (self.rating, self.id))
    
    @classmethod
    def find_active(cls, limit: int = 100, offset: int = 0) -> List['Author']:
        """Find all active authors"""
        db = cls.get_db()
        query = "SELECT * FROM authors WHERE is_active = 1 ORDER BY name LIMIT ? OFFSET ?"
        results = db.execute_query(query, (limit, offset))
        return [cls.from_dict(data) for data in results]
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['Author']:
        """Find author by email"""
        db = cls.get_db()
        query = "SELECT * FROM authors WHERE email = ?"
        result = db.execute_query(query, (email,))
        return cls.from_dict(result[0]) if result else None
    
    def get_expertise_list(self) -> List[str]:
        """Get expertise as a list"""
        if self.expertise:
            return [e.strip() for e in self.expertise.split(',')]
        return []
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for public API (excluding sensitive data)"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'title': self.title,
            'bio': self.bio,
            'location': self.location,
            'expertise': self.get_expertise_list(),
            'twitter_url': self.get_twitter_url(),
            'linkedin_url': self.get_full_linkedin_url(),
            'image_url': self.image_url,
            'article_count': self.article_count,
            'rating': self.rating,
            'joined_date': self.joined_date,
            'is_active': self.is_active
        }
    
    def __repr__(self) -> str:
        return f"<Author id={self.id} slug='{self.slug}' name='{self.name}' active={self.is_active}>"