# Content Management Guide

Complete guide to managing content in your Influencer News CMS.

## 🎯 Overview

Your CMS uses a **database-first approach** where all content is stored in SQLite and HTML pages are generated automatically. This ensures consistency and enables powerful management features.

## 🛠️ Management Tools

### Command-Line Tool (`scripts/sync_content.py`)

The simplified primary tool for content management:

```bash
# Sync all content (most common - recommended)
python3 scripts/sync_content.py
python3 scripts/sync_content.py sync

# Sync specific content types
python3 scripts/sync_content.py articles
python3 scripts/sync_content.py authors
python3 scripts/sync_content.py categories
python3 scripts/sync_content.py trending

# View content statistics
python3 scripts/sync_content.py stats

# Check database connection and system status
python3 scripts/sync_content.py status
```

**Key Features:**
- **Pagination Support**: Limits queries to reasonable page sizes (50 articles, 100 authors/categories/trending)
- **Bidirectional Sync**: Automatically removes content when source files are deleted
- **Foreign Key Protection**: Prevents deletion of referenced content with clear error messages
- **Performance Optimized**: Handles thousands of articles without memory issues

### GUI Content Manager (`scripts/content_manager.py`)

Visual interface for content management (requires tkinter):

```bash
python3 scripts/content_manager.py
```

**GUI Features:**
- Browse all content types with search/filter
- Add, edit, delete content with forms
- Real-time sync with progress tracking
- Database query interface
- Image management tools
- Site statistics dashboard

## 📝 Content Types

### Authors

**Purpose**: Writer profiles with social links and expertise  
**Generated**: `integrated/authors/author_{slug}.html`  
**Listing**: `authors.html`

**Database Fields**:
- `name` - Full name
- `title` - Job title/position
- `bio` - Brief description
- `email` - Contact email
- `location` - Geographic location
- `expertise` - Comma-separated skills
- `twitter` - Twitter handle
- `linkedin` - LinkedIn profile URL

**Adding Authors**:
```python
from src.models.author import Author

Author.create(
    name="Jane Smith",
    title="Senior Reporter",
    bio="Technology journalist with 5 years experience",
    email="jane@example.com",
    location="New York, NY",
    expertise="Technology, AI, Creator Economy",
    twitter="@janesmith",
    linkedin="https://linkedin.com/in/janesmith"
)
```

### Categories

**Purpose**: Content organization and navigation  
**Generated**: `integrated/categories/category_{slug}.html`  
**Listing**: `integrated/categories.html`

**Database Fields**:
- `name` - Category name
- `slug` - URL-friendly identifier
- `description` - Brief description
- `color` - Theme color (hex code)
- `icon` - Emoji or icon

**Available Categories**:
- Business (💼)
- Technology (💻)
- Entertainment (🎬)
- Fashion (👗)
- Creator Economy (💰)
- Charity (❤️)
- Lifestyle (🌟)

### Trending Topics

**Purpose**: Hot topics with heat scoring  
**Generated**: `integrated/trending/trend_{slug}.html`  
**Listing**: `integrated/trending.html`

**Database Fields**:
- `title` - Topic title
- `slug` - URL identifier
- `description` - Brief description
- `heat_score` - Trending intensity (0-100)
- `content` - Detailed analysis

**Heat Score Levels**:
- 90-100: 🔥🔥🔥 Extremely Hot
- 70-89: 🔥🔥 Very Hot
- 50-69: 🔥 Hot
- 0-49: 📈 Rising

### Articles

**Purpose**: News articles and stories  
**Generated**: `integrated/articles/article_{id}.html`  
**Updates**: Homepage and search page

**Database Fields**:
- `title` - Article headline
- `content` - Full article content
- `excerpt` - Brief summary
- `author_id` - Link to author
- `category_id` - Link to category
- `published_at` - Publication date
- `image_url` - Featured image

## 🔄 Content Workflow

### 1. Database-First Approach

All content lives in the SQLite database (`data/infnews.db`). HTML pages are generated from this data.

### 2. Adding New Content

**Option A: Using Dynamic Templates**
1. Use template from `docs/templates/` as structure reference
2. Replace {{variable}} placeholders with actual content
3. Process via content management tools
4. Sync to generate HTML

**Option B: Direct Database**
```python
# Example: Adding a new category
from src.models.category import Category

Category.create(
    name="Gaming",
    slug="gaming",
    description="Video game industry and gaming creators",
    color="#8B5CF6",
    icon="🎮"
)
```

**Option C: GUI Interface**
1. Launch `python3 content_manager.py`
2. Select content type
3. Click "Add New"
4. Fill form and save
5. Sync to generate HTML

### 3. Syncing Content

After making changes, always sync to update HTML:

```bash
# Sync specific type
python3 sync_content.py categories

# Sync everything (recommended)
python3 sync_content.py
```

**What Sync Does**:
- Generates individual content pages
- Updates listing pages
- Fixes navigation links
- Updates search index
- Maintains relationships

### 4. Content Relationships

**Articles → Authors**: Each article linked to one author  
**Articles → Categories**: Each article linked to one category  
**Images → All Content**: Polymorphic image relationships  

## 🖼️ Image Management

### Current System

Images are tracked in the database but files are sourced separately:

1. **External URLs**: Currently using Unsplash
2. **Local Structure**: Directories ready for local files
3. **Procurement List**: `data/image_procurement_list.csv` lists 12 images to source
4. **Placeholders**: SVG fallbacks active

