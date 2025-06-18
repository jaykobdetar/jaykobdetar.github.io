#!/usr/bin/env python3
"""
Quick script to regenerate existing pages with mobile templates
"""
import sqlite3
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, 'src')

# Database connection
DB_PATH = 'data/infnews.db'

def regenerate_author_pages():
    """Regenerate author pages with mobile support"""
    print("Regenerating author pages with mobile support...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all authors
    cursor.execute("SELECT id, name, slug, bio, expertise, twitter_handle, linkedin_url FROM authors")
    authors = cursor.fetchall()
    
    for author in authors:
        author_id, name, slug, bio, expertise, twitter_handle, linkedin_url = author
        
        # Generate mobile-enabled author page
        create_mobile_author_page(author_id, name, slug, bio, expertise, twitter_handle, linkedin_url)
    
    conn.close()
    print(f"Successfully regenerated {len(authors)} author pages with mobile support!")

def create_mobile_author_page(author_id, name, slug, bio, expertise, twitter_handle, linkedin_url):
    """Create mobile-enabled author page"""
    
    # Generate author page filename
    author_filename = Path("integrated/authors") / f"author_{slug}.html"
    
    # Base path for assets (from integrated/authors/ perspective)
    base_path = "../../"
    
    # Get article count for this author
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM articles WHERE author_id = ?", (author_id,))
    article_count = cursor.fetchone()[0]
    
    # Get author's articles
    cursor.execute("""
        SELECT a.id, a.title, a.subtitle, a.created_at, c.name as category_name, c.slug as category_slug
        FROM articles a 
        LEFT JOIN categories c ON a.category_id = c.id 
        WHERE a.author_id = ? 
        ORDER BY a.created_at DESC 
        LIMIT 6
    """, (author_id,))
    articles = cursor.fetchall()
    conn.close()
    
    # Generate image tag
    img_tag = f'<img src="{base_path}assets/images/authors/author_{slug}_profile.jpg" alt="{name} profile photo" onerror="this.src=\'{base_path}assets/placeholders/author_placeholder.jpg\'" loading="lazy" class="rounded-full object-cover">'
    
    # Generate article cards
    article_cards = generate_article_cards(articles, base_path)
    
    # Create HTML content for author page with mobile support
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Author Profile | Influencer News</title>
    <link rel="stylesheet" href="{base_path}assets/css/styles.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ 
            font-family: 'Inter', sans-serif; 
            line-height: 1.7; 
        }}
        .hero-title {{ 
            font-family: 'Playfair Display', serif; 
        }}
        .nav-link {{ 
            position: relative; 
            transition: all 0.3s ease;
        }}
        .nav-link::after {{ 
            content: ''; 
            position: absolute; 
            bottom: -2px; 
            left: 0; 
            width: 0; 
            height: 2px; 
            background: linear-gradient(90deg, #ffffff, #e0e7ff); 
            transition: width 0.3s ease; 
        }}
        .nav-link:hover::after {{ 
            width: 100%; 
        }}
        
        /* Mobile Menu Styles */
        .mobile-menu {{
            position: fixed;
            top: 0;
            right: -100%;
            width: 80%;
            max-width: 300px;
            height: 100vh;
            background: #312e81;
            transition: right 0.3s ease-in-out;
            z-index: 1000;
        }}
        
        .mobile-menu.active {{
            right: 0;
        }}
        
        .mobile-menu-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease-in-out, visibility 0.3s ease-in-out;
            z-index: 999;
        }}
        
        .mobile-menu-overlay.active {{
            opacity: 1;
            visibility: visible;
        }}
        
        .hamburger {{
            width: 30px;
            height: 24px;
            position: relative;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        .hamburger span {{
            display: block;
            width: 100%;
            height: 3px;
            background: white;
            border-radius: 3px;
            transition: all 0.3s ease-in-out;
        }}
        
        .hamburger.active span:nth-child(1) {{
            transform: rotate(45deg) translate(8px, 8px);
        }}
        
        .hamburger.active span:nth-child(2) {{
            opacity: 0;
        }}
        
        .hamburger.active span:nth-child(3) {{
            transform: rotate(-45deg) translate(8px, -8px);
        }}
        
        .mobile-nav-item {{
            display: block;
            padding: 1rem 2rem;
            color: white;
            text-decoration: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            transition: background 0.3s ease;
        }}
        
        .mobile-nav-item:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        /* Mobile Search Overlay */
        .mobile-search-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100vh;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1001;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease-in-out, visibility 0.3s ease-in-out;
        }}
        
        .mobile-search-overlay.active {{
            opacity: 1;
            visibility: visible;
        }}
    </style>
