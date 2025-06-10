# Database Schema Documentation

Complete documentation of the SQLite database schema for Influencer News CMS.

## 🗄️ Overview

The CMS uses SQLite as its primary database with a normalized schema design emphasizing data integrity and performance.

**Database File**: `data/infnews.db`  
**Engine**: SQLite 3  
**Features**: Foreign keys enabled, full-text search, indexes  
**Size**: ~50KB with sample data  

## 📊 Tables Overview

| Table | Purpose | Records | Relationships |
|-------|---------|---------|---------------|
| `authors` | Writer profiles | 4 | → articles |
| `categories` | Content classification | 7 | → articles |
| `trending_topics` | Hot topics tracking | 4 | Independent |
| `articles` | News articles | 0+ | ← authors, categories |
| `images` | Media asset tracking | 12 | ↔ All content |
| `article_sections` | Article content blocks | 0+ | ← articles |
| `related_articles` | Article relationships | 0+ | ← articles |

## 🏗️ Schema Definition

### Authors Table

```sql
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

-- Indexes
CREATE INDEX idx_authors_slug ON authors(slug);
CREATE INDEX idx_authors_active ON authors(is_active);
```

**Sample Data**:
```sql
INSERT INTO authors (name, slug, title, bio, email, location, expertise, twitter, linkedin) VALUES
('Jessica Kim', 'jessica-kim', 'Beauty & Fashion Editor', 
 'Former Vogue digital editor covering beauty influencer partnerships', 
 'jessica.kim@influencernews.com', 'Los Angeles, CA',
 'Beauty, Fashion, Influencer Collabs', '@jessicakim', 
 'https://linkedin.com/in/jessicakim');
```

### Categories Table

```sql
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

-- Indexes
CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_featured ON categories(is_featured);
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

**Sample Data**:
```sql
INSERT INTO categories (name, slug, description, color, icon, sort_order) VALUES
('Technology', 'technology', 'Latest in tech, AI, and digital innovation', '#3B82F6', '💻', 1),
('Creator Economy', 'creator-economy', 'Business of content creation and monetization', '#10B981', '💰', 2),
('Entertainment', 'entertainment', 'Celebrity culture and entertainment industry news', '#F59E0B', '🎬', 3);
```

### Trending Topics Table

```sql
CREATE TABLE trending_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    content TEXT,               -- Detailed analysis
    heat_score INTEGER DEFAULT 0,  -- 0-100
    growth_rate REAL DEFAULT 0.0,  -- Percentage
    hashtag TEXT,
    category_id INTEGER,
    start_date TEXT DEFAULT CURRENT_TIMESTAMP,
    peak_date TEXT,
    status TEXT DEFAULT 'active',  -- active, rising, steady, declining
    mentions_youtube INTEGER DEFAULT 0,
    mentions_tiktok INTEGER DEFAULT 0,
    mentions_instagram INTEGER DEFAULT 0,
    mentions_twitter INTEGER DEFAULT 0,
    mentions_twitch INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Indexes
CREATE INDEX idx_trending_slug ON trending_topics(slug);
CREATE INDEX idx_trending_heat ON trending_topics(heat_score DESC);
CREATE INDEX idx_trending_status ON trending_topics(status);
CREATE INDEX idx_trending_category ON trending_topics(category_id);
```

**Sample Data**:
```sql
INSERT INTO trending_topics (title, slug, description, heat_score, hashtag, status) VALUES
('AI Content Creation Revolution', 'ai-content-creation-revolution',
 'Artificial intelligence tools transforming how creators make content',
 95, '#AICreators', 'active');
```

### Articles Table

```sql
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

-- Indexes
CREATE INDEX idx_articles_slug ON articles(slug);
CREATE INDEX idx_articles_author ON articles(author_id);
CREATE INDEX idx_articles_category ON articles(category_id);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_featured ON articles(featured);
CREATE INDEX idx_articles_trending ON articles(trending);
CREATE INDEX idx_articles_publish_date ON articles(publish_date DESC);

-- Full-text search
CREATE VIRTUAL TABLE articles_fts USING fts5(
    title, excerpt, content, tags,
    content_rowid=articles
);
```

### Images Table

```sql
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

-- Indexes
CREATE INDEX idx_images_content ON images(content_type, content_id);
CREATE INDEX idx_images_type ON images(image_type);
CREATE INDEX idx_images_local ON images(local_filename);
```

**Sample Data**:
```sql
INSERT INTO images (content_type, content_id, image_type, original_url, local_filename, alt_text) VALUES
('author', 1, 'profile', 
 'https://images.unsplash.com/photo-1494790108755-2616c395d75b',
 'author_jessica-kim_profile.jpg', 'Jessica Kim profile photo');
```

### Article Sections Table

```sql
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

-- Indexes
CREATE INDEX idx_sections_article ON article_sections(article_id, order_num);
```

### Related Articles Table

```sql
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

