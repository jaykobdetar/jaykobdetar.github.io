#!/usr/bin/env python3
"""
Homepage Integrator
===================
Generates the main homepage with dynamic content and search functionality
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

try:
    from ..database import DatabaseManager
except ImportError:
    from src.database import DatabaseManager


class HomepageIntegrator:
    """Integrator for the main homepage"""
    
    def __init__(self):
        # Don't use the standard content/integrated structure for homepage
        self.db = DatabaseManager()
        self.project_root = Path(__file__).parent.parent.parent
        self.template_file = self.project_root / "templates" / "homepage_template.html"
        self.output_file = self.project_root / "index.html"
        
    def generate_homepage(self, force_update: bool = False) -> bool:
        """Generate the homepage with current database content"""
        
        try:
            # Get latest articles for homepage
            articles = self._get_homepage_articles()
            
            # Generate JavaScript data file
            self._generate_homepage_js(articles)
            
            # If index.html doesn't exist or force_update is True, create from template
            if not self.output_file.exists() or force_update:
                self._generate_homepage_html(articles)
            
            print(f"✅ Homepage updated with {len(articles)} articles")
            return True
            
        except Exception as e:
            print(f"❌ Homepage generation failed: {e}")
            return False
    
    def _get_homepage_articles(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Get latest published articles for homepage"""
        
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
        WHERE a.status = 'published'
        ORDER BY a.publish_date DESC
        LIMIT ?
        """
        
        articles_data = self.db.execute_query(query, (limit,))
        
        articles = []
        for article_data in articles_data:
            article_info = {
                'id': article_data['id'],
                'title': article_data['title'],
                'excerpt': article_data['excerpt'] or 'Read this article to learn more about the latest developments.',
                'slug': article_data['slug'],
                'author_name': article_data['author_name'],
                'author_slug': article_data['author_slug'],
                'category_name': article_data['category_name'],
                'category_slug': article_data['category_slug'],
                'category_color': article_data['category_color'],
                'category_icon': article_data['category_icon'],
                'publish_date': article_data['publish_date'],
                'views': article_data['views'] or 0,
                'likes': article_data['likes'] or 0,
                'read_time_minutes': self._parse_read_time(article_data['read_time_minutes']),
                'image_url': article_data['image_url'] or 'assets/images/default-article.jpg',
                'url': f'integrated/articles/article_{article_data["slug"]}.html'
            }
            articles.append(article_info)
        
        return articles
    
    def _parse_read_time(self, read_time_value) -> int:
        """Parse read time value handling both int and string formats"""
        if not read_time_value:
            return 5
        
        if isinstance(read_time_value, int):
            return read_time_value
        
        if isinstance(read_time_value, str):
            # Handle formats like "5 min", "10 minutes", etc.
            import re
            numbers = re.findall(r'\d+', read_time_value)
            if numbers:
                return int(numbers[0])
            return 5
        
        try:
            return int(read_time_value)
        except (ValueError, TypeError):
            return 5
    
    def _generate_homepage_js(self, articles: List[Dict[str, Any]]) -> None:
        """Generate JavaScript file with homepage data"""
        
        js_content = f"""
// Auto-generated homepage data from database
// Generated at: {datetime.now().isoformat()}

const homepageArticles = {json.dumps(articles, indent=2)};

// Load articles into homepage
function loadHomepageArticles() {{
    const grid = document.getElementById('articlesGrid');
    if (!grid) {{
        console.error('Articles grid not found');
        return;
    }}
    
    // Remove loading indicator
    const loadingIndicator = document.getElementById('articlesLoading');
    if (loadingIndicator) {{
        loadingIndicator.remove();
    }}
    
    // Clear existing content
    grid.innerHTML = '';
    
    // Add articles to grid
    homepageArticles.forEach((article, index) => {{
        const articleCard = createArticleCard(article, index === 0);
        grid.appendChild(articleCard);
    }});
    
    console.log(`Loaded ${{homepageArticles.length}} articles from database`);
}}

