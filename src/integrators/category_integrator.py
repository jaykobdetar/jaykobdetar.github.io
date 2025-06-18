#!/usr/bin/env python3
"""
Category Integrator
==================
Handles category content integration with database
"""

from pathlib import Path
from typing import Dict, List, Any
try:
    from .base_integrator import BaseIntegrator
    from ..models.category import Category
    from ..models.article import Article
except ImportError:
    from src.integrators.base_integrator import BaseIntegrator
    from src.models.category import Category
    from src.models.article import Article


class CategoryIntegrator(BaseIntegrator):
    """Category content integrator"""
    
    def __init__(self):
        super().__init__('categories', 'categories')
        
    def sync_all(self):
        """Sync all categories from database"""
        self.update_progress("Starting category sync...")
        
        try:
            # Get all categories from database
            categories = Category.find_all()
            
            if not categories:
                self.update_progress("No categories found in database")
                return
                
            # Create individual category pages
            for category in categories:
                self.create_category_page(category)
                
            # Create categories listing page
            self.create_categories_listing(categories)
            
            self.update_progress(f"Synced {len(categories)} categories successfully")
            
        except Exception as e:
            self.update_progress(f"Error syncing categories: {e}")
            raise
            
    def create_category_page(self, category):
        """Create individual category page"""
        try:
            # Get path manager for this location
            path_manager = self.get_path_manager(f"integrated/categories/category_{category.slug}.html")
            base_path = path_manager.get_base_path()
            
            # Read template
            template_content = self.get_category_template(base_path)
            
            # Get articles in this category
            articles = Article.find_all(category_id=category.id)
            
            # Generate article cards
            articles_html = self.generate_article_cards(articles, category.slug, base_path)
            
            # Generate dynamic search data
            search_data = self.generate_dynamic_search_data()
            search_data_js = str(search_data).replace("'", '"')  # Convert to JS array format
            
            # Replace placeholders
            replacements = {
                '{{CATEGORY_NAME}}': category.name,
                '{{CATEGORY_DESCRIPTION}}': getattr(category, 'description', f'Latest news and updates about {category.name.lower()}'),
                '{{CATEGORY_COLOR}}': getattr(category, 'color', '#4F46E5'),
                '{{ARTICLES_CONTENT}}': articles_html,
                '{{ARTICLE_COUNT}}': str(len(articles)),
                '{{SEARCH_DATA}}': search_data_js
            }
            
            content = template_content
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            
            # Save file
            filename = self.integrated_dir / f"category_{category.slug}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.update_progress(f"Created category page: {filename.name}")
            
        except Exception as e:
            self.update_progress(f"Error creating category page for {category.name}: {e}")
            
    def create_categories_listing(self, categories):
        """Create categories listing page"""
        try:
            # Get path manager for this location
            path_manager = self.get_path_manager("integrated/categories.html")
            base_path = path_manager.get_base_path()
            
            # Read template
            template_content = self.get_categories_listing_template(base_path)
            
            # Generate category cards
            categories_html = self.generate_category_cards(categories, base_path)
            
            # Generate dynamic search data
            search_data = self.generate_dynamic_search_data()
            search_data_js = str(search_data).replace("'", '"')  # Convert to JS array format
            
            # Replace placeholders
            content = template_content.replace('{{CATEGORIES_CONTENT}}', categories_html)
            content = content.replace('{{CATEGORY_COUNT}}', str(len(categories)))
            content = content.replace('{{SEARCH_DATA}}', search_data_js)
            
            # Save file (listing goes in main integrated dir, not subfolder)
            from pathlib import Path
            filename = Path("integrated") / "categories.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.update_progress(f"Created categories listing: {filename.name}")
            
        except Exception as e:
            self.update_progress(f"Error creating categories listing: {e}")
            import traceback
            traceback.print_exc()
            raise
            
    def generate_category_cards(self, categories, base_path=""):
        """Generate HTML for category cards"""
        cards_html = ""
        
        for category in categories:
            # Get article count for this category
            articles = Article.find_all(category_id=category.id)
            article_count = len(articles)
            
            # Get category color or default
            color = getattr(category, 'color', '#4F46E5')
            
            cards_html += f'''
            <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                <div class="h-32" style="background: linear-gradient(135deg, {color}, {color}99);"></div>
                <div class="p-6">
                    <h3 class="text-xl font-bold text-gray-900 mb-2">{self.escape_html(category.name)}</h3>
                    <p class="text-gray-600 mb-4">{self.escape_html(getattr(category, 'description', f'Latest news and updates about {category.name.lower()}'))}</p>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-500">{article_count} articles</span>
                        <a href="categories/category_{category.slug}.html" 
                           class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white"
                           style="background-color: {color};">
                            View Category →
                        </a>
                    </div>
                </div>
            </div>
            '''
            
        return cards_html
        
    def generate_article_cards(self, articles, category_slug, base_path=""):
        """Generate HTML for article cards in category"""
        if not articles:
            return '''
            <div class="col-span-full text-center py-16">
                <div class="text-gray-400 text-6xl mb-4">📄</div>
                <h3 class="text-xl font-semibold text-gray-600 mb-2">No Articles Yet</h3>
                <p class="text-gray-500">Check back soon for the latest updates in this category!</p>
            </div>
            '''
            
        cards_html = ""
        for article in articles:
            # Get author info
            author = article.get_author()
            author_name = author.name if author else "Unknown Author"
            
            # Format views
            views = getattr(article, 'views', 0)
            views_formatted = f"{views:,}" if isinstance(views, int) else str(views)
            
            # Handle image URL properly - use proper assets structure
            image_url = getattr(article, 'image_url', None)
            if not image_url or image_url == 'None' or image_url is None:
                image_url = f"{base_path}assets/placeholders/article_placeholder.svg"
            elif image_url.startswith('http'):
                # External URLs should be converted to local assets
                image_url = f"{base_path}assets/images/articles/article_{article.id}_hero.jpg"
            elif not image_url.startswith(('/', 'assets')):
                # Ensure proper assets folder structure
                image_url = f"{base_path}assets/images/articles/{image_url}"
            
            cards_html += f'''
            <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                <div class="relative">
                    <img src="{image_url}" 
                         alt="{self.escape_html(article.title)}" 
                         class="w-full h-48 object-cover">
                </div>
                <div class="p-6">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-gray-500 text-sm">{author_name} • {self.format_date_relative(getattr(article, 'created_at', ''))}</span>
                    </div>
                    <h3 class="text-lg font-bold mb-3 hover:text-indigo-600 transition">
                        <a href="{base_path}integrated/articles/article_{article.slug}.html">{self.escape_html(article.title)}</a>
                    </h3>
                    <p class="text-gray-700 mb-4 text-sm">
                        {self.escape_html(getattr(article, 'excerpt', article.title)[:150])}...
                    </p>
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-gray-500">👁 {views_formatted} views</span>
                        <a href="{base_path}integrated/articles/article_{article.slug}.html" 
                           class="text-indigo-600 font-medium">Read →</a>
                    </div>
                </div>
            </div>
            '''
            
        return cards_html
    
    def generate_dynamic_search_data(self):
        """Generate dynamic search data from database"""
        try:
            # Get categories, authors, and popular article titles
            from ..models.category import Category
            from ..models.author import Author
            from ..models.article import Article
            
            search_items = []
            
            # Add category names
            categories = Category.find_all()
            for category in categories:
                search_items.append(category.name)
            
            # Add author names
            authors = Author.find_all(limit=20)  # Top 20 authors
            for author in authors:
                search_items.append(author.name)
            
            # Add popular article titles (first few words)
            articles = Article.find_all(limit=15)  # Top 15 articles
            for article in articles:
                # Extract first 2-3 significant words from title
                title_words = article.title.split()[:3]
                if len(title_words) >= 2:
                    search_items.append(' '.join(title_words))
            
            # Add some general search terms if list is too short
            if len(search_items) < 10:
                fallback_terms = [
                    'Creator Economy', 'Social Media', 'Content Creation', 
                    'Brand Partnerships', 'Influencer Marketing', 'Platform Updates',
                    'YouTube', 'TikTok', 'Instagram', 'Trending Content'
                ]
                search_items.extend(fallback_terms)
            
            # Remove duplicates and limit to reasonable number
            search_items = list(dict.fromkeys(search_items))[:20]
            
            return search_items
            
        except Exception as e:
            self.update_progress(f"Error generating search data: {e}")
            # Fallback to basic terms
            return [
                'Creator Economy', 'Social Media', 'Content Creation',
                'Brand Partnerships', 'Influencer Marketing', 'Platform Updates'
            ]
        
    def get_category_template(self, base_path=""):
        """Get category page template"""
        return ('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{CATEGORY_NAME}} - Influencer News</title>
    <link rel="stylesheet" href="{base_path}assets/css/styles.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .hero-title { font-family: 'Playfair Display', serif; }
    
        /* Mobile Menu Styles */
        .mobile-menu {
            position: fixed;
            top: 0;
            right: -100%;
            width: 80%;
            max-width: 300px;
            height: 100vh;
            background: #312e81;
            transition: right 0.3s ease-in-out;
            z-index: 1000;
        }
        
        .mobile-menu.active {
            right: 0;
        }
        
        .mobile-menu-overlay {
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
        }
        
        .mobile-menu-overlay.active {
            opacity: 1;
            visibility: visible;
        }
        
        .hamburger {
            width: 30px;
            height: 24px;
            position: relative;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .hamburger span {
            display: block;
            width: 100%;
            height: 3px;
            background: white;
            border-radius: 3px;
            transition: all 0.3s ease-in-out;
        }
        
        .hamburger.active span:nth-child(1) {
            transform: rotate(45deg) translate(8px, 8px);
        }
        
        .hamburger.active span:nth-child(2) {
            opacity: 0;
        }
        
        .hamburger.active span:nth-child(3) {
            transform: rotate(-45deg) translate(8px, -8px);
        }
        
        .mobile-nav-item {
            display: block;
            padding: 1rem 2rem;
            color: white;
            text-decoration: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            transition: background 0.3s ease;
        }
        
        .mobile-nav-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        /* Mobile Search Overlay */
        .mobile-search-overlay {
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
        }
        
        .mobile-search-overlay.active {
            opacity: 1;
            visibility: visible;
        }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Mobile Menu Overlay -->
    <div class="mobile-menu-overlay" id="mobileMenuOverlay"></div>
    
    <!-- Mobile Menu -->
    <div class="mobile-menu" id="mobileMenu">
        <div class="p-6 border-b border-indigo-600">
            <div class="flex justify-between items-center">
                <h2 class="text-xl font-bold text-white">Menu</h2>
                <button id="closeMobileMenu" class="text-white text-2xl">&times;</button>
            </div>
        </div>
        <nav class="p-6">
            <ul class="space-y-4">
                <li><a href="{base_path}index.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Home</a></li>
                <li><a href="{base_path}search.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Search</a></li>
                <li><a href="{base_path}authors.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Authors</a></li>
                <li><a href="{base_path}integrated/categories.html" class="mobile-nav-item block text-indigo-200 text-lg py-2 border-b border-indigo-600/30">Categories</a></li>
                <li><a href="{base_path}integrated/trending.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Trending</a></li>
            </ul>
        </nav>
    </div>

    <!-- Mobile Search Overlay -->
    <div class="mobile-search-overlay" id="mobileSearchOverlay">
        <div class="mobile-search-container">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-800">Search</h2>
                <button id="closeMobileSearch" class="text-gray-500 text-3xl">&times;</button>
            </div>
            <div class="relative mb-6">
                <input type="text" id="mobileSearchInput" placeholder="Search articles, authors, categories..." 
                       class="w-full px-4 py-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                       onkeyup="handleMobileSearch(event)">
                <button onclick="performMobileSearch()" 
                        class="absolute right-3 top-1/2 transform -translate-y-1/2 text-indigo-600 text-xl">🔍</button>
            </div>
            <div id="mobileSearchSuggestions" class="bg-white border border-gray-200 rounded-lg hidden max-h-60 overflow-y-auto"></div>
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
            <div class="flex items-center space-x-4">
                <nav class="hidden md:block">
                    <ul class="flex space-x-8">
                        <li><a href="{base_path}index.html" class="hover:text-indigo-200 transition font-medium">Home</a></li>
                        <li><a href="{base_path}search.html" class="hover:text-indigo-200 transition font-medium">Search</a></li>
                        <li><a href="{base_path}authors.html" class="hover:text-indigo-200 transition font-medium">Authors</a></li>
                        <li><a href="{base_path}integrated/categories.html" class="hover:text-indigo-200 transition font-medium text-indigo-200">Categories</a></li>
                        <li><a href="{base_path}integrated/trending.html" class="hover:text-indigo-200 transition font-medium">Trending</a></li>
                    </ul>
                </nav>
                
                <!-- Mobile Search Button -->
                <button class="md:hidden text-white text-xl" id="mobileSearchToggle" aria-label="Open mobile search">
                    🔍
                </button>
                
                <!-- Mobile Menu Button -->
                <button class="md:hidden hamburger" id="mobileMenuToggle" aria-label="Toggle mobile menu">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
            </div>
        </div>
    </header>

    <!-- Category Hero -->
    <section class="py-20" style="background: linear-gradient(135deg, {{CATEGORY_COLOR}}, {{CATEGORY_COLOR}}99);">
        <div class="container mx-auto px-4 text-center text-white">
            <h1 class="text-5xl font-bold mb-4 hero-title">{{CATEGORY_NAME}}</h1>
            <p class="text-xl mb-6">{{CATEGORY_DESCRIPTION}}</p>
            <div class="text-lg">
                <span class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                    {{ARTICLE_COUNT}} articles available
                </span>
            </div>
        </div>
    </section>

    <!-- Articles Grid -->
    <main class="container mx-auto px-4 py-12">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {{ARTICLES_CONTENT}}
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-300 py-12 mt-20">
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
        
        function openMobileMenu() {
            mobileMenu.classList.add('active');
            mobileMenuOverlay.classList.add('active');
            mobileMenuToggle.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        function closeMobileMenuFunc() {
            mobileMenu.classList.remove('active');
            mobileMenuOverlay.classList.remove('active');
            mobileMenuToggle.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', openMobileMenu);
        }
        
        if (closeMobileMenu) {
            closeMobileMenu.addEventListener('click', closeMobileMenuFunc);
        }
        
        if (mobileMenuOverlay) {
            mobileMenuOverlay.addEventListener('click', closeMobileMenuFunc);
        }
        
        // Close mobile menu when clicking on a link
        document.querySelectorAll('.mobile-nav-item').forEach(item => {
            item.addEventListener('click', closeMobileMenuFunc);
        });
        
        // Mobile Search Functionality
        const mobileSearchToggle = document.getElementById('mobileSearchToggle');
        const closeMobileSearchBtn = document.getElementById('closeMobileSearch');
        const mobileSearchOverlay = document.getElementById('mobileSearchOverlay');
        const mobileSearchInput = document.getElementById('mobileSearchInput');
        const mobileSearchSuggestions = document.getElementById('mobileSearchSuggestions');
        
        const searchData = {{SEARCH_DATA}};
        
        function openMobileSearch() {
            mobileSearchOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            // Focus on search input after animation
            setTimeout(() => {
                mobileSearchInput.focus();
            }, 300);
        }
        
        function closeMobileSearchFunc() {
            mobileSearchOverlay.classList.remove('active');
            document.body.style.overflow = '';
            mobileSearchSuggestions.classList.add('hidden');
            mobileSearchInput.value = '';
        }
        
        if (mobileSearchToggle) {
            mobileSearchToggle.addEventListener('click', openMobileSearch);
        }
        
        if (closeMobileSearchBtn) {
            closeMobileSearchBtn.addEventListener('click', closeMobileSearchFunc);
        }
        
        if (mobileSearchOverlay) {
            mobileSearchOverlay.addEventListener('click', function(e) {
                if (e.target === mobileSearchOverlay) {
                    closeMobileSearchFunc();
                }
            });
        }
        
        function handleMobileSearch(event) {
            const query = event.target.value.toLowerCase();
            
            if (query.length > 1) {
                const matches = searchData.filter(item => 
                    item.toLowerCase().includes(query)
                ).slice(0, 5);
                
                if (matches.length > 0) {
                    mobileSearchSuggestions.innerHTML = matches.map(match => 
                        `<div class="p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0" onclick="selectMobileSuggestion('${match}')">${match}</div>`
                    ).join('');
                    mobileSearchSuggestions.classList.remove('hidden');
                } else {
                    mobileSearchSuggestions.classList.add('hidden');
                }
            } else {
                mobileSearchSuggestions.classList.add('hidden');
            }
            
            if (event.key === 'Enter') {
                performMobileSearch();
            }
        }
        
        function selectMobileSuggestion(suggestion) {
            mobileSearchInput.value = suggestion;
            mobileSearchSuggestions.classList.add('hidden');
            performMobileSearch();
        }
        
        function performMobileSearch() {
            const query = mobileSearchInput.value;
            if (query.trim()) {
                // Close mobile search and redirect to search page
                closeMobileSearchFunc();
                window.location.href = `{base_path}search.html?q=${encodeURIComponent(query)}`;
            }
        }

    </script>
</body>
</html>''').replace('{base_path}', base_path)

    # Required abstract methods
    def parse_content_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a category file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Split into sections
        sections = content.split('\n---\n')
        if len(sections) < 2:
            raise ValueError(f"Invalid format in {file_path}. Missing '---' separator.")
        
        # Parse metadata
        metadata = self.parse_metadata_section(sections[0])
        description_content = '\n---\n'.join(sections[1:]).strip()
        
        # Map color names to hex codes
        color_map = {
            'blue': '#3B82F6',
            'green': '#10B981', 
            'orange': '#F59E0B',
            'pink': '#EC4899',
            'purple': '#8B5CF6',
            'red': '#EF4444',
            'gray': '#6B7280'
        }
        
        color = metadata.get('color', 'gray')
        if color in color_map:
            color = color_map[color]
        elif not color.startswith('#'):
            color = '#6B7280'  # Default gray
        
        return {
            'name': metadata.get('name', ''),
            'slug': metadata.get('slug', ''),
            'description': metadata.get('description', description_content.split('\n')[0] if description_content else ''),
            'color': color,
            'icon': metadata.get('icon', '📁'),
            'sort_order': int(metadata.get('sort_order', 999))
        }
        
    def create_content_page(self, content_data):
        """Create content page - use create_category_page instead"""
        pass
        
    def update_listing_page(self, content_list):
        """Update listing page - use create_categories_listing instead"""
        pass
        
    def create_sample_file(self):
        """Create sample file"""
        pass
    
    def process_category(self, content_data: Dict[str, Any]) -> bool:
        """Process category content and add to database"""
        try:
            # Generate slug from filename or title
            slug = content_data.get('slug') or content_data.get('name', '').lower().replace(' ', '-')
            if not slug and 'filename' in content_data:
                slug = content_data['filename'].replace('.txt', '')
                
            # Check if category already exists
            existing = Category.find_by_slug(slug)
            if existing:
                self.update_progress(f"Category '{content_data.get('name', slug)}' already exists, skipping")
                return False
            
            # Create category
            category = Category(
                name=content_data.get('name', slug.title()),
                slug=slug,
                description=content_data.get('description', ''),
                color=content_data.get('color', '#6B7280'),
                icon=content_data.get('icon', '📁'),
                sort_order=content_data.get('sort_order', 999)
            )
            
            # Save to database
            category.save()
            
            # Handle image if provided
            if content_data.get('image'):
                self.convert_image_urls(
                    content={'image': content_data['image'], 'name': category.name},
                    content_type='category',
                    content_id=category.id,
                    slug=slug
                )
            
            self.update_progress(f"Successfully added category: {category.name}")
            return True
            
        except Exception as e:
            self.update_progress(f"Error processing category: {str(e)}")
            return False

    def get_categories_listing_template(self, base_path=""):
        """Get categories listing template"""
        return ('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Categories - Influencer News</title>
    <link rel="stylesheet" href="{base_path}assets/css/styles.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .hero-title { font-family: 'Playfair Display', serif; }
    
        /* Mobile Menu Styles */
        .mobile-menu {
            position: fixed;
            top: 0;
            right: -100%;
            width: 80%;
            max-width: 300px;
            height: 100vh;
            background: #312e81;
            transition: right 0.3s ease-in-out;
            z-index: 1000;
        }
        
        .mobile-menu.active {
            right: 0;
        }
        
        .mobile-menu-overlay {
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
        }
        
        .mobile-menu-overlay.active {
            opacity: 1;
            visibility: visible;
        }
        
        .hamburger {
            width: 30px;
            height: 24px;
            position: relative;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .hamburger span {
            display: block;
            width: 100%;
            height: 3px;
            background: white;
            border-radius: 3px;
            transition: all 0.3s ease-in-out;
        }
        
        .hamburger.active span:nth-child(1) {
            transform: rotate(45deg) translate(8px, 8px);
        }
        
        .hamburger.active span:nth-child(2) {
            opacity: 0;
        }
        
        .hamburger.active span:nth-child(3) {
            transform: rotate(-45deg) translate(8px, -8px);
        }
        
        .mobile-nav-item {
            display: block;
            padding: 1rem 2rem;
            color: white;
            text-decoration: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            transition: background 0.3s ease;
        }
        
        .mobile-nav-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        /* Mobile Search Overlay */
        .mobile-search-overlay {
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
        }
        
        .mobile-search-overlay.active {
            opacity: 1;
            visibility: visible;
        }
    </style>
</head>
<body class="bg-gray-50">
    <!-- Mobile Menu Overlay -->
    <div class="mobile-menu-overlay" id="mobileMenuOverlay"></div>
    
    <!-- Mobile Menu -->
    <div class="mobile-menu" id="mobileMenu">
        <div class="p-6 border-b border-indigo-600">
            <div class="flex justify-between items-center">
                <h2 class="text-xl font-bold text-white">Menu</h2>
                <button id="closeMobileMenu" class="text-white text-2xl">&times;</button>
            </div>
        </div>
        <nav class="p-6">
            <ul class="space-y-4">
                <li><a href="{base_path}index.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Home</a></li>
                <li><a href="{base_path}search.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Search</a></li>
                <li><a href="{base_path}authors.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Authors</a></li>
                <li><a href="{base_path}integrated/categories.html" class="mobile-nav-item block text-indigo-200 text-lg py-2 border-b border-indigo-600/30">Categories</a></li>
                <li><a href="{base_path}integrated/trending.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Trending</a></li>
            </ul>
        </nav>
    </div>

    <!-- Mobile Search Overlay -->
    <div class="mobile-search-overlay" id="mobileSearchOverlay">
        <div class="mobile-search-container">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-800">Search</h2>
                <button id="closeMobileSearch" class="text-gray-500 text-3xl">&times;</button>
            </div>
            <div class="relative mb-6">
                <input type="text" id="mobileSearchInput" placeholder="Search articles, authors, categories..." 
                       class="w-full px-4 py-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                       onkeyup="handleMobileSearch(event)">
                <button onclick="performMobileSearch()" 
                        class="absolute right-3 top-1/2 transform -translate-y-1/2 text-indigo-600 text-xl">🔍</button>
            </div>
            <div id="mobileSearchSuggestions" class="bg-white border border-gray-200 rounded-lg hidden max-h-60 overflow-y-auto"></div>
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
            <div class="flex items-center space-x-4">
                <nav class="hidden md:block">
                    <ul class="flex space-x-8">
                        <li><a href="{base_path}index.html" class="hover:text-indigo-200 transition font-medium">Home</a></li>
                        <li><a href="{base_path}search.html" class="hover:text-indigo-200 transition font-medium">Search</a></li>
                        <li><a href="{base_path}authors.html" class="hover:text-indigo-200 transition font-medium">Authors</a></li>
                        <li><a href="{base_path}integrated/categories.html" class="hover:text-indigo-200 transition font-medium text-indigo-200">Categories</a></li>
                        <li><a href="{base_path}integrated/trending.html" class="hover:text-indigo-200 transition font-medium">Trending</a></li>
                    </ul>
                </nav>
                
                <!-- Mobile Search Button -->
                <button class="md:hidden text-white text-xl" id="mobileSearchToggle" aria-label="Open mobile search">
                    🔍
                </button>
                
                <!-- Mobile Menu Button -->
                <button class="md:hidden hamburger" id="mobileMenuToggle" aria-label="Toggle mobile menu">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="bg-gradient-to-br from-indigo-900 via-purple-800 to-indigo-700 text-white py-20">
        <div class="container mx-auto px-4 text-center">
            <h1 class="text-5xl font-bold mb-4 hero-title">Content Categories</h1>
            <p class="text-xl mb-6">Explore our diverse range of influencer and creator content</p>
            <div class="text-lg">
                <span class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                    {{CATEGORY_COUNT}} categories available
                </span>
            </div>
        </div>
    </section>

    <!-- Categories Grid -->
    <main class="container mx-auto px-4 py-12">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {{CATEGORIES_CONTENT}}
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-300 py-12 mt-20">
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
        
        function openMobileMenu() {
            mobileMenu.classList.add('active');
            mobileMenuOverlay.classList.add('active');
            mobileMenuToggle.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        function closeMobileMenuFunc() {
            mobileMenu.classList.remove('active');
            mobileMenuOverlay.classList.remove('active');
            mobileMenuToggle.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', openMobileMenu);
        }
        
        if (closeMobileMenu) {
            closeMobileMenu.addEventListener('click', closeMobileMenuFunc);
        }
        
        if (mobileMenuOverlay) {
            mobileMenuOverlay.addEventListener('click', closeMobileMenuFunc);
        }
        
        // Close mobile menu when clicking on a link
        document.querySelectorAll('.mobile-nav-item').forEach(item => {
            item.addEventListener('click', closeMobileMenuFunc);
        });
        
        // Mobile Search Functionality
        const mobileSearchToggle = document.getElementById('mobileSearchToggle');
        const closeMobileSearchBtn = document.getElementById('closeMobileSearch');
        const mobileSearchOverlay = document.getElementById('mobileSearchOverlay');
        const mobileSearchInput = document.getElementById('mobileSearchInput');
        const mobileSearchSuggestions = document.getElementById('mobileSearchSuggestions');
        
        const searchData = {{SEARCH_DATA}};
        
        function openMobileSearch() {
            mobileSearchOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            // Focus on search input after animation
            setTimeout(() => {
                mobileSearchInput.focus();
            }, 300);
        }
        
        function closeMobileSearchFunc() {
            mobileSearchOverlay.classList.remove('active');
            document.body.style.overflow = '';
            mobileSearchSuggestions.classList.add('hidden');
            mobileSearchInput.value = '';
        }
        
        if (mobileSearchToggle) {
            mobileSearchToggle.addEventListener('click', openMobileSearch);
        }
        
        if (closeMobileSearchBtn) {
            closeMobileSearchBtn.addEventListener('click', closeMobileSearchFunc);
        }
        
        if (mobileSearchOverlay) {
            mobileSearchOverlay.addEventListener('click', function(e) {
                if (e.target === mobileSearchOverlay) {
                    closeMobileSearchFunc();
                }
            });
        }
        
        function handleMobileSearch(event) {
            const query = event.target.value.toLowerCase();
            
            if (query.length > 1) {
                const matches = searchData.filter(item => 
                    item.toLowerCase().includes(query)
                ).slice(0, 5);
                
                if (matches.length > 0) {
                    mobileSearchSuggestions.innerHTML = matches.map(match => 
                        `<div class="p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0" onclick="selectMobileSuggestion('${match}')">${match}</div>`
                    ).join('');
                    mobileSearchSuggestions.classList.remove('hidden');
                } else {
                    mobileSearchSuggestions.classList.add('hidden');
                }
            } else {
                mobileSearchSuggestions.classList.add('hidden');
            }
            
            if (event.key === 'Enter') {
                performMobileSearch();
            }
        }
        
        function selectMobileSuggestion(suggestion) {
            mobileSearchInput.value = suggestion;
            mobileSearchSuggestions.classList.add('hidden');
            performMobileSearch();
        }
        
        function performMobileSearch() {
            const query = mobileSearchInput.value;
            if (query.trim()) {
                // Close mobile search and redirect to search page
                closeMobileSearchFunc();
                window.location.href = `{base_path}search.html?q=${encodeURIComponent(query)}`;
            }
        }

    </script>
</body>
</html>''').replace('{base_path}', base_path)
    
    def update_all_listing_pages(self):
        """Update all listing pages with current categories from database"""
        self.update_progress("Updating category listing pages...")
        
        # Get all categories from database
        from ..models.category import Category
        categories = Category.find_all()
        
        # Update the main categories listing page
        self.create_categories_listing(categories)
        
        self.update_progress(f"Updated listing pages with {len(categories)} categories")
