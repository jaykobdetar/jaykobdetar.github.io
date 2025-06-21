#!/usr/bin/env python3
"""
PWA API Server for Influencer News
Provides all necessary API endpoints for Progressive Web App functionality
"""

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_manager import DatabaseManager
from src.models.article import Article
from src.models.author import Author
from src.models.category import Category
from src.models.trending import TrendingTopic

class PWAAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for PWA API endpoints"""
    
    def __init__(self, *args, **kwargs):
        self.db = DatabaseManager()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Route requests to appropriate handlers
            if path == '/api/search':
                self.handle_search(query_params)
            elif path == '/api/articles':
                self.handle_articles(query_params)
            elif path.startswith('/api/articles/'):
                article_id = path.split('/')[-1]
                self.handle_article_detail(article_id)
            elif path == '/api/authors':
                self.handle_authors(query_params)
            elif path.startswith('/api/authors/'):
                author_slug = path.split('/')[-1]
                self.handle_author_detail(author_slug)
            elif path == '/api/categories':
                self.handle_categories(query_params)
            elif path.startswith('/api/categories/'):
                category_slug = path.split('/')[-1]
                self.handle_category_detail(category_slug)
            elif path == '/api/trending':
                self.handle_trending(query_params)
            elif path == '/api/analytics':
                self.handle_analytics_get()
            elif path == '/api/manifest':
                self.handle_manifest()
            elif path == '/api/health':
                self.handle_health()
            else:
                self.send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            if path == '/api/analytics':
                self.handle_analytics_post()
            else:
                self.send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_search(self, query_params):
        """Handle search API requests"""
        query = query_params.get('q', [''])[0]
        limit = int(query_params.get('limit', [20])[0])
        offset = int(query_params.get('offset', [0])[0])
        
        # Import search backend
        search_script_dir = os.path.dirname(__file__)
        if search_script_dir not in sys.path:
            sys.path.insert(0, search_script_dir)
        from search_backend import SearchBackend
        
        search_backend = SearchBackend()
        results = search_backend.search_all(query, limit, offset)
        
        self.send_json_response(results)
    
    def handle_articles(self, query_params):
        """Handle articles list API"""
        limit = int(query_params.get('limit', [20])[0])
        offset = int(query_params.get('offset', [0])[0])
        category = query_params.get('category', [None])[0]
        
        # Build query
        query = """
            SELECT 
                a.id, a.title, a.slug, a.excerpt, a.views, a.likes,
                a.read_time_minutes, a.publish_date, a.image_url,
                au.name as author_name, au.slug as author_slug,
                c.name as category_name, c.slug as category_slug,
                c.color as category_color, c.icon as category_icon
            FROM articles a
            JOIN authors au ON a.author_id = au.id
            JOIN categories c ON a.category_id = c.id
        """
        
        params = []
        if category:
            query += " AND c.slug = ?"
            params.append(category)
        
        query += " ORDER BY a.publish_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        articles = self.db.execute_query(query, params)
        
        # Format articles for API
        formatted_articles = []
        for article in articles:
            formatted_articles.append({
                'id': article['id'],
                'title': article['title'],
                'slug': article['slug'],
                'excerpt': article['excerpt'] or 'No excerpt available',
                'author_name': article['author_name'],
                'author_slug': article['author_slug'],
                'category_name': article['category_name'],
                'category_slug': article['category_slug'],
                'category_color': article['category_color'],
                'category_icon': article['category_icon'],
                'publish_date': article['publish_date'],
                'views': article['views'] or 0,
                'likes': article['likes'] or 0,
                'read_time_minutes': article['read_time_minutes'],
                'image_url': article['image_url'] or 'assets/images/default-article.jpg',
                'url': f"integrated/articles/article_{article['slug']}.html"
            })
        
        response = {
            'success': True,
            'articles': formatted_articles,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': len(formatted_articles),
                'has_more': len(formatted_articles) == limit
            },
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def handle_article_detail(self, article_id):
        """Handle individual article detail API"""
        try:
            article_id = int(article_id)
            article = Article.find_by_id(article_id)
            
            if not article:
                self.send_error_response(404, "Article not found")
                return
            
            # Get full article data with content
            query = """
                SELECT 
                    a.*, 
                    au.name as author_name, au.slug as author_slug, au.bio as author_bio,
                    c.name as category_name, c.slug as category_slug, c.description as category_description
                FROM articles a
                JOIN authors au ON a.author_id = au.id
                JOIN categories c ON a.category_id = c.id
                WHERE a.id = ?             """
            
            article_data = self.db.execute_one(query, (article_id,))
            
            if not article_data:
                self.send_error_response(404, "Article not found")
                return
            
            response = {
                'success': True,
                'article': {
                    'id': article_data['id'],
                    'title': article_data['title'],
                    'slug': article_data['slug'],
                    'content': article_data['content'],
                    'excerpt': article_data['excerpt'],
                    'author': {
                        'name': article_data['author_name'],
                        'slug': article_data['author_slug'],
                        'bio': article_data['author_bio']
                    },
                    'category': {
                        'name': article_data['category_name'],
                        'slug': article_data['category_slug'],
                        'description': article_data['category_description']
                    },
                    'publish_date': article_data['publish_date'],
                    'views': article_data['views'] or 0,
                    'likes': article_data['likes'] or 0,
                    'read_time': article_data['read_time_minutes'],
                    'image_url': article_data['image_url'] or 'assets/images/default-article.jpg'
                },
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except ValueError:
            self.send_error_response(400, "Invalid article ID")
    
    def handle_authors(self, query_params):
        """Handle authors list API"""
        limit = int(query_params.get('limit', [20])[0])
        offset = int(query_params.get('offset', [0])[0])
        
        authors = Author.find_all(limit=limit + offset)[offset:]
        
        formatted_authors = []
        for author in authors:
            formatted_authors.append({
                'slug': author.slug,
                'name': author.name,
                'title': author.title or '',
                'bio': author.bio or '',
                'expertise': author.expertise or [],
                'article_count': author.article_count or 0,
                'url': f"integrated/authors/author_{author.slug}.html"
            })
        
        response = {
            'success': True,
            'authors': formatted_authors,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': len(formatted_authors)
            },
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def handle_author_detail(self, author_slug):
        """Handle individual author detail API"""
        author = Author.find_by_slug(author_slug)
        
        if not author:
            self.send_error_response(404, "Author not found")
            return
        
        # Get author's recent articles
        query = """
            SELECT id, title, slug, excerpt, publish_date, views, likes, read_time_minutes
            FROM articles 
            WHERE author_id = ?
            ORDER BY publish_date DESC 
            LIMIT 10
        """
        recent_articles = self.db.execute_query(query, (author.id,))
        
        response = {
            'success': True,
            'author': {
                'slug': author.slug,
                'name': author.name,
                'title': author.title or '',
                'bio': author.bio or '',
                'expertise': author.expertise or [],
                'article_count': author.article_count or 0,
                'recent_articles': recent_articles
            },
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def handle_categories(self, query_params):
        """Handle categories list API"""
        categories = Category.find_all()
        
        formatted_categories = []
        for category in categories:
            formatted_categories.append({
                'slug': category.slug,
                'name': category.name,
                'description': category.description or '',
                'icon': category.icon or '📁',
                'color': category.color or '#6B7280',
                'article_count': category.article_count or 0,
                'url': f"integrated/categories/category_{category.slug}.html"
            })
        
        response = {
            'success': True,
            'categories': formatted_categories,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def handle_category_detail(self, category_slug):
        """Handle individual category detail API"""
        category = Category.find_by_slug(category_slug)
        
        if not category:
            self.send_error_response(404, "Category not found")
            return
        
        # Get category's recent articles
        query = """
            SELECT a.id, a.title, a.slug, a.excerpt, a.publish_date, a.views, a.likes, a.read_time_minutes,
                   au.name as author_name, au.slug as author_slug
            FROM articles a
            JOIN authors au ON a.author_id = au.id
            WHERE a.category_id = ?             ORDER BY a.publish_date DESC 
            LIMIT 20
        """
        recent_articles = self.db.execute_query(query, (category.id,))
        
        response = {
            'success': True,
            'category': {
                'slug': category.slug,
                'name': category.name,
                'description': category.description or '',
                'icon': category.icon or '📁',
                'color': category.color or '#6B7280',
                'article_count': category.article_count or 0,
                'recent_articles': recent_articles
            },
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def handle_trending(self, query_params):
        """Handle trending topics API"""
        limit = int(query_params.get('limit', [10])[0])
        
        trending_topics = TrendingTopic.find_all(limit=limit)
        
        formatted_topics = []
        for topic in trending_topics:
            formatted_topics.append({
                'slug': topic.slug,
                'title': topic.title,
                'description': topic.description or '',
                'heat_score': topic.heat_score or 0,
                'article_count': topic.article_count or 0,
                'url': f"integrated/trending/trend_{topic.slug}.html"
            })
        
        response = {
            'success': True,
            'trending': formatted_topics,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def handle_analytics_get(self):
        """Handle analytics GET requests - Privacy-focused no-op version"""
        try:
            # Return empty analytics data - no data collection
            response = {
                'success': True,
                'data': {
                    'total_events': 0,
                    'recent_events': [],
                    'message': 'No analytics data collected (privacy-focused)'
                },
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error_response(500, f"Analytics error: {str(e)}")
    
    def handle_analytics_post(self):
        """Handle analytics POST requests - Privacy-focused no-op version"""
        try:
            # Read posted data for CSRF validation
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = {}
            if content_length > 0:
                raw_data = self.rfile.read(content_length)
                try:
                    post_data = json.loads(raw_data.decode('utf-8'))
                except:
                    pass  # Invalid JSON, continue with no-op
            
            # Basic CSRF check if token provided
            csrf_token = post_data.get('csrf_token')
            if csrf_token:
                # Validate CSRF token - import here to avoid circular imports
                try:
                    from src.utils.security_middleware import security_middleware
                    if not security_middleware.validate_csrf_token(csrf_token, 'analytics_session'):
                        self.send_error_response(403, "CSRF validation failed")
                        return
                except ImportError:
                    pass  # Security middleware not available
            
            # Return success response without storing any data
            response = {
                'success': True,
                'message': 'Request acknowledged (no data stored - privacy focused)',
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error_response(500, f"Analytics error: {str(e)}")
    
    def handle_manifest(self):
        """Handle API manifest requests"""
        manifest = {
            'name': 'Influencer News API',
            'version': '2.0',
            'description': 'Progressive Web App API for Influencer News',
            'endpoints': {
                'search': '/api/search?q={query}&limit={limit}&offset={offset}',
                'articles': '/api/articles?limit={limit}&offset={offset}&category={category}',
                'article_detail': '/api/articles/{id}',
                'authors': '/api/authors?limit={limit}&offset={offset}',
                'author_detail': '/api/authors/{slug}',
                'categories': '/api/categories',
                'category_detail': '/api/categories/{slug}',
                'trending': '/api/trending?limit={limit}',
                'analytics': '/api/analytics'
            },
            'generated_at': datetime.datetime.now().isoformat()
        }
        
        self.send_json_response(manifest)
    
    def handle_health(self):
        """Handle health check requests"""
        try:
            # Test database connection
            test_query = self.db.execute_one("SELECT 1 as test")
            
            response = {
                'status': 'healthy',
                'database': 'connected' if test_query else 'disconnected',
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error_response(503, f"Health check failed: {str(e)}")
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_error_response(self, code, message):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_data = {
            'success': False,
            'error': message,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        json_data = json.dumps(error_data, indent=2)
        self.wfile.write(json_data.encode('utf-8'))

def main():
    """Main function to start the PWA API server"""
    port = int(os.environ.get('PORT', 8080))
    
    server = HTTPServer(('localhost', port), PWAAPIHandler)
    
    print(f"PWA API Server starting on http://localhost:{port}")
    print("Available endpoints:")
    print("  GET  /api/search?q={query}")
    print("  GET  /api/articles")
    print("  GET  /api/articles/{id}")
    print("  GET  /api/authors")
    print("  GET  /api/authors/{slug}")
    print("  GET  /api/categories")
    print("  GET  /api/categories/{slug}")
    print("  GET  /api/trending")
    print("  GET  /api/analytics")
    print("  POST /api/analytics")
    print("  GET  /api/manifest")
    print("  GET  /api/health")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down PWA API server...")
        server.server_close()

if __name__ == "__main__":
    main()