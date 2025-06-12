#!/usr/bin/env python3
"""
Mobile API Generator Script
===========================
Standalone script to generate mobile-optimized API endpoints
"""

import os
import sys
import json
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from database.db_manager import DatabaseManager
except ImportError:
    # Fallback to direct SQLite
    class DatabaseManager:
        def __init__(self):
            self.db_path = "data/infnews.db"
            
        def get_connection(self):
            return sqlite3.connect(self.db_path)
        
        def execute_one(self, query, params=None):
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params or [])
                result = cursor.fetchone()
                return dict(result) if result else None


@dataclass
class MobileResponse:
    """Standard mobile API response format"""
    success: bool
    data: Any = None
    error: str = None
    meta: Dict[str, Any] = None
    mobile_optimized: bool = True


class MobileAPIGenerator:
    """Generate mobile-optimized API endpoints"""
    
    def __init__(self):
        self.db = DatabaseManager()
        
        # Mobile-specific configuration
        self.mobile_config = {
            'max_excerpt_length': 120,
            'max_title_length': 60,
            'image_sizes': {
                'mobile': {'width': 320, 'height': 180},
                'tablet': {'width': 768, 'height': 432},
                'desktop': {'width': 1200, 'height': 675}
            },
            'cache_duration': 300,  # 5 minutes
            'pagination_limit': 20
        }
        
        # Create API endpoints directory
        self.api_dir = Path("api") / "mobile"
        self.api_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 API directory created: {self.api_dir}")
    
    def generate_all_endpoints(self) -> Dict[str, int]:
        """Generate all mobile-optimized API endpoints"""
        print("🚀 Starting mobile API generation...")
        
        stats = {
            'articles': 0,
            'authors': 0,
            'categories': 0,
            'trending': 0,
            'search': 0
        }
        
        try:
            # Generate article endpoints
            print("📰 Creating mobile article endpoints...")
            stats['articles'] = self.create_article_endpoints()
            
            # Generate author endpoints
            print("👥 Creating mobile author endpoints...")
            stats['authors'] = self.create_author_endpoints()
            
            # Generate category endpoints
            print("📂 Creating mobile category endpoints...")
            stats['categories'] = self.create_category_endpoints()
            
            # Generate trending endpoints
            print("🔥 Creating mobile trending endpoints...")
            stats['trending'] = self.create_trending_endpoints()
            
            # Generate search endpoints
            print("🔍 Creating mobile search endpoints...")
            stats['search'] = self.create_search_endpoints()
            
            # Create mobile manifest
            print("📋 Creating mobile API manifest...")
            self.create_api_manifest(stats)
            
            print("✅ Mobile API endpoints generated successfully!")
            
        except Exception as e:
            print(f"❌ Error generating mobile endpoints: {str(e)}")
            raise
        
        return stats
    
    def create_article_endpoints(self) -> int:
        """Create mobile-optimized article API endpoints"""
        try:
            # Get all articles from database
            with self.db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT a.*, 
                           auth.name as author_name, auth.slug as author_slug,
                           cat.name as category_name, cat.slug as category_slug
                    FROM articles a
                    LEFT JOIN authors auth ON a.author_id = auth.id
                    LEFT JOIN categories cat ON a.category_id = cat.id
                    ORDER BY a.publish_date DESC
                    LIMIT 1000
                """)
                
                articles_data = [dict(row) for row in cursor.fetchall()]
            
            if not articles_data:
                print("⚠️ No articles found in database")
                return 0
            
            # Create articles list endpoint
            mobile_articles = []
            for article_data in articles_data:
                mobile_article = self.optimize_article_for_mobile(article_data)
                mobile_articles.append(mobile_article)
            
            # Save articles list endpoint
            articles_response = MobileResponse(
                success=True,
                data=mobile_articles,
                meta={
                    'total': len(mobile_articles),
                    'generated_at': datetime.datetime.now().isoformat(),
                    'cache_duration': self.mobile_config['cache_duration']
                }
            )
            
            articles_file = self.api_dir / "articles.json"
            with open(articles_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(articles_response), f, indent=2, ensure_ascii=False)
            
            # Create individual article endpoints
            articles_detail_dir = self.api_dir / "articles"
            articles_detail_dir.mkdir(exist_ok=True)
            
            for article_data in articles_data:
                mobile_article = self.optimize_article_for_mobile(article_data, include_full_content=True)
                
                article_response = MobileResponse(
                    success=True,
                    data=mobile_article,
                    meta={
                        'generated_at': datetime.datetime.now().isoformat(),
                        'cache_duration': self.mobile_config['cache_duration']
                    }
                )
                
                article_file = articles_detail_dir / f"{article_data['id']}.json"
                with open(article_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(article_response), f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Created {len(articles_data)} article endpoints")
            return len(articles_data)
            
        except Exception as e:
            print(f"   ❌ Error creating article endpoints: {str(e)}")
            return 0
    
    def create_author_endpoints(self) -> int:
        """Create mobile-optimized author API endpoints"""
        try:
            # Get all authors from database
            with self.db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM authors ORDER BY name")
                authors_data = [dict(row) for row in cursor.fetchall()]
            
            if not authors_data:
                print("   ⚠️ No authors found in database")
                return 0
            
            # Create authors list endpoint
            mobile_authors = []
            for author_data in authors_data:
                mobile_author = self.optimize_author_for_mobile(author_data)
                mobile_authors.append(mobile_author)
            
            # Save authors list endpoint
            authors_response = MobileResponse(
                success=True,
                data=mobile_authors,
                meta={
                    'total': len(mobile_authors),
                    'generated_at': datetime.datetime.now().isoformat(),
                    'cache_duration': self.mobile_config['cache_duration']
                }
            )
            
            authors_file = self.api_dir / "authors.json"
            with open(authors_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(authors_response), f, indent=2, ensure_ascii=False)
            
            # Create individual author endpoints
            authors_detail_dir = self.api_dir / "authors"
            authors_detail_dir.mkdir(exist_ok=True)
            
            for author_data in authors_data:
                mobile_author = self.optimize_author_for_mobile(author_data, include_articles=True)
                
                author_response = MobileResponse(
                    success=True,
                    data=mobile_author,
                    meta={
                        'generated_at': datetime.datetime.now().isoformat(),
                        'cache_duration': self.mobile_config['cache_duration']
                    }
                )
                
                author_file = authors_detail_dir / f"{author_data['slug']}.json"
                with open(author_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(author_response), f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Created {len(authors_data)} author endpoints")
            return len(authors_data)
            
        except Exception as e:
            print(f"   ❌ Error creating author endpoints: {str(e)}")
            return 0
    
    def create_category_endpoints(self) -> int:
        """Create mobile-optimized category API endpoints"""
        try:
            # Get all categories from database
            with self.db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM categories ORDER BY name")
                categories_data = [dict(row) for row in cursor.fetchall()]
            
            if not categories_data:
                print("   ⚠️ No categories found in database")
                return 0
            
            # Create categories list endpoint
            mobile_categories = []
            for category_data in categories_data:
                mobile_category = self.optimize_category_for_mobile(category_data)
                mobile_categories.append(mobile_category)
            
            # Save categories list endpoint
            categories_response = MobileResponse(
                success=True,
                data=mobile_categories,
                meta={
                    'total': len(mobile_categories),
                    'generated_at': datetime.datetime.now().isoformat(),
                    'cache_duration': self.mobile_config['cache_duration']
                }
            )
            
            categories_file = self.api_dir / "categories.json"
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(categories_response), f, indent=2, ensure_ascii=False)
            
            # Create individual category endpoints
            categories_detail_dir = self.api_dir / "categories"
            categories_detail_dir.mkdir(exist_ok=True)
            
            for category_data in categories_data:
                mobile_category = self.optimize_category_for_mobile(category_data, include_articles=True)
                
                category_response = MobileResponse(
                    success=True,
                    data=mobile_category,
                    meta={
                        'generated_at': datetime.datetime.now().isoformat(),
                        'cache_duration': self.mobile_config['cache_duration']
                    }
                )
                
                category_file = categories_detail_dir / f"{category_data['slug']}.json"
                with open(category_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(category_response), f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Created {len(categories_data)} category endpoints")
            return len(categories_data)
            
        except Exception as e:
            print(f"   ❌ Error creating category endpoints: {str(e)}")
            return 0
    
    def create_trending_endpoints(self) -> int:
        """Create mobile-optimized trending API endpoints"""
        try:
            # Get all trending topics from database
            with self.db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM trending_topics ORDER BY created_at DESC")
                trending_data = [dict(row) for row in cursor.fetchall()]
            
            if not trending_data:
                print("   ⚠️ No trending topics found in database")
                return 0
            
            # Create trending list endpoint
            mobile_trending = []
            for topic_data in trending_data:
                mobile_topic = self.optimize_trending_for_mobile(topic_data)
                mobile_trending.append(mobile_topic)
            
            # Save trending list endpoint
            trending_response = MobileResponse(
                success=True,
                data=mobile_trending,
                meta={
                    'total': len(mobile_trending),
                    'generated_at': datetime.datetime.now().isoformat(),
                    'cache_duration': self.mobile_config['cache_duration']
                }
            )
            
            trending_file = self.api_dir / "trending.json"
            with open(trending_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(trending_response), f, indent=2, ensure_ascii=False)
            
            # Create individual trending endpoints
            trending_detail_dir = self.api_dir / "trending"
            trending_detail_dir.mkdir(exist_ok=True)
            
            for topic_data in trending_data:
                mobile_topic = self.optimize_trending_for_mobile(topic_data, include_details=True)
                
                topic_response = MobileResponse(
                    success=True,
                    data=mobile_topic,
                    meta={
                        'generated_at': datetime.datetime.now().isoformat(),
                        'cache_duration': self.mobile_config['cache_duration']
                    }
                )
                
                topic_file = trending_detail_dir / f"{topic_data['slug']}.json"
                with open(topic_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(topic_response), f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Created {len(trending_data)} trending endpoints")
            return len(trending_data)
            
        except Exception as e:
            print(f"   ❌ Error creating trending endpoints: {str(e)}")
            return 0
    
    def create_search_endpoints(self) -> int:
        """Create mobile-optimized search API endpoints"""
        try:
            # Create search index for mobile
            search_index = {
                'articles': [],
                'authors': [],
                'categories': [],
                'trending': []
            }
            
            # Index articles
            with self.db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                
                # Articles
                cursor = conn.execute("""
                    SELECT a.id, a.title, a.excerpt, a.slug, a.publish_date,
                           auth.name as author_name, cat.name as category_name
                    FROM articles a
                    LEFT JOIN authors auth ON a.author_id = auth.id
                    LEFT JOIN categories cat ON a.category_id = cat.id
                    ORDER BY a.publish_date DESC
                    LIMIT 1000
                """)
                
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    search_index['articles'].append({
                        'id': row_dict['id'],
                        'title': self.truncate_text(row_dict['title'] or '', self.mobile_config['max_title_length']),
                        'excerpt': self.truncate_text(row_dict['excerpt'] or '', self.mobile_config['max_excerpt_length']),
                        'author': row_dict['author_name'] or '',
                        'category': row_dict['category_name'] or '',
                        'date': row_dict['publish_date'],
                        'slug': row_dict['slug'],
                        'search_text': f"{row_dict['title']} {row_dict['excerpt'] or ''} {row_dict['author_name'] or ''} {row_dict['category_name'] or ''}".lower()
                    })
                
                # Authors
                cursor = conn.execute("SELECT * FROM authors")
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    search_index['authors'].append({
                        'slug': row_dict['slug'],
                        'name': row_dict['name'],
                        'title': row_dict.get('title', ''),
                        'bio': self.truncate_text(row_dict.get('bio', ''), self.mobile_config['max_excerpt_length']),
                        'search_text': f"{row_dict['name']} {row_dict.get('title', '')} {row_dict.get('bio', '')}".lower()
                    })
                
                # Categories
                cursor = conn.execute("SELECT * FROM categories")
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    search_index['categories'].append({
                        'slug': row_dict['slug'],
                        'name': row_dict['name'],
                        'description': self.truncate_text(row_dict.get('description', ''), self.mobile_config['max_excerpt_length']),
                        'search_text': f"{row_dict['name']} {row_dict.get('description', '')}".lower()
                    })
                
                # Trending topics
                cursor = conn.execute("SELECT * FROM trending_topics")
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    topic_field = row_dict.get('topic') or row_dict.get('title', '')
                    search_index['trending'].append({
                        'slug': row_dict['slug'],
                        'topic': topic_field,
                        'description': self.truncate_text(row_dict.get('description', ''), self.mobile_config['max_excerpt_length']),
                        'search_text': f"{topic_field} {row_dict.get('description', '')}".lower()
                    })
            
            # Save search index
            search_response = MobileResponse(
                success=True,
                data=search_index,
                meta={
                    'total_articles': len(search_index['articles']),
                    'total_authors': len(search_index['authors']),
                    'total_categories': len(search_index['categories']),
                    'total_trending': len(search_index['trending']),
                    'generated_at': datetime.datetime.now().isoformat(),
                    'cache_duration': self.mobile_config['cache_duration']
                }
            )
            
            search_file = self.api_dir / "search.json"
            with open(search_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(search_response), f, indent=2, ensure_ascii=False)
            
            total_indexed = sum(len(search_index[key]) for key in search_index)
            print(f"   ✅ Created search index with {total_indexed} items")
            return 1  # One search endpoint created
            
        except Exception as e:
            print(f"   ❌ Error creating search endpoints: {str(e)}")
            return 0
    
    def create_api_manifest(self, stats: Dict[str, int]):
        """Create API manifest with endpoint information"""
        try:
            manifest = {
                'version': '1.0',
                'generated_at': datetime.datetime.now().isoformat(),
                'mobile_optimized': True,
                'cache_duration': self.mobile_config['cache_duration'],
                'endpoints': {
                    'articles': {
                        'list': '/api/mobile/articles.json',
                        'detail': '/api/mobile/articles/{id}.json',
                        'count': stats['articles']
                    },
                    'authors': {
                        'list': '/api/mobile/authors.json',
                        'detail': '/api/mobile/authors/{slug}.json',
                        'count': stats['authors']
                    },
                    'categories': {
                        'list': '/api/mobile/categories.json',
                        'detail': '/api/mobile/categories/{slug}.json',
                        'count': stats['categories']
                    },
                    'trending': {
                        'list': '/api/mobile/trending.json',
                        'detail': '/api/mobile/trending/{slug}.json',
                        'count': stats['trending']
                    },
                    'search': {
                        'index': '/api/mobile/search.json',
                        'count': stats['search']
                    }
                },
                'mobile_config': self.mobile_config
            }
            
            manifest_file = self.api_dir / "manifest.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Created API manifest: {manifest_file}")
                
        except Exception as e:
            print(f"   ❌ Error creating API manifest: {str(e)}")
    
    def optimize_article_for_mobile(self, article_data: Dict[str, Any], include_full_content: bool = False) -> Dict[str, Any]:
        """Optimize article data for mobile consumption"""
        try:
            mobile_title = article_data.get('mobile_title') or article_data.get('title', '')
            mobile_excerpt = article_data.get('mobile_excerpt') or article_data.get('excerpt', '')
            
            mobile_article = {
                'id': article_data['id'],
                'title': self.truncate_text(mobile_title, self.mobile_config['max_title_length']),
                'slug': article_data.get('slug', ''),
                'excerpt': self.truncate_text(mobile_excerpt, self.mobile_config['max_excerpt_length']),
                'author': {
                    'name': article_data.get('author_name') or 'Unknown',
                    'slug': article_data.get('author_slug') or ''
                },
                'category': {
                    'name': article_data.get('category_name') or 'Uncategorized',
                    'slug': article_data.get('category_slug') or ''
                },
                'publication_date': article_data.get('publish_date'),
                'read_time': article_data.get('read_time') or 5,
                'views': article_data.get('view_count') or 0,
                'mobile_optimized': True
            }
            
            # Add mobile image information
            mobile_hero_image_id = article_data.get('mobile_hero_image_id')
            if mobile_hero_image_id:
                mobile_article['image'] = {
                    'mobile': f'/assets/images/responsive/img_{mobile_hero_image_id}_mobile_320x180.webp',
                    'tablet': f'/assets/images/responsive/img_{mobile_hero_image_id}_tablet_768x432.webp',
                    'desktop': f'/assets/images/responsive/img_{mobile_hero_image_id}_desktop_1200x675.webp',
                    'fallback': f'/assets/images/responsive/img_{mobile_hero_image_id}_mobile_320x180.jpeg'
                }
            else:
                mobile_article['image'] = {
                    'mobile': '/assets/placeholders/article_placeholder.svg',
                    'tablet': '/assets/placeholders/article_placeholder.svg',
                    'desktop': '/assets/placeholders/article_placeholder.svg',
                    'fallback': '/assets/placeholders/article_placeholder.svg'
                }
            
            # Include full content if requested
            if include_full_content:
                mobile_article['content'] = article_data.get('content', '')
                mobile_article['full_title'] = article_data.get('title', '')
                mobile_article['full_excerpt'] = article_data.get('excerpt', '')
            
            return mobile_article
            
        except Exception as e:
            print(f"   ⚠️ Error optimizing article {article_data.get('id', 'unknown')}: {str(e)}")
            return {}
    
    def optimize_author_for_mobile(self, author_data: Dict[str, Any], include_articles: bool = False) -> Dict[str, Any]:
        """Optimize author data for mobile consumption"""
        try:
            mobile_author = {
                'slug': author_data.get('slug', ''),
                'name': author_data.get('name', ''),
                'title': author_data.get('title', ''),
                'bio': self.truncate_text(author_data.get('bio', ''), self.mobile_config['max_excerpt_length']),
                'expertise': self.safe_json_parse(author_data.get('expertise', ''), []),
                'mobile_optimized': True
            }
            
            # Add mobile image information
            mobile_author['image'] = {
                'mobile': '/assets/placeholders/author_placeholder.svg',
                'tablet': '/assets/placeholders/author_placeholder.svg',
                'desktop': '/assets/placeholders/author_placeholder.svg'
            }
            
            # Include articles if requested
            if include_articles:
                try:
                    with self.db.get_connection() as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.execute("""
                            SELECT a.*, auth.name as author_name, cat.name as category_name
                            FROM articles a
                            LEFT JOIN authors auth ON a.author_id = auth.id
                            LEFT JOIN categories cat ON a.category_id = cat.id
                            WHERE auth.slug = ?
                            ORDER BY a.publish_date DESC
                            LIMIT 10
                        """, (author_data['slug'],))
                        
                        articles_data = [dict(row) for row in cursor.fetchall()]
                        mobile_author['recent_articles'] = [
                            self.optimize_article_for_mobile(article_data) 
                            for article_data in articles_data
                        ]
                        mobile_author['article_count'] = len(articles_data)
                except Exception as e:
                    mobile_author['recent_articles'] = []
                    mobile_author['article_count'] = 0
            
            return mobile_author
            
        except Exception as e:
            print(f"   ⚠️ Error optimizing author {author_data.get('slug', 'unknown')}: {str(e)}")
            return {}
    
    def optimize_category_for_mobile(self, category_data: Dict[str, Any], include_articles: bool = False) -> Dict[str, Any]:
        """Optimize category data for mobile consumption"""
        try:
            mobile_category = {
                'slug': category_data.get('slug', ''),
                'name': category_data.get('name', ''),
                'description': self.truncate_text(category_data.get('description', ''), self.mobile_config['max_excerpt_length']),
                'mobile_optimized': True
            }
            
            # Include articles if requested
            if include_articles:
                try:
                    with self.db.get_connection() as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.execute("""
                            SELECT a.*, auth.name as author_name, cat.name as category_name
                            FROM articles a
                            LEFT JOIN authors auth ON a.author_id = auth.id
                            LEFT JOIN categories cat ON a.category_id = cat.id
                            WHERE cat.slug = ?
                            ORDER BY a.publish_date DESC
                            LIMIT 10
                        """, (category_data['slug'],))
                        
                        articles_data = [dict(row) for row in cursor.fetchall()]
                        mobile_category['recent_articles'] = [
                            self.optimize_article_for_mobile(article_data) 
                            for article_data in articles_data
                        ]
                        mobile_category['article_count'] = len(articles_data)
                except Exception as e:
                    mobile_category['recent_articles'] = []
                    mobile_category['article_count'] = 0
            
            return mobile_category
            
        except Exception as e:
            print(f"   ⚠️ Error optimizing category {category_data.get('slug', 'unknown')}: {str(e)}")
            return {}
    
    def optimize_trending_for_mobile(self, topic_data: Dict[str, Any], include_details: bool = False) -> Dict[str, Any]:
        """Optimize trending topic data for mobile consumption"""
        try:
            topic_field = topic_data.get('topic') or topic_data.get('title', '')
            mobile_topic = {
                'slug': topic_data.get('slug', ''),
                'topic': topic_field,
                'description': self.truncate_text(topic_data.get('description', ''), self.mobile_config['max_excerpt_length']),
                'engagement_score': topic_data.get('engagement_score', 0),
                'mobile_optimized': True
            }
            
            # Include details if requested
            if include_details:
                mobile_topic['full_description'] = topic_data.get('description', '')
                mobile_topic['keywords'] = self.safe_json_parse(topic_data.get('keywords', ''), [])
                mobile_topic['related_articles'] = []  # Could be populated with related articles
            
            return mobile_topic
            
        except Exception as e:
            print(f"   ⚠️ Error optimizing trending topic {topic_data.get('slug', 'unknown')}: {str(e)}")
            return {}
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length with ellipsis"""
        if not text:
            return ''
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3].rstrip() + '...'
    
    def safe_json_parse(self, json_str: str, default: Any = None) -> Any:
        """Safely parse JSON string with fallback"""
        if not json_str or json_str.strip() == '':
            return default
        
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default
    
    def get_stats(self) -> Dict[str, Any]:
        """Get mobile API generation statistics"""
        stats = {}
        
        try:
            # Count API files
            api_files = list(self.api_dir.rglob("*.json"))
            stats['total_api_files'] = len(api_files)
            
            # Get content counts from database
            with self.db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("SELECT COUNT(*) as count FROM articles")
                stats['articles'] = cursor.fetchone()['count']
                
                cursor = conn.execute("SELECT COUNT(*) as count FROM authors")
                stats['authors'] = cursor.fetchone()['count']
                
                cursor = conn.execute("SELECT COUNT(*) as count FROM categories")
                stats['categories'] = cursor.fetchone()['count']
                
                cursor = conn.execute("SELECT COUNT(*) as count FROM trending_topics")
                stats['trending'] = cursor.fetchone()['count']
                
                # Check mobile-ready articles
                cursor = conn.execute("""
                    SELECT COUNT(*) as count FROM articles 
                    WHERE mobile_title IS NOT NULL OR mobile_excerpt IS NOT NULL
                """)
                stats['mobile_ready_articles'] = cursor.fetchone()['count']
            
            stats['last_generated'] = datetime.datetime.now().isoformat()
            stats['api_directory'] = str(self.api_dir)
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats


