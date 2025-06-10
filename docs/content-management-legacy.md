# Content Management Guide

## Overview

Your Influencer News CMS now has a comprehensive content management system with both GUI and command-line interfaces for managing all content types.

## Available Tools

### 1. GUI Content Manager (`content_manager.py`)

A full-featured GUI application for content management (requires tkinter):

```bash
python3 content_manager.py
```

**Features:**
- Browse all content types (articles, authors, categories, trending, images)
- Add, edit, and delete content
- Sync content to HTML pages
- Real-time search and filtering
- Database query interface
- Image management
- Site statistics

### 2. Command-Line Sync Tool (`sync_content.py`)

A lightweight command-line tool for syncing content:

```bash
# Check database connectivity
python3 sync_content.py check

# Show content statistics
python3 sync_content.py stats

# Sync all content types
python3 sync_content.py sync --all

# Sync specific content type
python3 sync_content.py sync --type authors
python3 sync_content.py sync --type categories
python3 sync_content.py sync --type trending
python3 sync_content.py sync --type articles

# List content of specific type
python3 sync_content.py list --type authors
python3 sync_content.py list --type categories
```

## Content Management Workflow

### 1. Database-First Approach

All content is stored in the SQLite database (`data/infnews.db`). HTML pages are generated from this database.

### 2. Adding New Content

**Option A: Direct Database Management**
```python
from src.database.db_manager import DatabaseManager
from src.models.author import Author

# Add new author
Author.create(
    name="New Author",
    title="Editor",
    bio="Author biography",
    email="author@example.com",
    location="City, State",
    expertise="Topic 1, Topic 2",
    twitter="@handle",
    linkedin="https://linkedin.com/in/profile"
)
```

**Option B: Use GUI Content Manager**
1. Launch `python3 content_manager.py`
2. Select content type from sidebar
3. Click "Add New" in actions panel
4. Fill out the form
5. Save and sync

### 3. Syncing Content to HTML

After making changes to the database, sync content to regenerate HTML pages:

```bash
# Sync everything
python3 sync_content.py sync --all

# Or use the GUI "Sync All" button
```

### 4. Content Types

**Authors**
- Stored in `authors` table
- Generated pages: `integrated/authors/author_{slug}.html`
- Listing page: `authors.html`

**Categories** 
- Stored in `categories` table
- Generated pages: `integrated/categories/category_{slug}.html`
- Listing page: `integrated/categories.html`

**Trending Topics**
- Stored in `trending_topics` table  
- Generated pages: `integrated/trending/trend_{slug}.html`
- Listing page: `integrated/trending.html`

**Articles**
- Stored in `articles` table
- Generated pages: `integrated/articles/article_{id}.html`
- Updates homepage and search page

**Images**
- Tracked in `images` table
- Local files in `assets/images/`
- Procurement list: `data/image_procurement_list.csv`

## Image Management

### Current Status
- External URLs tracked in database
- Local file structure ready
- Placeholder SVG images active
- 12 images ready for procurement

### Procurement Process
1. Review `data/image_procurement_list.csv`
2. Download each image to appropriate directory:
   - `assets/images/authors/`
   - `assets/images/categories/`
   - `assets/images/trending/`
   - `assets/images/articles/`
3. Images will replace placeholders automatically

### Image Naming Convention
```
# Authors
author_{slug}_profile.jpg
author_{slug}_thumbnail.jpg

# Categories
category_{slug}_banner.jpg

# Trending Topics
trending_{slug}_cover.jpg

# Articles
article_{id}_hero.jpg
article_{id}_thumbnail.jpg
```

## Database Schema

### Core Tables
- `authors` - Author profiles
- `categories` - Content categories
- `trending_topics` - Trending topics with heat scores
- `articles` - News articles
- `images` - Image asset tracking

### Relationships
- Articles → Authors (foreign key)
- Articles → Categories (foreign key) 
- Images → All content types (polymorphic)

## Troubleshooting

### Common Issues

**1. Module Import Errors**
```bash
# Ensure you're in the project root
cd /path/to/Template_News_Site-main
python3 sync_content.py check
```

**2. Database Connectivity**
```bash
# Check database exists and is accessible
python3 sync_content.py check
```

**3. Missing Content**
```bash
# Check what's in the database
python3 sync_content.py stats
python3 sync_content.py list --type authors
```

**4. Broken Links**
```bash
# Re-sync all content to fix navigation
python3 sync_content.py sync --all
```

### Getting Help

```bash
# Show help for sync tool
python3 sync_content.py --help

# Check specific content type
python3 sync_content.py list --type categories
```

## Integration with Existing Content

### From Previous JSON System
The migration has already converted all JSON data to SQLite. The old JSON files in `data/` are kept for reference but not used.

### Content File Processing
The system can still process `.txt` content files from the `content/` directories using the integrators' `process_new_content()` method, but the primary workflow is now database-first.

## Performance Tips

1. **Batch Operations**: Use `sync --all` rather than individual syncs
2. **Database Queries**: Use the GUI query interface for complex operations
3. **Image Management**: Process images in batches using the procurement CSV
4. **Content Updates**: Make multiple database changes before syncing

## Next Steps

1. **Source Images**: Download images from procurement list
2. **Add Content**: Use the management tools to add more articles and authors
3. **Customize**: Modify templates and styles as needed
4. **Deploy**: The generated HTML files are ready for static hosting

---

**Last Updated**: December 10, 2024  
**Tools**: GUI Content Manager, CLI Sync Tool  
**Database**: SQLite with full relationship support  
**Status**: Production Ready with Full Content Management