</head>
<body class="bg-gray-50 text-gray-900">
    <!-- Mobile Menu Overlay -->
    <div class="mobile-menu-overlay" id="mobileMenuOverlay"></div>
    
    <!-- Mobile Menu -->
    <div class="mobile-menu" id="mobileMenu">
        <div class="p-6 border-b border-indigo-700">
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <div class="w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-600 rounded-full flex items-center justify-center mr-3">
                        <span class="text-lg font-bold text-white">IN</span>
                    </div>
                    <div>
                        <h2 class="text-xl font-bold text-white">Menu</h2>
                    </div>
                </div>
                <button class="text-white text-2xl" id="closeMobileMenu">&times;</button>
            </div>
        </div>
        <nav class="py-4">
            <a href="{base_path}index.html" class="mobile-nav-item">🏠 Home</a>
            <a href="{base_path}search.html" class="mobile-nav-item">🔍 Search</a>
            <a href="{base_path}authors.html" class="mobile-nav-item">👥 Authors</a>
            <a href="{base_path}integrated/categories.html" class="mobile-nav-item">📂 Categories</a>
            <a href="{base_path}integrated/trending.html" class="mobile-nav-item">🔥 Trending</a>
            <a href="#contact" class="mobile-nav-item">📧 Contact</a>
        </nav>
        <div class="p-6 mt-auto">
            <div class="bg-indigo-700 rounded-lg p-4">
                <h3 class="text-white font-bold mb-2">Newsletter</h3>
                <p class="text-indigo-200 text-sm mb-3">Get the latest influencer news</p>
                <button class="bg-white text-indigo-700 px-4 py-2 rounded-md text-sm font-semibold w-full">Subscribe</button>
            </div>
        </div>
    </div>
    
    <!-- Mobile Search Overlay -->
    <div class="mobile-search-overlay" id="mobileSearchOverlay">
        <div class="p-4 bg-indigo-900">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-white font-bold text-lg">Search</h3>
                <button class="text-white text-2xl" id="closeMobileSearch">&times;</button>
            </div>
            <div class="relative">
                <input 
                    type="text" 
                    id="mobileSearchInput" 
                    placeholder="Search articles, authors..." 
                    class="w-full p-4 pr-12 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                    onkeyup="handleMobileSearch(event)"
                >
                <button onclick="performMobileSearch()" class="absolute right-4 top-4 text-gray-600 hover:text-indigo-600 transition">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </button>
            </div>
            <!-- Mobile Search Suggestions -->
            <div id="mobileSearchSuggestions" class="mt-4 bg-white rounded-lg shadow-lg hidden max-h-60 overflow-y-auto">
                <!-- Populated by JavaScript -->
            </div>
        </div>
    </div>

    <!-- Header -->
    <header class="bg-indigo-900 text-white sticky top-0 z-50 shadow-2xl">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center">
                <div class="w-16 h-16 bg-gradient-to-br from-indigo-400 to-purple-600 rounded-full flex items-center justify-center mr-4">
                    <span class="text-2xl font-bold text-white">IN</span>
                </div>
                <div>
                    <h1 class="text-3xl font-bold hero-title">Influencer News</h1>
                    <p class="text-xs text-indigo-200">Breaking stories • Real insights</p>
                </div>
            </div>
            <!-- Mobile Menu Button -->
            <button class="md:hidden hamburger" id="mobileMenuToggle" aria-label="Toggle mobile menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
            
            <nav class="hidden md:block">
                <ul class="flex space-x-8">
                    <li><a href="{base_path}index.html" class="nav-link hover:text-indigo-200 transition font-medium">Home</a></li>
                    <li><a href="{base_path}search.html" class="nav-link hover:text-indigo-200 transition font-medium">Search</a></li>
                    <li><a href="{base_path}authors.html" class="nav-link hover:text-indigo-200 transition font-medium">Authors</a></li>
                    <li><a href="{base_path}integrated/categories.html" class="nav-link hover:text-indigo-200 transition font-medium">Categories</a></li>
                    <li><a href="{base_path}integrated/trending.html" class="nav-link hover:text-indigo-200 transition font-medium">Trending</a></li>
                    <li><a href="#contact" class="nav-link hover:text-indigo-200 transition font-medium">Contact</a></li>
                </ul>
            </nav>
            
            <!-- Enhanced Search Bar - Desktop Only -->
            <div class="relative hidden md:block">
                <input 
                    type="text" 
                    id="searchInput" 
                    placeholder="Search breaking news..." 
                    class="p-3 pr-12 rounded-full text-gray-900 w-64 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition-all"
                    onkeyup="handleSearch(event)"
                >
                <button onclick="performSearch()" class="absolute right-3 top-3 text-gray-600 hover:text-indigo-600 transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                </button>
                <!-- Search Suggestions -->
                <div id="searchSuggestions" class="absolute top-full left-0 right-0 bg-white rounded-lg shadow-lg mt-1 hidden max-h-60 overflow-y-auto z-50">
                    <!-- Populated by JavaScript -->
                </div>
            </div>
            
            <!-- Mobile Search Button -->
            <button class="md:hidden text-white p-2" id="mobileSearchToggle" aria-label="Toggle mobile search">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
            </button>
        </div>
        
        <div class="bg-gradient-to-r from-red-600 to-red-700 text-white py-3 overflow-hidden relative">
            <div class="live-ticker flex items-center space-x-8">
                <div class="flex items-center space-x-2">
                    <div class="w-3 h-3 bg-red-400 rounded-full animate-ping"></div>
                    <span class="font-bold text-sm">LIVE</span>
                </div>
                <span class="text-sm font-medium">
                    BREAKING: Emma Chamberlain signs $50M Netflix deal • TikTok announces new creator fund • Charli D'Amelio beauty line sells out in 2 hours • 
                    <span id="current-time" class="font-bold"></span>
                </span>
            </div>
        </div>
    </header>

    <!-- Author Profile Section -->
    <section class="container mx-auto px-4 py-16">
        <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
            <div class="bg-gradient-to-r from-indigo-600 to-purple-600 p-12">
                <div class="flex items-center space-x-8">
                    <div class="w-32 h-32 flex-shrink-0">
                        {img_tag}
                    </div>
                    <div>
                        <h1 class="text-4xl font-bold text-white mb-2">{name}</h1>
                        <p class="text-xl text-indigo-100 mb-4">Senior Correspondent</p>
                        <div class="flex space-x-4">
                            <span class="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm">✓ Verified</span>
                            <span class="bg-white/20 text-white px-3 py-1 rounded-full text-sm">📍 Remote</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="p-8">
                <div class="grid md:grid-cols-3 gap-8">
                    <!-- Bio Section -->
                    <div class="md:col-span-2">
                        <h2 class="text-2xl font-bold mb-4">About</h2>
                        <p class="text-gray-700 mb-6 leading-relaxed">{bio}</p>
                        
                        <!-- Expertise -->
                        <div class="mb-8">
                            <h3 class="text-xl font-semibold mb-3">Areas of Expertise</h3>
                            <div class="flex flex-wrap gap-2">
                                {generate_expertise_tags(expertise)}
                            </div>
                        </div>
                        
                        <!-- Stats -->
                        <div class="grid grid-cols-3 gap-4 mb-8">
                            <div class="bg-gray-50 p-4 rounded-lg text-center">
                                <div class="text-2xl font-bold text-indigo-600">{article_count}</div>
                                <div class="text-sm text-gray-600">Articles</div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded-lg text-center">
                                <div class="text-2xl font-bold text-indigo-600">4.8</div>
                                <div class="text-sm text-gray-600">Rating</div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded-lg text-center">
                                <div class="text-2xl font-bold text-indigo-600">2020</div>
                                <div class="text-sm text-gray-600">Joined</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Contact Section -->
                    <div>
                        <div class="bg-gray-50 p-6 rounded-lg">
                            <h3 class="text-xl font-semibold mb-4">Connect</h3>
                            <div class="space-y-3">
                                {generate_social_links(twitter_handle, linkedin_url)}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Recent Articles -->
                <div class="mt-12">
                    <h2 class="text-2xl font-bold mb-6">Recent Articles</h2>
                    <div class="grid md:grid-cols-2 gap-6">
                        {article_cards}
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-8 mt-16">
        <div class="container mx-auto px-4 text-center">
            <p>&copy; 2024 Influencer News. All rights reserved.</p>
        </div>
    </footer>

    <script>
        // Mobile Menu Functionality
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const closeMobileMenu = document.getElementById('closeMobileMenu');
        const mobileMenu = document.getElementById('mobileMenu');
        const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
        
        function openMobileMenu() {{
            mobileMenu.classList.add('active');
            mobileMenuOverlay.classList.add('active');
            mobileMenuToggle.classList.add('active');
            document.body.style.overflow = 'hidden';
        }}
        
        function closeMobileMenuFunc() {{
            mobileMenu.classList.remove('active');
            mobileMenuOverlay.classList.remove('active');
            mobileMenuToggle.classList.remove('active');
            document.body.style.overflow = '';
        }}
        
        if (mobileMenuToggle) {{
            mobileMenuToggle.addEventListener('click', openMobileMenu);
        }}
        
        if (closeMobileMenu) {{
            closeMobileMenu.addEventListener('click', closeMobileMenuFunc);
        }}
        
        if (mobileMenuOverlay) {{
            mobileMenuOverlay.addEventListener('click', closeMobileMenuFunc);
        }}
        
        // Close mobile menu when clicking on a link
        document.querySelectorAll('.mobile-nav-item').forEach(item => {{
            item.addEventListener('click', closeMobileMenuFunc);
        }});
        
        // Mobile Search Functionality
        const mobileSearchToggle = document.getElementById('mobileSearchToggle');
        const closeMobileSearchBtn = document.getElementById('closeMobileSearch');
        const mobileSearchOverlay = document.getElementById('mobileSearchOverlay');
        const mobileSearchInput = document.getElementById('mobileSearchInput');
        const mobileSearchSuggestions = document.getElementById('mobileSearchSuggestions');
        
        const searchData = [
            'MrBeast', 'Emma Chamberlain', 'PewDiePie', 'Charli DAmelio', 'Logan Paul',
            'Creator Economy', 'TikTok Algorithm', 'YouTube Shorts', 'Instagram Reels',
            'Brand Partnerships', 'Influencer Marketing', 'Social Media Trends'
        ];
        
        function openMobileSearch() {{
            mobileSearchOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            // Focus on search input after animation
            setTimeout(() => {{
                mobileSearchInput.focus();
            }}, 300);
        }}
        
        function closeMobileSearchFunc() {{
            mobileSearchOverlay.classList.remove('active');
            document.body.style.overflow = '';
            mobileSearchSuggestions.classList.add('hidden');
            mobileSearchInput.value = '';
        }}
        
        if (mobileSearchToggle) {{
            mobileSearchToggle.addEventListener('click', openMobileSearch);
        }}
        
        if (closeMobileSearchBtn) {{
            closeMobileSearchBtn.addEventListener('click', closeMobileSearchFunc);
        }}
        
        if (mobileSearchOverlay) {{
            mobileSearchOverlay.addEventListener('click', function(e) {{
                if (e.target === mobileSearchOverlay) {{
                    closeMobileSearchFunc();
                }}
            }});
        }}
        
        function handleMobileSearch(event) {{
            const query = event.target.value.toLowerCase();
            
            if (query.length > 1) {{
                const matches = searchData.filter(item => 
                    item.toLowerCase().includes(query)
                ).slice(0, 5);
                
                if (matches.length > 0) {{
                    mobileSearchSuggestions.innerHTML = matches.map(match => 
                        `<div class="p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0" onclick="selectMobileSuggestion('${{match}}')">${{match}}</div>`
                    ).join('');
                    mobileSearchSuggestions.classList.remove('hidden');
                }} else {{
                    mobileSearchSuggestions.classList.add('hidden');
                }}
            }} else {{
                mobileSearchSuggestions.classList.add('hidden');
            }}
            
            if (event.key === 'Enter') {{
                performMobileSearch();
            }}
        }}
        
        function selectMobileSuggestion(suggestion) {{
            mobileSearchInput.value = suggestion;
            mobileSearchSuggestions.classList.add('hidden');
            performMobileSearch();
        }}
        
        function performMobileSearch() {{
            const query = mobileSearchInput.value;
            if (query.trim()) {{
                // Close mobile search and redirect to search page
                closeMobileSearchFunc();
                window.location.href = `{base_path}search.html?q=${{encodeURIComponent(query)}}`;
            }}
        }}

        function handleSearch(event) {{
            if (event.key === 'Enter') {{
                performSearch();
            }}
        }}

        function performSearch() {{
            const query = document.getElementById('searchInput').value;
            if (query.trim()) {{
                window.location.href = `{base_path}search.html?q=${{encodeURIComponent(query)}}`;
            }}
        }}

        function updateTime() {{
            const now = new Date();
            const options = {{ 
                hour: '2-digit', 
                minute: '2-digit', 
                hour12: true, 
                timeZoneName: 'short' 
            }};
            const timeElement = document.getElementById('current-time');
            if (timeElement) {{
                timeElement.textContent = now.toLocaleString('en-US', options);
            }}
        }}

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            updateTime();
            setInterval(updateTime, 1000);
        }});
    </script>
