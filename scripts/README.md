# Scripts Directory

This directory contains all utility scripts for managing the Influencer News CMS.

## Main Scripts

### Content Management

- **`sync_content.py`** - Primary content synchronization tool
  ```bash
  python3 scripts/sync_content.py          # Sync all content
  python3 scripts/sync_content.py articles # Sync specific type
  python3 scripts/sync_content.py stats    # View statistics
  ```

- **`content_manager.py`** - GUI content management tool (requires tkinter)
  ```bash
  python3 scripts/content_manager.py
  ```

### Search & Utilities

- **`search_backend.py`** - Search functionality implementation
- **`setup_responsive_images.py`** - Configure responsive image handling
- **`update_integrator_templates.py`** - Update HTML templates in integrators

## Subdirectories

### `/mobile` - Mobile Support Scripts

Scripts for mobile API generation:

- **`mobile_api_generator.py`** - Generate JSON API endpoints for mobile apps

### `/database` - Database Utilities

Database management and migration scripts:

- **`migrate_schema.py`** - Migrate database schema with data preservation
  ```bash
  python3 scripts/database/migrate_schema.py
  ```

## Usage Notes

1. **Always run from project root**: Scripts expect to be run from the main project directory
2. **Python path handling**: Scripts automatically add parent directories to Python path
3. **Database location**: Scripts look for database at `data/infnews.db` relative to project root

## Common Tasks

### Daily Content Management
```bash
# Add new content files to content/ directory, then:
python3 scripts/sync_content.py
```

### Mobile API Update
```bash
python3 scripts/mobile/mobile_api_generator.py
```

### Database Migration
```bash
# Always backup first!
python3 scripts/database/migrate_schema.py
```

### Full System Update
```bash
# Sync content and generate mobile API
python3 scripts/sync_content.py
python3 scripts/mobile/mobile_api_generator.py
```