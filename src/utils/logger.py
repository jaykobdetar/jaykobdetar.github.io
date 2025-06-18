"""
Advanced Logging System for Influencer News CMS
Provides structured logging with different levels and secure error handling
"""

import os
import sys
import logging
import logging.handlers
import traceback
from typing import Any, Dict, Optional
from datetime import datetime
from .config import config

class SecureFormatter(logging.Formatter):
    """Custom formatter that sanitizes sensitive information from logs"""
    
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        # Patterns to redact from logs
        self.sensitive_patterns = [
            (r'password["\']?\s*[:=]\s*["\']?([^"\'\\s]+)', r'password=***'),
            (r'api_key["\']?\s*[:=]\s*["\']?([^"\'\\s]+)', r'api_key=***'),
            (r'token["\']?\s*[:=]\s*["\']?([^"\'\\s]+)', r'token=***'),
            (r'secret["\']?\s*[:=]\s*["\']?([^"\'\\s]+)', r'secret=***'),
            (r'email["\']?\s*[:=]\s*["\']?([^"\'\\s]+@[^"\'\\s]+)', r'email=***@***.***'),
        ]
    
    def format(self, record):
        """Format log record and sanitize sensitive information"""
        # Format the record
        formatted = super().format(record)
        
        # Sanitize sensitive information
        import re
        for pattern, replacement in self.sensitive_patterns:
            formatted = re.sub(pattern, replacement, formatted, flags=re.IGNORECASE)
        
        return formatted

