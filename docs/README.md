# CMS Documentation

## Current Implementation Status

This documentation reflects the **actual current state** of the CMS, not planned or ideal features. The site can be completely rebranded through configuration files.

## Quick Start

### Prerequisites
- Python 3.7+
- Node.js (for Tailwind CSS)
- Web browser

### Basic Setup
```bash
# 1. Install Python dependencies (none required - uses built-in libraries)
# 2. Install Node dependencies for CSS
npm install

# 3. Build CSS
npm run build

# 4. Check database status
python scripts/sync_content.py status

# 5. Sync content (most important command)
python scripts/sync_content.py

# 6. Configure site branding (optional)
# Edit content/site/site-branding.txt
python scripts/sync_content.py site

# 7. Open index.html in browser
```

### What Actually Works
- Database content management via Python scripts
- Static HTML generation from database
- Basic content sync from .txt files
- Author, category, and trending topic management

### What's Currently Broken
- Search uses simulated data (backend fixed but not integrated)
- Image downloading system not implemented
- PWA missing all icon assets
- Content updates not supported (only add/delete)

## Architecture Overview

### Database Layer
- **Technology**: SQLite with comprehensive schema
- **Tables**: authors, categories, articles, trending_topics, images, article_sections, related_articles, site_config
- **Features**: Foreign keys, triggers, indexes
- **Issues**: Some referenced views don't exist

### Backend (Python)
- **Models**: Active Record pattern with direct database access
- **Integrators**: Convert database content to static HTML
- **Utilities**: Configuration, sanitization, path management
- **Issues**: Import path problems, incomplete implementations

### Frontend
- **Technology**: Static HTML with Tailwind CSS
- **JavaScript**: Inline, unstructured
- **Issues**: Hardcoded content, non-functional search, broken PWA

## Project Structure

```
├── index.html              # Homepage (mostly hardcoded)
├── search.html             # Search page (non-functional)
├── authors.html            # Authors listing
├── src/                    # Python source code
│   ├── database/           # Database manager and schema
│   ├── models/             # Data models (Article, Author, etc.)
│   ├── integrators/        # HTML generation from database
│   └── utils/              # Utilities and configuration
├── scripts/                # Command-line tools
│   ├── sync_content.py     # Main sync tool
│   └── search_backend.py   # Search API (broken imports)
├── integrated/             # Generated HTML pages
├── content/                # Source content files (.txt)
├── data/                   # Database and JSON files
├── assets/                 # CSS, JS, images
└── docs/                   # Documentation
```

## Core Commands

```bash
# Content Management
python scripts/sync_content.py              # Sync all content
python scripts/sync_content.py status       # Check database
python scripts/sync_content.py stats        # Show content counts
python scripts/sync_content.py articles     # Sync articles only

# CSS Development
npm run dev                                  # Watch mode
npm run build                               # Production build

# Shortcuts (wrapper scripts)
python sync.py                              # Same as sync_content.py
sync.bat                                    # Windows wrapper
```

## Content Management

### Supported Content Types
1. **Articles**: News articles with sections
2. **Authors**: Content creator profiles  
3. **Categories**: Content classification
4. **Trending Topics**: Hot topics with heat scores

### Content Format (.txt files)
Place files in `content/{type}/` directories:
- `content/articles/my-article.txt`
- `content/authors/author-name.txt`
- `content/categories/category-name.txt`
- `content/trending/topic-name.txt`

### Sync Process
1. Parses .txt files for metadata and content
2. Validates and sanitizes content
3. Stores in SQLite database
4. Generates static HTML pages
5. **Only adds new content - no updates supported**

## Known Issues & Limitations

### Critical Issues
1. **Search Broken**: Import errors prevent search from working
2. **Homepage Static**: Only shows one hardcoded article
3. **Mobile Methods Crash**: Reference non-existent database tables
4. **No Content Updates**: Can only add new content
5. **Missing Authentication**: No access control anywhere

### Security Issues
- No CSRF protection
- No rate limiting
- Input sanitization not consistently applied
- Service worker too permissive

### Performance Issues
- No real pagination (loads entire tables)
- No caching implemented
- Large CSS files
- Inline JavaScript

## Development

### File Structure
- **Configuration**: `config.yaml` (many options unused)
- **Database**: `data/infnews.db` (SQLite)
- **Logs**: `logs/cms.log` (if configured)
- **Generated Files**: `integrated/` directory

### Database Schema
Well-designed with proper relationships and constraints. See `src/database/schema.sql` for complete structure.

### Testing
Basic pytest tests exist but incomplete coverage:
```bash
pytest                    # Run all tests
pytest -v                # Verbose output
```

## Deployment

### Current State
- Static files can be hosted anywhere
- No server-side processing required
- **But**: Many features are broken or incomplete

### Production Readiness
**Not ready for production** due to:
- Broken search functionality
- Missing authentication
- Incomplete error handling
- No deployment automation

## Configuration

Main configuration in `config.yaml`:
- Database paths and settings
- Content limits and pagination
- Security settings
- Logging configuration
- **Many options defined but not implemented**

## Support

For issues with the current implementation:
1. Check this documentation for current limitations
2. Review `suggestions.txt` for known issues
3. Test database connectivity with `python scripts/sync_content.py status`

## Contributing

Before adding features:
1. Fix existing broken functionality
2. Complete partially implemented features
3. Add proper error handling
4. Implement missing authentication