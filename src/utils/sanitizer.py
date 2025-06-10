"""
Content sanitization and validation utilities
Provides comprehensive input validation and HTML sanitization
"""

import re
import html
import urllib.parse
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from .config import config
from .logger import get_logger, CMSException

logger = get_logger(__name__)

@dataclass
class ValidationResult:
    """Result of content validation"""
    is_valid: bool
    cleaned_content: str
    errors: List[str]
    warnings: List[str]

class ContentSanitizer:
    """Handles content sanitization and validation"""
    
    def __init__(self):
        self.max_content_length = config.get('security.max_content_length', 50000)
        self.max_title_length = config.get('security.max_title_length', 200)
        self.allowed_html_tags = set(config.get('security.allowed_html_tags', [
            'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        ]))
        self.sanitize_html = config.get('security.sanitize_html', True)
        
        # Dangerous patterns to detect
        self.dangerous_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',              # JavaScript URLs
            r'vbscript:',               # VBScript URLs
            r'data:',                   # Data URLs (can be dangerous)
            r'on\w+\s*=',              # Event handlers (onclick, onload, etc.)
            r'<iframe.*?>',             # Iframe tags
            r'<object.*?>',             # Object tags
            r'<embed.*?>',              # Embed tags
            r'<form.*?>',               # Form tags
            r'<input.*?>',              # Input tags
            r'<meta.*?>',               # Meta tags
            r'<link.*?>',               # Link tags (can load external content)
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                                for pattern in self.dangerous_patterns]
    
    def sanitize_content(self, content: str, content_type: str = 'general') -> ValidationResult:
        """
        Sanitize and validate content
        
        Args:
            content: Raw content to sanitize
            content_type: Type of content ('article', 'title', 'bio', 'general')
            
        Returns:
            ValidationResult with cleaned content and validation info
        """
        errors = []
        warnings = []
        cleaned_content = content
        
        try:
            # Basic input validation
            if not isinstance(content, str):
                cleaned_content = str(content)
                warnings.append("Content was converted to string")
            
            # Length validation
            max_length = self._get_max_length(content_type)
            if len(cleaned_content) > max_length:
                errors.append(f"Content exceeds maximum length of {max_length} characters")
                cleaned_content = cleaned_content[:max_length]
                warnings.append("Content was truncated to maximum length")
            
            # Detect dangerous patterns
            for pattern in self.compiled_patterns:
                if pattern.search(cleaned_content):
                    match = pattern.search(cleaned_content)
                    errors.append(f"Potentially dangerous content detected: {match.group()[:50]}...")
                    # Remove the dangerous content
                    cleaned_content = pattern.sub('', cleaned_content)
                    warnings.append("Dangerous content was removed")
            
            # HTML sanitization
            if self.sanitize_html:
                cleaned_content = self._sanitize_html(cleaned_content)
            
            # Content-specific validation
            if content_type == 'email':
                cleaned_content = self._validate_email(cleaned_content, errors)
            elif content_type == 'url':
                cleaned_content = self._validate_url(cleaned_content, errors)
            elif content_type == 'slug':
                cleaned_content = self._validate_slug(cleaned_content, errors, warnings)
            elif content_type == 'title':
                cleaned_content = self._validate_title(cleaned_content, errors, warnings)
            
            # Final cleanup
            cleaned_content = self._final_cleanup(cleaned_content)
            
            is_valid = len(errors) == 0
            
            if not is_valid:
                logger.warning(f"Content validation failed: {'; '.join(errors)}")
            elif warnings:
                logger.info(f"Content validation warnings: {'; '.join(warnings)}")
            
            return ValidationResult(
                is_valid=is_valid,
                cleaned_content=cleaned_content,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Content sanitization failed: {e}")
            return ValidationResult(
                is_valid=False,
                cleaned_content=content,
                errors=[f"Sanitization error: {str(e)}"],
                warnings=[]
            )
    
    def _get_max_length(self, content_type: str) -> int:
        """Get maximum length for content type"""
        length_map = {
            'title': self.max_title_length,
            'subtitle': self.max_title_length * 2,
            'bio': 1000,
            'description': 500,
            'email': 255,
            'url': 2048,
            'slug': 100,
            'name': 100,
            'general': self.max_content_length
        }
        return length_map.get(content_type, self.max_content_length)
    
    def _sanitize_html(self, content: str) -> str:
        """Sanitize HTML content"""
        # Remove all HTML tags except allowed ones
        if not self.allowed_html_tags:
            # Strip all HTML if no tags are allowed
            return re.sub(r'<[^>]+>', '', content)
        
        # Build pattern for allowed tags
        allowed_pattern = '|'.join(re.escape(tag) for tag in self.allowed_html_tags)
        
        # Remove disallowed HTML tags
        content = re.sub(
            rf'<(?!/?(?:{allowed_pattern})\b)[^>]*>',
            '',
            content,
            flags=re.IGNORECASE
        )
        
        # Clean up attributes from allowed tags (keep only safe ones)
        safe_attributes = ['href', 'title', 'alt']
        for tag in self.allowed_html_tags:
            # Pattern to match tag with any attributes
            tag_pattern = rf'<({tag})\s+([^>]*)>'
            
            def clean_attributes(match):
                tag_name = match.group(1)
                attrs = match.group(2)
                
                # Extract safe attributes
                cleaned_attrs = []
                for attr in safe_attributes:
                    attr_match = re.search(rf'{attr}\s*=\s*["\']([^"\']*)["\']', attrs, re.IGNORECASE)
                    if attr_match:
                        attr_value = attr_match.group(1)
                        # Additional validation for href attributes
                        if attr == 'href':
                            attr_value = self._validate_href(attr_value)
                        if attr_value:
                            cleaned_attrs.append(f'{attr}="{html.escape(attr_value)}"')
                
                if cleaned_attrs:
                    return f'<{tag_name} {" ".join(cleaned_attrs)}>'
                else:
                    return f'<{tag_name}>'
            
            content = re.sub(tag_pattern, clean_attributes, content, flags=re.IGNORECASE)
        
        return content
    
    def _validate_href(self, href: str) -> str:
        """Validate and clean href attributes"""
        if not href:
            return ""
        
        # Remove dangerous protocols
        dangerous_protocols = ['javascript:', 'vbscript:', 'data:', 'file:']
        href_lower = href.lower().strip()
        
        for protocol in dangerous_protocols:
            if href_lower.startswith(protocol):
                return ""  # Remove dangerous href
        
        # Allow only safe protocols
        safe_protocols = ['http:', 'https:', 'mailto:', 'tel:', '#']
        is_safe = any(href_lower.startswith(protocol) for protocol in safe_protocols)
        
        if not is_safe and not href.startswith('/'):  # Relative URLs are OK
            return ""  # Remove unsafe href
        
        return href
    
    def _validate_email(self, email: str, errors: List[str]) -> str:
        """Validate email format"""
        email = email.strip().lower()
        
        # Basic email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            errors.append("Invalid email format")
            return email
        
        # Additional checks
        if '..' in email:
            errors.append("Email contains consecutive dots")
        
        if email.startswith('.') or email.endswith('.'):
            errors.append("Email cannot start or end with a dot")
        
        return email
    
    def _validate_url(self, url: str, errors: List[str]) -> str:
        """Validate URL format"""
        url = url.strip()
        
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check for valid scheme
            if parsed.scheme not in ['http', 'https']:
                errors.append("URL must use http or https protocol")
            
            # Check for valid domain
            if not parsed.netloc:
                errors.append("URL must have a valid domain")
            
            # Reconstruct URL to normalize it
            return urllib.parse.urlunparse(parsed)
            
        except Exception:
            errors.append("Invalid URL format")
            return url
    
    def _validate_slug(self, slug: str, errors: List[str], warnings: List[str]) -> str:
        """Validate and clean slug"""
        original_slug = slug
        
        # Convert to lowercase
        slug = slug.lower().strip()
        
        # Replace spaces and special characters with hyphens
        slug = re.sub(r'[^a-z0-9\-]', '-', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        # Minimum length check
        if len(slug) < 2:
            errors.append("Slug must be at least 2 characters long")
        
        # Check if slug was modified
        if slug != original_slug:
            warnings.append("Slug was automatically cleaned")
        
        return slug
    
    def _validate_title(self, title: str, errors: List[str], warnings: List[str]) -> str:
        """Validate and clean title"""
        title = title.strip()
        
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title)
        
        # Check minimum length
        if len(title) < 5:
            errors.append("Title must be at least 5 characters long")
        
        # Check for excessive punctuation
        punct_count = sum(1 for c in title if c in '!?.')
        if punct_count > len(title) * 0.2:  # More than 20% punctuation
            warnings.append("Title contains excessive punctuation")
        
        return title
    
    def _final_cleanup(self, content: str) -> str:
        """Final content cleanup"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        # Remove null bytes
        content = content.replace('\x00', '')
        
        return content

class ModelValidator:
    """Validates model data before database operations"""
    
    def __init__(self):
        self.sanitizer = ContentSanitizer()
    
    def validate_article(self, article_data: Dict[str, Any]) -> ValidationResult:
        """Validate article data"""
        errors = []
        warnings = []
        cleaned_data = article_data.copy()
        
        # Required fields
        required_fields = ['title', 'slug', 'content', 'author_id', 'category_id']
        for field in required_fields:
            if field not in article_data or not article_data[field]:
                errors.append(f"Required field '{field}' is missing")
        
        # Validate and sanitize text fields
        text_fields = {
            'title': 'title',
            'subtitle': 'subtitle',
            'content': 'general',
            'meta_description': 'description',
            'slug': 'slug'
        }
        
        for field, content_type in text_fields.items():
            if field in article_data and article_data[field]:
                result = self.sanitizer.sanitize_content(
                    str(article_data[field]), 
                    content_type
                )
                cleaned_data[field] = result.cleaned_content
                errors.extend(result.errors)
                warnings.extend(result.warnings)
        
        # Validate numeric fields
        if 'read_time' in article_data:
            try:
                read_time = int(article_data['read_time'])
                if read_time < 1 or read_time > 120:  # 1-120 minutes
                    warnings.append("Read time should be between 1-120 minutes")
                    read_time = max(1, min(120, read_time))
                cleaned_data['read_time'] = read_time
            except (ValueError, TypeError):
                errors.append("Read time must be a valid number")
        
        # Validate tags
        if 'tags' in article_data:
            tags = article_data['tags']
            if isinstance(tags, str):
                try:
                    import json
                    tags = json.loads(tags)
                except:
                    tags = [tag.strip() for tag in tags.split(',')]
            
            if isinstance(tags, list):
                # Sanitize each tag
                cleaned_tags = []
                for tag in tags[:10]:  # Max 10 tags
                    tag_result = self.sanitizer.sanitize_content(str(tag), 'name')
                    if tag_result.is_valid and tag_result.cleaned_content:
                        cleaned_tags.append(tag_result.cleaned_content)
                
                cleaned_data['tags'] = cleaned_tags
                if len(tags) > 10:
                    warnings.append("Only first 10 tags were kept")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            cleaned_content=cleaned_data,
            errors=errors,
            warnings=warnings
        )
    
    def validate_author(self, author_data: Dict[str, Any]) -> ValidationResult:
        """Validate author data"""
        errors = []
        warnings = []
        cleaned_data = author_data.copy()
        
        # Required fields
        required_fields = ['name', 'slug']
        for field in required_fields:
            if field not in author_data or not author_data[field]:
                errors.append(f"Required field '{field}' is missing")
        
        # Validate text fields
        text_fields = {
            'name': 'name',
            'title': 'name',
            'bio': 'bio',
            'location': 'name',
            'expertise': 'description',
            'slug': 'slug'
        }
        
        for field, content_type in text_fields.items():
            if field in author_data and author_data[field]:
                result = self.sanitizer.sanitize_content(
                    str(author_data[field]), 
                    content_type
                )
                cleaned_data[field] = result.cleaned_content
                errors.extend(result.errors)
                warnings.extend(result.warnings)
        
        # Validate email
        if 'email' in author_data and author_data['email']:
            email_result = self.sanitizer.sanitize_content(
                str(author_data['email']), 
                'email'
            )
            cleaned_data['email'] = email_result.cleaned_content
            errors.extend(email_result.errors)
            warnings.extend(email_result.warnings)
        
        # Validate social links
        social_fields = ['twitter', 'linkedin', 'instagram', 'website']
        for field in social_fields:
            if field in author_data and author_data[field]:
                url_result = self.sanitizer.sanitize_content(
                    str(author_data[field]), 
                    'url'
                )
                cleaned_data[field] = url_result.cleaned_content
                errors.extend(url_result.errors)
                warnings.extend(url_result.warnings)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            cleaned_content=cleaned_data,
            errors=errors,
            warnings=warnings
        )

# Global instances
content_sanitizer = ContentSanitizer()
model_validator = ModelValidator()