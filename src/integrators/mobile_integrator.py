#!/usr/bin/env python3
"""
Mobile-Specific Content Integrator
==================================
Extends base integrators with mobile-optimized content generation and API endpoints
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .base_integrator import BaseIntegrator
from .article_integrator import ArticleIntegrator
from .author_integrator import AuthorIntegrator
from .category_integrator import CategoryIntegrator
from .trending_integrator import TrendingIntegrator
from models.article import Article
from models.author import Author
from models.category import Category
from models.trending import TrendingTopic
from database.db_manager import DatabaseManager


@dataclass
class MobileResponse:
    """Standard mobile API response format"""
    success: bool
    data: Any = None
    error: str = None
    meta: Dict[str, Any] = None
    mobile_optimized: bool = True


class MobileIntegrator(BaseIntegrator):
    """Mobile-specific content integrator with optimized output"""
    
    def __init__(self):
        super().__init__('mobile', 'mobile')
        
        # Initialize component integrators
        self.article_integrator = ArticleIntegrator()
        self.author_integrator = AuthorIntegrator()
        self.category_integrator = CategoryIntegrator()
        self.trending_integrator = TrendingIntegrator()
        
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
        
        # Create mobile API endpoints directory
        self.api_dir = Path("api") / "mobile"
        self.api_dir.mkdir(parents=True, exist_ok=True)
        
    def parse_content_file(self, file_path: Path) -> Dict[str, Any]:
        """Not implemented - mobile integrator doesn't parse files directly"""
        raise NotImplementedError("Mobile integrator doesn't parse content files")
    
    def create_content_page(self, content: Any):
        """Not implemented - mobile integrator creates API endpoints instead"""
        pass
    
    def update_listing_page(self, content_list: List[Any]):
        """Not implemented - mobile integrator creates API endpoints instead"""
        pass
    
    def create_sample_file(self):
        """Not implemented - mobile integrator doesn't create sample files"""
        pass
    
    def generate_mobile_api_endpoints(self) -> Dict[str, int]:
        """Generate all mobile-optimized API endpoints"""
        self.update_progress("Generating mobile API endpoints...", 0)
        
        stats = {
            'articles': 0,
            'authors': 0,
            'categories': 0,
            'trending': 0,
            'search': 0
        }
        
        try:
            # Generate article endpoints
            self.update_progress("Creating mobile article endpoints...", 20)
            stats['articles'] = self.create_mobile_article_endpoints()
            
            # Generate author endpoints
            self.update_progress("Creating mobile author endpoints...", 40)
            stats['authors'] = self.create_mobile_author_endpoints()
            
            # Generate category endpoints
            self.update_progress("Creating mobile category endpoints...", 60)
            stats['categories'] = self.create_mobile_category_endpoints()
            
            # Generate trending endpoints
            self.update_progress("Creating mobile trending endpoints...", 80)
            stats['trending'] = self.create_mobile_trending_endpoints()
            
            # Generate search endpoints
            self.update_progress("Creating mobile search endpoints...", 90)
            stats['search'] = self.create_mobile_search_endpoints()
            
            # Create mobile manifest
            self.update_progress("Creating mobile API manifest...", 95)
            self.create_mobile_api_manifest(stats)
            
            self.update_progress("Mobile API endpoints generated successfully!", 100)
            
        except Exception as e:
            self.update_progress(f"Error generating mobile endpoints: {str(e)}", 100)
            raise
        
        return stats
    
    def create_mobile_article_endpoints(self) -> int:
        """Create mobile-optimized article API endpoints"""
        try:
            # Get all articles from database
            articles = Article.find_all(limit=1000)
            
            if not articles:
                return 0
            
            # Create articles list endpoint
            mobile_articles = []
            for article in articles:
                mobile_article = self.optimize_article_for_mobile(article)
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
            
            for article in articles:
                mobile_article = self.optimize_article_for_mobile(article, include_full_content=True)
                
                article_response = MobileResponse(
                    success=True,
                    data=mobile_article,
                    meta={
                        'generated_at': datetime.datetime.now().isoformat(),
                        'cache_duration': self.mobile_config['cache_duration']
                    }
                )
                
                article_file = articles_detail_dir / f"{article.id}.json"
                with open(article_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(article_response), f, indent=2, ensure_ascii=False)
            
            return len(articles)
            
        except Exception as e:
            self.update_progress(f"Error creating article endpoints: {str(e)}")
            return 0
    
    def create_mobile_author_endpoints(self) -> int:
        """Create mobile-optimized author API endpoints"""
        try:
            # Get all authors from database
            authors = Author.find_all(limit=1000)
            
            if not authors:
                return 0
            
            # Create authors list endpoint
            mobile_authors = []
            for author in authors:
                mobile_author = self.optimize_author_for_mobile(author)
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
            
            for author in authors:
                mobile_author = self.optimize_author_for_mobile(author, include_articles=True)
                
                author_response = MobileResponse(
                    success=True,
                    data=mobile_author,
                    meta={
                        'generated_at': datetime.datetime.now().isoformat(),
                        'cache_duration': self.mobile_config['cache_duration']
                    }
                )
                
                author_file = authors_detail_dir / f"{author.slug}.json"
                with open(author_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(author_response), f, indent=2, ensure_ascii=False)
            
            return len(authors)
            
        except Exception as e:
            self.update_progress(f"Error creating author endpoints: {str(e)}")
            return 0
    
    def create_mobile_category_endpoints(self) -> int:
        """Create mobile-optimized category API endpoints"""
        try:
            # Get all categories from database
            categories = Category.find_all(limit=1000)
            
            if not categories:
                return 0
            
            # Create categories list endpoint
            mobile_categories = []
            for category in categories:
                mobile_category = self.optimize_category_for_mobile(category)
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
            
            for category in categories:
                mobile_category = self.optimize_category_for_mobile(category, include_articles=True)
                
                category_response = MobileResponse(
                    success=True,
                    data=mobile_category,
                    meta={
                        'generated_at': datetime.datetime.now().isoformat(),
                        'cache_duration': self.mobile_config['cache_duration']
                    }
                )
                
                category_file = categories_detail_dir / f"{category.slug}.json"
                with open(category_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(category_response), f, indent=2, ensure_ascii=False)
            
            return len(categories)
            
        except Exception as e:
            self.update_progress(f"Error creating category endpoints: {str(e)}")
            return 0
    
    def create_mobile_trending_endpoints(self) -> int:
        """Create mobile-optimized trending API endpoints"""
        try:
            # Get all trending topics from database
            trending_topics = TrendingTopic.find_all(limit=1000)
            
            if not trending_topics:
                return 0
            
            # Create trending list endpoint
            mobile_trending = []
            for topic in trending_topics:
                mobile_topic = self.optimize_trending_for_mobile(topic)
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
            
            for topic in trending_topics:
                mobile_topic = self.optimize_trending_for_mobile(topic, include_details=True)
                
                topic_response = MobileResponse(
                    success=True,
                    data=mobile_topic,
                    meta={
                        'generated_at': datetime.datetime.now().isoformat(),
                        'cache_duration': self.mobile_config['cache_duration']
                    }
                )
                
                topic_file = trending_detail_dir / f"{topic.slug}.json"
                with open(topic_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(topic_response), f, indent=2, ensure_ascii=False)
            
            return len(trending_topics)
            
        except Exception as e:
            self.update_progress(f"Error creating trending endpoints: {str(e)}")
            return 0
    
    def create_mobile_search_endpoints(self) -> int:
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
            articles = Article.find_all(limit=1000)
            for article in articles:
                # Use consistent field names from database
                excerpt_text = getattr(article, 'excerpt', None) or getattr(article, 'subtitle', '') or ''
                publish_date = getattr(article, 'publish_date', None) or getattr(article, 'publication_date', None)
                
                # Handle date formatting properly
                date_str = None
                if publish_date:
                    if hasattr(publish_date, 'isoformat'):
                        date_str = publish_date.isoformat()
                    else:
                        date_str = str(publish_date)  # Already a string
                
                search_index['articles'].append({
                    'id': article.id,
                    'title': self.truncate_text(article.title, self.mobile_config['max_title_length']),
                    'excerpt': self.truncate_text(excerpt_text, self.mobile_config['max_excerpt_length']),
                    'author': getattr(article, 'author_name', ''),
                    'category': getattr(article, 'category_name', ''),
                    'date': date_str,
                    'slug': article.slug,
                    'read_time': getattr(article, 'read_time_minutes', None) or getattr(article, 'read_time', None),
                    'views': getattr(article, 'views', 0) or getattr(article, 'view_count', 0),
                    'search_text': f"{article.title} {excerpt_text} {getattr(article, 'author_name', '')} {getattr(article, 'category_name', '')}".lower()
                })
            
            # Index authors
            authors = Author.find_all(limit=1000)
            for author in authors:
                search_index['authors'].append({
                    'slug': author.slug,
                    'name': author.name,
                    'title': author.title or '',
                    'bio': self.truncate_text(author.bio or '', self.mobile_config['max_excerpt_length']),
                    'search_text': f"{author.name} {author.title or ''} {author.bio or ''}".lower()
                })
            
            # Index categories
            categories = Category.find_all(limit=1000)
            for category in categories:
                search_index['categories'].append({
                    'slug': category.slug,
                    'name': category.name,
                    'description': self.truncate_text(category.description or '', self.mobile_config['max_excerpt_length']),
                    'search_text': f"{category.name} {category.description or ''}".lower()
                })
            
            # Index trending topics
            trending_topics = TrendingTopic.find_all(limit=1000)
            for topic in trending_topics:
                search_index['trending'].append({
                    'slug': topic.slug,
                    'topic': topic.topic,
                    'description': self.truncate_text(topic.description or '', self.mobile_config['max_excerpt_length']),
                    'search_text': f"{topic.topic} {topic.description or ''}".lower()
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
            
            return 1  # One search endpoint created
            
        except Exception as e:
            self.update_progress(f"Error creating search endpoints: {str(e)}")
            return 0
    
    def create_mobile_api_manifest(self, stats: Dict[str, int]):
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
                
        except Exception as e:
            self.update_progress(f"Error creating API manifest: {str(e)}")
    
    def optimize_article_for_mobile(self, article: Article, include_full_content: bool = False) -> Dict[str, Any]:
        """Optimize article data for mobile consumption"""
        try:
            mobile_article = {
                'id': article.id,
                'title': self.truncate_text(article.get_mobile_title(), self.mobile_config['max_title_length']),
                'slug': article.slug,
                'excerpt': self.truncate_text(article.get_mobile_excerpt(), self.mobile_config['max_excerpt_length']),
                'author': {
                    'name': article.author_name or 'Unknown',
                    'slug': article.author_slug or ''
                },
                'category': {
                    'name': article.category_name or 'Uncategorized',
                    'slug': article.category_slug or ''
                },
                'publication_date': article.publication_date.isoformat() if article.publication_date else None,
                'read_time': article.read_time or 5,
                'views': getattr(article, 'views', 0),
                'mobile_optimized': True
            }
            
            # Add mobile image information
            if hasattr(article, 'mobile_hero_image_id') and article.mobile_hero_image_id:
                mobile_article['image'] = {
                    'mobile': f'/assets/images/responsive/img_{article.mobile_hero_image_id}_mobile_320x180.webp',
                    'tablet': f'/assets/images/responsive/img_{article.mobile_hero_image_id}_tablet_768x432.webp',
                    'desktop': f'/assets/images/responsive/img_{article.mobile_hero_image_id}_desktop_1200x675.webp',
                    'fallback': f'/assets/images/responsive/img_{article.mobile_hero_image_id}_mobile_320x180.jpeg'
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
                mobile_article['content'] = article.content or ''
                mobile_article['full_title'] = article.title
                mobile_article['full_excerpt'] = article.subtitle or ''
            
            return mobile_article
            
        except Exception as e:
            self.update_progress(f"Error optimizing article {article.id}: {str(e)}")
            return {}
    
    def optimize_author_for_mobile(self, author: Author, include_articles: bool = False) -> Dict[str, Any]:
        """Optimize author data for mobile consumption"""
        try:
            mobile_author = {
                'slug': author.slug,
                'name': author.name,
                'title': author.title or '',
                'bio': self.truncate_text(author.bio or '', self.mobile_config['max_excerpt_length']),
                'expertise': author.expertise or [],
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
                # Get author's recent articles
                # Use existing method with proper filtering
                all_articles = Article.find_all(limit=100)
                author_articles = [a for a in all_articles if getattr(a, 'author_id', None) == author.id][:10]
                mobile_author['recent_articles'] = [
                    self.optimize_article_for_mobile(article) 
                    for article in author_articles
                ]
                mobile_author['article_count'] = len(author_articles)
            
            return mobile_author
            
        except Exception as e:
            self.update_progress(f"Error optimizing author {author.slug}: {str(e)}")
            return {}
    
    def optimize_category_for_mobile(self, category: Category, include_articles: bool = False) -> Dict[str, Any]:
        """Optimize category data for mobile consumption"""
        try:
            mobile_category = {
                'slug': category.slug,
                'name': category.name,
                'description': self.truncate_text(category.description or '', self.mobile_config['max_excerpt_length']),
                'mobile_optimized': True
            }
            
            # Include articles if requested
            if include_articles:
                # Get category's recent articles
                # Use existing method with proper filtering
                all_articles = Article.find_all(limit=100)
                category_articles = [a for a in all_articles if getattr(a, 'category_id', None) == category.id][:10]
                mobile_category['recent_articles'] = [
                    self.optimize_article_for_mobile(article) 
                    for article in category_articles
                ]
                mobile_category['article_count'] = len(category_articles)
            
            return mobile_category
            
        except Exception as e:
            self.update_progress(f"Error optimizing category {category.slug}: {str(e)}")
            return {}
    
    def optimize_trending_for_mobile(self, topic: TrendingTopic, include_details: bool = False) -> Dict[str, Any]:
        """Optimize trending topic data for mobile consumption"""
        try:
            mobile_topic = {
                'slug': topic.slug,
                'topic': topic.topic,
                'description': self.truncate_text(topic.description or '', self.mobile_config['max_excerpt_length']),
                'engagement_score': getattr(topic, 'engagement_score', 0),
                'mobile_optimized': True
            }
            
            # Include details if requested
            if include_details:
                mobile_topic['full_description'] = topic.description or ''
                mobile_topic['keywords'] = getattr(topic, 'keywords', [])
                mobile_topic['related_articles'] = []  # Could be populated with related articles
            
            return mobile_topic
            
        except Exception as e:
            self.update_progress(f"Error optimizing trending topic {topic.slug}: {str(e)}")
            return {}
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length with ellipsis"""
        if not text:
            return ''
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3].rstrip() + '...'
    
    def generate_mobile_sitemap(self) -> str:
        """Generate mobile-specific sitemap"""
        try:
            sitemap_urls = []
            base_url = "https://influencernews.com"  # Would be configurable
            
            # Add mobile API endpoints
            sitemap_urls.append(f"{base_url}/api/mobile/articles.json")
            sitemap_urls.append(f"{base_url}/api/mobile/authors.json")
            sitemap_urls.append(f"{base_url}/api/mobile/categories.json")
            sitemap_urls.append(f"{base_url}/api/mobile/trending.json")
            sitemap_urls.append(f"{base_url}/api/mobile/search.json")
            
            # Generate XML sitemap
            sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
            sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            
            for url in sitemap_urls:
                sitemap_xml += f'  <url>\n'
                sitemap_xml += f'    <loc>{url}</loc>\n'
                sitemap_xml += f'    <changefreq>daily</changefreq>\n'
                sitemap_xml += f'    <priority>0.8</priority>\n'
                sitemap_xml += f'  </url>\n'
            
            sitemap_xml += '</urlset>\n'
            
            # Save sitemap
            sitemap_file = self.api_dir / "sitemap.xml"
            with open(sitemap_file, 'w', encoding='utf-8') as f:
                f.write(sitemap_xml)
            
            return str(sitemap_file)
            
        except Exception as e:
            self.update_progress(f"Error generating mobile sitemap: {str(e)}")
            return ""
    
    def get_mobile_stats(self) -> Dict[str, Any]:
        """Get mobile-specific statistics"""
        stats = {}
        
        try:
            # Count mobile API files
            api_files = list(self.api_dir.rglob("*.json"))
            stats['total_api_files'] = len(api_files)
            
            # Get content counts
            stats['articles'] = self.db.execute_one("SELECT COUNT(*) as count FROM articles")['count']
            stats['authors'] = self.db.execute_one("SELECT COUNT(*) as count FROM authors")['count']
            stats['categories'] = self.db.execute_one("SELECT COUNT(*) as count FROM categories")['count']
            stats['trending'] = self.db.execute_one("SELECT COUNT(*) as count FROM trending_topics")['count']
            
            # Check if mobile fields exist
            stats['mobile_ready_articles'] = self.db.execute_one(
                "SELECT COUNT(*) as count FROM articles WHERE mobile_title IS NOT NULL OR mobile_excerpt IS NOT NULL"
            )['count']
            
            stats['last_generated'] = datetime.datetime.now().isoformat()
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats


def main():
    """Main function for testing mobile integrator"""
    mobile_integrator = MobileIntegrator()
    
    # Set progress callback for console output
    def progress_callback(content_type, message, progress=None):
        if progress is not None:
            print(f"[{content_type}] {progress:.1f}% - {message}")
        else:
            print(f"[{content_type}] {message}")
    
    mobile_integrator.set_progress_callback(progress_callback)
    
    # Generate mobile API endpoints
    try:
        stats = mobile_integrator.generate_mobile_api_endpoints()
        
        print("\n✅ Mobile API Integration Complete!")
        print(f"📱 Articles: {stats['articles']} endpoints")
        print(f"👥 Authors: {stats['authors']} endpoints")
        print(f"📂 Categories: {stats['categories']} endpoints")
        print(f"🔥 Trending: {stats['trending']} endpoints")
        print(f"🔍 Search: {stats['search']} endpoints")
        
        # Generate mobile sitemap
        sitemap = mobile_integrator.generate_mobile_sitemap()
        if sitemap:
            print(f"🗺️ Sitemap: {sitemap}")
        
        # Show mobile stats
        mobile_stats = mobile_integrator.get_mobile_stats()
        print(f"\n📊 Mobile Stats:")
        for key, value in mobile_stats.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())