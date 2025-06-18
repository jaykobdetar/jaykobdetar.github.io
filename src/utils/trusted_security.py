"""
Trusted Security Implementation
===============================
Security implementation using trusted, industry-standard libraries:
- bleach for HTML sanitization
- html5lib for HTML parsing
- CSP headers for browser protection
- Comprehensive input validation
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse
from datetime import datetime

try:
    import bleach
    from bleach.css_sanitizer import CSSSanitizer
    import html5lib
    HAS_BLEACH = True
except ImportError:
    HAS_BLEACH = False
    print("WARNING: bleach and html5lib not installed. Run: pip install bleach html5lib")

try:
    from .config import config
    from .logger import get_logger
except ImportError:
    from src.utils.config import config
    from src.utils.logger import get_logger

logger = get_logger(__name__)

class TrustedSanitizer:
    """HTML sanitization using bleach - industry standard library"""
    
    def __init__(self):
        """Initialize with secure defaults from configuration"""
        
        # Get security configuration
        security_config = config.get_security_config()
        
        # Load allowed tags from config, with comprehensive defaults
        config_tags = security_config.get('allowed_html_tags', [])
        default_tags = [
            'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'mark',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'dl', 'dt', 'dd',
            'blockquote', 'pre', 'code',
            'a', 'img', 'figure', 'figcaption',
            'table', 'thead', 'tbody', 'tr', 'td', 'th',
            'div', 'span', 'section', 'article', 'header', 'footer',
            'hr', 'sub', 'sup', 'small',
        ]
        
        # Merge config tags with defaults (ensure minimum security)
        self.ALLOWED_TAGS = list(set(config_tags + default_tags)) if config_tags else default_tags
        
        # Get additional security settings from config
        additional_settings = config.get('security.html_sanitization', {})
        
        # Safe HTML attributes (extended if configured)
        default_attributes = {
            'a': ['href', 'title', 'rel'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'blockquote': ['cite'],
            'table': ['summary'],
            'td': ['colspan', 'rowspan'],
            'th': ['colspan', 'rowspan', 'scope'],
            'div': ['class'],
            'span': ['class'],
            'p': ['class'],
            'h1': ['class'], 'h2': ['class'], 'h3': ['class'], 
            'h4': ['class'], 'h5': ['class'], 'h6': ['class'],
        }
        
        # Allow config to extend attributes
        config_attributes = additional_settings.get('allowed_attributes', {})
        self.ALLOWED_ATTRIBUTES = {**default_attributes, **config_attributes}
        
        # Safe URL protocols (configurable)
        self.ALLOWED_PROTOCOLS = additional_settings.get('allowed_protocols', 
                                                         ['http', 'https', 'mailto', 'tel'])
        
        # CSS sanitizer for safe styling
        if HAS_BLEACH:
            css_properties = additional_settings.get('allowed_css_properties', [
                'color', 'background-color', 'font-size', 'font-weight',
                'text-align', 'text-decoration', 'margin', 'padding',
                'border', 'border-radius', 'display', 'float',
            ])
            self.css_sanitizer = CSSSanitizer(allowed_css_properties=css_properties)
    
    def sanitize_html(self, content: str, allow_tags: bool = True) -> str:
        """
        Sanitize HTML content using bleach (trusted library)
        
        Args:
            content: HTML content to sanitize
            allow_tags: Whether to allow HTML tags or strip all
            
        Returns:
            Sanitized HTML content
        """
        if not content:
            return ""
        
        if not HAS_BLEACH:
            # Fallback to basic HTML escaping if bleach not available
            import html
            logger.warning("bleach not available, using basic HTML escaping")
            return html.escape(content)
        
        try:
            if allow_tags:
                # Use bleach to sanitize with allowed tags and attributes
                sanitized = bleach.clean(
                    content,
                    tags=self.ALLOWED_TAGS,
                    attributes=self.ALLOWED_ATTRIBUTES,
                    protocols=self.ALLOWED_PROTOCOLS,
                    strip=True,  # Strip disallowed tags rather than escape
                    strip_comments=True,  # Remove HTML comments
                )
                
                # Additional validation with html5lib for proper parsing
                try:
                    parsed = html5lib.parse(sanitized, treebuilder="etree")
                    # If parsing succeeds, content is well-formed
                except Exception as e:
                    logger.warning(f"HTML parsing validation failed: {e}")
                    # Fall back to text-only content
                    sanitized = bleach.clean(content, tags=[], strip=True)
                
            else:
                # Strip all HTML tags
                sanitized = bleach.clean(content, tags=[], strip=True)
            
            return sanitized.strip()
            
        except Exception as e:
            logger.error(f"HTML sanitization failed: {e}")
            # Fallback to basic escaping
            import html
            return html.escape(content)
    
    def sanitize_text(self, content: str) -> str:
        """Sanitize plain text content (no HTML allowed)"""
        return self.sanitize_html(content, allow_tags=False)
    
    def sanitize_url(self, url: str) -> str:
        """
        Sanitize and validate URL
        
        Args:
            url: URL to sanitize
            
        Returns:
            Sanitized URL or empty string if invalid
        """
        if not url:
            return ""
        
        url = url.strip()
        
        try:
            parsed = urlparse(url)
            
            # Only allow safe protocols
            if parsed.scheme and parsed.scheme not in self.ALLOWED_PROTOCOLS:
                logger.warning(f"Blocked unsafe URL protocol: {parsed.scheme}")
                return ""
            
            # Block javascript: and data: URLs
            if url.lower().startswith(('javascript:', 'data:', 'vbscript:')):
                logger.warning(f"Blocked dangerous URL: {url[:50]}...")
                return ""
            
            # Reconstruct URL to normalize it
            if parsed.scheme and parsed.netloc:
                return parsed.geturl()
            elif url.startswith('/') or url.startswith('#'):
                # Relative URLs are okay
                return url
            else:
                # Invalid URL structure
                return ""
                
        except Exception as e:
            logger.warning(f"URL validation failed: {e}")
            return ""

class TrustedValidator:
    """Input validation using secure, trusted patterns"""
    
    def __init__(self):
        """Initialize validator with secure patterns from configuration"""
        self.sanitizer = TrustedSanitizer()
        
        # Compile regex patterns for performance
        self._compile_patterns()
        
        # Get security configuration
        security_config = config.get_security_config()
        
        # Security limits from config with sensible defaults
        self.MAX_CONTENT_LENGTH = security_config.get('max_content_length', 50000)
        self.MAX_TITLE_LENGTH = security_config.get('max_title_length', 200)
        self.MAX_BIO_LENGTH = config.get('security.max_bio_length', 2000)
        self.MAX_URL_LENGTH = config.get('security.max_url_length', 2048)
        self.MAX_EMAIL_LENGTH = config.get('security.max_email_length', 254)  # RFC 5321 limit
        
        # Additional configurable limits
        self.MAX_EXCERPT_LENGTH = config.get('security.max_excerpt_length', 500)
        self.MAX_SLUG_LENGTH = config.get('security.max_slug_length', 100)
        self.MIN_SLUG_LENGTH = config.get('security.min_slug_length', 2)
        
    def _compile_patterns(self):
        """Compile regex patterns for validation"""
        
        # Email validation (RFC 5322 compliant)
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        )
        
        # Slug validation (URL-safe identifiers)
        self.slug_pattern = re.compile(r'^[a-z0-9-]+$')
        
        # Dangerous patterns that should be blocked
        self.dangerous_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'data:(?!image/)', re.IGNORECASE),  # Allow data: images only
            re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers
            re.compile(r'<iframe[^>]*>', re.IGNORECASE),
            re.compile(r'<object[^>]*>', re.IGNORECASE),
            re.compile(r'<embed[^>]*>', re.IGNORECASE),
            re.compile(r'<form[^>]*>', re.IGNORECASE),
        ]
        
        # SQL injection patterns (for logging, not blocking legitimate content)
        self.sql_patterns = [
            re.compile(r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+', re.IGNORECASE),
            re.compile(r'[\'\"]\s*(or|and)\s*[\'\"]\s*=\s*[\'\"]\s*[\'\"]\s*', re.IGNORECASE),
            re.compile(r'(\-\-|\#|/\*|\*/)', re.IGNORECASE),
        ]
    
    def validate_and_sanitize_text(self, content: str, field_name: str, 
                                  max_length: Optional[int] = None,
                                  min_length: int = 0,
                                  allow_html: bool = False,
                                  required: bool = True) -> str:
        """
        Validate and sanitize text content with comprehensive security checks
        
        Args:
            content: Content to validate
            field_name: Field name for error messages
            max_length: Maximum allowed length
            min_length: Minimum required length
            allow_html: Whether to allow HTML content
            required: Whether field is required
            
        Returns:
            Sanitized content
            
        Raises:
            ValueError: If validation fails
        """
        
        # Handle None/empty content
        if content is None:
            content = ""
        
        if not isinstance(content, str):
            content = str(content)
        
        # Strip whitespace
        content = content.strip()
        
        # Check if required
        if required and not content:
            raise ValueError(f"{field_name} is required")
        
        if not content and not required:
            return ""
        
        # Length validation
        if len(content) < min_length:
            raise ValueError(f"{field_name} must be at least {min_length} characters")
        
        if max_length and len(content) > max_length:
            raise ValueError(f"{field_name} must be no more than {max_length} characters")
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern.search(content):
                logger.warning(f"Dangerous content detected in {field_name}: {pattern.pattern}")
                raise ValueError(f"Content contains unsafe elements in {field_name}")
        
        # Log potential SQL injection attempts (but don't block)
        for pattern in self.sql_patterns:
            if pattern.search(content):
                logger.warning(f"Potential SQL injection pattern in {field_name}: {content[:100]}...")
        
        # Sanitize content
        if allow_html:
            content = self.sanitizer.sanitize_html(content, allow_tags=True)
        else:
            content = self.sanitizer.sanitize_text(content)
        
        return content
    
    def validate_email(self, email: str, required: bool = True) -> str:
        """Validate email address using trusted patterns"""
        
        if not email and not required:
            return ""
        
        if not email and required:
            raise ValueError("Email is required")
        
        email = email.strip().lower()
        
        if len(email) > self.MAX_EMAIL_LENGTH:
            raise ValueError(f"Email too long (max {self.MAX_EMAIL_LENGTH} characters)")
        
        if not self.email_pattern.match(email):
            raise ValueError("Invalid email format")
        
        return email
    
    def validate_url(self, url: str, required: bool = False) -> str:
        """Validate URL using trusted sanitization"""
        
        if not url and not required:
            return ""
        
        if not url and required:
            raise ValueError("URL is required")
        
        url = url.strip()
        
        if len(url) > self.MAX_URL_LENGTH:
            raise ValueError(f"URL too long (max {self.MAX_URL_LENGTH} characters)")
        
        sanitized_url = self.sanitizer.sanitize_url(url)
        
        if not sanitized_url and url:
            raise ValueError("Invalid or unsafe URL")
        
        return sanitized_url
    
    def validate_slug(self, slug: str, required: bool = True) -> str:
        """Validate URL slug"""
        
        if not slug and not required:
            return ""
        
        if not slug and required:
            raise ValueError("Slug is required")
        
        slug = slug.strip().lower()
        
        # Basic format validation
        if not self.slug_pattern.match(slug):
            raise ValueError("Slug can only contain lowercase letters, numbers, and hyphens")
        
        if len(slug) < self.MIN_SLUG_LENGTH:
            raise ValueError(f"Slug must be at least {self.MIN_SLUG_LENGTH} characters")
        
        if len(slug) > self.MAX_SLUG_LENGTH:
            raise ValueError(f"Slug must be no more than {self.MAX_SLUG_LENGTH} characters")
        
        if slug.startswith('-') or slug.endswith('-'):
            raise ValueError("Slug cannot start or end with a hyphen")
        
        if '--' in slug:
            raise ValueError("Slug cannot contain consecutive hyphens")
        
        return slug
    
    def validate_integer(self, value: Union[int, str], field_name: str,
                        min_value: Optional[int] = None,
                        max_value: Optional[int] = None,
                        required: bool = True) -> int:
        """Validate integer input with bounds checking"""
        
        if value is None and not required:
            return 0
        
        if value is None and required:
            raise ValueError(f"{field_name} is required")
        
        # Convert string to int if needed
        if isinstance(value, str):
            value = value.strip()
            if not value and not required:
                return 0
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"{field_name} must be a valid integer")
        
        if not isinstance(value, int):
            raise ValueError(f"{field_name} must be an integer")
        
        if min_value is not None and value < min_value:
            raise ValueError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValueError(f"{field_name} must be no more than {max_value}")
        
        return value
    
    def generate_safe_slug(self, text: str) -> str:
        """Generate URL-safe slug from text"""
        
        if not text:
            return ""
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Limit length using configured max
        if len(slug) > self.MAX_SLUG_LENGTH:
            slug = slug[:self.MAX_SLUG_LENGTH].rstrip('-')
        
        # Ensure it matches our slug pattern
        if not slug or not self.slug_pattern.match(slug):
            return "content"  # Fallback slug
        
        return slug

class CSPGenerator:
    """Generate Content Security Policy headers"""
    
    @staticmethod
    def get_strict_csp(nonce: str = None) -> str:
        """Get strict CSP for maximum security with nonce support - NO UNSAFE FALLBACKS"""
        # Get CSP configuration
        csp_config = config.get('security.csp', {})
        
        # Build script-src directive
        script_sources = csp_config.get('script_sources', ['self', 'https://cdn.jsdelivr.net'])
        script_src_parts = []
        for source in script_sources:
            if source == 'self':
                script_src_parts.append("'self'")
            else:
                script_src_parts.append(source)
        
        # Build style-src directive
        style_sources = csp_config.get('style_sources', ['self', 'https://fonts.googleapis.com'])
        style_src_parts = []
        for source in style_sources:
            if source == 'self':
                style_src_parts.append("'self'")
            else:
                style_src_parts.append(source)
        
        # Add nonce if provided
        if nonce:
            script_src_parts.append(f"'nonce-{nonce}'")
            style_src_parts.append(f"'nonce-{nonce}'")
        
        script_src = " ".join(script_src_parts)
        style_src = " ".join(style_src_parts)
        
        # Get other directives from config with secure defaults
        directives = {
            "default-src": "'self'",
            "script-src": script_src,
            "style-src": style_src,
            "img-src": csp_config.get('img_sources', "'self' data: https: blob:"),
            "font-src": csp_config.get('font_sources', "'self' https://fonts.gstatic.com"),
            "connect-src": csp_config.get('connect_sources', "'self'"),
            "media-src": csp_config.get('media_sources', "'self'"),
            "object-src": "'none'",
            "frame-src": "'none'",
            "base-uri": "'self'",
            "form-action": "'self'",
            "frame-ancestors": "'none'",
            "upgrade-insecure-requests": ""
        }
        
        # Build CSP header
        csp_parts = []
        for directive, value in directives.items():
            if value:  # Skip empty values
                csp_parts.append(f"{directive} {value}")
            else:
                csp_parts.append(directive)
        
        return "; ".join(csp_parts)
    
    @staticmethod
    def get_relaxed_csp() -> str:
        """Get more permissive CSP for development"""
        return "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:",
            "style-src 'self' 'unsafe-inline' https:",
            "img-src 'self' data: https: blob:",
            "font-src 'self' https:",
            "connect-src 'self' https:",
            "media-src 'self' https:",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ])

# Global instances for convenience
trusted_sanitizer = TrustedSanitizer()
trusted_validator = TrustedValidator()
csp_generator = CSPGenerator()