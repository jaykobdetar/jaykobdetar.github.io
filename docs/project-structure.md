# Project Structure

This document describes the organization of the Influencer News CMS project.

## Directory Structure

```
influencer-news-cms/
│
├── api/                      # Mobile API JSON endpoints
│   └── mobile/              # Mobile-specific API responses
│       ├── articles.json
│       ├── articles/        # Individual article JSON files
│       ├── authors.json
│       ├── authors/         # Individual author JSON files
│       ├── categories.json
│       ├── categories/      # Individual category JSON files
│       ├── trending.json
│       └── trending/        # Individual trending topic JSON files
│
├── assets/                   # Static assets
│   ├── css/                 # Compiled CSS files
│   │   └── styles.min.css   # Minified production CSS
│   ├── images/              # Images and media
│   │   ├── placeholders/    # Placeholder images by type
│   │   └── screenshots/     # System screenshots
│   └── js/                  # JavaScript files
│       └── mobile-touch.js  # Mobile gesture support
│
├── content/                  # Content source files
│   ├── articles/            # Article content in text format
│   ├── authors/             # Author profiles
│   ├── categories/          # Category descriptions
│   └── trending/            # Trending topic content
│
├── data/                     # Database and data files
│   ├── infnews.db           # Main SQLite database
│   ├── articles_db.json     # JSON database backups
│   ├── authors_db.json
│   ├── categories_db.json
│   ├── trending_db.json
│   └── backups/             # Database backups
│
├── docs/                     # Documentation
│   ├── templates/           # Content templates
│   │   ├── article_template.txt
│   │   ├── author_template.txt
│   │   ├── category_template.txt
│   │   └── trending_template.txt
│   ├── README.md            # Documentation index
│   ├── architecture.md      # System architecture
│   ├── database-schema.md   # Database documentation
│   ├── content-management.md
│   ├── deployment.md
│   ├── quick-start.md
│   ├── troubleshooting.md
│   ├── FAQ.md
│   ├── SYNC_USAGE.md
│   ├── MOBILE_IMPROVEMENTS_SUMMARY.md
│   ├── SECURITY_ASSESSMENT.md
│   └── mobile_compatibility_progress.txt
│
├── integrated/               # Generated HTML pages
│   ├── articles/            # Article pages
│   ├── authors/             # Author profile pages
│   ├── categories/          # Category listing pages
│   ├── trending/            # Trending topic pages
│   ├── categories.html      # Categories index
│   └── trending.html        # Trending index
│
├── logs/                     # Application logs
│
├── scripts/                  # Utility scripts
│   ├── content_manager.py   # GUI content management tool
│   ├── sync_content.py      # Content sync utility
│   ├── search_backend.py    # Search indexing script
│   ├── setup_responsive_images.py
│   ├── update_integrator_templates.py
│   ├── mobile/              # Mobile-specific scripts
│   │   ├── mobile_api_generator.py
│   │   ├── mobile_backend_integration.py
│   │   ├── mobile_search_wrapper.py
│   │   └── regenerate_mobile_pages.py
│   └── database/            # Database utilities
│       └── migrate_schema.py
│
├── src/                      # Source code
│   ├── database/            # Database layer
│   │   ├── __init__.py
│   │   ├── db_manager.py    # Database operations
│   │   ├── schema.sql       # Current database schema
│   │   └── migrations/      # Schema migrations
│   │       ├── schema_old.sql
│   │       ├── schema_new.sql
│   │       ├── schema_upgrade.sql
│   │       └── mobile_migration.sql
│   │
│   ├── integrators/         # HTML generation
│   │   ├── __init__.py
│   │   ├── base_integrator.py
│   │   ├── article_integrator.py
│   │   ├── author_integrator.py
│   │   ├── category_integrator.py
│   │   ├── trending_integrator.py
│   │   ├── mobile_integrator.py
│   │   └── unintegrator.py
│   │
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── base.py          # Base model class
│   │   ├── article.py       # Article model
│   │   ├── author.py        # Author model
│   │   ├── category.py      # Category model
│   │   ├── trending.py      # Trending topic model
│   │   └── image.py         # Image model
│   │
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── backup.py        # Backup utilities
│       ├── config.py        # Configuration
│       ├── image_manager.py
│       ├── image_processor.py
│       ├── logger.py        # Logging utilities
│       ├── path_manager.py  # Path management
│       ├── responsive_image_manager.py
│       ├── sanitizer.py     # Content sanitization
│       ├── security_analyzer.py
│       └── validators.py
│
├── tests/                    # Test files
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_integration_database.py
│   ├── test_unit_backup.py
│   ├── test_unit_models.py
│   ├── test_unit_sanitizer.py
│   ├── test_integrators.py
│   ├── test_template_integration.py
│   ├── test_existing_content.py
│   └── debug/               # Debug HTML files
│       └── debug_categories_test.html
│
├── 404.html                 # 404 error page
├── article.html             # Article template page
├── authors.html             # Authors listing page
├── config.yaml              # Configuration file
├── index.html               # Homepage
├── LICENSE                  # License file
├── manifest.json            # PWA manifest
├── package.json             # Node.js dependencies
├── package-lock.json
├── requirements.txt         # Python dependencies
├── search.html              # Search page
├── sw.js                    # Service worker
└── tailwind.config.js       # Tailwind CSS config
```

## Key Directories

### `/src` - Source Code
Contains all Python source code organized by functionality:
- **database/**: Database management and schema
- **integrators/**: HTML page generation from database
- **models/**: Data models (Article, Author, Category, etc.)
- **utils/**: Utility functions and helpers

### `/scripts` - Utility Scripts
Executable scripts for various tasks:
- **Content Management**: `content_manager.py`, `sync_content.py`
- **Mobile Support**: Scripts in `mobile/` subdirectory
- **Database**: Migration and maintenance scripts

### `/content` - Content Files
Text-based content files that are processed into the database:
- Articles, authors, categories, and trending topics
- Uses template format defined in `/docs/templates`

### `/integrated` - Generated HTML
Static HTML files generated from database content:
- Automatically created by integrators
- Should not be edited manually

### `/api/mobile` - Mobile API
JSON API endpoints for mobile app integration:
- Automatically generated from database
- Provides RESTful access to content

### `/tests` - Test Suite
Comprehensive test coverage:
- Unit tests for models and utilities
- Integration tests for database and integrators
- Debug HTML files for testing

## File Naming Conventions

- **Python files**: `snake_case.py`
- **HTML files**: `kebab-case.html` or `snake_case.html`
- **Content files**: Match entity slug (e.g., `sarah-chen.txt`)
- **JSON files**: `snake_case.json`
- **Test files**: `test_*.py`

## Important Files

### Configuration
- `config.yaml` - Main configuration file
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `tailwind.config.js` - CSS framework configuration

### Entry Points
- `index.html` - Homepage
- `scripts/sync_content.py` - Main content sync script
- `scripts/content_manager.py` - GUI management tool

### Documentation
- `docs/README.md` - Documentation index
- `docs/quick-start.md` - Getting started guide
- `docs/templates/` - Content templates

## Development Workflow

1. **Add Content**: Create text files in `/content` following templates
2. **Sync to Database**: Run `python scripts/sync_content.py`
3. **Generate HTML**: Integrators create files in `/integrated`
4. **Mobile API**: Run mobile scripts to update `/api/mobile`
5. **Test**: Run test suite with `pytest`

## Maintenance

- **Backups**: Stored in `/data/backups`
- **Logs**: Application logs in `/logs`
- **Migrations**: Database schema changes in `/src/database/migrations`