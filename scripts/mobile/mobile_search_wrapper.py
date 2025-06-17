#!/usr/bin/env python3
"""
Mobile Search Wrapper
=====================
Wrapper that provides mobile-optimized search functionality
"""

import sys
import os
import json
from typing import Dict, Any, Optional

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mobile_backend_integration import MobileBackendIntegrator
    mobile_backend = MobileBackendIntegrator()
    MOBILE_BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Mobile backend not available: {e}")
    MOBILE_BACKEND_AVAILABLE = False
    mobile_backend = None

def mobile_search(query: str, content_type: str = 'all', limit: int = 10, user_agent: str = '') -> Dict[str, Any]:
    """Perform mobile-optimized search"""
    if not MOBILE_BACKEND_AVAILABLE or not mobile_backend:
        return {
            'success': False,
            'error': 'Mobile backend not available',
            'data': [],
            'meta': {'total': 0}
        }
    
    # Detect device type
    device_info = mobile_backend.detect_mobile_device(user_agent)
    
    # Perform search
    search_results = mobile_backend.search_mobile_content(query, content_type, limit)
    
    # Add device info to meta
    if search_results.get('meta'):
        search_results['meta']['device_info'] = device_info
    
    return search_results

def get_mobile_suggestions(query: str, limit: int = 5) -> Dict[str, Any]:
    """Get mobile search suggestions"""
    if not MOBILE_BACKEND_AVAILABLE or not mobile_backend:
        return {
            'success': False,
            'error': 'Mobile backend not available',
            'data': []
        }
    
    return mobile_backend.get_mobile_suggestions(query, limit)

def get_mobile_content(content_type: str, identifier: str) -> Dict[str, Any]:
    """Get mobile-optimized content by type and identifier"""
    if not MOBILE_BACKEND_AVAILABLE or not mobile_backend:
        return {
            'success': False,
            'error': 'Mobile backend not available'
        }
    
    if content_type == 'article':
        try:
            article_id = int(identifier)
            return mobile_backend.get_mobile_article(article_id)
        except ValueError:
            return {'success': False, 'error': 'Invalid article ID'}
    elif content_type == 'author':
        return mobile_backend.get_mobile_author(identifier)
    elif content_type == 'category':
        return mobile_backend.get_mobile_category(identifier)
    elif content_type == 'trending':
        return mobile_backend.get_mobile_trending(identifier)
    else:
        return {'success': False, 'error': f'Unknown content type: {content_type}'}

if __name__ == "__main__":
    # Command line interface for testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Mobile Search Interface')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--type', type=str, default='all', help='Content type (all, articles, authors, categories, trending)')
    parser.add_argument('--limit', type=int, default=10, help='Result limit')
    parser.add_argument('--suggestions', type=str, help='Get suggestions for query')
    parser.add_argument('--content', nargs=2, metavar=('TYPE', 'ID'), help='Get content by type and ID/slug')
    
    args = parser.parse_args()
    
    if args.search:
        results = mobile_search(args.search, args.type, args.limit)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif args.suggestions:
        suggestions = get_mobile_suggestions(args.suggestions)
        print(json.dumps(suggestions, indent=2, ensure_ascii=False))
    elif args.content:
        content_type, identifier = args.content
        content = get_mobile_content(content_type, identifier)
        print(json.dumps(content, indent=2, ensure_ascii=False))
    else:
        print("Mobile Search Interface")
        print("Usage examples:")
        print("  python mobile_search_wrapper.py --search 'MrBeast'")
        print("  python mobile_search_wrapper.py --suggestions 'Creator'")
        print("  python mobile_search_wrapper.py --content article 10")
        print("  python mobile_search_wrapper.py --content author alex-rivera")
