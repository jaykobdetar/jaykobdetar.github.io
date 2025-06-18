"""
Security Middleware
===================
Middleware for adding security headers and CSP to responses
"""

import logging
import secrets
import base64
from typing import Dict, Optional
from .trusted_security import CSPGenerator

logger = logging.getLogger(__name__)

# Create separate security logger for validation failures (no user data)
security_logger = logging.getLogger('security.validation')
if not security_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)
    security_logger.setLevel(logging.WARNING)

class SecurityMiddleware:
    """Middleware to add security headers to HTTP responses"""
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize security middleware
        
        Args:
            strict_mode: Whether to use strict CSP or relaxed CSP
        """
        self.strict_mode = strict_mode
        self.csp_generator = CSPGenerator()
        self._current_nonce = None
    
    def generate_nonce(self) -> str:
        """Generate a cryptographically secure nonce for CSP"""
        nonce_bytes = secrets.token_bytes(16)
        nonce = base64.b64encode(nonce_bytes).decode('ascii')
        self._current_nonce = nonce
        return nonce
    
    def get_current_nonce(self) -> str:
        """Get the current nonce, generating one if needed"""
        if not self._current_nonce:
            return self.generate_nonce()
        return self._current_nonce
    
    def get_security_headers(self) -> Dict[str, str]:
        """
        Get security headers for HTTP responses
        
        Returns:
            Dictionary of security headers
        """
        
        # Choose CSP based on mode
        nonce = self.get_current_nonce()
        if self.strict_mode:
            csp = self.csp_generator.get_strict_csp(nonce)
        else:
            csp = self.csp_generator.get_relaxed_csp()
        
        headers = {
            # Content Security Policy
            'Content-Security-Policy': csp,
            
            # Prevent MIME type sniffing
            'X-Content-Type-Options': 'nosniff',
            
            # Prevent clickjacking
            'X-Frame-Options': 'DENY',
            
            # Enable XSS filtering
            'X-XSS-Protection': '1; mode=block',
            
            # Control referrer information
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Control browser features
            'Permissions-Policy': 'camera=(), microphone=(), location=(), payment=(), usb=()',
            
            # Additional security headers
            'X-Permitted-Cross-Domain-Policies': 'none',
            'Cross-Origin-Embedder-Policy': 'require-corp',
            'Cross-Origin-Opener-Policy': 'same-origin',
            'Cross-Origin-Resource-Policy': 'same-origin'
        }
        
        return headers
    
    def apply_headers_to_response(self, response_headers: Dict[str, str]) -> Dict[str, str]:
        """
        Apply security headers to response headers
        
        Args:
            response_headers: Existing response headers
            
        Returns:
            Updated response headers with security headers
        """
        security_headers = self.get_security_headers()
        
        # Merge headers (security headers take precedence)
        updated_headers = response_headers.copy()
        updated_headers.update(security_headers)
        
        return updated_headers
    
    def get_meta_tags(self) -> str:
        """
        Get security-related meta tags for HTML pages
        
        Returns:
            HTML meta tags string
        """
        
        # Choose CSP based on mode
        nonce = self.get_current_nonce()
        if self.strict_mode:
            csp = self.csp_generator.get_strict_csp(nonce)
        else:
            csp = self.csp_generator.get_relaxed_csp()
        
        meta_tags = f'''
        <!-- Security Headers -->
        <meta http-equiv="Content-Security-Policy" content="{csp}">
        <meta http-equiv="X-Content-Type-Options" content="nosniff">
        <meta http-equiv="X-Frame-Options" content="DENY">
        <meta http-equiv="X-XSS-Protection" content="1; mode=block">
        <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
        '''
        
        return meta_tags.strip()

class InputValidator:
    """Server-side input validation for form submissions and API requests"""
    
    @staticmethod
    def validate_search_query(query: str, client_ip: str = None) -> str:
        """
        Validate search query input
        
        Args:
            query: Search query string
            client_ip: Client IP address (not logged per privacy policy)
            
        Returns:
            Validated query string
            
        Raises:
            ValueError: If query is invalid
        """
        try:
            if not query:
                raise ValueError("Search query cannot be empty")
            
            if not isinstance(query, str):
                raise ValueError("Search query must be a string")
            
            query = query.strip()
            
            # Length limits
            if len(query) > 200:
                security_logger.warning(
                    f"Search query too long: {len(query)} chars"
                )
                raise ValueError("Search query too long (max 200 characters)")
            
            if len(query) < 1:
                raise ValueError("Search query too short (min 1 character)")
            
            # Block dangerous patterns
            dangerous_patterns = [
                '<script', 'javascript:', 'vbscript:', 'on[a-z]+='
            ]
            
            query_lower = query.lower()
            for pattern in dangerous_patterns:
                if pattern in query_lower:
                    security_logger.warning(
                        f"SECURITY ALERT: Dangerous pattern '{pattern}' detected in search query"
                    )
                    raise ValueError("Invalid characters in search query")
            
            return query
            
        except ValueError as e:
            # Log validation failures without user data
            security_logger.warning(
                f"Search validation failed: {str(e)}"
            )
            raise
    
    @staticmethod
    def validate_pagination_params(limit: str, offset: str, client_ip: str = None) -> tuple:
        """
        Validate pagination parameters
        
        Args:
            limit: Number of items per page
            offset: Starting position
            
        Returns:
            Tuple of (validated_limit, validated_offset)
            
        Raises:
            ValueError: If parameters are invalid
        """
        try:
            limit = int(limit) if limit else 20
            offset = int(offset) if offset else 0
        except ValueError:
            raise ValueError("Pagination parameters must be integers")
        
        # Reasonable limits
        if limit < 1 or limit > 100:
            raise ValueError("Page limit must be between 1 and 100")
        
        if offset < 0:
            raise ValueError("Page offset cannot be negative")
        
        if offset > 10000:  # Prevent excessive pagination
            raise ValueError("Page offset too large")
        
        return limit, offset
    
    @staticmethod
    def validate_content_type(content_type: str) -> str:
        """
        Validate content type filter
        
        Args:
            content_type: Content type string
            
        Returns:
            Validated content type
            
        Raises:
            ValueError: If content type is invalid
        """
        allowed_types = ['all', 'article', 'author', 'category', 'trending']
        
        if not content_type:
            return 'all'
        
        content_type = content_type.lower().strip()
        
        if content_type not in allowed_types:
            raise ValueError(f"Invalid content type. Must be one of: {', '.join(allowed_types)}")
        
        return content_type

# Global instances
security_middleware = SecurityMiddleware(strict_mode=True)
security_middleware_dev = SecurityMiddleware(strict_mode=False)
input_validator = InputValidator()