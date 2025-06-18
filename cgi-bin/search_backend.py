#!/usr/bin/env python3
"""
CGI Script for Search Backend
Provides search functionality via CGI interface
"""

import cgi
import cgitb
import json
import sys
import os

# Enable CGI error reporting
cgitb.enable()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

try:
    from utils.trusted_security import trusted_validator
    from utils.security_middleware import input_validator
    HAS_SECURITY = True
except ImportError:
    HAS_SECURITY = False

def send_json_response(data):
    """Send JSON response with proper headers"""
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *")
    print("")  # Empty line required between headers and body
    print(json.dumps(data, indent=2))

def main():
    """Main CGI handler"""
    # Get form data
    form = cgi.FieldStorage()
    
    # Extract parameters
    query = form.getvalue('q', '')
    limit = int(form.getvalue('limit', '20'))
    offset = int(form.getvalue('offset', '0'))
    
    # Validate input
    if HAS_SECURITY:
        try:
            query = input_validator.validate_search_query(query)
            limit, offset = input_validator.validate_pagination_params(str(limit), str(offset))
        except ValueError as e:
            send_json_response({
                'error': str(e),
                'query': query,
                'articles': [],
                'authors': [],
                'categories': [],
                'trending': [],
                'total_results': 0
            })
            return
    
    # Initialize response
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
        send_json_response(results)
        return
    
    # Perform search
    db = DatabaseManager()
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
    
    article_results = db.execute_query(
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
            'url': f"integrated/articles/article_{article_data['slug']}.html",
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
    author_results = db.execute_query(
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
    
    # Calculate total results
    results['total_results'] = (
        len(results['articles']) + 
        len(results['authors'])
    )
    
    # Send response
    send_json_response(results)

if __name__ == '__main__':
    main()