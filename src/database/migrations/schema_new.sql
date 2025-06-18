-- Influencer News CMS Database Schema
-- Version 2.0 - Upgraded to match comprehensive documentation
-- Includes all advanced features from docs/database-schema.md

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Authors table with comprehensive profile information
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    title TEXT,
    bio TEXT,
    email TEXT,
    location TEXT,
    expertise TEXT,  -- Comma-separated
    twitter TEXT,
    linkedin TEXT,
    image_url TEXT,
    joined_date TEXT DEFAULT CURRENT_TIMESTAMP,
    article_count INTEGER DEFAULT 0,
    rating REAL DEFAULT 0.0,
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Categories table with hierarchical support and styling
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#6B7280',  -- Hex color
    icon TEXT DEFAULT '📁',         -- Emoji icon
    parent_id INTEGER,              -- For subcategories
    sort_order INTEGER DEFAULT 999,
    article_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);

-- Articles table with comprehensive content management
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    excerpt TEXT,               -- Brief summary
    content TEXT,               -- Full article content
    author_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    status TEXT DEFAULT 'draft', -- draft, published, archived
    featured BOOLEAN DEFAULT 0,
    trending BOOLEAN DEFAULT 0,
    publish_date TEXT,
    image_url TEXT,             -- Featured image
    hero_image_url TEXT,        -- Large hero image
    thumbnail_url TEXT,         -- Small thumbnail
    tags TEXT,                  -- Comma-separated
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    read_time_minutes INTEGER DEFAULT 0,
    seo_title TEXT,
    seo_description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE RESTRICT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- Trending topics table with comprehensive social media tracking
CREATE TABLE trending_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    content TEXT,               -- Detailed analysis
    heat_score INTEGER DEFAULT 0,  -- 0-100
    growth_rate REAL DEFAULT 0.0,  -- Percentage
    momentum REAL DEFAULT 0.0,     -- Rate of heat score change
    article_count INTEGER DEFAULT 0,
    related_articles TEXT,         -- JSON array of article IDs
    hashtag TEXT,
    icon TEXT DEFAULT '🔥',         -- Emoji icon
    category_id INTEGER,
    start_date TEXT DEFAULT CURRENT_TIMESTAMP,
    peak_date TEXT,
    status TEXT DEFAULT 'active',  -- active, rising, steady, declining
    mentions_youtube INTEGER DEFAULT 0,
    mentions_tiktok INTEGER DEFAULT 0,
    mentions_instagram INTEGER DEFAULT 0,
    mentions_twitter INTEGER DEFAULT 0,
    mentions_twitch INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Images table for comprehensive image management
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,     -- 'author', 'category', 'trending', 'article'
    content_id INTEGER NOT NULL,    -- ID of the related content
    image_type TEXT NOT NULL,       -- 'profile', 'thumbnail', 'hero', 'banner', 'cover'
    original_url TEXT,              -- External URL if applicable
    local_filename TEXT,            -- Local file path
    alt_text TEXT,
    caption TEXT,
    width INTEGER,
    height INTEGER,
    file_size INTEGER,              -- In bytes
    mime_type TEXT,
    is_placeholder BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Article sections for structured content
CREATE TABLE article_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    heading TEXT,
    content TEXT NOT NULL,
    section_type TEXT DEFAULT 'paragraph', -- paragraph, heading, quote, list, image
    order_num INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Related articles with relationship types
CREATE TABLE related_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    related_article_id INTEGER NOT NULL,
    relationship_type TEXT DEFAULT 'related', -- related, follow_up, series
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (related_article_id) REFERENCES articles(id) ON DELETE CASCADE,
    UNIQUE(article_id, related_article_id)
);

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

-- Authors indexes
CREATE INDEX idx_authors_slug ON authors(slug);
CREATE INDEX idx_authors_active ON authors(is_active);
CREATE INDEX idx_authors_email ON authors(email);

-- Categories indexes  
CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_featured ON categories(is_featured);
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_sort ON categories(sort_order);

