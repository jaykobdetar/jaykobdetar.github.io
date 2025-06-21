#!/usr/bin/env python3
"""
Remove status column from articles table
This script removes the draft/published concept entirely
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

def remove_status_column():
    """Remove status column from articles table"""
    db = DatabaseManager()
    
    print("🔄 Removing status column from articles table...")
    
    try:
        # Check if status column exists
        columns = db.execute_query("PRAGMA table_info(articles)")
        has_status = any(col['name'] == 'status' for col in columns)
        
        if not has_status:
            print("✅ Status column doesn't exist - nothing to do")
            return
        
        print("📋 Creating backup of articles table...")
        
        # Create backup table
        db.execute_write("""
            CREATE TABLE articles_backup AS 
            SELECT * FROM articles
        """)
        
        print("🗑️ Dropping original articles table...")
        db.execute_write("DROP TABLE articles")
        
        print("🔧 Creating new articles table without status column...")
        
        # Recreate articles table without status column
        db.execute_write("""
            CREATE TABLE articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                excerpt TEXT,               -- Brief summary
                content TEXT,               -- Full article content
                author_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                featured BOOLEAN DEFAULT 0,
                trending BOOLEAN DEFAULT 0,
                publish_date TEXT,
                image_url TEXT,             -- Featured image
                hero_image_url TEXT,        -- Large hero image
                thumbnail_url TEXT,         -- Thumbnail image
                tags TEXT,                  -- JSON array of tags
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                read_time_minutes INTEGER DEFAULT 5,
                seo_title TEXT,             -- SEO optimized title
                seo_description TEXT,       -- SEO meta description
                mobile_title TEXT,          -- Mobile-optimized title
                mobile_excerpt TEXT,        -- Mobile-optimized excerpt
                mobile_hero_image_id INTEGER,
                last_modified TEXT DEFAULT CURRENT_TIMESTAMP,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES authors(id),
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (mobile_hero_image_id) REFERENCES images(id)
            )
        """)
        
        print("📊 Migrating data from backup table...")
        
        # Copy data back without status column
        db.execute_write("""
            INSERT INTO articles (
                id, title, slug, excerpt, content, author_id, category_id,
                featured, trending, publish_date, image_url, hero_image_url,
                thumbnail_url, tags, views, likes, comments, read_time_minutes,
                seo_title, seo_description, mobile_title, mobile_excerpt,
                mobile_hero_image_id, last_modified, created_at, updated_at
            )
            SELECT 
                id, title, slug, excerpt, content, author_id, category_id,
                featured, trending, publish_date, image_url, hero_image_url,
                thumbnail_url, tags, views, likes, comments, read_time_minutes,
                seo_title, seo_description, mobile_title, mobile_excerpt,
                mobile_hero_image_id, last_modified, created_at, updated_at
            FROM articles_backup
        """)
        
        print("🧹 Cleaning up backup table...")
        db.execute_write("DROP TABLE articles_backup")
        
        # Recreate the view without status
        print("🔄 Recreating article_full_view...")
        
        db.execute_write("DROP VIEW IF EXISTS article_full_view")
        db.execute_write("""
            CREATE VIEW article_full_view AS 
            SELECT 
                a.id, a.title, a.slug, a.excerpt, a.content, 
                a.mobile_title, a.mobile_excerpt, a.mobile_hero_image_id, 
                a.featured, a.trending, a.publish_date, a.views, a.likes, 
                a.read_time_minutes, a.image_url, a.hero_image_url, 
                a.thumbnail_url, a.last_modified, a.created_at, a.updated_at, 
                au.id as author_id, au.name as author_name, au.slug as author_slug, 
                au.title as author_title, c.id as category_id, c.name as category_name, 
                c.slug as category_slug, c.color as category_color, c.icon as category_icon 
            FROM articles a 
            JOIN authors au ON a.author_id = au.id 
            JOIN categories c ON a.category_id = c.id
        """)
        
        # Check result
        count = db.execute_query("SELECT COUNT(*) as count FROM articles")[0]['count']
        print(f"✅ Successfully migrated {count} articles")
        print("✅ Status column removed - articles are now either synced or not synced")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("🔄 Attempting to restore from backup...")
        try:
            db.execute_write("DROP TABLE IF EXISTS articles")
            db.execute_write("ALTER TABLE articles_backup RENAME TO articles")
            print("✅ Restored from backup")
        except:
            print("❌ Could not restore from backup - manual intervention required")
        sys.exit(1)

if __name__ == '__main__':
    remove_status_column()