def main():
    """Main function for generating mobile API endpoints"""
    print("🚀 Mobile API Generator for Influencer News")
    print("=" * 50)
    
    try:
        # Initialize mobile API generator
        generator = MobileAPIGenerator()
        
        # Generate all endpoints
        stats = generator.generate_all_endpoints()
        
        print("\n" + "=" * 50)
        print("✅ Mobile API Generation Complete!")
        print(f"📱 Articles: {stats['articles']} endpoints")
        print(f"👥 Authors: {stats['authors']} endpoints")
        print(f"📂 Categories: {stats['categories']} endpoints")
        print(f"🔥 Trending: {stats['trending']} endpoints")
        print(f"🔍 Search: {stats['search']} endpoints")
        
        # Show additional stats
        mobile_stats = generator.get_stats()
        print(f"\n📊 Mobile API Stats:")
        for key, value in mobile_stats.items():
            if key != 'error':
                print(f"   {key}: {value}")
        
        # Show API directory structure
        print(f"\n📁 API Files Generated:")
        for api_file in sorted(generator.api_dir.rglob("*.json")):
            relative_path = api_file.relative_to(generator.api_dir.parent)
            print(f"   {relative_path}")
        
        print(f"\n🎯 Mobile API endpoints are now available at: /{generator.api_dir}")
        print("   These can be used by the mobile app and progressive web app!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())