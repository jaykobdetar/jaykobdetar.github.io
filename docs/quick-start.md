# Quick Start Guide

Get your Influencer News CMS up and running in 5 minutes!

## 🚀 Prerequisites

- Python 3.7 or higher
- Web browser (Chrome, Firefox, Safari, Edge)
- Terminal/Command prompt access

## ⚡ 5-Minute Setup

### 1. Verify Installation
```bash
# Navigate to project directory
cd Template_News_Site-main

# Check Python version
python3 --version

# Verify database
python3 sync_content.py check
```

Expected output:
```
🔍 Checking database...
✅ Database connected successfully
📋 Found 7 tables
🔗 Foreign keys: ✅ Enabled
```

### 2. View Your Website
Open `index.html` in your browser:
```bash
# Option 1: Direct file open
open index.html

# Option 2: Full path
file:///path/to/Template_News_Site-main/index.html
```

### 3. Check Content Status
```bash
# View current content
python3 sync_content.py stats
```

Expected output:
```
📊 Content Statistics
==============================
Authors        :   4
Categories     :   7
Trending Topics:   4
Articles       :   0
Images         :  12
```

### 4. Test Content Management
```bash
# Check system status
python3 sync_content.py status

# View content statistics
python3 sync_content.py stats

# Sync all content to HTML (most common command)
python3 sync_content.py
```

### 5. Add Your First Content
```bash
# Copy a content template
cp docs/templates/article_template.txt content/articles/my-first-article.txt

# Edit the file with your content
# Then sync to generate HTML
python3 sync_content.py articles
```

## 🎯 What You Have Now

### ✅ Working Website
- **Homepage**: `index.html` with featured content
- **Authors**: `authors.html` with 4 author profiles
- **Categories**: `integrated/categories.html` with 7 categories
- **Trending**: `integrated/trending.html` with 4 hot topics
- **Search**: `search.html` with database-powered search

### ✅ Content Management Tools
- **CLI Tool**: `sync_content.py` for command-line management
- **GUI Tool**: `content_manager.py` for visual management (requires tkinter)
- **Templates**: Ready-to-use content templates in `docs/templates/`

### ✅ Database System
- **SQLite Database**: `data/infnews.db` with all your content
- **Relationships**: Foreign keys linking articles to authors and categories
- **Image Tracking**: Comprehensive image management system

## 🔄 Basic Workflow

### Adding New Content
1. **Choose content type** (article, author, category, trending)
2. **Copy template** from `docs/templates/`
3. **Edit with your content**
4. **Add to database** (via Python models or GUI)
5. **Sync to HTML**: `python3 sync_content.py sync --all`

### Managing Existing Content
1. **View content**: `python3 sync_content.py list --type [type]`
2. **Edit in database** (via GUI or Python)
3. **Re-sync**: `python3 sync_content.py sync --all`

## 🛠️ Common Commands

```bash
# Check system health
python3 sync_content.py check

# View all content
python3 sync_content.py stats

# List specific content type
python3 sync_content.py list --type authors
python3 sync_content.py list --type categories

# Sync specific content type
python3 sync_content.py sync --type authors

# Sync everything
python3 sync_content.py sync --all

# Test search
python3 search_backend.py "technology"

# Launch GUI (if tkinter available)
python3 content_manager.py
```

## 🎨 Customization Basics

### Change Site Branding
Edit the header in any HTML file:
```html
<!-- In index.html, authors.html, etc. -->
<h1 class="text-3xl font-bold">Your Site Name</h1>
```

### Add Site Logo
Replace the logo section in headers:
```html
<!-- Replace this section -->
<div class="w-16 h-16 bg-gradient-to-br from-indigo-400 to-purple-600 rounded-full flex items-center justify-center mr-4">
    <span class="text-2xl font-bold text-white">IN</span>
</div>
<!-- With your logo -->
<img src="assets/images/logo.png" alt="Your Logo" class="w-16 h-16">
```

### Modify Colors
The site uses Tailwind CSS. Key color classes:
- `bg-indigo-900` - Header background
- `text-indigo-600` - Links and accents
- `from-indigo-400 to-purple-600` - Gradients

## 📱 Mobile & Desktop

Your site is fully responsive and works on:
- ✅ Desktop browsers
- ✅ Tablets
- ✅ Mobile phones
- ✅ All modern browsers

## 🔍 Testing Your Setup

### 1. Navigation Test
Click through all navigation links:
- Home → Authors → Categories → Trending → Search
- Verify all pages load correctly

### 2. Search Test
- Go to `search.html`
- Search for "technology" or "business"
- Verify results appear

### 3. Content Test
- Visit individual author profiles
- Check category pages
- Browse trending topics

## 🆘 Need Help?

If something isn't working:

1. **Check [Troubleshooting Guide](troubleshooting.md)**
2. **Verify system requirements**
3. **Run diagnostic**: `python3 sync_content.py check`
4. **Check [FAQ](FAQ.md)** for common issues

## 🎯 Next Steps

Once everything is working:

1. **Add your content** using the templates
2. **Source images** from `data/image_procurement_list.csv`
3. **Customize styling** to match your brand
4. **Deploy to web hosting** (see [Deployment Guide](deployment.md))

---

**🎉 Congratulations!** Your Influencer News CMS is ready to use!

For detailed features and advanced usage, see the [Content Management Guide](content-management.md).