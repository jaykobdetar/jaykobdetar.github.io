"""Image model for Influencer News CMS"""

from typing import Optional, Dict, Any
from .base import BaseModel

class Image(BaseModel):
    """Image model representing media assets"""
    
    _table_name = "images"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Image specific fields
        self.content_type: str = kwargs.get('content_type', '')
        self.content_id: int = kwargs.get('content_id', 0)
        self.image_type: str = kwargs.get('image_type', '')
        self.original_url: Optional[str] = kwargs.get('original_url')
        self.local_filename: str = kwargs.get('local_filename', '')
        self.alt_text: Optional[str] = kwargs.get('alt_text')
        self.caption: Optional[str] = kwargs.get('caption')
        self.width: Optional[int] = kwargs.get('width')
        self.height: Optional[int] = kwargs.get('height')
        self.file_size: Optional[int] = kwargs.get('file_size')
        self.mime_type: Optional[str] = kwargs.get('mime_type')
        self.is_placeholder: bool = kwargs.get('is_placeholder', False)
    
    @classmethod
    def find_by_id(cls, image_id: int) -> Optional['Image']:
        """Find image by ID"""
        db = cls.get_db()
        query = "SELECT * FROM images WHERE id = ?"
        data = db.execute_one(query, (image_id,))
        return cls.from_dict(data) if data else None
    
    @classmethod
    def find_by_content(cls, content_type: str, content_id: int, 
                       image_type: Optional[str] = None) -> Optional['Image']:
        """Find image by content reference"""
        db = cls.get_db()
        
        if image_type:
            data = db.get_image(content_type, content_id, image_type)
        else:
            # Get first image if no type specified
            images = db.get_images(content_type, content_id)
            data = images[0] if images else None
        
        return cls.from_dict(data) if data else None
    
    def save(self) -> int:
        """Save image to database"""
        db = self.get_db()
        
        if self.id:
            # Update existing image
            return db.update_image(
                self.id,
                local_filename=self.local_filename,
                alt_text=self.alt_text,
                caption=self.caption,
                width=self.width,
                height=self.height,
                file_size=self.file_size,
                mime_type=self.mime_type,
                is_placeholder=self.is_placeholder
            )
        else:
            # Create new image
            self.id = db.create_image(
                content_type=self.content_type,
                content_id=self.content_id,
                image_type=self.image_type,
                local_filename=self.local_filename,
                original_url=self.original_url,
                alt_text=self.alt_text,
                caption=self.caption,
                width=self.width,
                height=self.height,
                file_size=self.file_size,
                mime_type=self.mime_type,
                is_placeholder=self.is_placeholder
            )
        
        return self.id
    
    def get_full_path(self, base_path: str = "assets/images") -> str:
        """Get full relative path to image file"""
        # Determine subdirectory based on content type
        subdirs = {
            'article': 'articles',
            'author': 'authors',
            'category': 'categories',
            'trending': 'trending'
        }
        
        subdir = subdirs.get(self.content_type, self.content_type)
        return f"{base_path}/{subdir}/{self.local_filename}"
    
    def get_placeholder_path(self, base_path: str = "assets/placeholders") -> str:
        """Get path to placeholder image"""
        placeholders = {
            'article': 'article_placeholder.jpg',
            'author': 'author_placeholder.jpg',
            'category': 'category_placeholder.jpg',
            'trending': 'trending_placeholder.jpg'
        }
        
        placeholder = placeholders.get(self.content_type, 'default_placeholder.jpg')
        return f"{base_path}/{placeholder}"
    
    def get_dimensions_string(self) -> str:
        """Get dimensions as string (e.g., '1200x600')"""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "unknown"
    
    def get_file_size_string(self) -> str:
        """Get human-readable file size"""
        if not self.file_size:
            return "unknown"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} TB"
    
    def to_html_tag(self, css_class: str = "", base_path: str = "../") -> str:
        """Generate HTML img tag"""
        path = self.get_full_path()
        placeholder = self.get_placeholder_path()
        
        # Build attributes
        attrs = [
            f'src="{base_path}{path}"',
            f'alt="{self.alt_text or ""}"',
            f'onerror="this.src=\'{base_path}{placeholder}\'"'
        ]
        
        if css_class:
            attrs.append(f'class="{css_class}"')
        
        if self.width and self.height:
            attrs.append(f'width="{self.width}"')
            attrs.append(f'height="{self.height}"')
        
        return f'<img {" ".join(attrs)}>'
    
    def __repr__(self) -> str:
        return f"<Image id={self.id} {self.content_type}:{self.content_id} type='{self.image_type}'>"