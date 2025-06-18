# CLAUDE.md

This file provides guidance to Claude Code when working with this Influencer News CMS repository.

## Current Project State

This is a **partially implemented** static site generator with significant gaps between ideal design and current reality. Many features are incomplete or broken.

## Working Commands

### Content Management
```bash
# WORKING - Check database status and connectivity
python scripts/sync_content.py status

# WORKING - View content statistics and counts
python scripts/sync_content.py stats

# WORKING - Sync content from .txt files to database and generate HTML
python scripts/sync_content.py

# WORKING - Sync specific content types
python scripts/sync_content.py articles
python scripts/sync_content.py authors
python scripts/sync_content.py categories
python scripts/sync_content.py trending
```

### CSS Development
```bash
# WORKING - Build production CSS with Tailwind
npm run build

# WORKING - Development mode with watch
npm run dev
```

### Broken Commands
```bash
# BROKEN - Search backend has import errors
python scripts/search_backend.py "search term"

# NO TESTS - Testing infrastructure incomplete
pytest
```

## Architecture Reality

### What Actually Works

1. **Database Layer** (`src/database/`)
   - SQLite database with well-designed schema
   - DatabaseManager with connection pooling, transactions, foreign keys
   - 7 tables: authors, categories, articles, trending_topics, images, article_sections, related_articles

2. **Models Layer** (`src/models/`)
   - Active Record pattern with BaseModel
   - CRUD operations work correctly
   - **WARNING**: Mobile and FTS methods reference non-existent tables

3. **Content Sync** (`scripts/sync_content.py`)
   - Parses .txt files from `content/` directories
   - Validates and sanitizes content
   - Generates static HTML pages in `integrated/`
   - **LIMITATION**: Only adds new content, cannot update existing

4. **Basic Frontend**
   - Static HTML with Tailwind CSS
   - Database-generated pages work

### What's Broken

1. **Homepage** (`index.html`)
   - Shows only ONE hardcoded article
   - Load More button references empty array
   - Live reader count is fake random numbers

2. **Search System**
   - Backend script has wrong import path: `src` should be `../src`
   - Frontend search does nothing
   - No actual search functionality

3. **PWA Features**
   - All icon files missing (192x192.png, 512x512.png, etc.)
   - Manifest shortcuts broken
   - Service worker references non-existent endpoints

4. **Mobile Methods**
   - Article mobile methods crash (reference missing `mobile_metrics` table)
   - Mobile view references missing `article_mobile_view`

5. **Image System**
   - Tracks external URLs but doesn't download images
   - Procurement list generated but unused

## Critical Issues to Fix

### High Priority
1. **Fix Search Backend Import**: Change `src` to `../src` in search_backend.py
2. **Homepage Dynamic Loading**: Replace hardcoded article with database loading
3. **Remove Broken Mobile Methods**: Comment out methods that reference missing tables
4. **Implement Missing Database Views**: Create `article_mobile_view` or remove references

### Medium Priority
1. **Content Updates**: Implement modification of existing content
2. **Image Download**: Complete image management system
3. **PWA Assets**: Add missing icon files and fix manifest
4. **Authentication**: Add user system and access control

## Content Management Reality

### File-to-Database Sync
- Place `.txt` files in `content/{type}/` directories
- Run `python scripts/sync_content.py` to process
- **IMPORTANT**: Can only ADD new content, not update existing
- Must manually edit database or delete file and re-add to change content

### Content Format
```
METADATA:
Title: Article Title
Author: Author Name (must exist in database first)
Category: category-slug (must exist in database first)

CONTENT:
Article content here...
```

## Database Schema Notes

### Existing Tables (All Work)
- `authors` - Content creator profiles
- `categories` - Content classification  
- `articles` - Main content with relationships
- `trending_topics` - Hot topics with heat scores
- `images` - External URL tracking
- `article_sections` - Article subsections
- `related_articles` - Article relationships

### Missing but Referenced
- `mobile_metrics` - Referenced by Article.track_mobile_view()
- `image_variants` - Referenced by Article.get_responsive_images()
- `articles_fts` - Referenced by Article.search_fts()
- `article_mobile_view` - Referenced by search_backend.py

## Configuration

- Main config: `config.yaml`
- Many options defined but not implemented in code
- Database path: `data/infnews.db`
- Generated HTML: `integrated/` directory

## Development Workflow

1. **Before making changes**: Read `docs/current-state-overview.md` for limitations
2. **Adding content**: Use content management commands above
3. **Fixing bugs**: Check `suggestions.txt` for known issues
4. **Testing**: Manual testing required (no automated tests)

## Security Notes

- **No authentication system** - everything is public
- **Input sanitization** exists but not comprehensive
- **Foreign key constraints** prevent data corruption
- **HTML sanitization** removes dangerous tags

## Performance Characteristics

- **Database**: Queries mostly work but some lack LIMIT clauses
- **Frontend**: Large inline CSS/JS, no optimization
- **Pagination**: JavaScript-only, not database-level
- **Caching**: Service worker only, no backend caching

## Known Limitations

1. Cannot update existing content (only add new)
2. Search completely broken
3. Homepage static instead of dynamic
4. Mobile features crash on missing tables
5. Image downloading not implemented
6. No user authentication
7. No content versioning
8. No deployment automation

## Documentation

- `docs/README.md` - Accurate project overview
- `docs/current-state-overview.md` - What works vs what's broken
- `docs/content-management.md` - How to add content
- `docs/technical-reference.md` - API and database details
- `suggestions.txt` - All known issues and improvements needed