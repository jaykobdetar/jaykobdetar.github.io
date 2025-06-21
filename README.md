# Influencer News CMS

A modern, secure, database-driven content management system for influencer and creator economy news.

**Live Demo**: https://jaykobdetar.github.io

## ⚠️ Current Status

This is a **work-in-progress** project with some features still under development

## ✨ Features

- **🔒 Security First**: Industry-standard HTML sanitization, CSP headers with nonces
- **📱 Mobile PWA**: Progressive Web App with offline support and responsive design  
- **🔍 Search System**: Search across articles, authors, and categories (currently using LIKE queries)
- **📊 Database-Driven**: SQLite with normalized schema and efficient queries
- **⚡ Performance**: Optimized loading, caching, and pagination
- **🎨 Modern UI**: Tailwind CSS with smooth animations and gradients

## 🚀 Quick Start

**Simple Sync (Recommended)**
```bash
# Windows
sync.bat

# macOS/Linux  
python3 sync.py
```

**Manual Script Execution**
```bash
python scripts/sync_content.py         # Sync all content
python scripts/generate_homepage_simple.py  # Update homepage
python scripts/search_backend.py       # Update search index
```

## 📁 Project Structure

```
├── src/              # Core source code
│   ├── models/       # Database models (Article, Author, Category)
│   ├── integrators/  # HTML generators and processors
│   └── utils/        # Security, database, and utility modules
├── content/          # Content source files (.txt format)
├── integrated/       # Generated HTML pages
├── assets/           # CSS, JavaScript, images
├── api/mobile/       # JSON API endpoints
├── data/             # SQLite database and backups
├── scripts/          # Build and utility scripts
├── docs/             # Documentation
└── tests/            # Test suite
```

## 📚 Documentation

### Core Documentation
- **[Technical Reference](docs/technical-reference.md)** - Architecture and implementation details
- **[Content Management](docs/content-management.md)** - Adding and managing content
- **[Security Guide](docs/SECURITY.md)** - Security features and best practices
- **[Current State Overview](docs/current-state-overview.md)** - Feature status and roadmap

### Development
- **[FAQ](docs/FAQ.md)** - Common questions and troubleshooting
- **[CLAUDE.md](docs/CLAUDE.md)** - Development notes and context
- **[Templates](docs/templates/)** - Content templates and examples

## 🔧 Content Management

### Adding New Content

1. **Create content file** using templates in `docs/templates/`:
   ```bash
   # Copy template
   cp docs/templates/article_template.txt content/articles/my-new-article.txt
   ```

2. **Edit content** with your article details:
   ```
   title: Your Article Title
   author: Author Name
   category: Technology
   excerpt: Brief description...
   ---
   Your article content here...
   ```

3. **Sync to database and generate HTML**:
   ```bash
   python3 sync.py
   ```

### Content Types
- **Articles**: Main news content (`content/articles/`)
- **Authors**: Writer profiles (`content/authors/`)
- **Categories**: Topic organization (`content/categories/`)
- **Trending**: Featured content (`content/trending/`)

## 🛡️ Security Features

- **HTML Sanitization**: DOMPurify (client) + bleach (server)
- **Content Security Policy**: Strict CSP with cryptographic nonces
- **Input Validation**: Length limits and type checking
- **XSS Protection**: Multiple layers of protection
- **No User Data Logging**: Privacy-focused, no IP tracking

## 🔍 Search System

- **Basic Search**: LIKE-based search across content (FTS5 currently disabled)
- **Search Suggestions**: Basic search suggestions
- **Multi-Type Results**: Articles, authors, categories, trending
- **Mobile Interface**: Touch-friendly search interface

## 🏗️ Build Commands

```bash
# Content operations
python scripts/sync_content.py              # Sync all content
python scripts/sync_content.py --update     # Update existing content

# Database operations  
python scripts/create_missing_tables_simple.py  # Create missing tables
python scripts/database/migrate_schema.py       # Run database migrations

# Generation
python scripts/generate_homepage_simple.py      # Update homepage
python scripts/mobile/mobile_api_generator.py   # Generate mobile API

# Development
npm run dev          # Watch Tailwind CSS changes
python -m pytest    # Run test suite
```

## 📊 Database Schema

- **articles**: Main content with basic search
- **authors**: Writer profiles and statistics  
- **categories**: Topic organization with icons
- **trending**: Featured content management
- **mobile_metrics**: Mobile usage analytics (planned)
- **image_variants**: Responsive image storage (planned)

## 🌐 API Endpoints

Mobile-friendly JSON API:
- `/api/mobile/articles.json` - Article listings
- `/api/mobile/search.json` - Search functionality
- `/api/mobile/authors.json` - Author profiles
- `/api/mobile/categories.json` - Category organization

## 📱 PWA Features

- **Offline Support**: Service worker with intelligent caching
- **App-Like Experience**: Installable on mobile devices
- **Push Notifications**: Ready for notification implementation
- **Fast Loading**: Optimized assets and lazy loading

## 🧪 Testing

```bash
python -m pytest tests/                    # Full test suite
python -m pytest tests/test_unit_models.py # Model tests
python -m pytest tests/test_integration_database.py # Database tests
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need Help?** Check the [FAQ](docs/FAQ.md) or [technical documentation](docs/technical-reference.md).
