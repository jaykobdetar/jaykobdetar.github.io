-- Mobile Enhancement Migration
-- Adds mobile-specific fields and tables to support mobile optimization

-- Add mobile-specific fields to articles table
ALTER TABLE articles ADD COLUMN mobile_title TEXT;
ALTER TABLE articles ADD COLUMN mobile_excerpt TEXT;
ALTER TABLE articles ADD COLUMN mobile_hero_image_id INTEGER;

-- Create image variants table for responsive images
CREATE TABLE image_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL,
    variant_type TEXT NOT NULL, -- 'mobile', 'tablet', 'desktop', 'thumbnail'
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    format TEXT NOT NULL, -- 'jpeg', 'webp', 'avif'
    file_size INTEGER,
    filename TEXT NOT NULL,
    cdn_url TEXT,
    quality INTEGER DEFAULT 85,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- Create mobile metrics table for performance tracking
CREATE TABLE mobile_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    mobile_views INTEGER DEFAULT 0,
    tablet_views INTEGER DEFAULT 0,
    desktop_views INTEGER DEFAULT 0,
    avg_load_time_ms INTEGER,
    avg_interaction_time_seconds INTEGER,
    bounce_rate DECIMAL(5,2),
    scroll_depth_percent INTEGER,
    date_recorded DATE DEFAULT (date('now')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Create device sessions table for analytics
CREATE TABLE device_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    device_type TEXT NOT NULL, -- 'mobile', 'tablet', 'desktop'
    screen_width INTEGER,
    screen_height INTEGER,
    user_agent TEXT,
    ip_hash TEXT, -- Hashed IP for privacy
    pages_visited INTEGER DEFAULT 1,
    session_duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for mobile-related queries
CREATE INDEX idx_image_variants_image_id ON image_variants(image_id);
CREATE INDEX idx_image_variants_type ON image_variants(variant_type);
CREATE INDEX idx_mobile_metrics_article ON mobile_metrics(article_id);
CREATE INDEX idx_mobile_metrics_date ON mobile_metrics(date_recorded);
CREATE INDEX idx_device_sessions_type ON device_sessions(device_type);
CREATE INDEX idx_device_sessions_date ON device_sessions(created_at);

-- Create mobile-optimized view for articles
CREATE VIEW article_mobile_view AS
SELECT 
    a.id,
    COALESCE(a.mobile_title, a.title) as title,
    a.slug,
    COALESCE(a.mobile_excerpt, a.subtitle) as excerpt,
    a.publication_date,
    a.read_time,
    a.view_count,
    au.name as author_name,
    au.slug as author_slug,
    c.name as category_name,
    c.slug as category_slug,
    c.icon as category_icon,
    CASE 
        WHEN a.mobile_hero_image_id IS NOT NULL THEN a.mobile_hero_image_id
        ELSE (SELECT id FROM images WHERE content_type = 'article' AND content_id = a.id AND image_type = 'hero' LIMIT 1)
    END as hero_image_id
FROM articles a
JOIN authors au ON a.author_id = au.id
JOIN categories c ON a.category_id = c.id;

-- Create function to get responsive image URLs (stored procedure equivalent)
-- This will be implemented in Python code as SQLite doesn't support stored procedures

-- Add trigger to update device sessions timestamp
CREATE TRIGGER update_device_sessions_timestamp 
AFTER UPDATE ON device_sessions
BEGIN
    UPDATE device_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Insert sample image variants for existing images (if any exist)
-- This would typically be run after images are processed by the image generation system

-- Update the article_full_view to include mobile fields
DROP VIEW IF EXISTS article_full_view;
CREATE VIEW article_full_view AS
SELECT 
    a.id,
    a.title,
    a.mobile_title,
    a.slug,
    a.subtitle,
    a.mobile_excerpt,
    a.publication_date,
    a.read_time,
    a.tags,
    a.meta_description,
    a.content,
    a.view_count,
    a.mobile_hero_image_id,
    au.id as author_id,
    au.name as author_name,
    au.slug as author_slug,
    c.id as category_id,
    c.name as category_name,
    c.slug as category_slug,
    c.icon as category_icon
FROM articles a
JOIN authors au ON a.author_id = au.id
JOIN categories c ON a.category_id = c.id;