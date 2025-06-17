#!/usr/bin/env python3
"""
Search Backend for Influencer News CMS
Provides database-powered search functionality via JSON API
"""

import json
import sys
import os
from typing import List, Dict, Any
from urllib.parse import parse_qs

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import DatabaseManager
from models import Article, Author, Category, TrendingTopic

class SearchBackend:
    """Handles search queries and returns JSON results"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def search_all(self, query: str, limit: int = 20, offset: int = 0, 
                   content_type: str = 'all', device_type: str = 'desktop') -> Dict[str, Any]:
        """Search across all content types with pagination"""
        results = {
            'query': query,
            'articles': [],
            'authors': [],
            'categories': [],
            'trending': [],
            'total_results': 0,
            'page': offset // limit + 1,
            'per_page': limit,
            'has_more': False
        }
        
        if not query or len(query.strip()) < 2:
            return results
        
        # Search articles with pagination
        if content_type in ['all', 'articles']:
            # Get total count for pagination
            total_articles = self.db.execute_one(
                "SELECT COUNT(*) as count FROM article_full_view WHERE title LIKE ? OR subtitle LIKE ? OR content LIKE ?",
                (f"%{query}%", f"%{query}%", f"%{query}%")
            )['count']
            
            # Get articles with LIMIT and OFFSET
            article_query = """
            SELECT * FROM article_full_view
            WHERE title LIKE ? OR subtitle LIKE ? OR content LIKE ?
            ORDER BY publication_date DESC
            LIMIT ? OFFSET ?
            """
            article_results = self.db.execute_query(
                article_query, 
                (f"%{query}%", f"%{query}%", f"%{query}%", limit, offset)
            )
            
            for article_data in article_results:
                article = Article.from_dict(article_data)
                results['articles'].append({
                    'id': article.id,
                    'title': article.title,
                    'subtitle': article.subtitle,
                    'author_name': article.author_name,
                    'category_name': article.category_name,
                    'category_icon': article.category_icon,
                    'publication_date': article.publication_date,
                    'url': f"integrated/articles/article_{article.id}.html",
                    'type': 'article'
                })
                
            results['total_articles'] = total_articles
        
        # Search authors
        author_query = f"""
        SELECT * FROM authors 
        WHERE name LIKE ? OR bio LIKE ? OR expertise LIKE ?
        LIMIT ?
        """
        search_pattern = f"%{query}%"
        author_results = self.db.execute_query(
            author_query, 
            (search_pattern, search_pattern, search_pattern, limit//4)
        )
        
        for author_data in author_results:
            author = Author.from_dict(author_data)
            results['authors'].append({
                'id': author.id,
                'name': author.name,
                'bio': author.bio,
                'expertise': author.expertise,
                'article_count': author.get_article_count(),
                'url': f"integrated/authors/author_{author.slug}.html",
                'type': 'author'
            })
        
        # Search categories
        category_query = f"""
        SELECT * FROM categories 
        WHERE name LIKE ? OR description LIKE ?
        LIMIT ?
        """
        category_results = self.db.execute_query(
            category_query, 
            (search_pattern, search_pattern, limit//4)
        )
        
        for category_data in category_results:
            category = Category.from_dict(category_data)
            results['categories'].append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'icon': category.icon,
                'article_count': category.article_count,
                'url': f"integrated/categories/category_{category.slug}.html",
                'type': 'category'
            })
        
        # Search trending topics
        trending_query = f"""
        SELECT * FROM trending_topics 
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY heat_score DESC
        LIMIT ?
        """
        trending_results = self.db.execute_query(
            trending_query, 
            (search_pattern, search_pattern, limit//4)
        )
        
        for trending_data in trending_results:
            trending = TrendingTopic.from_dict(trending_data)
            results['trending'].append({
                'id': trending.id,
                'title': trending.title,
                'description': trending.description,
                'icon': trending.icon,
                'heat_score': trending.heat_score,
                'article_count': trending.article_count,
                'url': f"integrated/trending/trend_{trending.slug}.html",
                'type': 'trending'
            })
        
        # Calculate total results
        results['total_results'] = (
            len(results['articles']) + 
            len(results['authors']) + 
            len(results['categories']) + 
            len(results['trending'])
        )
        
        return results
    
    def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Get search suggestions based on query"""
        if not query or len(query.strip()) < 2:
            return []
        
        suggestions = []
        search_pattern = f"%{query}%"
        
        # Get article title suggestions
        article_titles = self.db.execute_query(
            "SELECT title FROM articles WHERE title LIKE ? LIMIT ?",
            (search_pattern, limit)
        )
        suggestions.extend([row['title'] for row in article_titles])
        
        # Get author name suggestions
        author_names = self.db.execute_query(
            "SELECT name FROM authors WHERE name LIKE ? LIMIT ?",
            (search_pattern, limit)
        )
        suggestions.extend([row['name'] for row in author_names])
        
        # Get category suggestions
        categories = self.db.execute_query(
            "SELECT name FROM categories WHERE name LIKE ? LIMIT ?",
            (search_pattern, limit)
        )
        suggestions.extend([row['name'] for row in categories])
        
        # Remove duplicates and limit
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:limit]
    
    def search_mobile_optimized(self, query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Search optimized for mobile devices with smaller payloads"""
        results = {
            'query': query,
            'articles': [],
            'total_results': 0,
            'has_more': False
        }
        
        if not query or len(query.strip()) < 2:
            return results
        
        # Search articles using mobile view for optimized data
        article_query = """
        SELECT * FROM article_mobile_view 
        WHERE title LIKE ? OR excerpt LIKE ? 
        ORDER BY publication_date DESC 
        LIMIT ? OFFSET ?
        """
        search_pattern = f"%{query}%"
        article_results = self.db.execute_query(
            article_query, 
            (search_pattern, search_pattern, limit, offset)
        )
        
        for article_data in article_results:
            article = Article.from_dict(article_data)
            results['articles'].append(article.to_mobile_dict())
        
        # Get total count for pagination
        count_query = """
        SELECT COUNT(*) as total FROM article_mobile_view 
        WHERE title LIKE ? OR excerpt LIKE ?
        """
        count_result = self.db.execute_query(count_query, (search_pattern, search_pattern))
        total_count = count_result[0]['total'] if count_result else 0
        
        results['total_results'] = total_count
        results['has_more'] = (offset + limit) < total_count
        
        return results
    
    def get_mobile_suggestions(self, query: str, limit: int = 3) -> List[Dict[str, str]]:
        """Get mobile-optimized search suggestions"""
        if not query or len(query.strip()) < 2:
            return []
        
        suggestions = []
        search_pattern = f"%{query}%"
        
        # Get article suggestions with mobile titles
        article_query = """
        SELECT COALESCE(mobile_title, title) as title, slug 
        FROM articles 
        WHERE COALESCE(mobile_title, title) LIKE ? 
        LIMIT ?
        """
        article_results = self.db.execute_query(article_query, (search_pattern, limit))
        
        for row in article_results:
            suggestions.append({
                'text': row['title'],
                'type': 'article',
                'url': f"integrated/articles/article_{row['slug']}.html"
            })
        
        return suggestions[:limit]
    
    def detect_device_type(self, user_agent: str) -> str:
        """Detect device type from user agent string"""
        if not user_agent:
            return 'desktop'
        
        user_agent = user_agent.lower()
        
        # Mobile devices
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']
        if any(keyword in user_agent for keyword in mobile_keywords):
            return 'mobile'
        
        # Tablet devices
        tablet_keywords = ['tablet', 'ipad', 'kindle', 'playbook']
        if any(keyword in user_agent for keyword in tablet_keywords):
            return 'tablet'
        
        return 'desktop'

def handle_cgi_request():
    """Handle CGI-style request for search"""
    # Get query parameters
    query_string = os.environ.get('QUERY_STRING', '')
    params = parse_qs(query_string)
    
    search_query = params.get('q', [''])[0]
    action = params.get('action', ['search'])[0]
    limit = int(params.get('limit', ['20'])[0])
    offset = int(params.get('offset', ['0'])[0])
    content_type = params.get('type', ['all'])[0]
    
    search_backend = SearchBackend()
    
    # Set content type
    print("Content-Type: application/json")
    print()  # Empty line required for CGI
    
    try:
        if action == 'suggestions':
            results = search_backend.get_suggestions(search_query, limit)
            print(json.dumps({'suggestions': results}))
        else:
            results = search_backend.search_all(search_query, limit, offset, content_type)
            print(json.dumps(results))
    except Exception as e:
        error_response = {
            'error': str(e),
            'query': search_query,
            'total_results': 0
        }
        print(json.dumps(error_response))

def main():
    """Main entry point for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python search_backend.py <search_query>")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    search_backend = SearchBackend()
    results = search_backend.search_all(query)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    # Check if running as CGI
    if 'REQUEST_METHOD' in os.environ:
        handle_cgi_request()
    else:
        main()