-- Missing Database Tables and Views
-- This file adds tables referenced by the models but missing from schema.sql

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Mobile metrics table for tracking device-specific analytics
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
);

-- Image variants table for responsive images
CREATE TABLE IF NOT EXISTS image_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL,
    variant_type TEXT NOT NULL,  -- 'thumbnail', 'mobile', 'tablet', 'desktop', 'large'
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    local_filename TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    quality INTEGER DEFAULT 80,  -- JPEG quality setting
    format TEXT DEFAULT 'webp',  -- Image format: webp, jpg, png
    is_optimized BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- Full-text search virtual table (re-enable FTS)
CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
    title, 
    excerpt, 
    content, 
    tags,
    content_rowid=articles  -- Links to articles table
);

-- Create mobile-optimized view
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
WHERE a.status = 'published';

-- Indexes for mobile_metrics
CREATE INDEX IF NOT EXISTS idx_mobile_metrics_article ON mobile_metrics(article_id);
CREATE INDEX IF NOT EXISTS idx_mobile_metrics_date ON mobile_metrics(date_recorded);
CREATE INDEX IF NOT EXISTS idx_mobile_metrics_article_date ON mobile_metrics(article_id, date_recorded);

-- Indexes for image_variants
CREATE INDEX IF NOT EXISTS idx_image_variants_image ON image_variants(image_id);
CREATE INDEX IF NOT EXISTS idx_image_variants_type ON image_variants(variant_type);
CREATE INDEX IF NOT EXISTS idx_image_variants_size ON image_variants(width, height);

-- Triggers for mobile_metrics timestamps
CREATE TRIGGER IF NOT EXISTS update_mobile_metrics_timestamp 
AFTER UPDATE ON mobile_metrics
BEGIN
    UPDATE mobile_metrics SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Triggers for FTS table sync (if FTS is enabled)
CREATE TRIGGER IF NOT EXISTS articles_fts_insert AFTER INSERT ON articles
WHEN NEW.status = 'published'
BEGIN
    INSERT INTO articles_fts(rowid, title, excerpt, content, tags)
    VALUES (NEW.id, NEW.title, NEW.excerpt, NEW.content, COALESCE(NEW.tags, ''));
END;

CREATE TRIGGER IF NOT EXISTS articles_fts_delete AFTER DELETE ON articles
BEGIN
    DELETE FROM articles_fts WHERE rowid = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS articles_fts_update AFTER UPDATE ON articles
BEGIN
    DELETE FROM articles_fts WHERE rowid = OLD.id;
    INSERT INTO articles_fts(rowid, title, excerpt, content, tags)
    VALUES (NEW.id, NEW.title, NEW.excerpt, NEW.content, COALESCE(NEW.tags, ''));
END;

-- Update FTS for status changes
CREATE TRIGGER IF NOT EXISTS articles_fts_status_update AFTER UPDATE OF status ON articles
BEGIN
    DELETE FROM articles_fts WHERE rowid = OLD.id;
    -- Only insert if published
    INSERT INTO articles_fts(rowid, title, excerpt, content, tags)
    SELECT NEW.id, NEW.title, NEW.excerpt, NEW.content, COALESCE(NEW.tags, '')
    WHERE NEW.status = 'published';
END;