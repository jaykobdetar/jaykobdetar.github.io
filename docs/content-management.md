# Content Management Guide

## Overview

The CMS manages content through a combination of text files and database operations. Content is created as `.txt` files, parsed and stored in SQLite, then generated as static HTML pages. The entire site can be rebranded through configuration files.

## Current Limitations

**Important**: The system currently only supports **adding new content**. Updating existing content requires manual database editing or file deletion and re-sync.

## Content Types

### 1. Articles
News articles with metadata, content, and optional sections.

**Location**: `content/articles/`
**Generated**: `integrated/articles/article_{id}.html`

### 2. Authors  
Content creator profiles with bio and social links.

**Location**: `content/authors/`
**Generated**: `integrated/authors/author_{slug}.html`

### 3. Categories
Content classification with colors and icons.

**Location**: `content/categories/`
**Generated**: `integrated/categories/category_{slug}.html`

### 4. Trending Topics
Hot topics with heat scores and descriptions.

**Location**: `content/trending/`
**Generated**: `integrated/trending/trend_{slug}.html`

### 5. Site Configuration
Site-wide branding and settings that apply to all pages.

**Location**: `content/site/`
**Applies to**: All generated pages

## Content File Format

### Article Format
```
METADATA:
Title: Your Article Title
Author: Author Name (must exist in database)
Category: technology (must exist in database)
Slug: your-article-slug (optional)
Tags: AI, Technology, Innovation (optional)
Excerpt: Brief description for previews

CONTENT:
Main article content here. Can include basic HTML tags.

You can write multiple paragraphs.

SECTIONS:
## Section Heading
Content for this section.

## Another Section
More content here.
```

### Author Format
```
METADATA:
Name: Author Full Name
Title: Job Title or Role
Bio: Brief biography
Email: author@example.com (optional)
Location: City, State (optional)
Expertise: Technology, AI, Startups (optional)
Twitter: @username (optional)
LinkedIn: https://linkedin.com/in/username (optional)

CONTENT:
Extended biography or description.
```

### Category Format
```
METADATA:
Name: Category Name
Description: Brief category description
Color: #3B82F6 (hex color, optional)
Icon: 💻 (emoji icon, optional)

CONTENT:
Detailed category description.
```

### Trending Topic Format
```
METADATA:
Title: Trending Topic Title
Description: What this trend is about
Heat Score: 85 (0-100, optional)
Category: technology (optional)
Hashtag: #TrendingTopic (optional)

CONTENT:
Detailed analysis of the trending topic.
```

### Site Configuration Format
```
Site Name: Your Site Name
Site Tagline: Your tagline here
Logo Text: YSN
Theme Color: #059669
Footer Description: Your site description
Copyright Text: © 2025 Your Site Name. All rights reserved.
```

**Important**: Site configuration is stored in `content/site/site-branding.txt` and applies to all pages when synced.

## Content Management Commands

### Basic Sync Operations
```bash
# Sync all content types
python scripts/sync_content.py

# Sync specific content type
python scripts/sync_content.py site
python scripts/sync_content.py articles
python scripts/sync_content.py authors
python scripts/sync_content.py categories
python scripts/sync_content.py trending

# Check system status
python scripts/sync_content.py status

# View content statistics
python scripts/sync_content.py stats
```

### Wrapper Scripts
```bash
# Simple wrapper (calls sync_content.py)
python sync.py [arguments]

# Windows batch file
sync.bat [arguments]
```

## Content Creation Workflow

### Adding New Content

1. **Create Content File**
   ```bash
   # Use templates as starting point
   cp docs/templates/article_template.txt content/articles/my-new-article.txt
   ```

2. **Edit Content File**
   - Fill in metadata fields
   - Write content and sections
   - Ensure author and category exist

3. **Sync to Database**
   ```bash
   python scripts/sync_content.py articles
   ```

4. **Verify Generation**
   - Check `integrated/articles/` for new HTML file
   - Test in browser