-- Articles indexes
CREATE INDEX idx_articles_slug ON articles(slug);
CREATE INDEX idx_articles_author ON articles(author_id);
CREATE INDEX idx_articles_category ON articles(category_id);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_featured ON articles(featured);
CREATE INDEX idx_articles_trending ON articles(trending);
CREATE INDEX idx_articles_publish_date ON articles(publish_date DESC);

-- Trending topics indexes
CREATE INDEX idx_trending_slug ON trending_topics(slug);
CREATE INDEX idx_trending_heat ON trending_topics(heat_score DESC);
CREATE INDEX idx_trending_status ON trending_topics(status);
CREATE INDEX idx_trending_category ON trending_topics(category_id);

-- Images indexes
CREATE INDEX idx_images_content ON images(content_type, content_id);
CREATE INDEX idx_images_type ON images(image_type);
CREATE INDEX idx_images_local ON images(local_filename);

-- Article sections indexes
CREATE INDEX idx_sections_article ON article_sections(article_id, order_num);

-- Related articles indexes
CREATE INDEX idx_related_article ON related_articles(article_id);
CREATE INDEX idx_related_target ON related_articles(related_article_id);

-- ================================
-- FULL-TEXT SEARCH
-- ================================

-- Full-text search disabled due to corruption issues
-- CREATE VIRTUAL TABLE articles_fts USING fts5(
--     title, excerpt, content, tags,
--     content_rowid=articles
-- );

-- ================================
-- TRIGGERS FOR DATA INTEGRITY
-- ================================

-- Update timestamps automatically
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

-- Maintain article counts for authors
CREATE TRIGGER update_author_article_count_insert
AFTER INSERT ON articles
BEGIN
    UPDATE authors 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE author_id = NEW.author_id AND status = 'published'
    )
    WHERE id = NEW.author_id;
END;

CREATE TRIGGER update_author_article_count_delete
AFTER DELETE ON articles
BEGIN
    UPDATE authors 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE author_id = OLD.author_id AND status = 'published'
    )
    WHERE id = OLD.author_id;
END;

CREATE TRIGGER update_author_article_count_update
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

-- Maintain article counts for categories
CREATE TRIGGER update_category_article_count_insert
AFTER INSERT ON articles
BEGIN
    UPDATE categories 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE category_id = NEW.category_id AND status = 'published'
    )
    WHERE id = NEW.category_id;
END;

CREATE TRIGGER update_category_article_count_delete
AFTER DELETE ON articles
BEGIN
    UPDATE categories 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE category_id = OLD.category_id AND status = 'published'
    )
    WHERE id = OLD.category_id;
END;

CREATE TRIGGER update_category_article_count_update
AFTER UPDATE ON articles
BEGIN
    UPDATE categories 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE category_id = NEW.category_id AND status = 'published'
    )
    WHERE id = NEW.category_id;
    
    -- Update old category if category changed
    UPDATE categories 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE category_id = OLD.category_id AND status = 'published'
    )
    WHERE id = OLD.category_id AND OLD.category_id != NEW.category_id;
END;

-- FTS triggers disabled due to corruption issues
-- CREATE TRIGGER articles_fts_insert AFTER INSERT ON articles
-- BEGIN
--     INSERT INTO articles_fts(rowid, title, excerpt, content, tags)
--     VALUES (NEW.id, NEW.title, NEW.excerpt, NEW.content, NEW.tags);
-- END;

-- CREATE TRIGGER articles_fts_delete AFTER DELETE ON articles
-- BEGIN
--     DELETE FROM articles_fts WHERE rowid = OLD.id;
-- END;

-- CREATE TRIGGER articles_fts_update AFTER UPDATE ON articles
-- BEGIN
--     DELETE FROM articles_fts WHERE rowid = OLD.id;
--     INSERT INTO articles_fts(rowid, title, excerpt, content, tags)
--     VALUES (NEW.id, NEW.title, NEW.excerpt, NEW.content, NEW.tags);
-- END;

-- ================================
-- SAMPLE DATA
-- ================================

