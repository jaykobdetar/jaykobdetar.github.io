#!/usr/bin/env python3
"""
Generate Dynamic Homepage - Simple Version
Replaces hardcoded articles with dynamic content from database
"""

import os
import sys
import json
from datetime import datetime

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

def generate_homepage_data():
    """Generate homepage data from database"""
    
    db = DatabaseManager()
    
    # Get latest published articles with author and category info
    articles_query = """
    SELECT 
        a.id,
        a.title,
        a.slug,
        a.excerpt,
        a.views,
        a.likes,
        a.read_time_minutes,
        a.publish_date,
        a.image_url,
        au.name as author_name,
        au.slug as author_slug,
        c.name as category_name,
        c.slug as category_slug,
        c.color as category_color,
        c.icon as category_icon
    FROM articles a
    JOIN authors au ON a.author_id = au.id
    JOIN categories c ON a.category_id = c.id
    WHERE a.status = 'published'
    ORDER BY a.publish_date DESC
    LIMIT 6
    """
    
    try:
        articles_data = db.execute_query(articles_query)
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return None
    
    if not articles_data:
        print("⚠ No published articles found in database")
        # Create some sample data as fallback
        return create_sample_data()
    
    homepage_data = {
        'articles': [],
        'generated_at': datetime.now().isoformat(),
        'total_articles': len(articles_data)
    }
    
    for article_data in articles_data:
        article_info = {
            'id': article_data['id'],
            'title': article_data['title'],
            'excerpt': article_data['excerpt'] or 'Read this article to learn more about the latest developments in the influencer economy.',
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
            'read_time_minutes': article_data['read_time_minutes'] or '5 min',
            'image_url': article_data['image_url'] or 'assets/images/default-article.jpg',
            'url': f'integrated/articles/article_{article_data["slug"]}.html'
        }
        homepage_data['articles'].append(article_info)
    
    return homepage_data

def create_sample_data():
    """Create sample homepage data if no articles exist"""
    return {
        'articles': [
            {
                'id': 1,
                'title': 'New Platform Update Changes Everything for Creators',
                'excerpt': 'Major social media platform announces algorithm changes that could reshape how creators build audiences and earn revenue in 2025.',
                'slug': 'platform-update-creators',
                'author_name': 'Alex Rivera',
                'author_slug': 'alex-rivera',
                'category_name': 'Technology',
                'category_slug': 'technology',
                'category_color': '#3B82F6',
                'category_icon': '💻',
                'publish_date': '2024-01-15',
                'views': 29552,
                'likes': 1240,
                'read_time_minutes': 7,
                'image_url': 'assets/images/articles/article_5_hero.jpg',
                'url': 'integrated/articles/article_platform-update-creators.html'
            }
        ],
        'generated_at': datetime.now().isoformat(),
        'total_articles': 1
    }

def create_homepage_js():
    """Create JavaScript file with homepage data"""
    
    homepage_data = generate_homepage_data()
    
    if not homepage_data:
        print("❌ Cannot generate homepage - no data available")
        return False
    
    js_content = f"""
// Auto-generated homepage data from database
// Generated at: {homepage_data['generated_at']}

const homepageArticles = {json.dumps(homepage_data['articles'], indent=2)};

// Load articles into homepage
function loadHomepageArticles() {{
    const grid = document.getElementById('articlesGrid');
    if (!grid) {{
        console.error('Articles grid not found');
        return;
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

// Enhanced load more functionality
let allArticles = [...homepageArticles];
let articlesPerPage = 6;
let currentPage = 1;

function loadMoreArticles() {{
    console.log('Loading more articles...');
    
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {{
        loadMoreBtn.innerHTML = '<span class="animate-spin">⟳</span> Loading...';
        loadMoreBtn.disabled = true;
        
        // Simulate API call - in real implementation, fetch from search backend
        setTimeout(() => {{
            // For now, just hide the button as we don't have more articles
            loadMoreBtn.innerHTML = 'No more articles';
            loadMoreBtn.disabled = true;
            loadMoreBtn.className = loadMoreBtn.className.replace('hover:from-indigo-700 hover:to-purple-700', 'bg-gray-400 cursor-not-allowed');
        }}, 1000);
    }}
}}

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
    
    # Create assets directories if they don't exist
    assets_js_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'js')
    assets_data_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'data')
    
    os.makedirs(assets_js_dir, exist_ok=True)
    os.makedirs(assets_data_dir, exist_ok=True)
    
    # Write JavaScript file
    js_file_path = os.path.join(assets_js_dir, 'homepage-dynamic.js')
    
    with open(js_file_path, 'w') as f:
        f.write(js_content)
    
    print(f"✅ Homepage JavaScript generated: {js_file_path}")
    print(f"📊 Generated data for {len(homepage_data['articles'])} articles")
    
    # Also create a data-only JSON file for other uses
    json_file_path = os.path.join(assets_data_dir, 'homepage-articles.json')
    
    with open(json_file_path, 'w') as f:
        json.dump(homepage_data, f, indent=2)
    
    print(f"✅ Homepage JSON data: {json_file_path}")
    
    return True

if __name__ == "__main__":
    print("🏠 Generating dynamic homepage content...")
    
    if create_homepage_js():
        print("\n✅ Homepage generation completed successfully!")
        print("\nNext steps:")
        print("1. Include assets/js/homepage-dynamic.js in index.html")
        print("2. Remove hardcoded article from index.html")
        print("3. Test the dynamic loading")
    else:
        print("\n❌ Homepage generation failed!")
        sys.exit(1)