-- Add Missing Database Fields Migration
-- This script adds missing fields to the articles table that are referenced in the code

-- Add mobile-specific fields to articles table
ALTER TABLE articles ADD COLUMN mobile_title TEXT;
ALTER TABLE articles ADD COLUMN mobile_excerpt TEXT;
ALTER TABLE articles ADD COLUMN mobile_hero_image_id INTEGER;

-- Add last_modified field for tracking content updates
ALTER TABLE articles ADD COLUMN last_modified TEXT DEFAULT CURRENT_TIMESTAMP;

-- Add foreign key constraint for mobile_hero_image_id
-- Note: Cannot add foreign key constraint to existing table in SQLite
-- This is a limitation that would need to be handled in application code

-- Update existing records to have last_modified = updated_at
UPDATE articles SET last_modified = updated_at WHERE last_modified IS NULL;

-- Create trigger to automatically update last_modified when articles are updated
CREATE TRIGGER update_articles_last_modified 
AFTER UPDATE ON articles
BEGIN
    UPDATE articles SET last_modified = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Create missing database views referenced in the code
CREATE VIEW IF NOT EXISTS article_mobile_view AS
SELECT 
    a.id,
    a.title,
    a.slug,
    a.excerpt,
    a.mobile_title,
    a.mobile_excerpt,
    a.mobile_hero_image_id,
    a.status,
    a.featured,
    a.trending,
    a.publish_date,
    a.views,
    a.likes,
    a.read_time_minutes,
    a.image_url,
    a.hero_image_url,
    a.thumbnail_url,
    a.last_modified,
    au.id as author_id,
    au.name as author_name,
    au.slug as author_slug,
    au.title as author_title,
    c.id as category_id,
    c.name as category_name,
    c.slug as category_slug,
    c.color as category_color,
    c.icon as category_icon
FROM articles a
JOIN authors au ON a.author_id = au.id
JOIN categories c ON a.category_id = c.id
WHERE a.status = 'published';

-- Update the article_full_view to include new fields
DROP VIEW IF EXISTS article_full_view;
CREATE VIEW article_full_view AS
SELECT 
    a.id,
    a.title,
    a.slug,
    a.excerpt,
    a.mobile_title,
    a.mobile_excerpt,
    a.mobile_hero_image_id,
    a.status,
    a.featured,
    a.trending,
    a.publish_date,
    a.views,
    a.likes,
    a.read_time_minutes,
    a.image_url,
    a.hero_image_url,
    a.thumbnail_url,
    a.last_modified,
    a.created_at,
    a.updated_at,
    au.id as author_id,
    au.name as author_name,
    au.slug as author_slug,
    au.title as author_title,
    c.id as category_id,
    c.name as category_name,
    c.slug as category_slug,
    c.color as category_color,
    c.icon as category_icon
FROM articles a
JOIN authors au ON a.author_id = au.id
JOIN categories c ON a.category_id = c.id;