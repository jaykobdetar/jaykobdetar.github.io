# Troubleshooting Guide

Complete troubleshooting guide for common issues in the Influencer News CMS.

## 🚨 Quick Diagnostics

Before diving into specific issues, run these quick checks:

```bash
# 1. Check you're in the right directory
pwd
# Should show: .../Template_News_Site-main

# 2. Verify Python version
python3 --version
# Should be 3.7 or higher

# 3. Test database connectivity
python3 sync_content.py check

# 4. Check content status
python3 sync_content.py stats
```

## 🐍 Python & Import Issues

### Problem: Module Import Errors

**Error Messages**:
```
ModuleNotFoundError: No module named 'src'
ImportError: cannot import name 'DatabaseManager'
```

**Solutions**:

1. **Check Working Directory**:
```bash
# Ensure you're in project root
cd Template_News_Site-main
ls -la  # Should see src/, data/, docs/, etc.
```

2. **Python Path Issues**:
```bash
# Option A: Run from project root
python3 sync_content.py check

# Option B: Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 sync_content.py check
```

3. **Missing __init__.py Files**:
```bash
# Check for init files
find src/ -name "__init__.py"
# Should find several __init__.py files
```

**Fix**: If __init__.py files are missing:
```bash
touch src/__init__.py
touch src/database/__init__.py
touch src/models/__init__.py
touch src/utils/__init__.py
touch src/integrators/__init__.py
```

### Problem: tkinter Not Available

**Error**:
```
ModuleNotFoundError: No module named 'tkinter'
```

**Solutions**:

1. **Install tkinter** (Ubuntu/Debian):
```bash
sudo apt-get install python3-tk
```

2. **Install tkinter** (CentOS/RHEL):
```bash
sudo yum install tkinter
# or
sudo dnf install python3-tkinter
```

3. **Use CLI Instead**:
```bash
# Skip GUI, use command-line tools
python3 sync_content.py sync --all
```

## 🗄️ Database Issues

### Problem: Database Not Found

**Error**:
```
sqlite3.OperationalError: unable to open database file
```

**Solutions**:

1. **Check Database Exists**:
```bash
ls -la data/infnews.db
# Should show the database file
```

2. **Recreate Database**:
```bash
# If database is missing, recreate it
python3 -c "
from src.database.db_manager import DatabaseManager
db = DatabaseManager()
print('Database recreated')
"
```

3. **Check Permissions**:
```bash
# Ensure database is readable/writable
chmod 664 data/infnews.db
```

### Problem: Foreign Key Constraint Errors

**Error**:
```
sqlite3.IntegrityError: FOREIGN KEY constraint failed
```

**Solutions**:

1. **Check Foreign Key Status**:
```bash
python3 -c "
from src.database.db_manager import DatabaseManager
with DatabaseManager().get_connection() as conn:
    result = conn.execute('PRAGMA foreign_keys').fetchone()
    print('Foreign keys enabled:', bool(result[0]))
"
```

2. **Verify Related Records Exist**:
```python
# When adding article, ensure author and category exist
from src.models import Author, Category, Article

# Check author exists
author = Author.find_by_id(1)
if not author:
    print("Author with ID 1 not found")

# Check category exists  
category = Category.find_by_id(1)
if not category:
    print("Category with ID 1 not found")
```

### Problem: Database Corruption

**Symptoms**:
- Sync commands fail unexpectedly
- Inconsistent data between runs
- SQL errors on valid operations

**Solutions**:

1. **Check Database Integrity**:
```bash
python3 -c "
from src.database.db_manager import DatabaseManager
with DatabaseManager().get_connection() as conn:
    result = conn.execute('PRAGMA integrity_check').fetchone()
    print('Integrity check:', result[0])
"
```

2. **Backup and Restore**:
```bash
# Backup current database
cp data/infnews.db data/infnews.db.backup

# Recreate from schema
python3 -c "
from src.database.db_manager import DatabaseManager
import os
os.remove('data/infnews.db')
db = DatabaseManager()
print('Database recreated')
"
```

## 🌐 Web & Navigation Issues

### Problem: Broken Links or 404 Errors

**Symptoms**:
- Clicking navigation links leads to 404
- Images not loading
- CSS not applying

**Solutions**:

1. **Re-sync All Content**:
```bash
# Regenerate all HTML with correct paths
python3 sync_content.py sync --all
```

2. **Check File Structure**:
```bash
# Verify integrated pages exist
ls -la integrated/
ls -la integrated/authors/
ls -la integrated/categories/
```

3. **Verify Relative Paths**:
- From `integrated/categories.html` to `index.html` should be `../index.html`
- From `integrated/authors/author_name.html` to `index.html` should be `../../index.html`

### Problem: Images Not Loading

**Symptoms**:
- Broken image icons
- Placeholder images showing instead of content
- 404 errors for image files

**Solutions**:

1. **Check Image Status**:
```bash
# View image procurement list
cat data/image_procurement_list.csv
```

2. **Verify Image Directories**:
```bash
ls -la assets/images/
ls -la assets/images/authors/
ls -la assets/placeholders/
```

3. **Source Missing Images**:
- Download images from procurement list
- Place in correct directories with correct names
- Follow naming convention: `author_slug_profile.jpg`

### Problem: CSS Not Loading

**Symptoms**:
- Plain HTML with no styling
- Layout broken

**Solutions**:

1. **Check Internet Connection**:
- Tailwind CSS loads from CDN
- Test: https://cdn.tailwindcss.com

2. **View Page Source**:
- Verify `<script src="https://cdn.tailwindcss.com"></script>` exists
- Check for any JavaScript errors