-- Insert enhanced categories with colors and sort order
INSERT INTO categories (name, slug, description, color, icon, sort_order) VALUES
('Technology', 'technology', 'Latest in tech, AI, and digital innovation', '#3B82F6', '💻', 1),
('Creator Economy', 'creator-economy', 'Business of content creation and monetization', '#10B981', '💰', 2),
('Entertainment', 'entertainment', 'Celebrity culture and entertainment industry news', '#F59E0B', '🎬', 3),
('Business', 'business', 'Business strategies and entrepreneurship', '#8B5CF6', '💼', 4),
('Fashion', 'fashion', 'Style trends and fashion industry news', '#EC4899', '👗', 5),
('Charity', 'charity', 'Philanthropy and social impact', '#EF4444', '❤️', 6),
('Lifestyle', 'lifestyle', 'Lifestyle trends and personal development', '#6B7280', '🌟', 7);

-- Insert enhanced authors with full profile data
INSERT INTO authors (name, slug, title, bio, email, location, expertise, twitter, linkedin, rating, is_active) VALUES
('Jessica Kim', 'jessica-kim', 'Beauty & Fashion Editor', 
 'Former Vogue digital editor covering beauty influencer partnerships and fashion industry trends', 
 'jessica.kim@influencernews.com', 'Los Angeles, CA',
 'Beauty, Fashion, Influencer Partnerships', '@jessicakim', 
 'https://linkedin.com/in/jessicakim', 4.8, 1),

('Sarah Chen', 'sarah-chen', 'Tech Correspondent', 
 'Covers AI, creator tools, and emerging technologies in the influencer space',
 'sarah.chen@influencernews.com', 'San Francisco, CA',
 'Technology, AI, Creator Tools', '@sarahchen_tech',
 'https://linkedin.com/in/sarahchen', 4.9, 1),

('Alex Rivera', 'alex-rivera', 'Business Reporter',
 'Specializes in creator economy, brand partnerships, and influencer marketing strategies',
 'alex.rivera@influencernews.com', 'New York, NY', 
 'Creator Economy, Brand Partnerships, Marketing', '@alexrivera_biz',
 'https://linkedin.com/in/alexrivera', 4.7, 1),

('Michael Torres', 'michael-torres', 'Entertainment Editor',
 'Covers celebrity influencers, entertainment industry trends, and pop culture intersections',
 'michael.torres@influencernews.com', 'Los Angeles, CA',
 'Entertainment, Celebrity Culture, Pop Culture', '@migueltorres',
 'https://linkedin.com/in/michaeltorres', 4.6, 1),

('Maria Lopez', 'maria-lopez', 'Social Impact Writer',
 'Focuses on influencer-driven charitable initiatives and social justice movements',
 'maria.lopez@influencernews.com', 'Austin, TX',
 'Social Impact, Charity, Activism', '@marialopez_impact',
 'https://linkedin.com/in/marialopez', 4.8, 1);

-- Insert enhanced trending topics with social media tracking
INSERT INTO trending_topics (title, slug, description, content, heat_score, growth_rate, hashtag, status, mentions_youtube, mentions_tiktok, mentions_instagram, mentions_twitter) VALUES
('AI Content Creation Revolution', 'ai-content-creation-revolution',
 'Artificial intelligence tools transforming how creators make content',
 'The rise of AI tools like ChatGPT, Midjourney, and automated video editing is fundamentally changing content creation...', 
 95, 15.5, '#AICreators', 'active', 2500, 8900, 4200, 12000),

('Creator Burnout Crisis', 'creator-burnout-crisis', 
 'Mental health challenges facing content creators in 2024',
 'A growing conversation about sustainable content creation and creator wellbeing...', 
 87, 8.2, '#CreatorBurnout', 'rising', 1800, 6500, 3100, 8900),

('MrBeast Creator Fund', 'mrbeast-creator-fund',
 'MrBeast launches $100M fund to support emerging creators',
 'YouTube sensation MrBeast announces unprecedented investment in creator ecosystem...', 
 92, 12.1, '#MrBeastFund', 'active', 3200, 15000, 8900, 18500);

-- Create views for common queries
CREATE VIEW article_full_view AS
SELECT 
    a.id,
    a.title,
    a.slug,
    a.excerpt,
    a.status,
    a.featured,
    a.trending,
    a.publish_date,
    a.views,
    a.likes,
    a.read_time_minutes,
    a.image_url,
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

-- Performance optimization
ANALYZE;