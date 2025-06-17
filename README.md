# Influencer News CMS

A modern, database-driven content management system for influencer and creator economy news.

View demo site: https://jaykobdetar.github.io/index.html

## 🚀 Quick Start

**Option 1: Using wrapper (easier)**
```bash
# Windows
sync.bat status        # Check system status
sync.bat               # Sync all content
sync.bat stats         # View statistics

# macOS/Linux  
python3 sync.py status # Check system status
python3 sync.py        # Sync all content
python3 sync.py stats  # View statistics
```

**Option 2: Direct script execution**
```bash
python scripts/sync_content.py status  # Check system status
python scripts/sync_content.py         # Sync all content
python scripts/sync_content.py stats   # View statistics
```

## 📁 Project Structure

```
├── scripts/          # Utility scripts
├── src/              # Source code (models, integrators, utils)
├── content/          # Content source files
├── integrated/       # Generated HTML pages
├── api/mobile/       # Mobile API endpoints
├── docs/             # Documentation
└── tests/            # Test suite
```

See [docs/project-structure.md](docs/project-structure.md) for detailed structure.

## 📚 Documentation

- [Quick Start Guide](docs/quick-start.md)
- [Project Structure](docs/project-structure.md)
- [Content Management](docs/content-management.md)
- [Templates](docs/templates/)
- [Full Documentation](docs/README.md)

## 🛠️ Key Features

- **Database-Driven**: SQLite database for content management
- **Mobile-Ready**: Responsive design with PWA support
- **SEO Optimized**: Built-in SEO features and metadata
- **Security**: XSS protection and content sanitization
- **Search**: Full-text search functionality
- **API**: JSON API for mobile apps

## 📝 Adding Content

1. Create content file in `content/` directory using templates
2. Run `python3 sync.py` to sync to database and generate HTML
3. View your content on the website

## 🔧 Advanced Usage

For direct script access:
```bash
# From project root
python3 scripts/sync_content.py
python3 scripts/content_manager.py
python3 scripts/mobile/mobile_api_generator.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.