#!/usr/bin/env python3
"""
Author Integrator
=================
Manages author profiles and generates author pages using SQLite database
"""

import random
from pathlib import Path
from typing import Dict, List, Any, Optional
try:
    from .base_integrator import BaseIntegrator
    from ..models import Author, Article, Image
except ImportError:
    from src.integrators.base_integrator import BaseIntegrator
    from src.models import Author, Article, Image


class AuthorIntegrator(BaseIntegrator):
    """Integrator for managing author profiles with database backend"""
    
    def __init__(self):
        super().__init__('authors', 'authors')
        
        # Role mappings
        self.roles = {
            'senior': ['Senior Editor', 'Senior Reporter', 'Senior Correspondent'],
            'correspondent': ['Correspondent', 'Reporter', 'Journalist'],
            'contributor': ['Contributor', 'Guest Writer', 'Freelancer']
        }
    
    def sync_all(self):
        """Sync all authors from database"""
        self.update_progress("Starting author sync...")
        
        try:
            # Get all authors from database
            authors = Author.find_all()
            
            if not authors:
                self.update_progress("No authors found in database")
                return
                
            # Create individual author pages
            for author in authors:
                self.create_content_page(author)
                
            # Update the authors listing page
            self.update_listing_page(authors)
            
            self.update_progress(f"Synced {len(authors)} authors successfully")
            
        except Exception as e:
            self.update_progress(f"Error syncing authors: {e}")
            raise
    
    def parse_content_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse an author file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Split into sections
        sections = content.split('\n---\n')
        if len(sections) < 2:
            raise ValueError(f"Invalid format in {file_path}. Missing '---' separator.")
        
        # Parse metadata
        metadata = self.parse_metadata_section(sections[0])
        bio_content = '\n---\n'.join(sections[1:]).strip()
        
        # Validate required fields
        required_fields = ['name', 'title', 'bio', 'image']
        self.validate_required_fields(metadata, required_fields, file_path)
        
        # Determine role category
        title_lower = metadata['title'].lower()
        role_category = 'contributor'  # default
        for role, titles in self.roles.items():
            if any(t.lower() in title_lower for t in titles):
                role_category = role
                break
        
        # Parse expertise list
        expertise = [e.strip() for e in metadata.get('expertise', '').split(',') if e.strip()]
        
        return {
            'name': metadata['name'],
            'title': metadata['title'],
            'bio': metadata['bio'],
            'extended_bio': bio_content,
            'image': metadata['image'],
            'location': metadata.get('location', 'Remote'),
            'expertise': expertise,
            'email': metadata.get('email', ''),
            'twitter': metadata.get('twitter', ''),
            'linkedin': metadata.get('linkedin', ''),
            'articles_written': int(metadata.get('articles_written', random.randint(10, 500))),
            'role_category': role_category,
            'rating': round(random.uniform(4.5, 5.0), 1),
            'joined_date': metadata.get('joined_date', '2020-01-01'),
            'verified': metadata.get('verified', 'true').lower() == 'true'
        }
    
    def process_author(self, content_data: Dict[str, Any]) -> bool:
        """Process author content and store in database"""
        # Generate slug from filename
        slug = content_data['filename'].replace('.txt', '')
        
        # Check if already exists
        existing = Author.find_by_slug(slug)
        if existing:
            self.update_progress(f"Author {content_data['name']} already exists", None)
            return False
        
        # Create author in database
        author = Author(
            name=content_data['name'],
            slug=slug,
            title=content_data['title'],
            bio=content_data['bio'],
            location=content_data.get('location'),
            expertise=', '.join(content_data['expertise']),
            linkedin=content_data.get('linkedin'),
            twitter=content_data.get('twitter'),
            rating=content_data.get('rating', 0.0),
            joined_date=content_data.get('joined_date', '2025-01-01')
        )
        author.save()
        
        # Convert image URL to local reference
        if content_data.get('image'):
            self.convert_image_urls(content_data, 'author', author.id, slug)
        
        # Create author page
        self.create_content_page(author)
        
        return True
    
    def create_content_page(self, author: Author):
        """Create individual author page"""
        # Generate author page filename
        author_filename = self.integrated_dir / f"author_{author.slug}.html"
        
        # Get path manager for this location
        path_manager = self.get_path_manager(f"integrated/authors/author_{author.slug}.html")
        base_path = path_manager.get_base_path()
        
        # Get author's articles
        articles = author.get_articles(limit=10)
        
        # Get author's images
        profile_image = author.get_profile_image()
        
        # Generate image tag
        if profile_image:
            img_tag = self.image_manager.generate_img_tag(
                profile_image['local_filename'],
                profile_image['alt_text'],
                'author',
                'rounded-full object-cover',
                base_path
            )
        else:
            # Use placeholder
            img_tag = f'<img src="{base_path}assets/placeholders/author_placeholder.svg" alt="{author.name}" class="rounded-full object-cover">'
        
        # Create HTML content for author page with mobile support
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{author.name} - Author Profile | Influencer News</title>
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
                        <h1 class="text-4xl font-bold text-white mb-2">{self.escape_html(author.name)}</h1>
                        <p class="text-xl text-indigo-100 mb-4">{self.escape_html(author.title or 'Contributor')}</p>
                        <div class="flex space-x-4">
                            {'<span class="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm">✓ Verified</span>' if hasattr(author, 'verified') else ''}
                            {f'<span class="bg-white/20 text-white px-3 py-1 rounded-full text-sm">📍 {self.escape_html(author.location)}</span>' if author.location else ''}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="p-8">
                <div class="grid md:grid-cols-3 gap-8">
                    <!-- Bio Section -->
                    <div class="md:col-span-2">
                        <h2 class="text-2xl font-bold mb-4">About</h2>
                        <p class="text-gray-700 mb-6 leading-relaxed">{self.escape_html(author.bio)}</p>
                        
                        <!-- Expertise -->
                        <div class="mb-8">
                            <h3 class="text-xl font-semibold mb-3">Areas of Expertise</h3>
                            <div class="flex flex-wrap gap-2">
                                {' '.join([f'<span class="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm">{self.escape_html(exp)}</span>' for exp in (author.expertise.split(', ') if author.expertise else [])])}
                            </div>
                        </div>
                        
                        <!-- Stats -->
                        <div class="grid grid-cols-3 gap-4 mb-8">
                            <div class="bg-gray-50 p-4 rounded-lg text-center">
                                <div class="text-2xl font-bold text-indigo-600">{author.get_article_count()}</div>
                                <div class="text-sm text-gray-600">Articles</div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded-lg text-center">
                                <div class="text-2xl font-bold text-indigo-600">{author.rating if hasattr(author, 'rating') and author.rating else 'N/A'}</div>
                                <div class="text-sm text-gray-600">Rating</div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded-lg text-center">
                                <div class="text-2xl font-bold text-indigo-600">{author.joined_date.split('-')[0] if author.joined_date else 'N/A'}</div>
                                <div class="text-sm text-gray-600">Joined</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Contact Section -->
                    <div>
                        <div class="bg-gray-50 p-6 rounded-lg">
                            <h3 class="text-xl font-semibold mb-4">Connect</h3>
                            <div class="space-y-3">
                                {f'<a href="mailto:{author.email}" class="flex items-center text-gray-700 hover:text-indigo-600"><span class="mr-2">📧</span> Email</a>' if hasattr(author, 'email') and author.email else ''}
                                {f'<a href="{author.get_twitter_url()}" target="_blank" class="flex items-center text-gray-700 hover:text-indigo-600"><span class="mr-2">🐦</span> Twitter</a>' if author.twitter else ''}
                                {f'<a href="{author.get_full_linkedin_url()}" target="_blank" class="flex items-center text-gray-700 hover:text-indigo-600"><span class="mr-2">💼</span> LinkedIn</a>' if author.linkedin else ''}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Recent Articles -->
                <div class="mt-12">
                    <h2 class="text-2xl font-bold mb-6">Recent Articles</h2>
                    <div class="grid md:grid-cols-2 gap-6">
                        {self._generate_article_cards(articles, base_path)}
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
            'Sarah Chen', 'Jessica Kim', 'Alex Rivera', 'Michael Torres', 'Maria Lopez',
            'Creator Economy', 'Business Reporter', 'Tech Correspondent', 'Entertainment Editor'
        ];
        
        function openMobileSearch() {{
            mobileSearchOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
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
            
            // Add scroll listeners
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {{
                        target.scrollIntoView({{ behavior: 'smooth' }});
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>'''
        
        # Write the HTML file
        with open(author_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_article_cards(self, articles: List[Article], base_path: str) -> str:
        """Generate HTML for article cards"""
        if not articles:
            return '<p class="text-gray-500 col-span-2">No articles published yet.</p>'
        
        cards = []
        for article in articles[:6]:  # Limit to 6 articles
            # Get article thumbnail
            thumbnail = article.get_thumbnail_image()
            if thumbnail:
                img_tag = self.image_manager.generate_img_tag(
                    thumbnail['local_filename'],
                    thumbnail['alt_text'],
                    'article',
                    'w-full h-48 object-cover',
                    base_path
                )
            else:
                img_tag = f'<img src="{base_path}assets/placeholders/article_placeholder.svg" alt="{article.title}" class="w-full h-48 object-cover">'
            
            card = f'''
            <article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition">
                {img_tag}
                <div class="p-6">
                    <div class="flex items-center mb-2">
                        <span class="bg-{self.get_category_color(article.category_slug)}-100 text-{self.get_category_color(article.category_slug)}-800 px-2 py-1 rounded text-xs">
                            {article.category_icon or ''} {article.category_name}
                        </span>
                        <span class="text-gray-500 text-sm ml-auto">{self.format_date_relative(article.publication_date)}</span>
                    </div>
                    <h3 class="text-xl font-semibold mb-2 line-clamp-2">
                        <a href="{base_path}integrated/articles/article_{article.id}.html" class="hover:text-indigo-600">
                            {self.escape_html(article.title)}
                        </a>
                    </h3>
                    <p class="text-gray-600 line-clamp-2">{self.escape_html(article.subtitle or '')}</p>
                </div>
            </article>
            '''
            cards.append(card)
        
        return '\n'.join(cards)
    
    def update_listing_page(self, authors: List[Author]):
        """Update the main authors listing page"""
        # This will be called from update_all_listing_pages
        self._regenerate_authors_page()
    
    def update_all_listing_pages(self):
        """Update all author-related listing pages"""
        self._regenerate_authors_page()
    
    def _regenerate_authors_page(self):
        """Regenerate the main authors.html page"""
        # Get all authors from database
        authors = Author.find_all()
        
        # Get path manager for authors.html
        path_manager = self.get_path_manager("authors.html")
        base_path = path_manager.get_base_path()
        
        # Generate author cards
        author_cards = []
        for author in authors:
            # Get author's profile image
            profile_image = author.get_profile_image()
            
            if profile_image:
                img_tag = self.image_manager.generate_img_tag(
                    profile_image['local_filename'],
                    profile_image['alt_text'],
                    'author',
                    'w-24 h-24 rounded-full object-cover',
                    base_path
                )
            else:
                img_tag = f'<img src="{base_path}assets/placeholders/author_placeholder.svg" alt="{author.name}" class="w-24 h-24 rounded-full object-cover">'
            
            article_count = author.get_article_count()
            
            card = f'''
            <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition">
                <div class="flex items-center space-x-4 mb-4">
                    {img_tag}
                    <div>
                        <h3 class="text-xl font-semibold">
                            <a href="{base_path}integrated/authors/author_{author.slug}.html" class="hover:text-indigo-600">
                                {self.escape_html(author.name)}
                            </a>
                        </h3>
                        <p class="text-gray-600">{self.escape_html(author.title or 'Contributor')}</p>
                    </div>
                </div>
                <p class="text-gray-700 mb-4 line-clamp-3">{self.escape_html(author.bio)}</p>
                <div class="flex justify-between items-center">
                    <span class="text-sm text-gray-500">{article_count} articles</span>
                    <a href="{base_path}integrated/authors/author_{author.slug}.html" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                        View Profile →
                    </a>
                </div>
            </div>
            '''
            author_cards.append(card)
        
        # Update authors.html
        authors_html_path = Path("authors.html")
        if authors_html_path.exists():
            with open(authors_html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find and replace the authors grid section
            import re
            pattern = r'<div[^>]*id="authorsGrid"[^>]*>.*?</div>\s*(?=<!--\s*Join Our Team Section\s*-->)'
            replacement = f'<div id="authorsGrid" class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">\n{"".join(author_cards)}\n</div>'
            
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            with open(authors_html_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def create_sample_file(self):
        """Create a sample author file"""
        sample_content = '''Name: Jane Smith
Title: Senior Technology Correspondent
Bio: Award-winning journalist covering the intersection of technology and influencer culture
Image: https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop&crop=face
Location: San Francisco, CA
Expertise: Technology, AI, Creator Tools, Platform Analysis
Email: jane.smith@influencernews.com
Twitter: @janesmith_tech
LinkedIn: linkedin.com/in/janesmith
Articles Written: 127
Joined Date: 2021-03-15
Verified: true

---

Jane Smith is an award-winning technology correspondent with over a decade of experience covering the digital landscape. She specializes in analyzing how emerging technologies shape the creator economy and influence digital culture.

Before joining Influencer News, Jane was a senior writer at TechCrunch, where she broke several major stories about creator platforms and monetization tools. She has also contributed to Wired, The Verge, and MIT Technology Review.

Jane's reporting focuses on:

• **Platform Innovation**: Deep dives into how social media platforms evolve their creator tools and monetization features
• **AI and Creators**: Exploring how artificial intelligence is transforming content creation and audience engagement
• **Creator Economy Trends**: Analysis of market movements, funding rounds, and industry shifts
• **Technology Ethics**: Examining the ethical implications of influencer marketing and creator platforms

She holds a Master's degree in Digital Media from MIT and a Bachelor's in Journalism from Northwestern University. When she's not reporting on the latest tech trends, Jane hosts a weekly podcast about the creator economy and speaks at industry conferences worldwide.

Jane has been recognized with several awards, including:
- 2023 Digital Journalism Award for Technology Reporting
- 2022 Creator Economy Reporter of the Year
- 2021 Tech Writers Guild Excellence Award

Connect with Jane to discuss technology trends, creator tools, or potential story ideas. She's always interested in hearing from creators and industry professionals about emerging technologies and their impact on the digital landscape.'''
        
        sample_path = self.content_dir / "jane-smith.txt"
        with open(sample_path, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        self.update_progress(f"Created sample author file: {sample_path}", 100)
    
