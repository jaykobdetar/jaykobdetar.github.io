-- Influencer News CMS Database Schema
-- Version 1.0
-- Includes comprehensive image management

-- Authors table
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    bio TEXT,
    expertise TEXT,
    linkedin_url TEXT,
    twitter_handle TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT, -- Emoji icon
    article_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Articles table
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    subtitle TEXT,
    author_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    publication_date DATE NOT NULL,
    read_time INTEGER, -- in minutes
    tags TEXT, -- JSON array stored as text
    meta_description TEXT,
    content TEXT NOT NULL,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES authors(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Trending topics table
CREATE TABLE trending_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT, -- Emoji icon
    category_id INTEGER,
    heat_score INTEGER DEFAULT 0,
    article_count INTEGER DEFAULT 0,
    related_articles TEXT, -- JSON array of article IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Images table for comprehensive image management
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL, -- 'article', 'author', 'category', 'trending'
    content_id INTEGER NOT NULL,
    image_type TEXT NOT NULL, -- 'hero', 'thumbnail', 'profile', 'icon', 'banner', 'cover'
    original_url TEXT, -- Store for procurement reference
    local_filename TEXT NOT NULL, -- Generated filename
    alt_text TEXT,
    caption TEXT,
    width INTEGER,
    height INTEGER,
    file_size INTEGER, -- in bytes
    mime_type TEXT,
    is_placeholder BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Article sections for structured content
CREATE TABLE article_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    section_order INTEGER NOT NULL,
    section_type TEXT NOT NULL, -- 'heading', 'paragraph', 'quote', 'list', 'callout'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Related articles junction table
CREATE TABLE related_articles (
    article_id INTEGER NOT NULL,
    related_article_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (article_id, related_article_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (related_article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_articles_author ON articles(author_id);
CREATE INDEX idx_articles_category ON articles(category_id);
CREATE INDEX idx_articles_date ON articles(publication_date);
CREATE INDEX idx_articles_slug ON articles(slug);
CREATE INDEX idx_authors_slug ON authors(slug);
CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_trending_slug ON trending_topics(slug);
CREATE INDEX idx_images_content ON images(content_type, content_id);
CREATE INDEX idx_images_type ON images(image_type);

-- Create views for common queries
CREATE VIEW article_full_view AS
SELECT 
    a.id,
    a.title,
    a.slug,
    a.subtitle,
    a.publication_date,
    a.read_time,
    a.tags,
    a.meta_description,
    a.content,
    a.view_count,
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

-- Create trigger to update timestamps
CREATE TRIGGER update_authors_timestamp 
AFTER UPDATE ON authors
BEGIN
    UPDATE authors SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_categories_timestamp 
AFTER UPDATE ON categories
BEGIN
    UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_articles_timestamp 
AFTER UPDATE ON articles
BEGIN
    UPDATE articles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_trending_timestamp 
AFTER UPDATE ON trending_topics
BEGIN
    UPDATE trending_topics SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_images_timestamp 
AFTER UPDATE ON images
BEGIN
    UPDATE images SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Insert default categories including the missing "lifestyle" category
INSERT INTO categories (name, slug, description, icon) VALUES
('Technology', 'technology', 'Latest in tech, AI, and digital innovation', '💻'),
('Business', 'business', 'Business strategies and entrepreneurship', '💼'),
('Entertainment', 'entertainment', 'Movies, music, and pop culture', '🎬'),
('Fashion', 'fashion', 'Style trends and fashion industry news', '👗'),
('Creator Economy', 'creator-economy', 'Insights into the creator economy', '🎨'),
('Charity', 'charity', 'Philanthropy and social impact', '❤️'),
('Lifestyle', 'lifestyle', 'Lifestyle trends and personal development', '🌟');