class CMSLogger:
    """Central logging manager for the CMS"""
    
    def __init__(self):
        self.loggers = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = config.get_log_config()
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_config['filename'])
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_config['level']))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create secure formatter
        formatter = SecureFormatter(log_config['format'])
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_config['filename'],
            maxBytes=log_config['maxBytes'],
            backupCount=log_config['backupCount'],
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, log_config['level']))
        
        # Console handler (only for WARNING and above in production)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        if config.is_development_mode():
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.WARNING)
        
        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Prevent propagation to avoid duplicate logs
        root_logger.propagate = False
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def log_error(self, logger: logging.Logger, error: Exception, 
                  context: Optional[Dict[str, Any]] = None,
                  user_message: Optional[str] = None):
        """
        Log error with context and stack trace
        
        Args:
            logger: Logger instance
            error: Exception to log
            context: Additional context information
            user_message: User-friendly error message
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
        }
        
        if context:
            error_info['context'] = context
        
        if user_message:
            error_info['user_message'] = user_message
        
        # Log the error with stack trace in development
        if config.is_development_mode():
            logger.error(
                f"Error: {error_info['error_type']}: {error_info['error_message']}\n"
                f"Context: {context}\n"
                f"Stack trace:\n{traceback.format_exc()}"
            )
        else:
            # In production, log without full stack trace
            logger.error(
                f"Error: {error_info['error_type']}: {error_info['error_message']}"
                f"{' | Context: ' + str(context) if context else ''}"
            )
    
    def log_security_event(self, logger: logging.Logger, event_type: str, 
                          details: Dict[str, Any]):
        """
        Log security-related events
        
        Args:
            logger: Logger instance
            event_type: Type of security event
            details: Event details
        """
        security_info = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        logger.warning(f"SECURITY: {event_type} | {details}")
    
    def log_performance(self, logger: logging.Logger, operation: str, 
                       duration: float, details: Optional[Dict[str, Any]] = None):
        """
        Log performance metrics
        
        Args:
            logger: Logger instance
            operation: Operation name
            duration: Duration in seconds
            details: Additional performance details
        """
        perf_info = {
            'operation': operation,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            perf_info.update(details)
        
        if duration > 5.0:  # Log slow operations
            logger.warning(f"SLOW_OPERATION: {operation} took {duration:.2f}s | {details}")
        else:
            logger.info(f"PERFORMANCE: {operation} completed in {duration:.2f}s")

# Global logger manager
cms_logger = CMSLogger()

class CMSException(Exception):
    """Base exception class for CMS operations"""
    
    def __init__(self, message: str, error_code: str = None, 
                 user_message: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code or 'CMS_ERROR'
        self.user_message = user_message or "An error occurred. Please try again."
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()

class DatabaseException(CMSException):
    """Exception for database-related errors"""
    
    def __init__(self, message: str, query: str = None, **kwargs):
        super().__init__(message, error_code='DB_ERROR', **kwargs)
        if query:
            self.context['query'] = query

class ValidationException(CMSException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, error_code='VALIDATION_ERROR', **kwargs)
        if field:
            self.context['field'] = field

class SecurityException(CMSException):
    """Exception for security-related errors"""
    
    def __init__(self, message: str, threat_type: str = None, **kwargs):
        super().__init__(message, error_code='SECURITY_ERROR', **kwargs)
        if threat_type:
            self.context['threat_type'] = threat_type

class FileSystemException(CMSException):
    """Exception for file system errors"""
    
    def __init__(self, message: str, file_path: str = None, **kwargs):
        super().__init__(message, error_code='FILESYSTEM_ERROR', **kwargs)
        if file_path:
            self.context['file_path'] = file_path

class ContentException(CMSException):
    """Exception for content processing errors"""
    
    def __init__(self, message: str, content_type: str = None, **kwargs):
        super().__init__(message, error_code='CONTENT_ERROR', **kwargs)
        if content_type:
            self.context['content_type'] = content_type

def handle_exception(logger: logging.Logger, exc: Exception, 
                    operation: str = None) -> CMSException:
    """
    Handle and convert exceptions to CMS exceptions
    
    Args:
        logger: Logger instance
        exc: Original exception
        operation: Operation that caused the exception
        
    Returns:
        CMSException with appropriate type and context
    """
    context = {'operation': operation} if operation else {}
    
    # Convert common exceptions to CMS exceptions
    if isinstance(exc, FileNotFoundError):
        cms_exc = FileSystemException(
            f"File not found: {exc}",
            user_message="The requested file could not be found.",
            context=context
        )
    elif isinstance(exc, PermissionError):
        cms_exc = FileSystemException(
            f"Permission denied: {exc}",
            user_message="Permission denied. Please check file permissions.",
            context=context
        )
    elif isinstance(exc, OSError):
        cms_exc = FileSystemException(
            f"File system error: {exc}",
            user_message="A file system error occurred.",
            context=context
        )
    elif 'sqlite' in str(type(exc)).lower():
        cms_exc = DatabaseException(
            f"Database error: {exc}",
            user_message="A database error occurred. Please try again.",
            context=context
        )
    elif isinstance(exc, ValueError):
        cms_exc = ValidationException(
            f"Validation error: {exc}",
            user_message="Invalid input provided.",
            context=context
        )
    elif isinstance(exc, CMSException):
        # Already a CMS exception
        cms_exc = exc
    else:
        # Generic exception
        cms_exc = CMSException(
            f"Unexpected error: {exc}",
            error_code='UNKNOWN_ERROR',
            user_message="An unexpected error occurred. Please try again.",
            context=context
        )
    
    # Log the exception
    cms_logger.log_error(logger, cms_exc, cms_exc.context, cms_exc.user_message)
    
    return cms_exc

def log_function_call(logger: logging.Logger):
    """Decorator to log function calls and performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            func_name = f"{func.__module__}.{func.__name__}"
            
            logger.debug(f"CALL: {func_name} started")
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                cms_logger.log_performance(logger, func_name, duration)
                logger.debug(f"CALL: {func_name} completed successfully")
                
                return result
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                cms_exc = handle_exception(logger, e, func_name)
                
                logger.debug(f"CALL: {func_name} failed after {duration:.2f}s")
                raise cms_exc
        
        return wrapper
    return decorator

# Convenience functions for getting loggers
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return cms_logger.get_logger(name)

def log_error(logger: logging.Logger, error: Exception, **kwargs):
    """Log an error"""
    cms_logger.log_error(logger, error, **kwargs)

def log_security_event(logger: logging.Logger, event_type: str, details: Dict[str, Any]):
    """Log a security event"""
    cms_logger.log_security_event(logger, event_type, details)

def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs):
    """Log performance metrics"""
    cms_logger.log_performance(logger, operation, duration, **kwargs)