3. **Use Local CSS** (if needed):
```html
<!-- Replace CDN link with local file -->
<link rel="stylesheet" href="assets/css/tailwind.min.css">
```

## 🔍 Search Issues

### Problem: Search Not Working

**Symptoms**:
- Search returns no results
- Search page doesn't load
- API errors

**Solutions**:

1. **Test Search Backend**:
```bash
# Test search directly
python3 search_backend.py "technology"
# Should return JSON with results
```

2. **Check Database Content**:
```bash
# Verify content exists to search
python3 sync_content.py list --type categories
python3 sync_content.py list --type authors
```

3. **Verify Search HTML**:
- Open `search.html` in browser
- Check browser console for JavaScript errors
- Verify API endpoint is accessible

### Problem: Search Returns Empty Results

**Solutions**:

1. **Add Content to Database**:
```bash
# Check if database has content
python3 sync_content.py stats
# If counts are 0, add content first
```

2. **Check Search Terms**:
- Try broader search terms
- Search for known content (e.g., "Technology", "Business")

3. **Rebuild Search Index**:
```bash
# Re-sync content to rebuild search
python3 sync_content.py sync --all
```

## 🔧 Content Management Issues

### Problem: Sync Commands Fail

**Error**:
```
❌ Failed to sync authors: 'Author' object has no attribute 'sync_all'
```

**Solutions**:

1. **Check Method Exists**:
```python
# Verify integrator has sync_all method
from src.integrators.author_integrator import AuthorIntegrator
integrator = AuthorIntegrator()
hasattr(integrator, 'sync_all')  # Should be True
```

2. **Update Integrators**:
- Ensure all integrators inherit from BaseIntegrator
- Verify all required abstract methods are implemented

### Problem: Content Not Appearing

**Symptoms**:
- Added content to database but not showing on website
- Old content still showing after updates

**Solutions**:

1. **Sync After Changes**:
```bash
# Always sync after database changes
python3 sync_content.py sync --all
```

2. **Clear Browser Cache**:
- Hard refresh: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)
- Clear browser cache completely

3. **Verify Database Changes**:
```bash
# Check if changes are in database
python3 sync_content.py list --type authors
```

### Problem: GUI Application Won't Start

**Error**:
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**Solutions**:

1. **Use CLI Instead**:
```bash
# Use command-line tools instead of GUI
python3 sync_content.py sync --all
```

2. **Set Display** (Linux):
```bash
export DISPLAY=:0
python3 content_manager.py
```

3. **Use Remote GUI** (SSH):
```bash
ssh -X username@server
python3 content_manager.py
```

## 📱 Mobile & Browser Issues

### Problem: Mobile Layout Broken

**Symptoms**:
- Text too small on mobile
- Navigation menu not working
- Content overflowing screen

**Solutions**:

1. **Check Viewport Meta Tag**:
```html
<!-- Should be in all HTML files -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

2. **Test Responsive Design**:
- Use browser dev tools
- Test on actual mobile devices
- Check CSS media queries

3. **Re-sync Content**:
```bash
# Ensure latest responsive templates
python3 sync_content.py sync --all
```

### Problem: Browser Compatibility

**Symptoms**:
- Site works in Chrome but not Internet Explorer
- JavaScript errors in older browsers

**Solutions**:

1. **Check Browser Support**:
- Tailwind CSS requires modern browsers
- IE11 and below not supported

2. **Use Modern Browser**:
- Chrome 60+
- Firefox 60+  
- Safari 12+
- Edge 18+

## 🚨 Emergency Recovery

### Complete System Reset

If everything is broken, follow these steps:

1. **Backup Current State**:
```bash
cp -r Template_News_Site-main Template_News_Site-main.backup
```

2. **Check Database**:
```bash
python3 sync_content.py check
python3 sync_content.py stats
```

3. **Regenerate Everything**:
```bash
# Nuclear option: regenerate all content
python3 sync_content.py sync --all
```

4. **Test Basic Functionality**:
```bash
# Test each component
python3 search_backend.py "test"
open index.html
```

### Starting Over

If you need to start completely fresh:

1. **Save Your Content**:
```bash
# Export any custom content first
cp -r content/ content.backup/
```

2. **Reset Database**:
```bash
rm data/infnews.db
python3 -c "from src.database.db_manager import DatabaseManager; DatabaseManager()"
```

3. **Rebuild Everything**:
```bash
python3 sync_content.py sync --all
```

## 📞 Getting Additional Help

### Self-Help Resources

1. **Check Documentation**:
   - [Quick Start Guide](quick-start.md)
   - [Content Management Guide](content-management.md)
   - [Architecture Overview](architecture.md)

2. **Run Diagnostics**:
```bash
python3 sync_content.py check
python3 sync_content.py stats
```

3. **Check File Permissions**:
```bash
ls -la data/
ls -la integrated/
```

### Common Error Patterns

**Import Errors**: Usually working directory or Python path issues  
**Database Errors**: Often permission or foreign key constraint issues  
**Sync Errors**: Usually missing content or relationship problems  
**Display Errors**: Often browser cache or CSS loading issues  

### Debug Mode

Enable verbose output for troubleshooting:

```python
# Add debug prints to any Python file
import logging
logging.basicConfig(level=logging.DEBUG)

# For database operations
from src.database.db_manager import DatabaseManager
db = DatabaseManager()
# Database operations will show SQL queries
```

---

**Last Updated**: December 10, 2024  
**Support**: Check FAQ.md for additional help  
**Emergency**: Use system reset procedures above