-- Schema Upgrade Script
-- Upgrades current schema.sql to match comprehensive docs/database-schema.md
-- Run this script to add missing fields, indexes, and features

-- First, backup existing data
-- sqlite3 data/infnews.db ".backup data/infnews_backup_$(date +%Y%m%d).db"

BEGIN TRANSACTION;

-- Upgrade Authors Table
ALTER TABLE authors ADD COLUMN title TEXT;
ALTER TABLE authors ADD COLUMN email TEXT;
ALTER TABLE authors ADD COLUMN location TEXT;
ALTER TABLE authors ADD COLUMN image_url TEXT;
ALTER TABLE authors ADD COLUMN joined_date TEXT DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE authors ADD COLUMN article_count INTEGER DEFAULT 0;
ALTER TABLE authors ADD COLUMN rating REAL DEFAULT 0.0;
ALTER TABLE authors ADD COLUMN is_active BOOLEAN DEFAULT 1;

-- Rename columns in authors (SQLite doesn't support column rename directly)
-- We'll handle this in the full schema replacement

-- Upgrade Categories Table  
ALTER TABLE categories ADD COLUMN color TEXT DEFAULT '#6B7280';
ALTER TABLE categories ADD COLUMN parent_id INTEGER;
ALTER TABLE categories ADD COLUMN sort_order INTEGER DEFAULT 999;
ALTER TABLE categories ADD COLUMN is_featured BOOLEAN DEFAULT 0;

-- Add foreign key constraint for parent_id (will be handled in schema replacement)

-- Upgrade Articles Table
ALTER TABLE articles ADD COLUMN excerpt TEXT;
ALTER TABLE articles ADD COLUMN status TEXT DEFAULT 'draft';
ALTER TABLE articles ADD COLUMN featured BOOLEAN DEFAULT 0;
ALTER TABLE articles ADD COLUMN trending BOOLEAN DEFAULT 0;
ALTER TABLE articles ADD COLUMN publish_date TEXT;
ALTER TABLE articles ADD COLUMN image_url TEXT;
ALTER TABLE articles ADD COLUMN hero_image_url TEXT;
ALTER TABLE articles ADD COLUMN thumbnail_url TEXT;
ALTER TABLE articles ADD COLUMN likes INTEGER DEFAULT 0;
ALTER TABLE articles ADD COLUMN comments INTEGER DEFAULT 0;
ALTER TABLE articles ADD COLUMN seo_title TEXT;
ALTER TABLE articles ADD COLUMN seo_description TEXT;

-- Rename view_count to views (will handle in schema replacement)
-- Rename read_time to read_time_minutes (will handle in schema replacement)
-- Rename publication_date to publish_date (will handle in schema replacement)

-- Upgrade Trending Topics Table
ALTER TABLE trending_topics ADD COLUMN content TEXT;
ALTER TABLE trending_topics ADD COLUMN growth_rate REAL DEFAULT 0.0;
ALTER TABLE trending_topics ADD COLUMN hashtag TEXT;
ALTER TABLE trending_topics ADD COLUMN start_date TEXT DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE trending_topics ADD COLUMN peak_date TEXT;
ALTER TABLE trending_topics ADD COLUMN status TEXT DEFAULT 'active';
ALTER TABLE trending_topics ADD COLUMN mentions_youtube INTEGER DEFAULT 0;
ALTER TABLE trending_topics ADD COLUMN mentions_tiktok INTEGER DEFAULT 0;
ALTER TABLE trending_topics ADD COLUMN mentions_instagram INTEGER DEFAULT 0;
ALTER TABLE trending_topics ADD COLUMN mentions_twitter INTEGER DEFAULT 0;
ALTER TABLE trending_topics ADD COLUMN mentions_twitch INTEGER DEFAULT 0;

-- Remove related_articles column (will handle in schema replacement)

-- Upgrade Article Sections Table
ALTER TABLE article_sections ADD COLUMN heading TEXT;
-- Rename section_order to order_num (will handle in schema replacement)

-- Upgrade Related Articles Table
ALTER TABLE related_articles ADD COLUMN relationship_type TEXT DEFAULT 'related';
-- Add id primary key and modify structure (will handle in schema replacement)

-- Add missing indexes
CREATE INDEX IF NOT EXISTS idx_authors_active ON authors(is_active);
CREATE INDEX IF NOT EXISTS idx_categories_featured ON categories(is_featured);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_trending_heat ON trending_topics(heat_score DESC);
CREATE INDEX IF NOT EXISTS idx_trending_status ON trending_topics(status);
CREATE INDEX IF NOT EXISTS idx_trending_category ON trending_topics(category_id);
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_featured ON articles(featured);
CREATE INDEX IF NOT EXISTS idx_articles_trending ON articles(trending);
CREATE INDEX IF NOT EXISTS idx_articles_publish_date ON articles(publish_date DESC);
CREATE INDEX IF NOT EXISTS idx_images_local ON images(local_filename);
CREATE INDEX IF NOT EXISTS idx_sections_article ON article_sections(article_id, section_order);

-- Add advanced triggers
CREATE TRIGGER IF NOT EXISTS update_author_article_count 
AFTER INSERT ON articles
BEGIN
    UPDATE authors 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE author_id = NEW.author_id AND status = 'published'
    )
    WHERE id = NEW.author_id;
END;

CREATE TRIGGER IF NOT EXISTS update_author_article_count_delete
AFTER DELETE ON articles
BEGIN
    UPDATE authors 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE author_id = OLD.author_id AND status = 'published'
    )
    WHERE id = OLD.author_id;
END;

CREATE TRIGGER IF NOT EXISTS update_author_article_count_update
AFTER UPDATE ON articles
BEGIN
    UPDATE authors 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE author_id = NEW.author_id AND status = 'published'
    )
    WHERE id = NEW.author_id;
    
    -- Update old author if author changed
    UPDATE authors 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE author_id = OLD.author_id AND status = 'published'
    )
    WHERE id = OLD.author_id AND OLD.author_id != NEW.author_id;
END;

COMMIT;

-- Note: Full-text search virtual table will be created in the complete schema replacement
-- Some column renames require recreating tables, which will be done in the full upgrade