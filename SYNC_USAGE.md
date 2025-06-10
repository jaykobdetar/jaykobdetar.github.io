# Content Sync Tool - Quick Guide

## Simple Commands

### Most Common Usage
```bash
python3 sync_content.py
```
Syncs all content types (articles, authors, categories, trending). This is what you'll use 99% of the time.

### Sync Specific Content Types
```bash
python3 sync_content.py articles     # Sync only articles
python3 sync_content.py authors      # Sync only authors  
python3 sync_content.py categories   # Sync only categories
python3 sync_content.py trending     # Sync only trending topics
```

### Check Status & Statistics
```bash
python3 sync_content.py stats        # Show content counts
python3 sync_content.py status       # Check database connection
```

## What the Sync Does

1. **Reads content files** from the `content/` folder
2. **Updates the database** with any new or changed content
3. **Removes deleted content** from database and website
4. **Generates HTML pages** for all content
5. **Updates homepage** and search page with current content
6. **Cleans up orphaned files** that no longer have source content

## Content Workflow

1. **Add content**: Create `.txt` files in the appropriate `content/` subfolder
2. **Run sync**: `python3 sync_content.py` 
3. **Remove content**: Delete `.txt` files from `content/` folder
4. **Run sync again**: `python3 sync_content.py` (removes from website)

That's it! The sync tool handles everything automatically.

## File Locations

- **Source content**: `content/articles/`, `content/authors/`, etc.
- **Generated pages**: `integrated/articles/`, `integrated/authors/`, etc.
- **Main pages**: `index.html`, `search.html` (updated automatically)

## Help

```bash
python3 sync_content.py --help       # Show all options
```