#!/usr/bin/env python3
"""
Mobile Template Updater for Integrators
=======================================
Updates all integrator templates to include mobile support
"""

import re
import os
from pathlib import Path
from typing import Dict, List


class MobileTemplateUpdater:
    """Updates integrator templates with mobile support"""
    
    def __init__(self):
        self.src_dir = Path("src/integrators")
        self.integrator_files = [
            "category_integrator.py",
            "trending_integrator.py", 
            "author_integrator.py",
            "article_integrator.py"
        ]
        
        # Mobile CSS styles to inject
        self.mobile_css = '''
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
        }'''
        
        # Mobile HTML to inject after <body>
        self.mobile_html = '''    <!-- Mobile Menu Overlay -->
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
            <a href="{{HOME_PATH}}" class="mobile-nav-item">🏠 Home</a>
            <a href="{{SEARCH_PATH}}" class="mobile-nav-item">🔍 Search</a>
            <a href="{{AUTHORS_PATH}}" class="mobile-nav-item">👥 Authors</a>
            <a href="{{CATEGORIES_PATH}}" class="mobile-nav-item">📂 Categories</a>
            <a href="{{TRENDING_PATH}}" class="mobile-nav-item">🔥 Trending</a>
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
'''
        
        # Mobile JavaScript to inject
        self.mobile_js = '''
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
                window.location.href = `{{SEARCH_URL}}?q=${encodeURIComponent(query)}`;
            }
        }
'''
    
    def update_all_integrators(self):
        """Update all integrator files with mobile support"""
        print("🚀 Updating all integrator templates with mobile support...")
        
        results = {}
        
        for filename in self.integrator_files:
            file_path = self.src_dir / filename
            if file_path.exists():
                print(f"\n📄 Processing {filename}...")
                try:
                    result = self.update_integrator_file(file_path)
                    results[filename] = result
                    print(f"   ✅ {result['message']}")
                except Exception as e:
                    results[filename] = {"success": False, "message": str(e)}
                    print(f"   ❌ Error: {str(e)}")
            else:
                results[filename] = {"success": False, "message": "File not found"}
                print(f"   ⚠️ File not found: {filename}")
        
        return results
    
    def update_integrator_file(self, file_path: Path) -> Dict[str, any]:
        """Update a single integrator file with mobile support"""
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # 1. Replace Tailwind CDN with optimized CSS
        if 'cdn.tailwindcss.com' in content:
            # Determine the correct path depth based on integrator type
            if 'article_integrator' in str(file_path):
                css_path = '../../assets/css/styles.min.css'
            elif any(x in str(file_path) for x in ['category_integrator', 'trending_integrator', 'author_integrator']):
                css_path = '../assets/css/styles.min.css'
            else:
                css_path = 'assets/css/styles.min.css'
            
            content = re.sub(
                r'<script src="https://cdn\.tailwindcss\.com"></script>',
                f'<link rel="stylesheet" href="{css_path}">',
                content
            )
            changes_made.append("Replaced Tailwind CDN with optimized CSS")
        
        # 2. Add mobile CSS styles
        if self.mobile_css.strip() not in content:
            # Find the closing </style> tag and inject mobile CSS before it
            content = re.sub(
                r'(\s*)(</style>)',
                r'\1' + self.mobile_css + r'\1\2',
                content
            )
            changes_made.append("Added mobile CSS styles")
        
        # 3. Add mobile HTML elements after <body>
        if 'mobile-menu' not in content:
            # Customize mobile HTML based on the integrator type
            mobile_html = self.customize_mobile_html(file_path)
            
            # Find <body> tag and inject mobile HTML after it
            content = re.sub(
                r'(<body[^>]*>)',
                r'\1\n' + mobile_html,
                content
            )
            changes_made.append("Added mobile menu and search overlay HTML")
        
        # 4. Add mobile navigation buttons to header
        if 'mobileMenuToggle' not in content:
            # Add hamburger menu button
            header_pattern = r'(</nav>)'
            hamburger_html = '''            <!-- Mobile Menu Button -->
            <button class="md:hidden hamburger" id="mobileMenuToggle" aria-label="Toggle mobile menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
            '''
            
            content = re.sub(header_pattern, hamburger_html + r'\1', content)
            changes_made.append("Added mobile menu button to header")
        
        # 5. Update desktop navigation to be hidden on mobile
        if 'hidden md:block' not in content:
            content = re.sub(
                r'<nav class="([^"]*)"',
                r'<nav class="hidden md:block \1"',
                content
            )
            changes_made.append("Made desktop navigation hidden on mobile")
        
        # 6. Add mobile search button if search bar exists
        if 'searchInput' in content and 'mobileSearchToggle' not in content:
            search_pattern = r'(</div>\s*</div>\s*</header>)'
            mobile_search_html = '''            
            <!-- Mobile Search Button -->
            <button class="md:hidden text-white p-2" id="mobileSearchToggle" aria-label="Toggle mobile search">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
            </button>
        </div>
        </div>
    </header>'''
            
            content = re.sub(search_pattern, mobile_search_html, content)
            changes_made.append("Added mobile search button")
        
        # 7. Add mobile JavaScript
        if 'openMobileMenu' not in content:
            # Customize mobile JS based on integrator type
            mobile_js = self.customize_mobile_js(file_path)
            
            # Find where to inject JS (before closing script tag or at end)
            if '</script>' in content:
                content = re.sub(
                    r'(\s*)(</script>)',
                    r'\1' + mobile_js + r'\1\2',
                    content,
                    count=1
                )
            else:
                # Add script tag at end of body
                content = re.sub(
                    r'(</body>)',
                    r'    <script>\n' + mobile_js + r'\n    </script>\n\1',
                    content
                )
            changes_made.append("Added mobile JavaScript functionality")
        
        # Write the updated content back to the file
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"Updated with {len(changes_made)} changes: {', '.join(changes_made)}",
                "changes": changes_made
            }
        else:
            return {
                "success": True,
                "message": "No changes needed - mobile support already present",
                "changes": []
            }
    
    def customize_mobile_html(self, file_path: Path) -> str:
        """Customize mobile HTML based on integrator type"""
        mobile_html = self.mobile_html
        
        # Determine navigation paths based on integrator type
        if 'article_integrator' in str(file_path):
            # Articles are 2 levels deep: integrated/articles/
            paths = {
                '{{HOME_PATH}}': '../../index.html',
                '{{SEARCH_PATH}}': '../../search.html',
                '{{AUTHORS_PATH}}': '../../authors.html',
                '{{CATEGORIES_PATH}}': '../categories.html',
                '{{TRENDING_PATH}}': '../trending.html'
            }
        elif any(x in str(file_path) for x in ['category_integrator', 'trending_integrator']):
            # Categories/trending are 2 levels deep: integrated/categories/ or integrated/trending/
            paths = {
                '{{HOME_PATH}}': '../../index.html',
                '{{SEARCH_PATH}}': '../../search.html',
                '{{AUTHORS_PATH}}': '../../authors.html',
                '{{CATEGORIES_PATH}}': '../categories.html',
                '{{TRENDING_PATH}}': '../trending.html'
            }
        elif 'author_integrator' in str(file_path):
            # Authors are 2 levels deep: integrated/authors/
            paths = {
                '{{HOME_PATH}}': '../../index.html',
                '{{SEARCH_PATH}}': '../../search.html',
                '{{AUTHORS_PATH}}': '../../authors.html',
                '{{CATEGORIES_PATH}}': '../categories.html',
                '{{TRENDING_PATH}}': '../trending.html'
            }
        else:
            # Default paths
            paths = {
                '{{HOME_PATH}}': 'index.html',
                '{{SEARCH_PATH}}': 'search.html',
                '{{AUTHORS_PATH}}': 'authors.html',
                '{{CATEGORIES_PATH}}': 'integrated/categories.html',
                '{{TRENDING_PATH}}': 'integrated/trending.html'
            }
        
        # Replace path placeholders
        for placeholder, path in paths.items():
            mobile_html = mobile_html.replace(placeholder, path)
        
        return mobile_html
    
    def customize_mobile_js(self, file_path: Path) -> str:
        """Customize mobile JavaScript based on integrator type"""
        mobile_js = self.mobile_js
        
        # Determine search URL path based on integrator type
        if 'article_integrator' in str(file_path):
            search_url = '../../search.html'
        elif any(x in str(file_path) for x in ['category_integrator', 'trending_integrator', 'author_integrator']):
            search_url = '../../search.html'
        else:
            search_url = 'search.html'
        
        mobile_js = mobile_js.replace('{{SEARCH_URL}}', search_url)
        
        return mobile_js


def main():
    """Main function to update all integrator templates"""
    print("🚀 Mobile Template Updater for Integrators")
    print("=" * 50)
    
    updater = MobileTemplateUpdater()
    results = updater.update_all_integrators()
    
    print("\n" + "=" * 50)
    print("📊 Update Summary:")
    
    success_count = 0
    for filename, result in results.items():
        if result["success"]:
            success_count += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} {filename}: {result['message']}")
    
    print(f"\n🎯 {success_count}/{len(results)} integrators updated successfully!")
    
    if success_count == len(results):
        print("✨ All integrator templates now have mobile support!")
        print("📱 Generated pages will include:")
        print("   - Mobile navigation menu with hamburger button")
        print("   - Mobile search overlay")
        print("   - Responsive design optimizations")
        print("   - Touch-friendly interactions")
    else:
        print("⚠️  Some integrators failed to update. Check the errors above.")
    
    return 0 if success_count == len(results) else 1


if __name__ == "__main__":
    exit(main())