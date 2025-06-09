#!/usr/bin/env python3
"""
Link Verification & Fix Script
===============================
This script ensures all links between pages work correctly.
"""

import os
import re
from pathlib import Path

class LinkFixer:
    def __init__(self):
        self.pages = {
            'index.html': 'Homepage',
            'search.html': 'Search Page', 
            'article.html': 'Article Template',
            'authors.html': 'Authors Page',
            '404.html': '404 Page'
        }
        
        self.fixes_applied = 0

    def fix_navigation_links(self):
        """Fix navigation links across all pages"""
        navigation_fixes = {
            'index.html': [
                ('class="nav-link hover:text-indigo-200 transition font-medium">Home</a>', 'class="nav-link hover:text-indigo-200 transition font-medium text-indigo-200">Home</a>'),
                ('href="#"', 'href="index.html"'),
                ('searchRedirect()', 'performSearch()'),
            ],
            'search.html': [
                ('class="nav-link hover:text-indigo-200 transition font-medium">Search</a>', 'class="nav-link hover:text-indigo-200 transition font-medium text-indigo-200">Search</a>'),
            ],
            'article.html': [
                ('href="#"', 'href="search.html?category=business"'),
            ],
            'authors.html': [
                ('class="nav-link hover:text-indigo-200 transition font-medium">Authors</a>', 'class="nav-link hover:text-indigo-200 transition font-medium text-indigo-200">Authors</a>'),
            ],
            '404.html': [
                ('href="#"', 'href="search.html?category=business"'),
            ]
        }
        
        for filename, fixes in navigation_fixes.items():
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for old, new in fixes:
                    content = content.replace(old, new)
                
                if content != original_content:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Fixed navigation in {filename}")
                    self.fixes_applied += 1

    def add_missing_functions(self):
        """Add missing JavaScript functions"""
        
        # Fix homepage search function
        if os.path.exists('index.html'):
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'function handleSearch(' not in content:
                search_function = '''
        function handleSearch(event) {
            if (event.key === 'Enter') {
                performSearch();
            }
        }

        function performSearch() {
            const query = document.getElementById('searchInput').value;
            if (query.trim()) {
                window.location.href = `search.html?q=${encodeURIComponent(query)}`;
            }
        }'''
                
                # Insert before the last script tag
                content = content.replace('</script>\n</body>', search_function + '\n</script>\n</body>')
                
                with open('index.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ Added search functions to index.html")
                self.fixes_applied += 1

    def fix_article_links(self):
        """Fix article links to use proper filenames"""
        for filename in self.pages.keys():
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix article links
                content = re.sub(r'href="article\.html\?id=(\d+)"', r'href="article_\1.html"', content)
                content = re.sub(r'onclick="openArticle\((\d+)\)"', r'onclick="window.location.href=\'article_\1.html\'"', content)
                
                if content != original_content:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Fixed article links in {filename}")
                    self.fixes_applied += 1

    def verify_links(self):
        """Verify all links are working"""
        print("\n🔍 Verifying Links...")
        
        all_files = set()
        broken_links = []
        
        # Collect all HTML files
        for file in Path('.').glob('*.html'):
            all_files.add(file.name)
        
        # Check links in each file
        for filename in self.pages.keys():
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all href links
                links = re.findall(r'href="([^"]+)"', content)
                
                for link in links:
                    if link.startswith('#') or link.startswith('http') or link.startswith('mailto'):
                        continue  # Skip anchors, external links, and emails
                    
                    # Extract filename from link
                    if '?' in link:
                        link_file = link.split('?')[0]
                    else:
                        link_file = link
                    
                    if link_file and link_file not in all_files and not link_file.startswith('article_'):
                        broken_links.append(f"{filename} → {link}")
        
        if broken_links:
            print("⚠️  Found broken links:")
            for link in broken_links:
                print(f"   - {link}")
        else:
            print("✅ All links appear to be working!")

    def create_sitemap(self):
        """Create a simple sitemap"""
        sitemap_content = """# Website Sitemap

## Main Pages
- index.html (Homepage)
- search.html (Search & Browse)
- authors.html (Editorial Team)
- 404.html (Error Pages)

## Article Pages
- article.html (Template - used by Python script)
- article_1.html (Generated articles)
- article_2.html
- ...etc

## Navigation Structure
```
Homepage (index.html)
├── Search (search.html)
│   ├── Category filters
│   └── Search results
├── Authors (authors.html)
│   └── Author profiles
├── Individual Articles (article_X.html)
│   ├── Full content
│   ├── Comments
│   └── Related articles
└── 404 (404.html)
    └── Error handling
```

## Link Patterns
- Main navigation: index.html, search.html, authors.html
- Article links: article_ID.html (generated by script)
- Category links: search.html?category=CATEGORY
- Search links: search.html?q=QUERY
"""
        
        with open('SITEMAP.md', 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        print("📄 Created SITEMAP.md")

    def run_full_check(self):
        """Run all link fixes and verifications"""
        print("🔧 Influencer News - Link Verification & Fix")
        print("=" * 50)
        
        # Check if files exist
        missing_files = []
        for filename in self.pages.keys():
            if not os.path.exists(filename):
                missing_files.append(filename)
        
        if missing_files:
            print("❌ Missing required files:")
            for file in missing_files:
                print(f"   - {file}")
            print("\nPlease ensure all HTML files are saved with correct names!")
            return
        
        print("✅ All required files found!")
        
        # Apply fixes
        self.fix_navigation_links()
        self.add_missing_functions()
        self.fix_article_links()
        
        # Verify
        self.verify_links()
        
        # Create sitemap
        self.create_sitemap()
        
        print(f"\n🎉 Link verification complete!")
        print(f"📊 Applied {self.fixes_applied} fixes")
        
        if self.fixes_applied > 0:
            print("\n💡 Recommended next steps:")
            print("1. Test navigation between all pages")
            print("2. Run the article integration script: python integrate_articles.py") 
            print("3. Verify article links work after integration")

if __name__ == "__main__":
    fixer = LinkFixer()
    fixer.run_full_check()