### Image Naming Convention

```
authors/author_{slug}_profile.jpg
authors/author_{slug}_thumbnail.jpg
categories/category_{slug}_banner.jpg
trending/trending_{slug}_cover.jpg
articles/article_{id}_hero.jpg
articles/article_{id}_thumbnail.jpg
```

### Sourcing Images

1. **Review** `data/image_procurement_list.csv`
2. **Download** each image from the original URL
3. **Rename** according to the local filename
4. **Place** in appropriate `assets/images/` subdirectory
5. **Images automatically replace** placeholders

### Image Management via GUI

Use the Image Manager in `content_manager.py`:
- View all tracked images
- See procurement status
- Manage local files
- Generate reports

## 🔍 Search System

### Backend API (`search_backend.py`)

Database-powered search across all content types:

```bash
# Test search
python3 search_backend.py "creator economy"
```

**Response Format**:
```json
{
  "query": "creator economy",
  "articles": [...],
  "authors": [...],
  "categories": [...],
  "trending": [...],
  "total_results": 5
}
```

### Frontend (`search.html`)

Web interface for searching:
- Real-time search as you type
- Filter by content type
- Highlighted results
- Mobile-responsive design

### Search Features

- **Multi-content search**: Searches across all types
- **Relevance scoring**: Results ranked by relevance
- **Partial matching**: Finds partial word matches
- **Type filtering**: Filter results by content type

## 📊 Content Statistics

### Viewing Stats

```bash
# Quick overview
python3 sync_content.py stats

# Detailed breakdown
python3 content_manager.py  # Use GUI stats panel
```

### Current Content

- **4 Authors**: Complete profiles with expertise
- **7 Categories**: All major content areas covered
- **4 Trending Topics**: Hot topics with heat scores
- **0 Articles**: Ready for your content
- **12 Images**: Tracked for procurement

## 🎨 Content Templates

Dynamic templates available in `docs/templates/` using the new granular template system:

### Article Template (`article_template.txt`)
- Dynamic field placeholders ({{article.title}}, {{article.content}}, etc.)
- Formatting guidelines and options
- Template usage instructions
- Supports all article metadata fields

### Author Template (`author_template.txt`)
- Dynamic author fields ({{author.name}}, {{author.bio}}, etc.)
- Profile information structure
- Social media link formatting
- Extended biography guidelines

### Category Template (`category_template.txt`)
- Dynamic category fields ({{category.name}}, {{category.description}}, etc.)
- Color and icon specifications
- Hierarchical category support
- Extended description framework

### Trending Template (`trending_template.txt`)
- Dynamic trending fields ({{trending.title}}, {{trending.heat_score}}, etc.)
- Heat score and momentum tracking
- Analysis content structure
- Deprecated field references for migration

## 🔧 Advanced Management

### Database Direct Access

```python
from src.database.db_manager import DatabaseManager
from src.models import Author, Category, TrendingTopic, Article

# Get database connection
db = DatabaseManager()

# Query examples
authors = Author.find_all()
tech_category = Category.find_by_slug('technology')
hot_trends = TrendingTopic.find_all()

# Custom queries
with db.get_connection() as conn:
    cursor = conn.execute("SELECT * FROM authors WHERE location LIKE '%NY%'")
    ny_authors = cursor.fetchall()
```

### Batch Operations

```python
# Bulk update authors
authors = Author.find_all()
for author in authors:
    if not author.linkedin:
        author.linkedin = f"https://linkedin.com/in/{author.slug}"
        author.save()

# Sync after bulk changes
python3 sync_content.py
```

### Content Backup

```python
# Export all content
import json
from src.models import Author, Category, TrendingTopic

backup = {
    'authors': [author.to_dict() for author in Author.find_all()],
    'categories': [cat.to_dict() for cat in Category.find_all()],
    'trending': [trend.to_dict() for trend in TrendingTopic.find_all()]
}

with open('content_backup.json', 'w') as f:
    json.dump(backup, f, indent=2)
```

## 🚨 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure you're in project root
cd Template_News_Site-main
python3 sync_content.py status
```

**2. Sync Failures**
```bash
# Check database connectivity
python3 sync_content.py status

# Try individual sync
python3 sync_content.py authors
```

**3. Missing Content**
```bash
# Verify content exists
python3 sync_content.py stats

# Check database
python3 -c "from src.models.author import Author; print(len(Author.find_all()))"
```

**4. Broken Navigation**
```bash
# Re-sync all content to fix paths
python3 sync_content.py
```

### Getting Help

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review [FAQ](FAQ.md)
3. Run system verification: `python3 sync_content.py status`
4. Check file permissions and paths

## 🎯 Best Practices

### Content Creation

1. **Use templates** for consistency
2. **Fill all required fields** for best results
3. **Sync regularly** to keep HTML updated
4. **Test on mobile** and desktop
5. **Optimize images** for web

### Database Management

1. **Backup regularly** before major changes
2. **Use transactions** for bulk operations
3. **Maintain relationships** between content
4. **Monitor performance** with large datasets

### Performance

1. **Batch sync operations** when possible
2. **Optimize images** for web delivery
3. **Use CDN resources** (already implemented)
4. **Monitor page load times**

---

**Last Updated**: December 10, 2024  
**Status**: Production Ready  
**Total Content Items**: 15+ across all types