-- Indexes
CREATE INDEX idx_related_article ON related_articles(article_id);
CREATE INDEX idx_related_target ON related_articles(related_article_id);
```

## 🔗 Relationships

### Primary Relationships

```
authors (1) ←→ (N) articles
categories (1) ←→ (N) articles
trending_topics (1) ←→ (N) categories [optional]
```

### Polymorphic Relationships

```
images (N) ←→ (1) authors|categories|trending_topics|articles
```

### Self-Referencing Relationships

```
categories (1) ←→ (N) categories [parent/child]
articles (N) ←→ (N) articles [related articles]
```

## 🚀 Performance Optimizations

### Indexes

**Primary Indexes**:
- All foreign key columns indexed
- Slug columns for URL lookups
- Status columns for filtering
- Date columns for sorting

**Search Indexes**:
- Full-text search on articles content
- Composite indexes for common queries
- Partial indexes for active content

**Query Examples**:
```sql
-- Fast author lookup by slug
SELECT * FROM authors WHERE slug = 'jessica-kim';

-- Fast article listing by category
SELECT a.*, au.name as author_name 
FROM articles a 
JOIN authors au ON a.author_id = au.id 
WHERE a.category_id = 1 AND a.status = 'published'
ORDER BY a.publish_date DESC;

-- Fast trending topics by heat score
SELECT * FROM trending_topics 
WHERE status = 'active' 
ORDER BY heat_score DESC LIMIT 10;
```

### Query Optimization

**Common Patterns**:
```sql
-- Articles with author and category info
SELECT 
    a.id, a.title, a.excerpt, a.publish_date,
    au.name as author_name, au.slug as author_slug,
    c.name as category_name, c.slug as category_slug
FROM articles a
JOIN authors au ON a.author_id = au.id
JOIN categories c ON a.category_id = c.id
WHERE a.status = 'published'
ORDER BY a.publish_date DESC;

-- Search across all content types
SELECT 'article' as type, title, slug FROM articles WHERE title LIKE '%query%'
UNION ALL
SELECT 'author' as type, name, slug FROM authors WHERE name LIKE '%query%'
UNION ALL
SELECT 'category' as type, name, slug FROM categories WHERE name LIKE '%query%'
UNION ALL
SELECT 'trending' as type, title, slug FROM trending_topics WHERE title LIKE '%query%';
```

## 🔒 Data Integrity

### Foreign Key Constraints

**Enabled**: `PRAGMA foreign_keys = ON`  
**Behavior**: RESTRICT on delete (prevents orphaned records)  
**Cascade**: Only for dependent tables (sections, related articles)  

### Data Validation

**Required Fields**: NOT NULL constraints on essential fields  
**Unique Constraints**: Slugs and email addresses  
**Check Constraints**: Heat scores (0-100), ratings (0-5)  
**Default Values**: Timestamps, counters, status fields  

### Triggers

```sql
-- Update article count when articles change
CREATE TRIGGER update_author_article_count 
AFTER INSERT ON articles
BEGIN
    UPDATE authors 
    SET article_count = (
        SELECT COUNT(*) FROM articles 
        WHERE author_id = NEW.author_id AND status = 'published'
    )
    WHERE id = NEW.author_id;
END;

-- Update timestamps on record changes
CREATE TRIGGER update_authors_timestamp 
AFTER UPDATE ON authors
BEGIN
    UPDATE authors SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

## 📊 Database Statistics

### Current Content

```sql
-- Content summary
SELECT 
    'Authors' as content_type, COUNT(*) as count FROM authors
UNION ALL
SELECT 'Categories', COUNT(*) FROM categories  
UNION ALL
SELECT 'Trending Topics', COUNT(*) FROM trending_topics
UNION ALL
SELECT 'Articles', COUNT(*) FROM articles
UNION ALL
SELECT 'Images', COUNT(*) FROM images;
```

**Results**:
- Authors: 4
- Categories: 7  
- Trending Topics: 4
- Articles: 0
- Images: 12

### Storage Information

```sql
-- Database size and table info
SELECT 
    name,
    COUNT(*) as row_count
FROM sqlite_master 
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
GROUP BY name;

-- Database file size
SELECT page_count * page_size as size_bytes 
FROM pragma_page_count(), pragma_page_size();
```

## 🛠️ Database Maintenance

### Backup Strategy

```bash
# Regular backup
sqlite3 data/infnews.db ".backup data/infnews_backup_$(date +%Y%m%d).db"

# Export as SQL
sqlite3 data/infnews.db ".dump" > data/infnews_backup.sql
```

### Optimization

```sql
-- Analyze query performance
ANALYZE;

-- Vacuum database (reclaim space)
VACUUM;

-- Check integrity
PRAGMA integrity_check;

-- Update statistics
PRAGMA optimize;
```

### Migration Scripts

**Schema Changes**:
```sql
-- Example: Adding new column
ALTER TABLE authors ADD COLUMN twitter_verified BOOLEAN DEFAULT 0;

-- Example: Creating new index
CREATE INDEX idx_authors_verified ON authors(twitter_verified) 
WHERE twitter_verified = 1;
```

---

**Last Updated**: December 10, 2024  
**Schema Version**: 1.0.0  
**Database Engine**: SQLite 3.37+  
**Total Tables**: 7 (+ 1 FTS virtual table)