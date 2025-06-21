-- Initial schema for Influencer News CMS
-- Version: 1
-- Description: Core tables for the content management system

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Authors table
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    bio TEXT,
    image_url TEXT,
    title TEXT,
    location TEXT,
    expertise TEXT,
    social_twitter TEXT,
    social_instagram TEXT,
    social_youtube TEXT,
    article_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    color TEXT DEFAULT '#gray',
    icon TEXT DEFAULT '📁',
    article_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Articles table
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    excerpt TEXT,
    content TEXT,
    author_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'archived')),
    image_url TEXT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    read_time_minutes INTEGER DEFAULT 5,
    publish_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mobile_title TEXT,
    mobile_excerpt TEXT,
    mobile_hero_image_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Trending topics table
CREATE TABLE IF NOT EXISTS trending_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    heat_score INTEGER DEFAULT 0,
    article_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Images table
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    alt_text TEXT,
    caption TEXT,
    width INTEGER,
    height INTEGER,
    file_size INTEGER,
    mime_type TEXT,
    is_hero BOOLEAN DEFAULT FALSE,
    is_thumbnail BOOLEAN DEFAULT FALSE,
    article_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Article sections table
CREATE TABLE IF NOT EXISTS article_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    section_type TEXT NOT NULL CHECK(section_type IN ('paragraph', 'heading', 'image', 'quote', 'list', 'code', 'embed')),
    content TEXT,
    position INTEGER NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Related articles table
CREATE TABLE IF NOT EXISTS related_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    related_article_id INTEGER NOT NULL,
    relevance_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (related_article_id) REFERENCES articles(id) ON DELETE CASCADE,
    UNIQUE(article_id, related_article_id)
);

-- Mobile metrics table
CREATE TABLE IF NOT EXISTS mobile_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    mobile_views INTEGER DEFAULT 0,
    mobile_likes INTEGER DEFAULT 0,
    mobile_shares INTEGER DEFAULT 0,
    avg_read_depth REAL DEFAULT 0.0,
    bounce_rate REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Image variants table
CREATE TABLE IF NOT EXISTS image_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_image_id INTEGER NOT NULL,
    variant_type TEXT NOT NULL CHECK(variant_type IN ('thumbnail', 'mobile', 'desktop', 'social')),
    url TEXT NOT NULL,
    width INTEGER,
    height INTEGER,
    file_size INTEGER,
    quality INTEGER DEFAULT 85,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (original_image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_author ON articles(author_id);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category_id);
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_publish_date ON articles(publish_date);
CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);
CREATE INDEX IF NOT EXISTS idx_authors_slug ON authors(slug);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_trending_slug ON trending_topics(slug);
CREATE INDEX IF NOT EXISTS idx_images_article ON images(article_id);
CREATE INDEX IF NOT EXISTS idx_sections_article ON article_sections(article_id);
CREATE INDEX IF NOT EXISTS idx_related_articles ON related_articles(article_id);
CREATE INDEX IF NOT EXISTS idx_mobile_metrics_article ON mobile_metrics(article_id);
CREATE INDEX IF NOT EXISTS idx_image_variants_original ON image_variants(original_image_id);

-- Create view for mobile article data
CREATE VIEW IF NOT EXISTS article_mobile_view AS
SELECT 
    a.id,
    COALESCE(a.mobile_title, a.title) as title,
    COALESCE(a.mobile_excerpt, a.excerpt) as excerpt,
    a.slug,
    a.author_id,
    a.category_id,
    a.status,
    a.publish_date,
    a.read_time_minutes,
    COALESCE(m.mobile_views, a.views) as views,
    COALESCE(m.mobile_likes, a.likes) as likes,
    COALESCE(m.mobile_shares, a.comments) as shares,
    m.avg_read_depth,
    m.bounce_rate,
    COALESCE(img.url, a.image_url) as hero_image_url
FROM articles a
LEFT JOIN mobile_metrics m ON a.id = m.article_id
LEFT JOIN images img ON a.mobile_hero_image_id = img.id
WHERE a.status = 'published';

-- Add triggers to update timestamps
CREATE TRIGGER IF NOT EXISTS update_articles_timestamp 
AFTER UPDATE ON articles
BEGIN
    UPDATE articles SET updated_at = CURRENT_TIMESTAMP, last_modified = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_authors_timestamp
AFTER UPDATE ON authors
BEGIN
    UPDATE authors SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_categories_timestamp
AFTER UPDATE ON categories
BEGIN
    UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_trending_timestamp
AFTER UPDATE ON trending_topics
BEGIN
    UPDATE trending_topics SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_mobile_metrics_timestamp
AFTER UPDATE ON mobile_metrics
BEGIN
    UPDATE mobile_metrics SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;