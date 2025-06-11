#!/usr/bin/env python3
"""
Mobile Backend Integration Script
=================================
Integrates mobile API endpoints with the existing search backend
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Try to import the existing search backend
    from search_backend import search_mobile_optimized, detect_device_type
    SEARCH_BACKEND_AVAILABLE = True
except ImportError:
    SEARCH_BACKEND_AVAILABLE = False


class MobileBackendIntegrator:
    """Integrates mobile API with the existing backend systems"""
    
    def __init__(self):
        self.api_dir = Path("api") / "mobile"
        self.search_index = None
        self.load_search_index()
        
    def load_search_index(self):
        """Load the mobile search index"""
        try:
            search_file = self.api_dir / "search.json"
            if search_file.exists():
                with open(search_file, 'r', encoding='utf-8') as f:
                    search_data = json.load(f)
                    if search_data.get('success'):
                        self.search_index = search_data['data']
                        print(f"✅ Loaded search index with {len(self.search_index.get('articles', []))} articles")
                    else:
                        print("⚠️ Search index data format error")
            else:
                print("❌ Search index not found - run mobile_api_generator.py first")
        except Exception as e:
            print(f"❌ Error loading search index: {str(e)}")
    
    def search_mobile_content(self, query: str, content_type: str = 'all', limit: int = 10) -> Dict[str, Any]:
        """Search mobile content using the generated index"""
        if not self.search_index:
            return {
                'success': False,
                'error': 'Search index not available',
                'data': [],
                'meta': {'total': 0}
            }
        
        query_lower = query.lower().strip()
        if not query_lower:
            return {
                'success': False,
                'error': 'Empty search query',
                'data': [],
                'meta': {'total': 0}
            }
        
        results = {
            'articles': [],
            'authors': [],
            'categories': [],
            'trending': []
        }
        
        # Search each content type
        search_types = [content_type] if content_type != 'all' else ['articles', 'authors', 'categories', 'trending']
        
        for search_type in search_types:
            if search_type in self.search_index:
                items = self.search_index[search_type]
                for item in items:
                    if query_lower in item.get('search_text', '').lower():
                        results[search_type].append(item)
        
        # Flatten results if searching all types
        if content_type == 'all':
            all_results = []
            for result_type, items in results.items():
                for item in items[:limit]:
                    item['result_type'] = result_type
                    all_results.append(item)
            
            # Sort by relevance (simple scoring based on query matches)
            all_results.sort(key=lambda x: self.calculate_relevance_score(x, query_lower), reverse=True)
            final_results = all_results[:limit]
        else:
            final_results = results.get(content_type, [])[:limit]
        
        return {
            'success': True,
            'data': final_results,
            'meta': {
                'total': len(final_results),
                'query': query,
                'content_type': content_type,
                'generated_at': datetime.datetime.now().isoformat()
            }
        }
    
    def calculate_relevance_score(self, item: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for search result"""
        score = 0.0
        search_text = item.get('search_text', '').lower()
        
        # Exact phrase match gets highest score
        if query in search_text:
            score += 100
        
        # Word matches
        query_words = query.split()
        for word in query_words:
            if word in search_text:
                score += 10
        
        # Title/name matches get bonus
        title_fields = ['title', 'name', 'topic']
        for field in title_fields:
            if field in item and query in item[field].lower():
                score += 50
        
        return score
    
    def get_mobile_article(self, article_id: int) -> Dict[str, Any]:
        """Get mobile-optimized article by ID"""
        try:
            article_file = self.api_dir / "articles" / f"{article_id}.json"
            if article_file.exists():
                with open(article_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    'success': False,
                    'error': f'Article {article_id} not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error loading article: {str(e)}'
            }
    
    def get_mobile_author(self, author_slug: str) -> Dict[str, Any]:
        """Get mobile-optimized author by slug"""
        try:
            author_file = self.api_dir / "authors" / f"{author_slug}.json"
            if author_file.exists():
                with open(author_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    'success': False,
                    'error': f'Author {author_slug} not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error loading author: {str(e)}'
            }
    
    def get_mobile_category(self, category_slug: str) -> Dict[str, Any]:
        """Get mobile-optimized category by slug"""
        try:
            category_file = self.api_dir / "categories" / f"{category_slug}.json"
            if category_file.exists():
                with open(category_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    'success': False,
                    'error': f'Category {category_slug} not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error loading category: {str(e)}'
            }
    
    def get_mobile_trending(self, trending_slug: str) -> Dict[str, Any]:
        """Get mobile-optimized trending topic by slug"""
        try:
            trending_file = self.api_dir / "trending" / f"{trending_slug}.json"
            if trending_file.exists():
                with open(trending_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    'success': False,
                    'error': f'Trending topic {trending_slug} not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error loading trending topic: {str(e)}'
            }
    
    def get_mobile_suggestions(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Get mobile search suggestions"""
        if not self.search_index or not query.strip():
            return {
                'success': True,
                'data': [],
                'meta': {'total': 0}
            }
        
        query_lower = query.lower().strip()
        suggestions = []
        
        # Get suggestions from all content types
        for content_type, items in self.search_index.items():
            for item in items:
                # Check title/name fields for suggestions
                title_fields = ['title', 'name', 'topic']
                for field in title_fields:
                    if field in item:
                        field_value = item[field].lower()
                        if query_lower in field_value and len(field_value) > len(query_lower):
                            suggestions.append({
                                'text': item[field],
                                'type': content_type,
                                'slug': item.get('slug', ''),
                                'id': item.get('id', '')
                            })
        
        # Remove duplicates and sort
        unique_suggestions = []
        seen_texts = set()
        for suggestion in suggestions:
            if suggestion['text'] not in seen_texts:
                unique_suggestions.append(suggestion)
                seen_texts.add(suggestion['text'])
        
        # Sort by length (shorter suggestions first) and limit
        unique_suggestions.sort(key=lambda x: len(x['text']))
        final_suggestions = unique_suggestions[:limit]
        
        return {
            'success': True,
            'data': final_suggestions,
            'meta': {
                'total': len(final_suggestions),
                'query': query
            }
        }
    
    def detect_mobile_device(self, user_agent: str) -> Dict[str, Any]:
        """Detect if request is from mobile device"""
        mobile_indicators = [
            'mobile', 'android', 'iphone', 'ipad', 'blackberry', 
            'windows phone', 'opera mini', 'iemobile'
        ]
        
        user_agent_lower = user_agent.lower()
        is_mobile = any(indicator in user_agent_lower for indicator in mobile_indicators)
        
        device_type = 'mobile' if is_mobile else 'desktop'
        
        # More specific device detection
        if 'ipad' in user_agent_lower:
            device_type = 'tablet'
        elif 'android' in user_agent_lower and 'mobile' not in user_agent_lower:
            device_type = 'tablet'
        
        return {
            'is_mobile': is_mobile,
            'device_type': device_type,
            'user_agent': user_agent
        }
    
    def get_mobile_stats(self) -> Dict[str, Any]:
        """Get mobile backend integration statistics"""
        stats = {
            'search_index_available': self.search_index is not None,
            'search_backend_available': SEARCH_BACKEND_AVAILABLE,
            'api_directory': str(self.api_dir),
            'api_directory_exists': self.api_dir.exists()
        }
        
        if self.search_index:
            stats.update({
                'total_articles': len(self.search_index.get('articles', [])),
                'total_authors': len(self.search_index.get('authors', [])),
                'total_categories': len(self.search_index.get('categories', [])),
                'total_trending': len(self.search_index.get('trending', []))
            })
        
        # Count API files
        if self.api_dir.exists():
            api_files = list(self.api_dir.rglob("*.json"))
            stats['total_api_files'] = len(api_files)
        
        return stats
    
    def create_mobile_search_wrapper(self):
        """Create a wrapper script that integrates mobile search with the existing backend"""
        wrapper_content = '''#!/usr/bin/env python3
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
'''
        
        wrapper_file = Path("mobile_search_wrapper.py")
        with open(wrapper_file, 'w', encoding='utf-8') as f:
            f.write(wrapper_content)
        
        print(f"✅ Created mobile search wrapper: {wrapper_file}")
        return str(wrapper_file)


def main():
    """Main function for testing mobile backend integration"""
    print("🚀 Mobile Backend Integration for Influencer News")
    print("=" * 50)
    
    try:
        # Initialize mobile backend integrator
        integrator = MobileBackendIntegrator()
        
        # Show stats
        stats = integrator.get_mobile_stats()
        print("📊 Mobile Backend Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test search functionality
        print("\n🔍 Testing Mobile Search...")
        
        # Test search
        search_results = integrator.search_mobile_content("MrBeast", "all", 5)
        print(f"Search results for 'MrBeast': {search_results['meta']['total']} found")
        
        # Test suggestions
        suggestions = integrator.get_mobile_suggestions("Creator", 3)
        print(f"Suggestions for 'Creator': {suggestions['meta']['total']} found")
        
        # Test device detection
        mobile_device = integrator.detect_mobile_device("Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)")
        print(f"Device detection: {mobile_device}")
        
        # Create mobile search wrapper
        print("\n📝 Creating Mobile Search Wrapper...")
        wrapper_file = integrator.create_mobile_search_wrapper()
        
        print(f"\n✅ Mobile Backend Integration Complete!")
        print(f"🎯 Use {wrapper_file} for mobile search functionality")
        print("🔗 Mobile API endpoints are ready for frontend integration")
        
        return 0
        
    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())