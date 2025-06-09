#!/usr/bin/env python3
"""
Influencer News - Article Integration Script
============================================

This script automatically integrates new articles into your website by:
1. Reading formatted text files from the 'articles/' directory
2. Updating all HTML pages with new content
3. Maintaining proper links and article IDs
4. Creating individual article pages

Usage: python integrate_articles.py
"""

import os
import re
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any
import html

class ArticleIntegrator:
    def __init__(self):
        self.articles_dir = Path("articles")
        self.articles_dir.mkdir(exist_ok=True)
        
        # Load existing articles database
        self.db_file = Path("articles_db.json")
        self.articles_db = self.load_articles_db()
        
        # Category mappings for styling
        self.category_colors = {
            'business': 'green',
            'entertainment': 'orange', 
            'tech': 'blue',
            'fashion': 'pink',
            'charity': 'purple',
            'beauty': 'pink',
            'technology': 'blue'
        }
        
        # Author database
        self.authors = {
            'sarah chen': {
                'name': 'Sarah Chen',
                'title': 'Senior Business Reporter',
                'image': 'https://images.unsplash.com/photo-1494790108755-2616c395d75b?w=50&h=50&fit=crop&crop=face',
                'bio': 'Former TechCrunch senior writer specializing in creator economy trends.',
                'expertise': ['Creator Economy', 'Business', 'Startups']
            },
            'michael torres': {
                'name': 'Michael Torres', 
                'title': 'Entertainment Editor',
                'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50&h=50&fit=crop&crop=face',
                'bio': 'Celebrity culture and entertainment industry veteran.',
                'expertise': ['Celebrity News', 'Entertainment', 'Exclusive Interviews']
            },
            'alex rivera': {
                'name': 'Alex Rivera',
                'title': 'Tech Correspondent', 
                'image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50&h=50&fit=crop&crop=face',
                'bio': 'Platform algorithm specialist and former software engineer.',
                'expertise': ['Algorithms', 'Platform Updates', 'Tech Analysis']
            },
            'jessica kim': {
                'name': 'Jessica Kim',
                'title': 'Beauty & Fashion Editor',
                'image': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=50&h=50&fit=crop&crop=face', 
                'bio': 'Former Vogue digital editor covering beauty influencer partnerships.',
                'expertise': ['Beauty', 'Fashion', 'Influencer Collabs']
            },
            'david park': {
                'name': 'David Park',
                'title': 'Markets & Economics Editor',
                'image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=50&h=50&fit=crop&crop=face',
                'bio': 'Former Goldman Sachs analyst specializing in creator economy.',
                'expertise': ['Market Analysis', 'Economics', 'Data Science']
            }
        }

    def load_articles_db(self) -> Dict:
        """Load existing articles database"""
        if self.db_file.exists():
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'articles': [], 'next_id': 1}

    def save_articles_db(self):
        """Save articles database"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles_db, f, indent=2, ensure_ascii=False)

    def parse_article_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a formatted article text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Split into sections
        sections = content.split('\n---\n')
        if len(sections) < 2:
            raise ValueError(f"Invalid format in {file_path}. Missing '---' separator.")
        
        # Parse metadata
        metadata_section = sections[0].strip()
        article_content = '\n---\n'.join(sections[1:]).strip()
        
        metadata = {}
        for line in metadata_section.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip().lower()] = value.strip()
        
        # Validate required fields
        required_fields = ['title', 'author', 'category', 'image', 'excerpt']
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Missing required field '{field}' in {file_path}")
        
        # Process content sections
        content_sections = article_content.split('\n## ')
        processed_content = []
        
        for i, section in enumerate(content_sections):
            if i == 0:
                # First section might not have ## prefix
                if section.startswith('## '):
                    section = section[3:]
                processed_content.append(self.format_content_section('', section))
            else:
                lines = section.split('\n', 1)
                heading = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else ''
                processed_content.append(self.format_content_section(heading, body))
        
        # Generate article data
        article_id = self.articles_db['next_id']
        
        # Get author info
        author_key = metadata['author'].lower()
        author_info = self.authors.get(author_key, {
            'name': metadata['author'],
            'title': 'Contributor',
            'image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50&h=50&fit=crop&crop=face',
            'bio': 'Contributing writer for Influencer News.',
            'expertise': [metadata.get('category', 'General').title()]
        })
        
        return {
            'id': article_id,
            'title': metadata['title'],
            'author': author_info['name'],
            'author_info': author_info,
            'category': metadata['category'].lower(),
            'tags': [tag.strip() for tag in metadata.get('tags', '').split(',') if tag.strip()],
            'image': metadata['image'],
            'excerpt': metadata['excerpt'],
            'content': '\n'.join(processed_content),
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'views': str(self.generate_realistic_views()),
            'comments': str(self.generate_realistic_comments()),
            'read_time': self.calculate_read_time(article_content)
        }

    def format_content_section(self, heading: str, content: str) -> str:
        """Format a content section with proper HTML"""
        html_content = ""
        
        if heading:
            html_content += f'<h2 class="text-2xl font-bold text-gray-900 mt-8 mb-4">{html.escape(heading)}</h2>\n'
        
        # Process paragraphs and special formatting
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # Handle special formatting
            if para.startswith('> '):
                # Blockquote
                quote_text = para[2:].strip()
                if ' - ' in quote_text:
                    quote, author = quote_text.rsplit(' - ', 1)
                    html_content += f'''<blockquote class="border-l-4 border-gray-300 pl-6 italic text-gray-700 my-8 text-lg">
                        {html.escape(quote)}
                        <footer class="text-sm text-gray-500 mt-2">— {html.escape(author)}</footer>
                    </blockquote>\n'''
                else:
                    html_content += f'<blockquote class="border-l-4 border-gray-300 pl-6 italic text-gray-700 my-8 text-lg">{html.escape(quote_text)}</blockquote>\n'
            elif para.startswith('- '):
                # Bullet list
                items = [line[2:].strip() for line in para.split('\n') if line.strip().startswith('- ')]
                html_content += '<ul class="list-disc pl-6 text-gray-700 mb-6 space-y-2">\n'
                for item in items:
                    html_content += f'    <li>{html.escape(item)}</li>\n'
                html_content += '</ul>\n'
            elif para.startswith('[INFO]'):
                # Info box
                info_text = para[6:].strip()
                html_content += f'''<div class="bg-indigo-50 border-l-4 border-indigo-400 p-6 my-8">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-indigo-700">{html.escape(info_text)}</p>
                        </div>
                    </div>
                </div>\n'''
            else:
                # Regular paragraph
                html_content += f'<p class="text-gray-700 mb-6">{html.escape(para)}</p>\n'
        
        return html_content

    def generate_realistic_views(self) -> int:
        """Generate realistic view count"""
        import random
        return random.randint(50000, 2000000)

    def generate_realistic_comments(self) -> int:
        """Generate realistic comment count"""
        import random
        return random.randint(100, 5000)

    def calculate_read_time(self, content: str) -> str:
        """Calculate estimated read time"""
        word_count = len(content.split())
        minutes = max(1, round(word_count / 200))  # Average 200 WPM
        return f"{minutes} min"

    def create_article_page(self, article: Dict[str, Any]):
        """Create individual article page"""
        # Read the article template
        with open('article.html', 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders
        replacements = {
            'MrBeast Announces Revolutionary $100M Creator Support Fund - Influencer News': f"{article['title']} - Influencer News",
            'MrBeast Announces Revolutionary $100M Creator Support Fund to Transform YouTube Landscape': article['title'],
            'Sarah Chen': article['author_info']['name'],
            'Senior Business Reporter': article['author_info']['title'],
            'https://images.unsplash.com/photo-1494790108755-2616c395d75b?w=50&h=50&fit=crop&crop=face': article['author_info']['image'],
            'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=400&fit=crop': article['image'],
            'Published 2 hours ago': f"Published {self.format_date_relative(article['date'])}",
            '5 minute read': f"{article['read_time']} read",
            '1,247,892': article['views'],
            '24,156': str(int(article['views'].replace(',', '')) // 50),  # Likes = views / 50
            '2,847': article['comments'],
        }
        
        # Apply replacements
        for old, new in replacements.items():
            template = template.replace(old, new)
        
        # Replace content
        content_start = template.find('<div class="prose prose-lg max-w-none" id="articleContent">')
        content_end = template.find('</div>', content_start) + 6
        
        if content_start != -1 and content_end != -1:
            new_content = f'''<div class="prose prose-lg max-w-none" id="articleContent">
                <p class="text-xl text-gray-700 font-medium mb-6 leading-relaxed">
                    {html.escape(article['excerpt'])}
                </p>
                {article['content']}
            </div>'''
            template = template[:content_start] + new_content + template[content_end:]
        
        # Save the article page
        article_filename = f"article_{article['id']}.html"
        with open(article_filename, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"✅ Created article page: {article_filename}")

    def update_homepage(self, articles: List[Dict[str, Any]]):
        """Update homepage with latest articles"""
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate article cards HTML
        articles_html = ""
        for i, article in enumerate(articles[:6]):  # Show latest 6 articles
            card_class = "md:col-span-2 lg:col-span-1" if i == 0 else ""  # Featured article
            
            articles_html += f'''
                <div class="article-card bg-white rounded-xl shadow-lg overflow-hidden {card_class}">
                    <div class="relative">
                        <img src="{article['image']}" alt="{html.escape(article['title'])}" class="w-full h-48 object-cover">
                        <div class="absolute top-4 right-4">
                            <span class="category-{article['category']} bg-white/90 px-2 py-1 rounded text-xs font-bold uppercase">{article['category']}</span>
                        </div>
                    </div>
                    <div class="p-6">
                        <div class="flex items-center gap-2 mb-3">
                            <span class="text-gray-500 text-sm">{article['author']} • {self.format_date_relative(article['date'])}</span>
                        </div>
                        <h3 class="text-lg font-bold mb-3 hover:text-indigo-600 transition cursor-pointer">
                            {html.escape(article['title'])}
                        </h3>
                        <p class="text-gray-700 mb-4 text-sm">
                            {html.escape(article['excerpt'])}
                        </p>
                        <div class="flex items-center justify-between text-sm">
                            <span class="text-gray-500">👁 {article['views']} views</span>
                            <a href="article_{article['id']}.html" class="text-indigo-600 font-medium cursor-pointer">Read →</a>
                        </div>
                    </div>
                </div>
            '''
        
        # Replace articles section
        start_marker = '<div id="articlesGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">'
        end_marker = '</div>\n\n            <!-- Load More Button -->'
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            new_section = f'{start_marker}\n{articles_html}\n            </div>'
            content = content[:start_pos] + new_section + content[end_pos:]
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated homepage with latest articles")

    def update_search_page(self, articles: List[Dict[str, Any]]):
        """Update search page JavaScript with new articles"""
        with open('search.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate JavaScript articles array
        js_articles = "const articles = [\n"
        for article in articles:
            # Escape quotes properly for JavaScript
            title_escaped = html.escape(article['title']).replace('"', '\\"')
            excerpt_escaped = html.escape(article['excerpt']).replace('"', '\\"')
            
            js_articles += f'''            {{
                id: {article['id']},
                title: "{title_escaped}",
                author: "{article['author']}",
                date: "{self.format_date_relative(article['date'])}",
                category: "{article['category']}",
                views: "{article['views']}",
                image: "{article['image']}",
                excerpt: "{excerpt_escaped}",
                readTime: "{article['read_time']}",
                trending: {str(article.get('trending', False)).lower()}
            }},
'''
        js_articles += "        ];"
        
        # Replace articles array in JavaScript
        start_marker = "const articles = ["
        end_marker = "        ];"
        
        start_pos = content.find(start_marker)
        if start_pos != -1:
            end_pos = content.find(end_marker, start_pos) + len(end_marker)
            content = content[:start_pos] + js_articles + content[end_pos:]
        
        with open('search.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated search page with new articles")

    def format_date_relative(self, date_str: str) -> str:
        """Format date as relative time"""
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            now = datetime.datetime.now()
            diff = now - date_obj
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                minutes = max(1, diff.seconds // 60)
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        except:
            return "Recently"

    def process_new_articles(self):
        """Process all new article files"""
        processed_count = 0
        
        # Get list of existing article files
        existing_files = {article.get('filename', '') for article in self.articles_db['articles']}
        
        # Process each .txt file in articles directory
        for file_path in self.articles_dir.glob("*.txt"):
            if file_path.name in existing_files:
                print(f"⏭️  Skipping already processed: {file_path.name}")
                continue
            
            try:
                print(f"🔄 Processing: {file_path.name}")
                article = self.parse_article_file(file_path)
                article['filename'] = file_path.name
                
                # Add to database
                self.articles_db['articles'].append(article)
                self.articles_db['next_id'] += 1
                
                # Create individual article page
                self.create_article_page(article)
                
                processed_count += 1
                print(f"✅ Successfully processed: {article['title']}")
                
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {str(e)}")
                continue
        
        if processed_count > 0:
            # Sort articles by date (newest first)
            self.articles_db['articles'].sort(
                key=lambda x: x['date'], 
                reverse=True
            )
            
            # Update website pages
            self.update_homepage(self.articles_db['articles'])
            self.update_search_page(self.articles_db['articles'])
            
            # Save database
            self.save_articles_db()
            
            print(f"\n🎉 Successfully integrated {processed_count} new article(s)!")
            print(f"📊 Total articles in database: {len(self.articles_db['articles'])}")
        else:
            print("\n📝 No new articles to process.")

    def create_sample_article(self):
        """Create a sample article file for reference"""
        sample_content = """Title: Sample Article Title Here
