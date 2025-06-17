#!/usr/bin/env python3
"""
Create Missing Database Tables using existing DatabaseManager
"""

import os
import sys

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

def create_missing_tables():
    """Create missing database tables and views"""
    
    print("Creating missing database tables...")
    
    db = DatabaseManager()
    
    try:
        # Create mobile_metrics table
        print("Creating mobile_metrics table...")
        mobile_metrics_sql = """
        CREATE TABLE IF NOT EXISTS mobile_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            date_recorded TEXT NOT NULL,
            mobile_views INTEGER DEFAULT 0,
            tablet_views INTEGER DEFAULT 0,
            desktop_views INTEGER DEFAULT 0,
            avg_load_time_ms INTEGER DEFAULT 0,
            bounce_rate REAL DEFAULT 0.0,
            scroll_depth_percent INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
            UNIQUE(article_id, date_recorded)
        )
        """
        db.execute_write(mobile_metrics_sql)
        print("✓ mobile_metrics table created")
        
        # Create image_variants table
        print("Creating image_variants table...")
        image_variants_sql = """
        CREATE TABLE IF NOT EXISTS image_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            variant_type TEXT NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            local_filename TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            quality INTEGER DEFAULT 80,
            format TEXT DEFAULT 'webp',
            is_optimized BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
        )
        """
        db.execute_write(image_variants_sql)
        print("✓ image_variants table created")
        
        # Create article_mobile_view
        print("Creating article_mobile_view...")
        mobile_view_sql = """
        CREATE VIEW IF NOT EXISTS article_mobile_view AS
        SELECT 
            a.id,
            a.title,
            COALESCE(a.seo_title, a.title) as mobile_title,
            COALESCE(a.excerpt, substr(a.content, 1, 150) || '...') as excerpt,
            a.slug,
            a.author_id,
            a.category_id,
            a.publish_date,
            a.read_time_minutes,
            a.views,
            a.likes,
            a.image_url,
            au.name as author_name,
            au.slug as author_slug,
            c.name as category_name,
            c.slug as category_slug,
            c.icon as category_icon,
            c.color as category_color
        FROM articles a
        JOIN authors au ON a.author_id = au.id
        JOIN categories c ON a.category_id = c.id
        WHERE a.status = 'published'
        """
        db.execute_write(mobile_view_sql)
        print("✓ article_mobile_view created")
        
        # Create indexes
        print("Creating indexes...")
        db.execute_write("CREATE INDEX IF NOT EXISTS idx_mobile_metrics_article ON mobile_metrics(article_id)")
        db.execute_write("CREATE INDEX IF NOT EXISTS idx_mobile_metrics_date ON mobile_metrics(date_recorded)")
        db.execute_write("CREATE INDEX IF NOT EXISTS idx_image_variants_image ON image_variants(image_id)")
        db.execute_write("CREATE INDEX IF NOT EXISTS idx_image_variants_type ON image_variants(variant_type)")
        print("✓ Indexes created")
        
        # Try to create FTS table (may fail if FTS not available)
        print("Attempting to create FTS table...")
        try:
            fts_sql = """
            CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
                title, 
                excerpt, 
                content, 
                tags,
                content_rowid=articles
            )
            """
            db.execute_write(fts_sql)
            print("✓ articles_fts virtual table created")
            
            # Populate FTS with existing articles
            published_articles = db.execute_query("SELECT id, title, excerpt, content, tags FROM articles WHERE status = 'published'")
            for article in published_articles:
                insert_fts = """
                INSERT INTO articles_fts(rowid, title, excerpt, content, tags)
                VALUES (?, ?, ?, ?, ?)
                """
                db.execute_write(insert_fts, (
                    article['id'], 
                    article['title'], 
                    article['excerpt'] or '', 
                    article['content'] or '', 
                    article['tags'] or ''
                ))
            print(f"✓ FTS populated with {len(published_articles)} articles")
            
        except Exception as e:
            print(f"⚠ FTS creation failed (may not be available): {e}")
            
        print("\nVerifying tables...")
        
        # Check what tables exist
        tables = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        table_names = [t['name'] for t in tables]
        
        if 'mobile_metrics' in table_names:
            print("✓ mobile_metrics table exists")
        else:
            print("✗ mobile_metrics table missing")
            
        if 'image_variants' in table_names:
            print("✓ image_variants table exists") 
        else:
            print("✗ image_variants table missing")
            
        if 'articles_fts' in table_names:
            print("✓ articles_fts table exists")
        else:
            print("⚠ articles_fts table not available (FTS may not be supported)")
        
        # Check views
        views = db.execute_query("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        view_names = [v['name'] for v in views]
        
        if 'article_mobile_view' in view_names:
            print("✓ article_mobile_view exists")
        else:
            print("✗ article_mobile_view missing")
            
        return True
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

if __name__ == "__main__":
    if create_missing_tables():
        print("\n✅ Database tables created successfully!")
    else:
        print("\n❌ Database table creation failed!")
        sys.exit(1)