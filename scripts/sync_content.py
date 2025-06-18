#!/usr/bin/env python3
"""
Content Sync Tool
================
Command-line tool for syncing content from database to HTML pages
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path to import src modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our modules with proper module execution
try:
    import os
    
    # Ensure we're working from project root
    os.chdir(project_root)
    
    # Add project root to Python path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Now try importing - this should work since we're running as a script from project root
    from src.database.db_manager import DatabaseManager
    from src.models.article import Article
    from src.models.author import Author
    from src.models.category import Category
    from src.models.trending import TrendingTopic
    from src.integrators.author_integrator import AuthorIntegrator
    from src.integrators.category_integrator import CategoryIntegrator
    from src.integrators.trending_integrator import TrendingIntegrator
    from src.integrators.article_integrator import ArticleIntegrator
    from src.integrators.homepage_integrator import HomepageIntegrator
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Ensure you're running from the project root directory")
    print("2. Check that all src/ modules are present")
    print("3. Try running: python -c 'import sys; print(sys.path)'")
    print(f"\nCurrent directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    print(f"Python path includes project root: {str(project_root) in sys.path}")
    sys.exit(1)


class ContentSyncTool:
    """Command-line content sync tool"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.integrators = {
            'authors': AuthorIntegrator(),
            'categories': CategoryIntegrator(),
            'trending': TrendingIntegrator(),
            'articles': ArticleIntegrator()
        }
        # Homepage integrator is handled separately
        self.homepage_integrator = HomepageIntegrator()
        
    def sync_all(self):
        """Sync all content types with bidirectional sync"""
        print("🔄 Starting full content sync...")
        print("=" * 50)
        
        for content_type, integrator in self.integrators.items():
            print(f"\n📦 Syncing {content_type}...")
            try:
                # First sync files with database (bidirectional)
                stats = integrator.sync_with_files()
                print(f"  📁 File sync: +{stats['added']} ~{stats['updated']} -{stats['removed']} ={stats['skipped']} skipped")
                
                # Then regenerate all HTML pages
                integrator.sync_all()
                
                # Update listing pages to reflect changes
                integrator.update_all_listing_pages()
                print(f"✅ {content_type.title()} synced successfully")
            except Exception as e:
                print(f"❌ Failed to sync {content_type}: {e}")
                return False
                
        # Finally, regenerate homepage with updated content
        print(f"\n🏠 Updating homepage...")
        try:
            self.homepage_integrator.generate_homepage()
            print("✅ Homepage updated successfully")
        except Exception as e:
            print(f"⚠️ Homepage update failed: {e}")
            # Don't fail the entire sync for homepage issues
            
        print("\n" + "=" * 50)
        print("🎉 All content synced successfully!")
        return True
        
    def sync_type(self, content_type):
        """Sync specific content type with bidirectional sync"""
        if content_type not in self.integrators:
            print(f"❌ Unknown content type: {content_type}")
            print(f"Available types: {', '.join(self.integrators.keys())}")
            return False
            
        print(f"🔄 Syncing {content_type}...")
        try:
            integrator = self.integrators[content_type]
            
            # First sync files with database (bidirectional)
            stats = integrator.sync_with_files()
            print(f"  📁 File sync: +{stats['added']} ~{stats['updated']} -{stats['removed']} ={stats['skipped']} skipped")
            
            # Then regenerate all HTML pages
            integrator.sync_all()
            
            # Update listing pages to reflect changes
            integrator.update_all_listing_pages()
            print(f"✅ {content_type.title()} synced successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to sync {content_type}: {e}")
            return False
            
    def show_stats(self):
        """Show content statistics"""
        print("📊 Content Statistics")
        print("=" * 30)
        
        try:
            # Get counts from database
            stats = {
                'Authors': len(Author.find_all()),
                'Categories': len(Category.find_all()),
                'Trending Topics': len(TrendingTopic.find_all()),
                'Articles': len(Article.find_all())
            }
            
            # Get image count
            with self.db.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) as count FROM images")
                stats['Images'] = cursor.fetchone()['count']
                
            for content_type, count in stats.items():
                print(f"{content_type:15}: {count:3d}")
                
        except Exception as e:
            print(f"❌ Failed to get statistics: {e}")
            
            
    def check_database(self):
        """Check database connectivity and structure"""
        print("🔍 Checking database...")
        
        try:
            with self.db.get_connection() as conn:
                # Check tables exist
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                tables = [row['name'] for row in cursor.fetchall()]
                
                print(f"✅ Database connected successfully")
                print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
                
                # Check foreign keys are enabled
                cursor = conn.execute("PRAGMA foreign_keys")
                fk_status = cursor.fetchone()[0]
                print(f"🔗 Foreign keys: {'✅ Enabled' if fk_status else '❌ Disabled'}")
                
                return True
                
        except Exception as e:
            print(f"❌ Database check failed: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Influencer News Content Sync Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Common Usage:
  python3 sync_content.py                    # Sync all content (most common)
  python3 sync_content.py articles          # Sync only articles
  python3 sync_content.py stats             # Show content statistics
  python3 sync_content.py status            # Check database connection

Content Types: articles, authors, categories, trending, homepage
        """)
    
    parser.add_argument('action', nargs='?', default='sync',
                       choices=['sync', 'articles', 'authors', 'categories', 'trending', 'homepage', 'stats', 'status'],
                       help='What to do: sync all content (default), sync specific type, or show info')
    
    args = parser.parse_args()
    
    # Create tool instance
    tool = ContentSyncTool()
    
    # Execute action - much simpler logic
    if args.action == 'sync':
        print("🔄 Syncing all content...")
        success = tool.sync_all()
        sys.exit(0 if success else 1)
        
    elif args.action in ['articles', 'authors', 'categories', 'trending']:
        print(f"🔄 Syncing {args.action}...")
        success = tool.sync_type(args.action)
        sys.exit(0 if success else 1)
        
    elif args.action == 'homepage':
        print("🏠 Regenerating homepage...")
        success = tool.homepage_integrator.generate_homepage()
        sys.exit(0 if success else 1)
        
    elif args.action == 'stats':
        tool.show_stats()
        
    elif args.action == 'status':
        success = tool.check_database()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()