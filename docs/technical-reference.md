# Technical Reference

## Database Schema (Current State)

### Core Tables
```sql
-- All tables exist and working
authors (id, name, slug, title, bio, email, location, expertise, ...)
categories (id, name, slug, description, color, icon, parent_id, ...)
articles (id, title, slug, excerpt, content, author_id, category_id, ...)
trending_topics (id, title, slug, description, heat_score, ...)
images (id, content_type, content_id, image_type, ...)
article_sections (id, article_id, heading, content, order_num)
related_articles (id, article_id, related_article_id)
```

### Database Views
```sql
-- Exists and working
article_full_view  -- Articles with author/category info

-- Referenced but missing (will cause errors)
article_mobile_view  -- Used in search_backend.py
```

### Triggers & Constraints
- **Foreign keys**: Enabled and enforced
- **Triggers**: Auto-update timestamps and article counts
- **Indexes**: Defined for slug, publish_date, author_id, category_id

## Python API Reference

### DatabaseManager (`src/database/db_manager.py`)
```python
# Connection management
with db.get_connection() as conn:
    # Automatic commit/rollback

# CRUD operations
db.execute_query(sql, params)      # SELECT queries
db.execute_one(sql, params)        # Single row
db.execute_write(sql, params)      # INSERT/UPDATE/DELETE

# Content-specific methods (all working)
db.get_article(article_id=1)
db.get_articles(limit=20, offset=0)
db.create_article(title, slug, author_id, category_id, ...)
```

### Models (`src/models/`)
```python
# Base functionality (working)
Article.find_by_id(1)
Article.find_by_slug("my-article")
article.save()                     # Validates and sanitizes
article.delete()                   # Checks foreign keys

# Broken methods (will crash)
article.track_mobile_view()        # References missing table
article.get_responsive_images()    # References missing table
Article.search_fts()               # References missing table
```

### Integrators (`src/integrators/`)
```python
# Working functionality
integrator.sync_with_files()       # File to database sync
integrator.sync_all()              # Database to HTML
integrator.parse_content_file()    # Parse .txt files

# Content type integrators (all working)
ArticleIntegrator(), AuthorIntegrator()
CategoryIntegrator(), TrendingIntegrator()
```

### Configuration (`src/utils/config.py`)
```python
# Working configuration access
config.get('database.path')
config.get('limits.articles_per_page')
config.get_database_path()

# Many config options defined but unused
config.get('performance.enable_caching')  # Not implemented
config.get('images.generate_thumbnails')  # Not implemented
```

## Command Line Reference

### Working Commands
```bash
# Basic sync operations
python scripts/sync_content.py              # Full sync
python scripts/sync_content.py status       # Database check
python scripts/sync_content.py stats        # Content counts
python scripts/sync_content.py articles     # Sync articles only

# Wrapper scripts
python sync.py [args]                       # Calls sync_content.py
sync.bat [args]                            # Windows wrapper

# CSS development
npm run build-css                          # Tailwind compilation
npm run build-css-prod                     # Minified production
npm run dev                                # Watch mode
```

### Broken Commands
```bash
# These will fail due to import errors
python scripts/search_backend.py "query"   # Wrong import path
```

## Frontend JavaScript API

### Working Features
```javascript
// Live updates (fake data)
updateLiveReaders()                        // Random number generator
updateTime()                              // Clock display

// Mobile menu
openMobileMenu(), closeMobileMenuFunc()   // Hamburger menu

// Service worker
navigator.serviceWorker.register('/sw.js') // PWA functionality
```

### Broken Features
```javascript
// These reference empty arrays or broken endpoints
loadMoreArticles()                         // allArticles array empty
performSearch()                           // No actual search backend
selectSuggestion()                        // Hardcoded suggestions only
```

## File Formats

### Content File Format (.txt)
```
METADATA:
Title: Article Title
Author: Author Name (must exist in database)
Category: category-slug (must exist in database)
Slug: article-slug (optional, auto-generated)
Tags: tag1, tag2 (optional)

EXCERPT:
Brief description...

CONTENT:
Main article content...

SECTIONS:
## Section Heading
Section content...
```

### Configuration Format (config.yaml)
```yaml
database:
  path: "data/infnews.db"
  
limits:
  articles_per_page: 6              # Used in JavaScript
  max_articles_sync: 50             # Used in integrators
  
security:
  sanitize_html: true               # Used in sanitizer
  max_content_length: 50000         # Used in validation
  
# Many sections defined but not implemented
images:
  generate_thumbnails: true         # NOT IMPLEMENTED
performance:
  enable_caching: true              # NOT IMPLEMENTED
```

## Error Codes & Messages

### Database Errors
```
Foreign key constraint failed        # Deletion blocked by references
UNIQUE constraint failed            # Duplicate slug
NOT NULL constraint failed          # Missing required field
```

### Import Errors
```
ModuleNotFoundError: No module named 'database'  # Wrong import path
ModuleNotFoundError: No module named 'models'    # Path issue
```

### Validation Errors
```
Missing required field 'title'     # From sanitizer
Content exceeds maximum length      # Length validation
Invalid email format               # Email validation
```

## Security Configuration

### Currently Implemented
```python
# HTML sanitization (working)
allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
dangerous_patterns = [r'<script.*?>', r'javascript:', ...]

# SQL injection prevention (working)
# All queries use parameterized statements
```

### Missing Security Features
- No CSRF protection
- No rate limiting
- No authentication system
- No input length restrictions at database level
- No audit logging

## Performance Characteristics

### Database Performance
- **Queries**: Basic LIKE searches (no full-text search despite claims)
- **Pagination**: Some queries use LIMIT/OFFSET, others load all records
- **Indexes**: Exist but not optimally used
- **Connection**: One connection per operation (no pooling)

### Frontend Performance
- **CSS**: Large Tailwind file (~150KB estimated)
- **JavaScript**: All inline, no minification
- **Images**: External URLs, no optimization
- **Caching**: Service worker caches but no backend caching

## Deployment Requirements

### Minimum Requirements
- Static file hosting capability
- No server-side processing needed
- Modern web browser support

### Optional Enhancements
- Web server for proper MIME types
- HTTPS for PWA functionality
- Gzip compression for assets

### Production Issues
- No authentication means admin functions exposed
- Search broken means core functionality missing
- No monitoring or error reporting
- No backup/restore procedures