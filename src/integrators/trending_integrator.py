#!/usr/bin/env python3
"""
Trending Topics Integrator
==========================
Handles trending topics integration with database
"""

from pathlib import Path
from typing import Dict, List, Any
try:
    from .base_integrator import BaseIntegrator
    from ..models.trending import TrendingTopic
except ImportError:
    from src.integrators.base_integrator import BaseIntegrator
    from src.models.trending import TrendingTopic


class TrendingIntegrator(BaseIntegrator):
    """Trending topics content integrator"""
    
    def __init__(self):
        super().__init__('trending', 'trending')
        
    def sync_all(self):
        """Sync all trending topics from database"""
        self.update_progress("Starting trending topics sync...")
        
        try:
            # Get all trending topics from database
            topics = TrendingTopic.find_all()
            
            if not topics:
                self.update_progress("No trending topics found in database")
                return
                
            # Create individual trending topic pages
            for topic in topics:
                self.create_trending_page(topic)
                
            # Create trending listing page
            self.create_trending_listing(topics)
            
            self.update_progress(f"Synced {len(topics)} trending topics successfully")
            
        except Exception as e:
            self.update_progress(f"Error syncing trending topics: {e}")
            raise
            
    def create_trending_page(self, topic):
        """Create individual trending topic page"""
        try:
            # Get path manager for this location
            path_manager = self.get_path_manager(f"integrated/trending/trend_{topic.slug}.html")
            base_path = path_manager.get_base_path()
            
            # Read template
            template_content = self.get_trending_template(base_path)
            
            # Get dynamic data from topic
            heat_score = getattr(topic, 'heat_score', getattr(topic, 'trend_score', 0))
            description = getattr(topic, 'description', getattr(topic, 'analysis', f'Explore the latest on {topic.title}')[:200] + '...' if getattr(topic, 'analysis', '') else f'Explore the latest on {topic.title}')
            
            # Apply site branding first
            content = self._apply_site_branding(template_content)
            
            # Replace placeholders
            replacements = {
                '{{TOPIC_TITLE}}': topic.title,
                '{{TOPIC_DESCRIPTION}}': description,
                '{{HEAT_SCORE}}': str(heat_score),
                '{{TREND_CONTENT}}': self.generate_trend_content(topic, base_path)
            }
            
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            
            # Save file
            filename = self.integrated_dir / f"trend_{topic.slug}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.update_progress(f"Created trending page: {filename.name}")
            
        except Exception as e:
            self.update_progress(f"Error creating trending page for {topic.title}: {e}")
            
    def create_trending_listing(self, topics):
        """Create trending topics listing page"""
        try:
            # Get path manager for this location
            path_manager = self.get_path_manager("integrated/trending.html")
            base_path = path_manager.get_base_path()
            
            # Read template
            template_content = self.get_trending_listing_template(base_path)
            
            # Generate trending cards
            topics_html = self.generate_trending_cards(topics, base_path)
            
            # Apply site branding first
            content = self._apply_site_branding(template_content)
            
            # Replace placeholders
            content = content.replace('{{TRENDING_CONTENT}}', topics_html)
            content = content.replace('{{TOPIC_COUNT}}', str(len(topics)))
            
            # Save file (listing goes in main integrated dir, not subfolder)
            from pathlib import Path
            filename = Path("integrated") / "trending.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.update_progress(f"Created trending listing: {filename.name}")
            
        except Exception as e:
            self.update_progress(f"Error creating trending listing: {e}")
            
    def generate_trending_cards(self, topics, base_path=""):
        """Generate HTML for trending topic cards"""
        cards_html = ""
        
        # Sort by heat score (descending) - use trend_score as fallback
        sorted_topics = sorted(topics, key=lambda t: getattr(t, 'heat_score', getattr(t, 'trend_score', 0)), reverse=True)
        
        for i, topic in enumerate(sorted_topics):
            # Use heat_score or trend_score as fallback
            heat_score = getattr(topic, 'heat_score', getattr(topic, 'trend_score', 0))
            
            # Get custom icon if available, otherwise use heat-based indicator
            topic_icon = getattr(topic, 'icon', None)
            
            # Get heat indicator based on score ranges
            if heat_score >= 8000:
                heat_indicator = topic_icon or "🔥🔥🔥"
                heat_class = "text-red-600"
                heat_bg = "bg-red-100"
            elif heat_score >= 6000:
                heat_indicator = topic_icon or "🔥🔥"
                heat_class = "text-orange-600"
                heat_bg = "bg-orange-100"
            elif heat_score >= 3000:
                heat_indicator = topic_icon or "🔥"
                heat_class = "text-yellow-600"
                heat_bg = "bg-yellow-100"
            else:
                heat_indicator = topic_icon or "📈"
                heat_class = "text-blue-600"
                heat_bg = "bg-blue-100"
                
            # Rank badge
            rank_badge = ""
            if i < 3:
                rank_colors = ["bg-yellow-500", "bg-gray-400", "bg-orange-600"]
                rank_badge = f'<div class="absolute top-4 left-4 w-8 h-8 {rank_colors[i]} text-white rounded-full flex items-center justify-center font-bold text-sm">#{i+1}</div>'
            
            # Get description from analysis field if available, otherwise use description
            description_text = getattr(topic, 'description', '')
            if not description_text and hasattr(topic, 'analysis'):
                analysis_text = getattr(topic, 'analysis', '')
                description_text = analysis_text[:150] + '...' if len(analysis_text) > 150 else analysis_text
            elif not description_text:
                description_text = f'Discover more about {topic.title}'
                
            # Get image path - use proper assets folder structure
            image_url = getattr(topic, 'image_url', None) or f'{base_path}assets/placeholders/trending_placeholder.svg'
            
            cards_html += f'''
            <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow relative">
                {rank_badge}
                <div class="relative">
                    <img src="{image_url}" 
                         alt="{self.escape_html(topic.title)}" 
                         class="w-full h-48 object-cover">
                    <div class="absolute top-4 right-4">
                        <span class="{heat_bg} {heat_class} px-3 py-1 rounded-full text-sm font-bold">
                            {heat_indicator} {heat_score}
                        </span>
                    </div>
                </div>
                <div class="p-6">
                    <h3 class="text-xl font-bold mb-3 hover:text-emerald-600 transition">
                        <a href="trending/trend_{topic.slug}.html">{self.escape_html(topic.title)}</a>
                    </h3>
                    <p class="text-gray-700 mb-4 text-sm">
                        {self.escape_html(description_text)}
                    </p>
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-gray-500">{heat_indicator} Heat Score: {heat_score}</span>
                        <a href="trending/trend_{topic.slug}.html" 
                           class="text-emerald-600 font-medium">Explore →</a>
                    </div>
                </div>
            </div>
            '''
            
        return cards_html
        
    def generate_trend_content(self, topic, base_path=""):
        """Generate content for trending topic page using dynamic data"""
        # Use analysis field if available, otherwise fall back to content or generate default
        analysis_content = getattr(topic, 'analysis', '')
        content = getattr(topic, 'content', '')
        
        # Get dynamic metrics
        heat_score = getattr(topic, 'heat_score', getattr(topic, 'trend_score', 0))
        growth_rate = getattr(topic, 'growth_rate', 0)
        platform_data = getattr(topic, 'platform_data', {})
        
        # Calculate total mentions from platform data
        total_mentions = 0
        if isinstance(platform_data, dict):
            total_mentions = sum(platform_data.values())
        
        # Get engagement level based on heat score
        if heat_score >= 8000:
            engagement_level = "Viral"
        elif heat_score >= 5000:
            engagement_level = "Very High"
        elif heat_score >= 2000:
            engagement_level = "High"
        else:
            engagement_level = "Moderate"
        
        # Generate content using analysis if available
        if analysis_content:
            # Format the analysis content with proper HTML structure
            formatted_analysis = self.format_analysis_content(analysis_content)
            
            content = f'''
            <div class="bg-white rounded-2xl shadow-lg p-8 mb-8">
                <h2 class="text-3xl font-bold mb-6 hero-title">About This Trend</h2>
                <div class="text-gray-700 text-lg mb-6">
                    {formatted_analysis}
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="text-center p-4 bg-gray-50 rounded-lg">
                        <div class="text-3xl font-bold text-emerald-600">{heat_score:,}</div>
                        <div class="text-sm text-gray-600">Heat Score</div>
                    </div>
                    <div class="text-center p-4 bg-gray-50 rounded-lg">
                        <div class="text-3xl font-bold text-green-600">{total_mentions:,}</div>
                        <div class="text-sm text-gray-600">Total Mentions</div>
                    </div>
                    <div class="text-center p-4 bg-gray-50 rounded-lg">
                        <div class="text-3xl font-bold text-purple-600">{engagement_level}</div>
                        <div class="text-sm text-gray-600">Engagement</div>
                    </div>
                </div>
            </div>
            
            {self.generate_platform_breakdown(platform_data) if platform_data else ''}
            {self.generate_growth_metrics(growth_rate, heat_score)}
            '''
        else:
            # Generate default content based on topic
            description = getattr(topic, 'description', f'{topic.title} is currently trending in the influencer space.')
            content = f'''
            <div class="bg-white rounded-2xl shadow-lg p-8 mb-8">
                <h2 class="text-3xl font-bold mb-6 hero-title">About This Trend</h2>
                <p class="text-gray-700 text-lg mb-6">
                    {self.escape_html(description)}
                </p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="text-center p-4 bg-gray-50 rounded-lg">
                        <div class="text-3xl font-bold text-emerald-600">{heat_score:,}</div>
                        <div class="text-sm text-gray-600">Heat Score</div>
                    </div>
                    <div class="text-center p-4 bg-gray-50 rounded-lg">
                        <div class="text-3xl font-bold text-green-600">{total_mentions:,}</div>
                        <div class="text-sm text-gray-600">Total Mentions</div>
                    </div>
                    <div class="text-center p-4 bg-gray-50 rounded-lg">
                        <div class="text-3xl font-bold text-purple-600">{engagement_level}</div>
                        <div class="text-sm text-gray-600">Engagement</div>
                    </div>
                </div>
            </div>
            
            <div class="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-8 mb-8">
                <h3 class="text-2xl font-bold mb-4">Why It's Trending</h3>
                <p class="text-gray-700 mb-4">
                    This topic has gained significant traction in the influencer community due to its relevance 
                    to current events and creator interests.
                </p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 class="font-bold mb-2">Key Factors:</h4>
                        <ul class="list-disc list-inside text-gray-700 space-y-1">
                            <li>High engagement rates</li>
                            <li>Viral content creation</li>
                            <li>Platform algorithm boost</li>
                            <li>Creator community interest</li>
                        </ul>
                    </div>
                    <div>
                        <h4 class="font-bold mb-2">Impact Areas:</h4>
                        <ul class="list-disc list-inside text-gray-700 space-y-1">
                            <li>Content creation trends</li>
                            <li>Monetization opportunities</li>
                            <li>Brand partnerships</li>
                            <li>Platform features</li>
                        </ul>
                    </div>
                </div>
            </div>
            '''
        
        return content
        
    def format_analysis_content(self, analysis):
        """Format analysis content with proper HTML structure"""
        if not analysis:
            return ""
            
        # Split analysis into paragraphs and format
        paragraphs = analysis.split('\n\n')
        formatted = ""
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Check if it's a header (contains colons or is short)
                if ':' in paragraph and len(paragraph) < 100:
                    formatted += f'<h4 class="font-bold text-lg mb-3 mt-6">{self.escape_html(paragraph.strip())}</h4>\n'
                else:
                    formatted += f'<p class="mb-4">{self.escape_html(paragraph.strip())}</p>\n'
                    
        return formatted
        
    def generate_platform_breakdown(self, platform_data):
        """Generate platform breakdown visualization"""
        if not platform_data or not isinstance(platform_data, dict):
            return ""
            
        platform_cards = ""
        platforms = {
            'youtube': {'name': 'YouTube', 'color': 'red', 'icon': '🎥'},
            'tiktok': {'name': 'TikTok', 'color': 'pink', 'icon': '🎵'},
            'instagram': {'name': 'Instagram', 'color': 'purple', 'icon': '📸'},
            'twitter': {'name': 'Twitter', 'color': 'blue', 'icon': '🐦'},
            'twitch': {'name': 'Twitch', 'color': 'indigo', 'icon': '🎮'}
        }
        
        for platform, count in platform_data.items():
            if count > 0 and platform in platforms:
                info = platforms[platform]
                platform_cards += f'''
                <div class="bg-white p-4 rounded-lg shadow-sm border">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-semibold text-{info['color']}-600">{info['icon']} {info['name']}</span>
                        <span class="text-2xl font-bold text-{info['color']}-700">{count:,}</span>
                    </div>
                    <div class="text-sm text-gray-600">mentions</div>
                </div>
                '''
                
        if platform_cards:
            return f'''
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 mb-8">
                <h3 class="text-2xl font-bold mb-6">Platform Breakdown</h3>
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                    {platform_cards}
                </div>
            </div>
            '''
        return ""
        
    def generate_growth_metrics(self, growth_rate, heat_score):
        """Generate growth metrics section"""
        growth_indicator = "📈" if growth_rate > 0 else "📉" if growth_rate < 0 else "➡️"
        growth_color = "text-green-600" if growth_rate > 0 else "text-red-600" if growth_rate < 0 else "text-gray-600"
        
        return f'''
        <div class="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <h3 class="text-2xl font-bold mb-6">Trend Metrics</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-gradient-to-br from-indigo-50 to-blue-50 p-6 rounded-xl">
                    <div class="flex items-center mb-2">
                        <span class="text-2xl mr-2">{growth_indicator}</span>
                        <h4 class="font-bold text-lg">Growth Rate</h4>
                    </div>
                    <div class="text-3xl font-bold {growth_color} mb-2">{growth_rate:.1f}%</div>
                    <p class="text-sm text-gray-600">Current trend momentum</p>
                </div>
                <div class="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-xl">
                    <div class="flex items-center mb-2">
                        <span class="text-2xl mr-2">🔥</span>
                        <h4 class="font-bold text-lg">Heat Level</h4>
                    </div>
                    <div class="text-3xl font-bold text-purple-600 mb-2">{heat_score:,}</div>
                    <p class="text-sm text-gray-600">Current trending score</p>
                </div>
            </div>
        </div>
        '''
        
    def get_trending_template(self, base_path=""):
        """Get trending topic page template"""
        return ('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TOPIC_TITLE}} - Trending | Influencer News</title>
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
                <li><a href="{base_path}integrated/categories.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Categories</a></li>
                <li><a href="{base_path}integrated/trending.html" class="mobile-nav-item block text-indigo-200 text-lg py-2 border-b border-indigo-600/30">Trending</a></li>
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
                        class="absolute right-3 top-1/2 transform -translate-y-1/2 text-emerald-600 text-xl">🔍</button>
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
            <nav class="hidden md:block">
                <ul class="flex space-x-8">
                    <li><a href="{base_path}index.html" class="hover:text-indigo-200 transition font-medium">Home</a></li>
                    <li><a href="{base_path}search.html" class="hover:text-indigo-200 transition font-medium">Search</a></li>
                    <li><a href="{base_path}authors.html" class="hover:text-indigo-200 transition font-medium">Authors</a></li>
                    <li><a href="{base_path}integrated/categories.html" class="hover:text-indigo-200 transition font-medium">Categories</a></li>
                    <li><a href="{base_path}integrated/trending.html" class="hover:text-indigo-200 transition font-medium text-indigo-200">Trending</a></li>
                </ul>
                        <!-- Mobile Menu Button -->
            <button class="md:hidden hamburger" id="mobileMenuToggle" aria-label="Toggle mobile menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
            </nav>
        </div>
    </header>

    <!-- Trending Hero -->
    <section class="bg-gradient-to-br from-red-600 via-orange-500 to-yellow-500 text-white py-20">
        <div class="container mx-auto px-4 text-center">
            <div class="text-6xl mb-6">🔥</div>
            <h1 class="text-5xl font-bold mb-4 hero-title">{{TOPIC_TITLE}}</h1>
            <p class="text-xl mb-6">{{TOPIC_DESCRIPTION}}</p>
            <div class="text-lg">
                <span class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                    🔥 Heat Score: {{HEAT_SCORE}}
                </span>
            </div>
        </div>
    </section>

    <!-- Content -->
    <main class="container mx-auto px-4 py-12">
        {{TREND_CONTENT}}
        
        <!-- Related Articles -->
        <div class="bg-white rounded-2xl shadow-lg p-8 mt-8">
            <h3 class="text-2xl font-bold mb-6 hero-title">Related Articles</h3>
            <p class="text-gray-600">Articles related to this trending topic will appear here.</p>
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
        
        const searchData = [
            'MrBeast', 'Emma Chamberlain', 'PewDiePie', 'Charli DAmelio', 'Logan Paul',
            'Creator Economy', 'TikTok Algorithm', 'YouTube Shorts', 'Instagram Reels',
            'Brand Partnerships', 'Influencer Marketing', 'Social Media Trends'
        ];
        
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
        """Parse a trending topic file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Split into sections
        sections = content.split('\n---\n')
        if len(sections) < 2:
            raise ValueError(f"Invalid format in {file_path}. Missing '---' separator.")
        
        # Parse metadata
        metadata = self.parse_metadata_section(sections[0])
        topic_content = '\n---\n'.join(sections[1:]).strip()
        
        # Map field names from file format to expected format
        return {
            'title': metadata.get('topic', ''),
            'hashtag': metadata.get('hashtag', ''),
            'description': topic_content.split('\n')[0] if topic_content else '',
            'content': topic_content,
            'heat_score': int(metadata.get('trend_score', 50)),
            'growth_rate': float(metadata.get('growth_rate', 0.0)),
            'status': metadata.get('status', 'active'),
            'mentions_youtube': int(metadata.get('youtube_mentions', 0)),
            'mentions_tiktok': int(metadata.get('tiktok_mentions', 0)),
            'mentions_instagram': int(metadata.get('instagram_mentions', 0)),
            'mentions_twitter': int(metadata.get('twitter_mentions', 0)),
            'mentions_twitch': int(metadata.get('twitch_mentions', 0))
        }
        
    def create_content_page(self, content_data):
        """Create content page - use create_trending_page instead"""
        pass
        
    def update_listing_page(self, content_list):
        """Update listing page - use create_trending_listing instead"""
        pass
        
    def _apply_site_branding(self, html_content: str) -> str:
        """Apply site configuration to HTML content"""
        try:
            site_integrator = self.get_site_integrator()
            branding = site_integrator.get_config_section('branding')
            contact = site_integrator.get_config_section('contact')
            
            # Create replacements dictionary - use site config dynamically
            replacements = {
                # Site name replacements
                'Influencer News': branding.get('site_name'),
                # Title tag replacements
                ' - Influencer News': f" - {branding.get('site_name')}",
                '| Influencer News': f"| {branding.get('site_name')}",
                # Header logo text
                '>IN<': f">{branding.get('logo_text')}<",
                # Header tagline
                'Breaking stories • Real insights': branding.get('site_tagline'),
                # Theme color replacements - comprehensive
                '#4f46e5': branding.get('theme_color'),  # indigo-500
                '#6366f1': branding.get('theme_color'),  # indigo-500 variant
                '#312e81': branding.get('theme_color'),  # indigo-900
                '#4338ca': branding.get('theme_color'),  # indigo-700
                '#3730a3': branding.get('theme_color'),  # indigo-800
                '#1e1b4b': branding.get('theme_color'),  # indigo-950
                '#667eea': branding.get('theme_color'),  # custom indigo
                # Convert specific indigo classes to use theme color
                'bg-indigo-900': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}900",
                'bg-indigo-800': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}800",
                'bg-indigo-700': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}700",
                'bg-indigo-600': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'bg-indigo-500': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}500",
                'bg-indigo-400': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}400",
                'bg-indigo-200': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}200",
                'bg-indigo-100': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}100",
                'bg-indigo-50': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}50",
                'text-indigo-900': f"text-{self._get_theme_class_name(branding.get('theme_color'))}900",
                'text-indigo-800': f"text-{self._get_theme_class_name(branding.get('theme_color'))}800",
                'text-indigo-700': f"text-{self._get_theme_class_name(branding.get('theme_color'))}700",
                'text-indigo-600': f"text-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'text-indigo-200': f"text-{self._get_theme_class_name(branding.get('theme_color'))}200",
                'text-indigo-100': f"text-{self._get_theme_class_name(branding.get('theme_color'))}100",
                'border-indigo-700': f"border-{self._get_theme_class_name(branding.get('theme_color'))}700",
                'border-indigo-600': f"border-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'hover:bg-indigo-600': f"hover:bg-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'hover:text-indigo-600': f"hover:text-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'hover:text-indigo-200': f"hover:text-{self._get_theme_class_name(branding.get('theme_color'))}200",
                'focus:ring-indigo-400': f"focus:ring-{self._get_theme_class_name(branding.get('theme_color'))}400",
                'focus:ring-indigo-500': f"focus:ring-{self._get_theme_class_name(branding.get('theme_color'))}500",
                'from-indigo-400': f"from-{self._get_theme_class_name(branding.get('theme_color'))}400",
                'from-indigo-600': f"from-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'from-indigo-900': f"from-{self._get_theme_class_name(branding.get('theme_color'))}900",
                'to-purple-600': f"to-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'to-purple-800': f"to-{self._get_theme_class_name(branding.get('theme_color'))}800",
                'via-purple-800': f"via-{self._get_theme_class_name(branding.get('theme_color'))}800",
                # Footer copyright
                '© 2025 Influencer News': f"© 2025 {branding.get('site_name')}",
                # Contact info updates
                'news@influencernews.com': contact.get('contact_email'),
                '(555) 123-NEWS': contact.get('contact_phone'),
                '123 Creator Avenue': contact.get('business_address'),
                'Los Angeles, CA 90210': f"{contact.get('city', 'New York')}, {contact.get('state', 'NY')} {contact.get('zip_code', '10001')}"
            }
            
            # Apply all replacements
            for old_value, new_value in replacements.items():
                if old_value and new_value:  # Only replace if both values exist and are not None
                    html_content = html_content.replace(old_value, str(new_value))
            
            return html_content
            
        except Exception as e:
            print(f"Warning: Could not apply site branding to trending page: {e}")
            return html_content
    
    def _get_theme_class_name(self, theme_color: str) -> str:
        """Convert theme color to appropriate Tailwind class name"""
        if not theme_color:
            return 'indigo-'
        
        # Map common colors to Tailwind classes
        color_map = {
            '#059669': 'emerald-',
            '#10b981': 'emerald-',
            '#3b82f6': 'blue-',
            '#8b5cf6': 'violet-',
            '#f59e0b': 'amber-',
            '#ef4444': 'red-',
            '#6b7280': 'gray-'
        }
        
        return color_map.get(theme_color.lower(), 'emerald-')
    
    def create_sample_file(self):
        """Create sample file"""
        pass
    
    def process_trending(self, content_data: Dict[str, Any]) -> bool:
        """Process trending topic content and add to database"""
        try:
            # Generate slug from filename or title
            title = content_data.get('topic', content_data.get('title', ''))
            slug = content_data.get('slug') or title.lower().replace(' ', '-')
            if not slug and 'filename' in content_data:
                slug = content_data['filename'].replace('.txt', '')
                
            # Check if trending topic already exists
            existing = TrendingTopic.find_by_slug(slug)
            if existing:
                self.update_progress(f"Trending topic '{title}' already exists, skipping")
                return False
            
            # Get heat score from trend_score or heat_score
            heat_score = int(content_data.get('trend_score', content_data.get('heat_score', 50)))
            
            # Create trending topic with rich data
            topic = TrendingTopic(
                title=title,
                slug=slug,
                description=content_data.get('description', ''),
                content=content_data.get('content', ''),
                heat_score=heat_score,
                growth_rate=float(content_data.get('growth_rate', 0.0)),
                hashtag=content_data.get('hashtag', ''),
                status=content_data.get('status', 'active'),
                icon=content_data.get('icon', ''),
                analysis=content_data.get('analysis', ''),
                platform_data=content_data.get('platform_data', {}),
                mentions_youtube=int(content_data.get('mentions_youtube', content_data.get('platform_data', {}).get('youtube', 0))),
                mentions_tiktok=int(content_data.get('mentions_tiktok', content_data.get('platform_data', {}).get('tiktok', 0))),
                mentions_instagram=int(content_data.get('mentions_instagram', content_data.get('platform_data', {}).get('instagram', 0))),
                mentions_twitter=int(content_data.get('mentions_twitter', content_data.get('platform_data', {}).get('twitter', 0))),
                mentions_twitch=int(content_data.get('mentions_twitch', content_data.get('platform_data', {}).get('twitch', 0)))
            )
            
            # Save to database
            topic.save()
            
            # Handle image if provided
            if content_data.get('image'):
                self.convert_image_urls(
                    content={'image': content_data['image'], 'title': topic.title},
                    content_type='trending',
                    content_id=topic.id,
                    slug=slug
                )
            
            self.update_progress(f"Successfully added trending topic: {topic.title}")
            return True
            
        except Exception as e:
            self.update_progress(f"Error processing trending topic: {str(e)}")
            return False

    def get_trending_listing_template(self, base_path=""):
        """Get trending topics listing template"""
        return ('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trending Topics - Influencer News</title>
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
                <li><a href="{base_path}integrated/categories.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Categories</a></li>
                <li><a href="{base_path}integrated/trending.html" class="mobile-nav-item block text-indigo-200 text-lg py-2 border-b border-indigo-600/30">Trending</a></li>
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
                        class="absolute right-3 top-1/2 transform -translate-y-1/2 text-emerald-600 text-xl">🔍</button>
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
            <nav class="hidden md:block">
                <ul class="flex space-x-8">
                    <li><a href="{base_path}index.html" class="hover:text-indigo-200 transition font-medium">Home</a></li>
                    <li><a href="{base_path}search.html" class="hover:text-indigo-200 transition font-medium">Search</a></li>
                    <li><a href="{base_path}authors.html" class="hover:text-indigo-200 transition font-medium">Authors</a></li>
                    <li><a href="{base_path}integrated/categories.html" class="hover:text-indigo-200 transition font-medium">Categories</a></li>
                    <li><a href="{base_path}integrated/trending.html" class="hover:text-indigo-200 transition font-medium text-indigo-200">Trending</a></li>
                </ul>
                        <!-- Mobile Menu Button -->
            <button class="md:hidden hamburger" id="mobileMenuToggle" aria-label="Toggle mobile menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
            </nav>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="bg-gradient-to-br from-red-600 via-orange-500 to-yellow-500 text-white py-20">
        <div class="container mx-auto px-4 text-center">
            <div class="text-8xl mb-6">🔥</div>
            <h1 class="text-5xl font-bold mb-4 hero-title">Trending Now</h1>
            <p class="text-xl mb-6">Discover what's hot in the influencer world</p>
            <div class="text-lg">
                <span class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                    {{TOPIC_COUNT}} trending topics
                </span>
            </div>
        </div>
    </section>

    <!-- Trending Grid -->
    <main class="container mx-auto px-4 py-12">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {{TRENDING_CONTENT}}
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
        
        const searchData = [
            'MrBeast', 'Emma Chamberlain', 'PewDiePie', 'Charli DAmelio', 'Logan Paul',
            'Creator Economy', 'TikTok Algorithm', 'YouTube Shorts', 'Instagram Reels',
            'Brand Partnerships', 'Influencer Marketing', 'Social Media Trends'
        ];
        
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
        """Update all listing pages with current trending topics from database"""
        self.update_progress("Updating trending listing pages...")
        
        # Get all trending topics from database
        from ..models.trending import TrendingTopic
        trending_topics = TrendingTopic.find_all()
        
        # Update the main trending listing page
        self.create_trending_listing(trending_topics)
        
        self.update_progress(f"Updated listing pages with {len(trending_topics)} trending topics")