Author: Sarah Chen
Category: business
Image: https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=600&h=300&fit=crop
Tags: sample, demo, tutorial
Excerpt: This is a brief excerpt that will appear on the homepage and in search results. Keep it under 200 characters for best display.

---

This is the opening paragraph of your article. It should hook the reader and provide a compelling introduction to your topic.

## First Section Heading

This is the content under the first section. You can write multiple paragraphs here.

This is a second paragraph in the same section.

## Important Information Box

[INFO] This is an information box that will be highlighted with a special blue background. Use this for key facts or important details.

## Lists and Special Formatting

Here's how to create a bullet list:

- First item in the list
- Second item in the list  
- Third item with more details

## Quotes and Citations

You can include blockquotes like this:

> This is a quote from someone important. It will be styled nicely with proper formatting. - Quote Author

## Final Section

End your article with a strong conclusion that ties everything together and provides value to the reader.
"""
        
        sample_file = self.articles_dir / "sample_article.txt"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"📝 Created sample article: {sample_file}")
        print("📖 Edit this file and run the script again to see it integrated!")

def main():
    """Main function"""
    print("🚀 Influencer News - Article Integration Script")
    print("=" * 50)
    
    integrator = ArticleIntegrator()
    
    # Check if articles directory is empty
    txt_files = list(integrator.articles_dir.glob("*.txt"))
    if not txt_files:
        print("📁 No article files found. Creating sample article...")
        integrator.create_sample_article()
        return
    
    # Process articles
    integrator.process_new_articles()
    
    print("\n🔗 Article Links:")
    for article in integrator.articles_db['articles'][:5]:  # Show latest 5
        print(f"   • article_{article['id']}.html - {article['title']}")

if __name__ == "__main__":
    main()
