"""
Content Validation and Sanitization for Influencer News CMS
Provides input validation, HTML sanitization, and content security
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
from .config import config

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class ContentValidator:
    """Validates and sanitizes user-generated content"""
    
    def __init__(self):
        """Initialize validator with security config"""
        self.security_config = config.get_security_config()
        self.max_content_length = self.security_config['max_content_length']
        self.max_title_length = self.security_config['max_title_length']
        self.allowed_html_tags = set(self.security_config['allowed_html_tags'])
        self.sanitize_html = self.security_config['sanitize_html']
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for validation"""
        # HTML tag pattern
        self.html_tag_pattern = re.compile(r'<[^>]*?>', re.IGNORECASE)
        
        # Script injection patterns
        self.script_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'data:text/html', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            re.compile(r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)', re.IGNORECASE),
            re.compile(r'([\'\"]\s*(or|and)\s*[\'\"]\s*=\s*[\'\"]\s*)', re.IGNORECASE),
            re.compile(r'(\-\-|\#|/\*|\*/)', re.IGNORECASE),
        ]
        
        # Email validation pattern
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # URL validation pattern
        self.url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        # Slug pattern
        self.slug_pattern = re.compile(r'^[a-z0-9-]+$')
    
    def validate_string(self, value: str, field_name: str, 
                       max_length: Optional[int] = None,
                       min_length: int = 1,
                       required: bool = True) -> str:
        """
        Validate and sanitize string input
        
        Args:
            value: String to validate
            field_name: Name of field for error messages
            max_length: Maximum allowed length
            min_length: Minimum required length
            required: Whether field is required
            
        Returns:
            Sanitized string
            
        Raises:
            ValidationError: If validation fails
        """
        if not value and required:
            raise ValidationError(f"{field_name} is required")
        
        if not value and not required:
            return ""
        
        # Check type
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        # Strip whitespace
        value = value.strip()
        
        # Check length
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters")
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} must be no more than {max_length} characters")
        
        # Check for malicious content
        self._check_for_malicious_content(value, field_name)
        
        # Sanitize HTML if enabled
        if self.sanitize_html:
            value = self.sanitize_html_content(value)
        
        return value
    
    def validate_title(self, title: str) -> str:
        """Validate article/content title"""
        return self.validate_string(
            title, 
            "Title", 
            max_length=self.max_title_length,
            min_length=3,
            required=True
        )
    
    def validate_content(self, content: str) -> str:
        """Validate article content"""
        return self.validate_string(
            content,
            "Content",
            max_length=self.max_content_length,
            min_length=10,
            required=True
        )
    
    def validate_email(self, email: str, required: bool = True) -> str:
        """
        Validate email address
        
        Args:
            email: Email to validate
            required: Whether email is required
            
        Returns:
            Validated email
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email and not required:
            return ""
        
        if not email and required:
            raise ValidationError("Email is required")
        
        email = email.strip().lower()
        
        if not self.email_pattern.match(email):
            raise ValidationError("Invalid email format")
        
        if len(email) > 254:  # RFC 5321 limit
            raise ValidationError("Email address too long")
        
        return email
    
    def validate_url(self, url: str, required: bool = False) -> str:
        """
        Validate URL
        
        Args:
            url: URL to validate
            required: Whether URL is required
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url and not required:
            return ""
        
        if not url and required:
            raise ValidationError("URL is required")
        
        url = url.strip()
        
        # Basic URL validation
        if not self.url_pattern.match(url):
            raise ValidationError("Invalid URL format")
        
        # Additional security check
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError("Only HTTP and HTTPS URLs are allowed")
        
        return url
    
    def validate_slug(self, slug: str, required: bool = True) -> str:
        """
        Validate slug (URL-safe identifier)
        
        Args:
            slug: Slug to validate
            required: Whether slug is required
            
        Returns:
            Validated slug
            
        Raises:
            ValidationError: If slug is invalid
        """
        if not slug and not required:
            return ""
        
        if not slug and required:
            raise ValidationError("Slug is required")
        
        slug = slug.strip().lower()
        
        if not self.slug_pattern.match(slug):
            raise ValidationError("Slug can only contain lowercase letters, numbers, and hyphens")
        
        if len(slug) < 2:
            raise ValidationError("Slug must be at least 2 characters")
        
        if len(slug) > 100:
            raise ValidationError("Slug must be no more than 100 characters")
        
        if slug.startswith('-') or slug.endswith('-'):
            raise ValidationError("Slug cannot start or end with a hyphen")
        
        return slug
    
    def validate_integer(self, value: Union[int, str], field_name: str,
                        min_value: Optional[int] = None,
                        max_value: Optional[int] = None,
                        required: bool = True) -> int:
        """
        Validate integer input
        
        Args:
            value: Value to validate
            field_name: Name of field for error messages
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            required: Whether field is required
            
        Returns:
            Validated integer
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None and not required:
            return 0
        
        if value is None and required:
            raise ValidationError(f"{field_name} is required")
        
        # Convert string to int if needed
        if isinstance(value, str):
            value = value.strip()
            if not value and not required:
                return 0
            try:
                value = int(value)
            except ValueError:
                raise ValidationError(f"{field_name} must be a valid integer")
        
        if not isinstance(value, int):
            raise ValidationError(f"{field_name} must be an integer")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} must be no more than {max_value}")
        
        return value
    
    def sanitize_html_content(self, content: str) -> str:
        """
        Sanitize HTML content, removing dangerous elements
        
        Args:
            content: HTML content to sanitize
            
        Returns:
            Sanitized HTML content
        """
        if not content:
            return ""
        
        # Remove script tags and event handlers
        for pattern in self.script_patterns:
            content = pattern.sub('', content)
        
        # If we have allowed tags, filter to only those
        if self.allowed_html_tags:
            content = self._filter_allowed_tags(content)
        
        # Escape remaining content if no HTML is allowed
        if not self.allowed_html_tags:
            content = html.escape(content)
        
        return content
    
    def _filter_allowed_tags(self, content: str) -> str:
        """Filter HTML content to only allowed tags"""
        def replace_tag(match):
            tag = match.group(0)
            # Extract tag name
            tag_name_match = re.match(r'</?(\w+)', tag)
            if tag_name_match:
                tag_name = tag_name_match.group(1).lower()
                if tag_name in self.allowed_html_tags:
                    # Remove any event handlers from allowed tags
                    tag = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
                    return tag
            return ''  # Remove disallowed tags
        
        return self.html_tag_pattern.sub(replace_tag, content)
    
    def _check_for_malicious_content(self, content: str, field_name: str):
        """Check for potentially malicious content patterns"""
        # Check for script injection
        for pattern in self.script_patterns:
            if pattern.search(content):
                logger.warning(f"Script injection attempt detected in {field_name}")
                raise ValidationError(f"Invalid content detected in {field_name}")
        
        # Check for SQL injection (basic patterns)
        for pattern in self.sql_patterns:
            if pattern.search(content):
                logger.warning(f"Potential SQL injection detected in {field_name}")
                # Don't block legitimate content, just log and continue
    
    def validate_author_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate author data"""
        validated = {}
        
        validated['name'] = self.validate_string(data.get('name', ''), 'Name', max_length=100, min_length=2)
        validated['title'] = self.validate_string(data.get('title', ''), 'Title', max_length=100, required=False)
        validated['bio'] = self.validate_string(data.get('bio', ''), 'Bio', max_length=1000, required=False)
        validated['email'] = self.validate_email(data.get('email', ''), required=False)
        validated['location'] = self.validate_string(data.get('location', ''), 'Location', max_length=100, required=False)
        validated['expertise'] = self.validate_string(data.get('expertise', ''), 'Expertise', max_length=200, required=False)
        validated['twitter'] = self.validate_string(data.get('twitter', ''), 'Twitter', max_length=50, required=False)
        validated['linkedin'] = self.validate_url(data.get('linkedin', ''), required=False)
        
        # Generate slug if not provided
        if not data.get('slug'):
            validated['slug'] = self.generate_slug(validated['name'])
        else:
            validated['slug'] = self.validate_slug(data['slug'])
        
        return validated
    
    def validate_category_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate category data"""
        validated = {}
        
        validated['name'] = self.validate_string(data.get('name', ''), 'Name', max_length=50, min_length=2)
        validated['description'] = self.validate_string(data.get('description', ''), 'Description', max_length=500, required=False)
        validated['color'] = self.validate_string(data.get('color', ''), 'Color', max_length=20, required=False)
        validated['icon'] = self.validate_string(data.get('icon', ''), 'Icon', max_length=10, required=False)
        
        # Generate slug if not provided
        if not data.get('slug'):
            validated['slug'] = self.generate_slug(validated['name'])
        else:
            validated['slug'] = self.validate_slug(data['slug'])
        
        return validated
    
    def validate_article_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate article data"""
        validated = {}
        
        validated['title'] = self.validate_title(data.get('title', ''))
        validated['subtitle'] = self.validate_string(data.get('subtitle', ''), 'Subtitle', max_length=200, required=False)
        validated['content'] = self.validate_content(data.get('content', ''))
        validated['meta_description'] = self.validate_string(data.get('meta_description', ''), 'Meta Description', max_length=160, required=False)
        
        validated['author_id'] = self.validate_integer(data.get('author_id', 0), 'Author ID', min_value=1)
        validated['category_id'] = self.validate_integer(data.get('category_id', 0), 'Category ID', min_value=1)
        validated['read_time'] = self.validate_integer(data.get('read_time', 5), 'Read Time', min_value=1, max_value=120, required=False)
        
        # Validate publication date (should be in YYYY-MM-DD format)
        pub_date = data.get('publication_date', '')
        if pub_date:
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', pub_date):
                raise ValidationError("Publication date must be in YYYY-MM-DD format")
        validated['publication_date'] = pub_date
        
        # Generate slug if not provided
        if not data.get('slug'):
            validated['slug'] = self.generate_slug(validated['title'])
        else:
            validated['slug'] = self.validate_slug(data['slug'])
        
        # Validate tags (should be a list)
        tags = data.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        validated['tags'] = [self.validate_string(tag, 'Tag', max_length=50) for tag in tags[:10]]  # Limit to 10 tags
        
        return validated
    
    def validate_trending_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trending topic data"""
        validated = {}
        
        validated['title'] = self.validate_string(data.get('title', ''), 'Title', max_length=100, min_length=3)
        validated['description'] = self.validate_string(data.get('description', ''), 'Description', max_length=500, required=False)
        validated['heat_score'] = self.validate_integer(data.get('heat_score', 0), 'Heat Score', min_value=0, max_value=100, required=False)
        validated['icon'] = self.validate_string(data.get('icon', ''), 'Icon', max_length=10, required=False)
        
        # Generate slug if not provided
        if not data.get('slug'):
            validated['slug'] = self.generate_slug(validated['title'])
        else:
            validated['slug'] = self.validate_slug(data['slug'])
        
        return validated
    
    def generate_slug(self, text: str) -> str:
        """
        Generate URL-safe slug from text
        
        Args:
            text: Text to convert to slug
            
        Returns:
            Generated slug
        """
        if not text:
            return ""
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Limit length
        if len(slug) > 100:
            slug = slug[:100].rstrip('-')
        
        return slug or "content"

# Global validator instance
validator = ContentValidator()