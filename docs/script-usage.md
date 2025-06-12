# Script Usage Guide

This guide explains how to use the various scripts in the Influencer News CMS.

## Running Scripts

Due to the project structure and Python import system, there are two ways to run scripts:

### Method 1: Direct Script Execution (Recommended)

Run scripts directly from the project root directory:

```bash
# Content sync operations (Windows: use 'python' instead of 'python3')
python scripts/sync_content.py                    # Sync all content
python scripts/sync_content.py status             # Check database status
python scripts/sync_content.py stats              # View statistics
python scripts/sync_content.py articles           # Sync only articles
python scripts/sync_content.py authors            # Sync only authors
python scripts/sync_content.py categories         # Sync only categories
python scripts/sync_content.py trending           # Sync only trending
```

### Method 2: Other Scripts

For other utility scripts:

```bash
# Must be run from project root directory
cd /path/to/project

# GUI content manager (requires tkinter)
python scripts/content_manager.py

# Mobile scripts  
python scripts/mobile/mobile_api_generator.py
python scripts/mobile/regenerate_mobile_pages.py

# Database migration
python scripts/database/migrate_schema.py

# Search backend
python scripts/search_backend.py
```

## Platform Notes

### Windows Users
- Use `python` instead of `python3` in commands
- Ensure you're in the correct directory (use `cd` to navigate)
- Paths use backslashes but forward slashes also work

### macOS/Linux Users  
- Use `python3` in commands
- Standard Unix path conventions apply

## Common Issues

### Import Errors

If you see errors like:
```
ImportError: attempted relative import beyond top-level package
```

Solutions:
1. Use the wrapper scripts (sync.py)
2. Ensure you're in the project root directory
3. Check that all src/ files are present

### Module Not Found

If scripts can't find modules:
```
ModuleNotFoundError: No module named 'src'
```

This usually means:
- You're not running from the project root
- The src/ directory structure has been modified
- Python path is not set correctly

## Script Directory Structure

```
project-root/
├── sync.py                    # Wrapper for easy access
├── scripts/
│   ├── sync_content.py        # Main content sync tool
│   ├── content_manager.py     # GUI manager
│   ├── search_backend.py      # Search functionality
│   ├── mobile/
│   │   ├── mobile_api_generator.py
│   │   ├── mobile_backend_integration.py
│   │   └── regenerate_mobile_pages.py
│   └── database/
│       └── migrate_schema.py
└── src/                       # Source modules
    ├── models/
    ├── integrators/
    ├── database/
    └── utils/
```

## Best Practices

1. **Always run from project root**: This ensures consistent path resolution
2. **Use wrapper scripts**: They handle path setup automatically
3. **Check status first**: Run `python3 sync.py status` before major operations
4. **Backup before migrations**: Always backup database before schema changes

## Quick Reference

| Task | Command |
|------|---------|
| Sync all content | `python scripts/sync_content.py` |
| Check system status | `python scripts/sync_content.py status` |
| View statistics | `python scripts/sync_content.py stats` |
| Sync specific type | `python scripts/sync_content.py articles` |
| GUI manager | `python scripts/content_manager.py` |
| Generate mobile API | `python scripts/mobile/mobile_api_generator.py` |
| Migrate database | `python scripts/database/migrate_schema.py` |