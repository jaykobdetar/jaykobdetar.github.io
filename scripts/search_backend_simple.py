#!/usr/bin/env python3
"""
Simple Search Backend
Provides search functionality without complex model dependencies
Includes trusted input validation and sanitization
"""

import json
import sys
import os
from typing import List, Dict, Any

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

try:
    from utils.trusted_security import trusted_validator
    from utils.security_middleware import input_validator
    HAS_SECURITY = True
except ImportError:
    HAS_SECURITY = False
    print("WARNING: Security modules not available")

class SimpleSearchBackend:
    """Simple search backend using direct database queries"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def search_all(self, query: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search across all content types with input validation"""
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
        
        # Validate and sanitize input
        if HAS_SECURITY:
            try:
                # Validate search query
                query = input_validator.validate_search_query(query)
                
                # Validate pagination
                limit, offset = input_validator.validate_pagination_params(str(limit), str(offset))
                
                # Update results with validated values
                results['query'] = query
                results['page'] = offset // limit + 1
                results['per_page'] = limit
                
            except ValueError as e:
                # Return error in results
                results['error'] = str(e)
                return results
        
        if not query or len(query.strip()) < 2:
            return results
        
        search_pattern = f"%{query}%"
        
        # Search articles
        article_query = """
        SELECT 
            a.id, a.title, a.slug, a.excerpt, a.views, a.likes, 
            a.read_time_minutes, a.publish_date, a.image_url,
            au.name as author_name, au.slug as author_slug,
            c.name as category_name, c.slug as category_slug,
            c.color as category_color, c.icon as category_icon
        FROM articles a
        JOIN authors au ON a.author_id = au.id
        JOIN categories c ON a.category_id = c.id
        WHERE a.status = 'published' 
        AND (a.title LIKE ? OR a.excerpt LIKE ? OR a.content LIKE ?)
        ORDER BY a.publish_date DESC
        LIMIT ? OFFSET ?
        """
        
        article_results = self.db.execute_query(
            article_query, 
            (search_pattern, search_pattern, search_pattern, limit, offset)
        )
        
        for article_data in article_results:
            results['articles'].append({
                'id': article_data['id'],
                'title': article_data['title'],
                'excerpt': article_data['excerpt'] or 'No excerpt available',
                'author_name': article_data['author_name'],
                'category_name': article_data['category_name'],
                'category_icon': article_data['category_icon'],
                'publication_date': article_data['publish_date'],
                'url': f"integrated/articles/article_{article_data['id']}.html",
                'type': 'article',
                'views': article_data['views'] or 0
            })
        
        # Search authors
        author_query = """
        SELECT id, name, slug, bio, expertise, article_count
        FROM authors 
        WHERE name LIKE ? OR bio LIKE ? OR expertise LIKE ?
        LIMIT ?
        """
        author_results = self.db.execute_query(
            author_query, 
            (search_pattern, search_pattern, search_pattern, limit//4)
        )
        
        for author_data in author_results:
            results['authors'].append({
                'id': author_data['id'],
                'name': author_data['name'],
                'bio': author_data['bio'] or '',
                'expertise': author_data['expertise'] or '',
                'article_count': author_data['article_count'] or 0,
                'url': f"integrated/authors/author_{author_data['slug']}.html",
                'type': 'author'
            })
        
        # Search categories
        category_query = """
        SELECT id, name, slug, description, icon, article_count
        FROM categories 
        WHERE name LIKE ? OR description LIKE ?
        LIMIT ?
        """
        category_results = self.db.execute_query(
            category_query, 
            (search_pattern, search_pattern, limit//4)
        )
        
        for category_data in category_results:
            results['categories'].append({
                'id': category_data['id'],
                'name': category_data['name'],
                'description': category_data['description'] or '',
                'icon': category_data['icon'] or '📁',
                'article_count': category_data['article_count'] or 0,
                'url': f"integrated/categories/category_{category_data['slug']}.html",
                'type': 'category'
            })
        
        # Search trending topics
        trending_query = """
        SELECT id, title, slug, description, heat_score, article_count
        FROM trending_topics 
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY heat_score DESC
        LIMIT ?
        """
        trending_results = self.db.execute_query(
            trending_query, 
            (search_pattern, search_pattern, limit//4)
        )
        
        for trending_data in trending_results:
            results['trending'].append({
                'id': trending_data['id'],
                'title': trending_data['title'],
                'description': trending_data['description'] or '',
                'heat_score': trending_data['heat_score'] or 0,
                'article_count': trending_data['article_count'] or 0,
                'url': f"integrated/trending/trend_{trending_data['slug']}.html",
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
        """Get search suggestions"""
        if not query or len(query.strip()) < 2:
            return []
        
        suggestions = []
        search_pattern = f"%{query}%"
        
        # Get article title suggestions
        article_titles = self.db.execute_query(
            "SELECT title FROM articles WHERE title LIKE ? AND status = 'published' LIMIT ?",
            (search_pattern, limit)
        )
        suggestions.extend([row['title'] for row in article_titles])
        
        # Get author name suggestions
        author_names = self.db.execute_query(
            "SELECT name FROM authors WHERE name LIKE ? LIMIT ?",
            (search_pattern, limit)
        )
        suggestions.extend([row['name'] for row in author_names])
        
        # Remove duplicates and limit
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:limit]

def main():
    """Main entry point for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python search_backend_simple.py <search_query>")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    search_backend = SimpleSearchBackend()
    results = search_backend.search_all(query)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()