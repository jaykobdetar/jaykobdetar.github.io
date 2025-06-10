"""Author model for Influencer News CMS"""

from typing import List, Optional, Dict, Any
from .base import BaseModel

class Author(BaseModel):
    """Author model representing content creators"""
    
    _table_name = "authors"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Author specific fields
        self.name: str = kwargs.get('name', '')
        self.slug: str = kwargs.get('slug', '')
        self.bio: Optional[str] = kwargs.get('bio')
        self.expertise: Optional[str] = kwargs.get('expertise')
        self.linkedin_url: Optional[str] = kwargs.get('linkedin_url')
        self.twitter_handle: Optional[str] = kwargs.get('twitter_handle')
    
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
            SET name = ?, bio = ?, expertise = ?, 
                linkedin_url = ?, twitter_handle = ?
            WHERE id = ?
            """
            params = (self.name, self.bio, self.expertise,
                     self.linkedin_url, self.twitter_handle, self.id)
            db.execute_write(query, params)
        else:
            # Create new author
            self.id = db.create_author(
                name=self.name,
                slug=self.slug,
                bio=self.bio,
                expertise=self.expertise,
                linkedin_url=self.linkedin_url,
                twitter_handle=self.twitter_handle
            )
        
        return self.id
    
    def get_articles(self, limit: int = 20, offset: int = 0) -> List:
        """Get articles by this author"""
        from .article import Article
        return Article.find_all(author_id=self.id, limit=limit, offset=offset)
    
    def get_article_count(self) -> int:
        """Get total article count for this author"""
        db = self.get_db()
        query = "SELECT COUNT(*) as count FROM articles WHERE author_id = ?"
        result = db.execute_one(query, (self.id,))
        return result['count'] if result else 0
    
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
        if self.linkedin_url:
            if not self.linkedin_url.startswith(('http://', 'https://')):
                return f"https://{self.linkedin_url}"
            return self.linkedin_url
        return None
    
    def get_twitter_url(self) -> Optional[str]:
        """Get full Twitter URL"""
        if self.twitter_handle:
            handle = self.twitter_handle.lstrip('@')
            return f"https://twitter.com/{handle}"
        return None
    
    def __repr__(self) -> str:
        return f"<Author id={self.id} slug='{self.slug}' name='{self.name}'>"