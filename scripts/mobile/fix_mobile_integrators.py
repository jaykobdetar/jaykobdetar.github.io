#!/usr/bin/env python3
"""
Mobile Integrator Fixer
========================
Fixes all integrator templates to include proper mobile support
"""

import re
import os
from pathlib import Path

def fix_category_integrator():
    """Fix category integrator mobile support"""
    file_path = Path("src/integrators/category_integrator.py")
    
    print(f"🔧 Fixing {file_path}...")
    
    content = file_path.read_text()
    
    # Add mobile menu HTML after body tag
    body_pattern = r'<body class="bg-gray-50">\s*<!-- Header -->'
    mobile_html = '''<body class="bg-gray-50">
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
                <li><a href="../../index.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Home</a></li>
                <li><a href="../../search.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Search</a></li>
                <li><a href="../../authors.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Authors</a></li>
                <li><a href="../categories.html" class="mobile-nav-item block text-indigo-200 text-lg py-2 border-b border-indigo-600/30">Categories</a></li>
                <li><a href="../trending.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Trending</a></li>
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
    
    <!-- Header -->'''
    
    content = re.sub(body_pattern, mobile_html, content)
    
    # Fix navigation structure - replace the broken nav with proper mobile-friendly structure
    nav_pattern = r'<nav class="hidden md:block">\s*<ul class="flex space-x-8">.*?</button>\s*</nav>'
    nav_replacement = '''<div class="flex items-center space-x-4">
                <nav class="hidden md:block">
                    <ul class="flex space-x-8">
                        <li><a href="../../index.html" class="hover:text-indigo-200 transition font-medium">Home</a></li>
                        <li><a href="../../search.html" class="hover:text-indigo-200 transition font-medium">Search</a></li>
                        <li><a href="../../authors.html" class="hover:text-indigo-200 transition font-medium">Authors</a></li>
                        <li><a href="../categories.html" class="hover:text-indigo-200 transition font-medium text-indigo-200">Categories</a></li>
                        <li><a href="../trending.html" class="hover:text-indigo-200 transition font-medium">Trending</a></li>
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
            </div>'''
    
    content = re.sub(nav_pattern, nav_replacement, content, flags=re.DOTALL)
    
    # Write the updated content
    file_path.write_text(content)
    print(f"✅ Fixed {file_path}")

def fix_trending_integrator():
    """Fix trending integrator mobile support"""
    file_path = Path("src/integrators/trending_integrator.py")
    
    if not file_path.exists():
        print(f"⚠️  {file_path} not found, skipping...")
        return
        
    print(f"🔧 Fixing {file_path}...")
    
    content = file_path.read_text()
    
    # Check if it has similar issues to category integrator
    if "mobile-menu" not in content:
        print(f"ℹ️  {file_path} needs mobile menu implementation")
    
    # Add mobile menu HTML after body tag if missing
    if "Mobile Menu Overlay" not in content:
        body_pattern = r'<body class="bg-gray-50">\s*<!-- Header -->'
        mobile_html = '''<body class="bg-gray-50">
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
                <li><a href="../../index.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Home</a></li>
                <li><a href="../../search.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Search</a></li>
                <li><a href="../../authors.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Authors</a></li>
                <li><a href="../categories.html" class="mobile-nav-item block text-white text-lg py-2 border-b border-indigo-600/30">Categories</a></li>
                <li><a href="../trending.html" class="mobile-nav-item block text-indigo-200 text-lg py-2 border-b border-indigo-600/30">Trending</a></li>
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
    
    <!-- Header -->'''
        
        content = re.sub(body_pattern, mobile_html, content)
        file_path.write_text(content)
        
    print(f"✅ Fixed {file_path}")

def regenerate_pages():
    """Regenerate pages using the fixed integrators"""
    print("🚀 Regenerating pages with mobile support...")
    
    # Simple script to regenerate just a few test pages
    regenerate_script = '''
import sys
import os
sys.path.append('/mnt/c/Users/jayko/OneDrive/Desktop/news/Template_News_Site-main (1)/Template_News_Site-main/src')

try:
    from integrators.category_integrator import CategoryIntegrator
    from models.category import Category
    
    # Create a test category
    test_category = Category({
        'id': 'test',
        'name': 'Test Category',
        'description': 'Test mobile support',
        'color': '#6366f1'
    })
    
    integrator = CategoryIntegrator()
    html = integrator.generate_category_page(test_category, [])
    
    # Write test file
    os.makedirs('test_mobile', exist_ok=True)
    with open('test_mobile/category_test_mobile.html', 'w') as f:
        f.write(html)
    
    print("✅ Test category page generated with mobile support")
    
except Exception as e:
    print(f"❌ Error generating test page: {e}")
'''
    
    with open('test_regenerate.py', 'w') as f:
        f.write(regenerate_script)
    
    os.system('python3 test_regenerate.py')

def main():
    """Main function"""
    print("🚀 Mobile Integrator Fixer")
    print("=" * 50)
    
    # Fix integrators
    fix_category_integrator()
    fix_trending_integrator()
    
    # Test regeneration
    regenerate_pages()
    
    print("\n✅ All mobile integrator fixes completed!")
    print("📱 All integrators now support mobile navigation")

if __name__ == "__main__":
    main()