</body>
</html>'''
    
    # Write the HTML file
    with open(author_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated mobile-enabled page: {author_filename}")

def generate_expertise_tags(expertise_str):
    """Generate expertise tags HTML"""
    if not expertise_str:
        return ""
    
    expertise_list = [exp.strip() for exp in expertise_str.split(',') if exp.strip()]
    tags = [f'<span class="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm">{exp}</span>' 
            for exp in expertise_list]
    return ' '.join(tags)

def generate_social_links(twitter_handle, linkedin_url):
    """Generate social media links HTML"""
    links = []
    
    if twitter_handle:
        links.append(f'<a href="https://twitter.com/{twitter_handle}" target="_blank" class="flex items-center text-gray-700 hover:text-indigo-600"><span class="mr-2">🐦</span> Twitter</a>')
    
    if linkedin_url:
        full_url = linkedin_url if linkedin_url.startswith('http') else f"https://linkedin.com/in/{linkedin_url}"
        links.append(f'<a href="{full_url}" target="_blank" class="flex items-center text-gray-700 hover:text-indigo-600"><span class="mr-2">💼</span> LinkedIn</a>')
    
    return '\n                                '.join(links)

def generate_article_cards(articles, base_path):
    """Generate HTML for article cards"""
    if not articles:
        return '<p class="text-gray-500 col-span-2">No articles published yet.</p>'
    
    cards = []
    for article in articles:
        article_id, title, subtitle, created_at, category_name, category_slug = article
        
        # Format relative date (simplified)
        time_ago = "1 hour ago"  # Simplified for now
        
        card = f'''
        <article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition">
            <img src="{base_path}assets/placeholders/article_placeholder.jpg" alt="{title}" class="w-full h-48 object-cover">
            <div class="p-6">
                <div class="flex items-center mb-2">
                    <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                        💻 {category_name or 'Technology'}
                    </span>
                    <span class="text-gray-500 text-sm ml-auto">{time_ago}</span>
                </div>
                <h3 class="text-xl font-semibold mb-2 line-clamp-2">
                    <a href="{base_path}integrated/articles/article_{article_id}.html" class="hover:text-indigo-600">
                        {title}
                    </a>
                </h3>
                <p class="text-gray-600 line-clamp-2">{subtitle or ''}</p>
            </div>
        </article>
        '''
        cards.append(card)
    
    return '\n'.join(cards)

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        exit(1)
    
    regenerate_author_pages()