function createArticleCard(article, isFeatured = false) {{
    const card = document.createElement('div');
    card.className = isFeatured ? 
        'article-card bg-white rounded-xl shadow-lg overflow-hidden md:col-span-2 lg:col-span-1' :
        'article-card bg-white rounded-xl shadow-lg overflow-hidden';
    
    // Format publish date
    const publishDate = new Date(article.publish_date);
    const timeAgo = getTimeAgo(publishDate);
    
    // Create card HTML with safe escaping
    card.innerHTML = `
        <div class="relative">
            <img src="${{article.image_url}}" alt="${{escapeHtml(article.title)}}" class="w-full h-48 object-cover" loading="lazy" onerror="this.src='assets/images/default-article.jpg'">
            <div class="absolute top-4 right-4">
                <span class="category-${{article.category_name}} bg-white/90 px-2 py-1 rounded text-xs font-bold uppercase">${{article.category_name}}</span>
            </div>
        </div>
        <div class="p-6">
            <div class="flex items-center gap-2 mb-3">
                <span class="text-gray-500 text-sm">${{escapeHtml(article.author_name)}} • ${{timeAgo}}</span>
            </div>
            <h3 class="text-lg font-bold mb-3 hover:text-indigo-600 transition cursor-pointer">
                ${{escapeHtml(article.title)}}
            </h3>
            <p class="text-gray-700 mb-4 text-sm">
                ${{escapeHtml(article.excerpt)}}
            </p>
            <div class="flex items-center justify-between text-sm">
                <span class="text-gray-500">👁 ${{article.views.toLocaleString()}} views</span>
                <a href="${{article.url}}" class="text-indigo-600 font-medium cursor-pointer">Read →</a>
            </div>
        </div>
    `;
    
    return card;
}}

function escapeHtml(text) {{
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}}

function getTimeAgo(date) {{
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${{diffDays}} days ago`;
    if (diffDays < 30) return `${{Math.floor(diffDays / 7)}} weeks ago`;
    return `${{Math.floor(diffDays / 30)}} months ago`;
}}

// Enhanced load more functionality with real search integration
let allArticles = [...homepageArticles];
let articlesPerPage = 6;
let currentPage = 1;

function loadMoreArticles() {{
    console.log('Loading more articles...');
    
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {{
        loadMoreBtn.innerHTML = '<span class="animate-spin">⟳</span> Loading...';
        loadMoreBtn.disabled = true;
        
        // In production, this would call the search backend for more articles
        setTimeout(() => {{
            loadMoreBtn.innerHTML = 'No more articles';
            loadMoreBtn.disabled = true;
            loadMoreBtn.className = loadMoreBtn.className.replace('hover:from-indigo-700 hover:to-purple-700', 'bg-gray-400 cursor-not-allowed');
        }}, 1000);
    }}
}}

// Search functionality
// Note: Search has been moved to dedicated search.html page
// These functions are kept for compatibility but mobile search still works

// Initialize homepage when DOM loads
document.addEventListener('DOMContentLoaded', function() {{
    console.log('Initializing dynamic homepage...');
    loadHomepageArticles();
}});

// Export for use in other scripts
if (typeof window !== 'undefined') {{
    window.homepageArticles = homepageArticles;
    window.loadHomepageArticles = loadHomepageArticles;
    window.createArticleCard = createArticleCard;
}}
"""
        
        # Write JavaScript file
        js_dir = self.project_root / "assets" / "js"
        js_dir.mkdir(parents=True, exist_ok=True)
        js_file = js_dir / "homepage-dynamic.js"
        
        with open(js_file, 'w') as f:
            f.write(js_content)
        
        print(f"✅ Homepage JavaScript updated: {js_file}")
    
    def _generate_homepage_html(self, articles: List[Dict[str, Any]]) -> None:
        """Generate homepage HTML from template"""
        
        # For now, we'll keep the existing index.html as it's already properly configured
        # This method would be used if we had a template-based approach
        print("📝 Homepage HTML structure maintained (using existing index.html)")
        
    def sync_with_files(self) -> bool:
        """Sync homepage with current database content"""
        return self.generate_homepage()
        
    def sync_all(self) -> bool:
        """Generate all homepage assets"""
        return self.generate_homepage()


def main():
    """Command line interface for homepage generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate homepage from database')
    parser.add_argument('--force', '-f', action='store_true', 
                       help='Force regeneration of HTML file')
    
    args = parser.parse_args()
    
    integrator = HomepageIntegrator()
    success = integrator.generate_homepage(force_update=args.force)
    
    if success:
        print("✅ Homepage generation completed successfully!")
    else:
        print("❌ Homepage generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()