### Adding Dependencies

Authors and categories must exist before articles can reference them:

```bash
# 1. Add author first
echo "METADATA:
Name: New Author
Title: Content Creator
Bio: Author biography" > content/authors/new-author.txt

# 2. Sync authors
python scripts/sync_content.py authors

# 3. Then add articles referencing the author
echo "METADATA:
Title: New Article
Author: New Author
Category: technology" > content/articles/new-article.txt

# 4. Sync articles
python scripts/sync_content.py articles
```

## Content Templates

Templates are available in `docs/templates/`:

- `article_template.txt` - Article with all metadata fields
- `author_template.txt` - Author profile template  
- `category_template.txt` - Category definition
- `trending_template.txt` - Trending topic template
- `site_branding_template.txt` - Site configuration template

## Data Validation

### Required Fields
- **Articles**: title, author (must exist), category (must exist)
- **Authors**: name
- **Categories**: name
- **Trending**: title

### Automatic Processing
- **Slugs**: Auto-generated from titles if not provided
- **HTML Sanitization**: Dangerous content removed
- **Tag Processing**: Comma-separated tags converted to arrays

### Validation Errors
Common validation failures:
```
Missing required field 'title'
Author 'Unknown Author' not found in database
Category 'invalid-category' not found in database
Content exceeds maximum length of 50000 characters
```

## Content Updates & Deletion

### Current Limitations
- **No Update Support**: Cannot modify existing content via files
- **Manual Updates**: Must edit database directly or delete and re-add

### Deletion Process
1. **Remove File**: Delete the `.txt` file
2. **Sync**: Run sync command
3. **Cleanup**: System removes database entry and HTML file

**Warning**: Deletion may fail if content is referenced by other content (foreign key constraints).

## Image Management

### Current State
The image system is **partially implemented**:

- **URL Tracking**: External image URLs stored in database
- **Local References**: System generates local filenames
- **Procurement List**: CSV file tracks images to download
- **No Download**: Actual image downloading not implemented

### Image Usage
Reference images in content using external URLs:
```
![Alt text](https://example.com/image.jpg)
```

The system will track these URLs for future download implementation.

## Troubleshooting

### Common Issues

1. **Author Not Found**
   ```
   Error: Author 'Author Name' not found in database
   ```
   **Solution**: Create author first, then sync articles

2. **Category Not Found**
   ```
   Error: Category 'category-name' not found in database
   ```
   **Solution**: Create category first, then sync articles

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'database'
   ```
   **Solution**: Run commands from project root directory

4. **Foreign Key Errors**
   ```
   Cannot delete Category 'technology' - referenced by: 5 articles
   ```
   **Solution**: Remove or reassign referencing content first

### Debug Commands
```bash
# Check database connectivity
python scripts/sync_content.py status

# View content counts
python scripts/sync_content.py stats

# Test database queries
python -c "from src.database.db_manager import DatabaseManager; db = DatabaseManager(); print(db.get_authors())"
```

## File Organization

### Directory Structure
```
content/
├── articles/           # Article .txt files
├── authors/           # Author .txt files  
├── categories/        # Category .txt files
├── trending/          # Trending topic .txt files
└── site/              # Site configuration files

integrated/            # Generated HTML files
├── articles/
├── authors/
├── categories/
└── trending/

data/
├── infnews.db        # SQLite database
└── *.json            # Legacy data files
```

### Naming Conventions
- **Files**: Use kebab-case (my-article-title.txt)
- **Slugs**: Auto-generated as kebab-case
- **Generated HTML**: Follows pattern `{type}_{slug}.html`

## Best Practices

1. **Content Order**: Create authors and categories before articles
2. **Slug Consistency**: Use descriptive, SEO-friendly slugs
3. **Image Planning**: Note images needed for future download
4. **Backup**: Keep copies of content files as backup
5. **Testing**: Always test generated HTML in browser