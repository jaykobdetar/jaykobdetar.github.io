#!/usr/bin/env python3
"""
Trending Topics Integrator
==========================
Handles trending topics integration with database
"""

from pathlib import Path
from typing import Dict, List, Any
from .base_integrator import BaseIntegrator
from ..models.trending import TrendingTopic


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
            # Read template
            template_content = self.get_trending_template()
            
            # Replace placeholders
            replacements = {
                '{{TOPIC_TITLE}}': topic.title,
                '{{TOPIC_DESCRIPTION}}': getattr(topic, 'description', f'Explore the latest on {topic.title}'),
                '{{HEAT_SCORE}}': str(getattr(topic, 'heat_score', 0)),
                '{{TREND_CONTENT}}': self.generate_trend_content(topic)
            }
            
            content = template_content
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
                
            # No navigation path fixes needed since file is in main integrated dir
            
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
            # Read template
            template_content = self.get_trending_listing_template()
            
            # Generate trending cards
            topics_html = self.generate_trending_cards(topics)
            
            # Replace placeholders
            content = template_content.replace('{{TRENDING_CONTENT}}', topics_html)
            content = content.replace('{{TOPIC_COUNT}}', str(len(topics)))
            
            # No navigation path fixes needed since file is in main integrated dir
            
            # Save file (listing goes in main integrated dir, not subfolder)
            from pathlib import Path
            filename = Path("integrated") / "trending.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.update_progress(f"Created trending listing: {filename.name}")
            
        except Exception as e:
            self.update_progress(f"Error creating trending listing: {e}")
            
    def generate_trending_cards(self, topics):
        """Generate HTML for trending topic cards"""
        cards_html = ""
        
        # Sort by heat score (descending)
        sorted_topics = sorted(topics, key=lambda t: getattr(t, 'heat_score', 0), reverse=True)
        
        for i, topic in enumerate(sorted_topics):
            heat_score = getattr(topic, 'heat_score', 0)
            
            # Get heat indicator
            if heat_score >= 90:
                heat_indicator = "🔥🔥🔥"
                heat_class = "text-red-600"
                heat_bg = "bg-red-100"
            elif heat_score >= 70:
                heat_indicator = "🔥🔥"
                heat_class = "text-orange-600"
                heat_bg = "bg-orange-100"
            elif heat_score >= 50:
                heat_indicator = "🔥"
                heat_class = "text-yellow-600"
                heat_bg = "bg-yellow-100"
            else:
                heat_indicator = "📈"
                heat_class = "text-blue-600"
                heat_bg = "bg-blue-100"
                
            # Rank badge
            rank_badge = ""
            if i < 3:
                rank_colors = ["bg-yellow-500", "bg-gray-400", "bg-orange-600"]
                rank_badge = f'<div class="absolute top-4 left-4 w-8 h-8 {rank_colors[i]} text-white rounded-full flex items-center justify-center font-bold text-sm">#{i+1}</div>'
            
            cards_html += f'''
            <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow relative">
                {rank_badge}
                <div class="relative">
                    <img src="{getattr(topic, 'image_url', '/assets/placeholders/trending_placeholder.svg')}" 
                         alt="{self.escape_html(topic.title)}" 
                         class="w-full h-48 object-cover">
                    <div class="absolute top-4 right-4">
                        <span class="{heat_bg} {heat_class} px-3 py-1 rounded-full text-sm font-bold">
                            {heat_indicator} {heat_score}
                        </span>
                    </div>
                </div>
                <div class="p-6">
                    <h3 class="text-xl font-bold mb-3 hover:text-indigo-600 transition">
                        <a href="trending/trend_{topic.slug}.html">{self.escape_html(topic.title)}</a>
                    </h3>
                    <p class="text-gray-700 mb-4 text-sm">
                        {self.escape_html(getattr(topic, 'description', topic.title)[:150])}...
                    </p>
                    <div class="flex items-center justify-between text-sm">
                        <span class="text-gray-500">🔥 Heat Score: {heat_score}</span>
                        <a href="trending/trend_{topic.slug}.html" 
                           class="text-indigo-600 font-medium">Explore →</a>
                    </div>
                </div>
            </div>
            '''
            
        return cards_html
        
    def generate_trend_content(self, topic):
        """Generate content for trending topic page"""
        content = getattr(topic, 'content', '')
        
        if not content:
            # Generate default content based on topic
            content = f'''
            <div class="bg-white rounded-2xl shadow-lg p-8 mb-8">
                <h2 class="text-3xl font-bold mb-6 hero-title">About This Trend</h2>
                <p class="text-gray-700 text-lg mb-6">
                    {self.escape_html(getattr(topic, 'description', f'{topic.title} is currently trending in the influencer space.'))}
                </p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="text-center p-4 bg-gray-50 rounded-lg">
                        <div class="text-3xl font-bold text-indigo-600">{getattr(topic, 'heat_score', 0)}</div>
                        <div class="text-sm text-gray-600">Heat Score</div>
                    </div>
                    <div class="text-center p-4 bg-gray-50 rounded-lg">
                        <div class="text-3xl font-bold text-green-600">{getattr(topic, 'mentions', 'N/A')}</div>
                        <div class="text-sm text-gray-600">Mentions</div>
                    </div>
                    <div class="text-center p-4 bg-gray-50 rounded-lg">
                        <div class="text-3xl font-bold text-purple-600">{getattr(topic, 'engagement', 'High')}</div>
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
        
    def get_trending_template(self):
        """Get trending topic page template"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TOPIC_TITLE}} - Trending | Influencer News</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .hero-title { font-family: 'Playfair Display', serif; }
    </style>
</head>
<body class="bg-gray-50">
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
                    <li><a href="../../index.html" class="hover:text-indigo-200 transition font-medium">Home</a></li>
                    <li><a href="../../search.html" class="hover:text-indigo-200 transition font-medium">Search</a></li>
                    <li><a href="../../authors.html" class="hover:text-indigo-200 transition font-medium">Authors</a></li>
                    <li><a href="../categories.html" class="hover:text-indigo-200 transition font-medium">Categories</a></li>
                    <li><a href="../trending.html" class="hover:text-indigo-200 transition font-medium text-indigo-200">Trending</a></li>
                </ul>
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
</body>
</html>'''

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
        
    def create_sample_file(self):
        """Create sample file"""
        pass
    
    def process_trending(self, content_data: Dict[str, Any]) -> bool:
        """Process trending topic content and add to database"""
        try:
            # Generate slug from filename or title
            slug = content_data.get('slug') or content_data.get('title', '').lower().replace(' ', '-')
            if not slug and 'filename' in content_data:
                slug = content_data['filename'].replace('.txt', '')
                
            # Check if trending topic already exists
            existing = TrendingTopic.find_by_slug(slug)
            if existing:
                self.update_progress(f"Trending topic '{content_data.get('title', slug)}' already exists, skipping")
                return False
            
            # Create trending topic
            topic = TrendingTopic(
                title=content_data.get('title', slug.title()),
                slug=slug,
                description=content_data.get('description', ''),
                content=content_data.get('content', ''),
                heat_score=int(content_data.get('heat_score', 50)),
                growth_rate=float(content_data.get('growth_rate', 0.0)),
                hashtag=content_data.get('hashtag', ''),
                status=content_data.get('status', 'active'),
                mentions_youtube=int(content_data.get('mentions_youtube', 0)),
                mentions_tiktok=int(content_data.get('mentions_tiktok', 0)),
                mentions_instagram=int(content_data.get('mentions_instagram', 0)),
                mentions_twitter=int(content_data.get('mentions_twitter', 0)),
                mentions_twitch=int(content_data.get('mentions_twitch', 0))
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

    def get_trending_listing_template(self):
        """Get trending topics listing template"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trending Topics - Influencer News</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .hero-title { font-family: 'Playfair Display', serif; }
    </style>
</head>
<body class="bg-gray-50">
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
                    <li><a href="../../index.html" class="hover:text-indigo-200 transition font-medium">Home</a></li>
                    <li><a href="../../search.html" class="hover:text-indigo-200 transition font-medium">Search</a></li>
                    <li><a href="../../authors.html" class="hover:text-indigo-200 transition font-medium">Authors</a></li>
                    <li><a href="../categories.html" class="hover:text-indigo-200 transition font-medium">Categories</a></li>
                    <li><a href="../trending.html" class="hover:text-indigo-200 transition font-medium text-indigo-200">Trending</a></li>
                </ul>
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
</body>
</html>'''
    def update_all_listing_pages(self):
        """Update all listing pages with current trending topics from database"""
        self.update_progress("Updating trending listing pages...")
        
        # Get all trending topics from database
        from ..models.trending import TrendingTopic
        trending_topics = TrendingTopic.find_all()
        
        # Update the main trending listing page
        self.create_trending_listing(trending_topics)
        
        self.update_progress(f"Updated listing pages with {len(trending_topics)} trending topics")
