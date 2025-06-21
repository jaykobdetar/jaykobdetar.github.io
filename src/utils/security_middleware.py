"""
Security Middleware
===================
Middleware for adding security headers and CSP to responses
"""

import logging
import secrets
import base64
from typing import Dict, Optional, Any
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
        self._csrf_tokens = {}  # Store active CSRF tokens
        self._rate_limits = {}  # Store rate limiting data
    
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
    
    def generate_csrf_token(self, session_id: str = None) -> str:
        """
        Generate a CSRF token for a session
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            CSRF token string
        """
        # Generate a cryptographically secure token
        token_bytes = secrets.token_bytes(32)
        csrf_token = base64.b64encode(token_bytes).decode('ascii')
        
        # Store token with timestamp for expiration
        from datetime import datetime, timedelta
        expiry = datetime.now() + timedelta(hours=24)  # 24 hour expiry
        
        token_data = {
            'token': csrf_token,
            'expiry': expiry,
            'session_id': session_id
        }
        
        # Use session_id as key, or the token itself if no session
        key = session_id if session_id else csrf_token
        self._csrf_tokens[key] = token_data
        
        # Clean up expired tokens
        self._cleanup_expired_csrf_tokens()
        
        return csrf_token
    
    def validate_csrf_token(self, token: str, session_id: str = None) -> bool:
        """
        Validate a CSRF token
        
        Args:
            token: CSRF token to validate
            session_id: Optional session identifier
            
        Returns:
            True if token is valid, False otherwise
        """
        if not token:
            security_logger.warning("CSRF validation failed: No token provided")
            return False
        
        # Look up token by session_id if provided, otherwise by token
        key = session_id if session_id else token
        
        if key not in self._csrf_tokens:
            security_logger.warning(f"CSRF validation failed: Token not found for key {key[:10]}...")
            return False
        
        token_data = self._csrf_tokens[key]
        
        # Check if token matches
        if token_data['token'] != token:
            security_logger.warning("CSRF validation failed: Token mismatch")
            return False
        
        # Check if token is expired
        from datetime import datetime
        if datetime.now() > token_data['expiry']:
            security_logger.warning("CSRF validation failed: Token expired")
            del self._csrf_tokens[key]
            return False
        
        return True
    
    def invalidate_csrf_token(self, session_id: str = None, token: str = None) -> None:
        """
        Invalidate a CSRF token
        
        Args:
            session_id: Optional session identifier
            token: Optional token to invalidate
        """
        key = session_id if session_id else token
        if key and key in self._csrf_tokens:
            del self._csrf_tokens[key]
    
    def _cleanup_expired_csrf_tokens(self) -> None:
        """Remove expired CSRF tokens"""
        from datetime import datetime
        now = datetime.now()
        
        expired_keys = [
            key for key, data in self._csrf_tokens.items()
            if data['expiry'] < now
        ]
        
        for key in expired_keys:
            del self._csrf_tokens[key]
        
        if expired_keys:
            security_logger.info(f"Cleaned up {len(expired_keys)} expired CSRF tokens")
    
    def check_rate_limit(self, identifier: str, limit: int = 100, window_minutes: int = 60) -> bool:
        """
        Check if identifier is within rate limit
        
        Args:
            identifier: Client identifier (IP, user ID, etc)
            limit: Maximum requests allowed
            window_minutes: Time window in minutes
            
        Returns:
            True if within limit, False if exceeded
        """
        from datetime import datetime, timedelta
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean up old entries first
        self._cleanup_rate_limit_entries(window_start)
        
        # Get or create rate limit data for identifier
        if identifier not in self._rate_limits:
            self._rate_limits[identifier] = []
        
        request_times = self._rate_limits[identifier]
        
        # Remove requests outside the current window
        request_times[:] = [req_time for req_time in request_times if req_time > window_start]
        
        # Check if limit exceeded
        if len(request_times) >= limit:
            security_logger.warning(
                f"Rate limit exceeded for {identifier}: {len(request_times)} requests in {window_minutes} minutes"
            )
            return False
        
        # Add current request
        request_times.append(now)
        return True
    
    def _cleanup_rate_limit_entries(self, cutoff_time) -> None:
        """Remove old rate limit entries"""
        for identifier, request_times in list(self._rate_limits.items()):
            # Remove old requests
            request_times[:] = [req_time for req_time in request_times if req_time > cutoff_time]
            
            # Remove empty entries
            if not request_times:
                del self._rate_limits[identifier]
    
    def get_rate_limit_info(self, identifier: str, window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get rate limit information for identifier
        
        Args:
            identifier: Client identifier
            window_minutes: Time window in minutes
            
        Returns:
            Dictionary with rate limit info
        """
        from datetime import datetime, timedelta
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        if identifier not in self._rate_limits:
            return {
                'requests_made': 0,
                'window_start': window_start.isoformat(),
                'window_end': now.isoformat()
            }
        
        request_times = self._rate_limits[identifier]
        recent_requests = [req_time for req_time in request_times if req_time > window_start]
        
        return {
            'requests_made': len(recent_requests),
            'window_start': window_start.isoformat(),
            'window_end': now.isoformat(),
            'oldest_request': recent_requests[0].isoformat() if recent_requests else None,
            'newest_request': recent_requests[-1].isoformat() if recent_requests else None
        }
    
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

def csrf_protect(require_token: bool = True):
    """
    CSRF protection decorator for form submissions and API calls
    
    Args:
        require_token: Whether to require CSRF token validation
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This is a placeholder for CSRF validation
            # In a real application, this would check the request for CSRF token
            # For now, it just logs the CSRF protection attempt
            security_logger.info(f"CSRF protection applied to {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(limit: int = 100, window_minutes: int = 60, identifier_func=None):
    """
    Rate limiting decorator
    
    Args:
        limit: Maximum requests allowed
        window_minutes: Time window in minutes
        identifier_func: Function to get identifier from request (defaults to generic identifier)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get identifier (in a real app, this would be from request context)
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = "default_client"  # Fallback identifier
            
            # Check rate limit
            if not security_middleware.check_rate_limit(identifier, limit, window_minutes):
                security_logger.warning(f"Rate limit exceeded for {identifier} in {func.__name__}")
                raise ValueError(f"Rate limit exceeded. Maximum {limit} requests per {window_minutes} minutes.")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_form_csrf(form_data: dict, session_id: str = None) -> bool:
    """
    Validate CSRF token from form data
    
    Args:
        form_data: Form data dictionary
        session_id: Optional session identifier
        
    Returns:
        True if CSRF token is valid
    """
    csrf_token = form_data.get('csrf_token')
    if not csrf_token:
        security_logger.warning("CSRF validation failed: No token in form data")
        return False
    
    return security_middleware.validate_csrf_token(csrf_token, session_id)

# Global instances
security_middleware = SecurityMiddleware(strict_mode=True)
security_middleware_dev = SecurityMiddleware(strict_mode=False)
input_validator = InputValidator()