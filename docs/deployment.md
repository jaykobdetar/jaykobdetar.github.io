# Deployment Guide

Complete guide for deploying your Influencer News CMS to production.

## 🎯 Deployment Overview

The CMS is designed for **static hosting** with an optional Python backend for search and management features.

**Frontend**: Static HTML/CSS/JS files  
**Backend**: Optional Python API for search and management  
**Database**: Portable SQLite file  
**Assets**: Images and media files  

## 📦 Deployment Options

### Option 1: Static Only (Recommended)

Deploy just the HTML files for a fast, secure website.

**Pros**:
- ✅ Fast loading and global CDN support
- ✅ No server maintenance required  
- ✅ Secure (no server-side vulnerabilities)
- ✅ Cost-effective (often free)

**Cons**:
- ❌ No real-time search (static search only)
- ❌ No content management via web interface

**Best for**: Blogs, news sites, portfolio sites

### Option 2: Full Stack

Deploy both frontend and Python backend.

**Pros**:
- ✅ Full search functionality
- ✅ Web-based content management
- ✅ Real-time content updates

**Cons**:
- ❌ Requires Python hosting
- ❌ More complex deployment
- ❌ Higher hosting costs

**Best for**: Dynamic content sites, team collaboration

## 🚀 Static Deployment

### Files to Deploy

**Required Files**:
```
├── index.html
├── authors.html  
├── search.html
├── article.html
├── 404.html
├── integrated/
│   ├── authors/
│   ├── categories/
│   ├── trending/
│   ├── articles/
│   ├── categories.html
│   └── trending.html
└── assets/
    ├── images/
    └── placeholders/
```

**Optional Files** (for full functionality):
```
├── search_backend.py
├── data/infnews.db
└── src/
```

### Pre-Deployment Checklist

1. **Generate All Content**:
```bash
python3 sync_content.py sync --all
```

2. **Source Images**:
```bash
# Download images from procurement list
cat data/image_procurement_list.csv
# Place in assets/images/ directories
```

3. **Test Locally**:
```bash
# Open in browser and test all links
open index.html
```

4. **Validate HTML**:
- Check all navigation links
- Verify responsive design
- Test on mobile devices

### Static Hosting Providers

#### Netlify (Recommended)

**Setup**:
1. Create account at [netlify.com](https://netlify.com)
2. Drag and drop your project folder
3. Site will be live at `random-name.netlify.app`

**Features**:
- ✅ Free tier with custom domains
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Easy updates via drag-and-drop

**Configuration** (netlify.toml):
```toml
[build]
  publish = "."

[[redirects]]
  from = "/search/*"
  to = "/search.html"
  status = 200

[[redirects]]
  from = "/*"
  to = "/404.html"
  status = 404
```

#### Vercel

**Setup**:
1. Create account at [vercel.com](https://vercel.com)
2. Import project from GitHub or upload
3. Deploy with zero configuration

**Features**:
- ✅ Free tier
- ✅ Instant deployments
- ✅ Global CDN
- ✅ GitHub integration

#### GitHub Pages

**Setup**:
1. Create GitHub repository
2. Upload files to repository
3. Enable Pages in repository settings
4. Site available at `username.github.io/repository`

**Features**:
- ✅ Free for public repositories
- ✅ Git-based deployment
- ✅ Custom domains supported

**Configuration** (.github/workflows/deploy.yml):
```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
```

#### Other Options

**Cloudflare Pages**: Free tier, excellent performance  
**Firebase Hosting**: Google's hosting platform  
**AWS S3 + CloudFront**: Scalable, pay-as-you-go  
**Traditional Web Hosting**: Upload via FTP/SFTP  

### Custom Domain Setup

1. **Purchase Domain**: From registrar (Namecheap, GoDaddy, etc.)
2. **Configure DNS**: Point to your hosting provider
3. **Enable HTTPS**: Most providers offer automatic SSL

**DNS Configuration Example** (Netlify):
```
Type: CNAME
Name: www
Value: your-site.netlify.app

Type: A
Name: @
Value: 75.2.60.5  # Netlify's IP
```

## 🖥️ Full Stack Deployment

### Python Backend Requirements

**System Requirements**:
- Python 3.7+
- SQLite 3
- Write permissions for database

**Dependencies**:
```bash
pip install -r requirements.txt
# Currently no external dependencies required
```

### Platform Options

#### Heroku

**Setup**:
1. Install Heroku CLI
2. Create application
3. Deploy via Git

**Files needed**:

`Procfile`:
```
web: python3 search_backend.py --port=$PORT
```

`requirements.txt`:
```
# Add any future dependencies here
```

`runtime.txt`:
```
python-3.9.18
```

**Deployment**:
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### DigitalOcean App Platform

**Setup**:
1. Create DigitalOcean account
2. Create new app from GitHub
3. Configure build settings

**Configuration**:
```yaml
name: influencer-news-cms
services:
- name: web
  source_dir: /
  github:
    repo: your-username/your-repo
    branch: main
  run_command: python3 search_backend.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
```

#### VPS Deployment

**Setup on Ubuntu/Debian**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip nginx -y

# Clone your repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Install dependencies
pip3 install -r requirements.txt

# Configure Nginx
sudo nano /etc/nginx/sites-available/influencernews
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Static files
    location / {
        root /path/to/your/project;
        try_files $uri $uri/ /index.html;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Process Management** (systemd):
```ini
# /etc/systemd/system/influencernews.service
[Unit]
Description=Influencer News CMS API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/usr/bin/python3 search_backend.py --port=8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start Services**:
```bash
# Enable and start services
sudo systemctl enable influencernews
sudo systemctl start influencernews
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## 🔒 Security Considerations

### Static Deployment Security

**HTTPS**: Always enable HTTPS (most providers offer free SSL)  
**Headers**: Configure security headers via hosting provider  
**Content**: No server-side vulnerabilities to worry about  

### Full Stack Security

**Database Security**:
```python
# Use environment variables for sensitive config
import os

DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/infnews.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
```

**API Security**:
```python
# Add rate limiting
from time import time
from collections import defaultdict

request_counts = defaultdict(list)

def rate_limit(ip, limit=100, window=3600):
    now = time()
    requests = request_counts[ip]
    requests[:] = [req_time for req_time in requests if now - req_time < window]
    
    if len(requests) >= limit:
        return False
    
    requests.append(now)
    return True
```

**File Permissions**:
```bash
# Secure file permissions
chmod 644 *.html
chmod 644 assets/images/*
chmod 600 data/infnews.db
chmod 700 src/
```

## 📊 Performance Optimization

### Frontend Optimization

**Image Optimization**:
```bash
# Optimize images before deployment
# Use tools like ImageOptim, TinyPNG, or:
find assets/images -name "*.jpg" -exec jpegoptim --max=85 {} \;
find assets/images -name "*.png" -exec optipng -o2 {} \;
```

**HTML Minification**:
```bash
# Optional: Minify HTML files
# Use tools like html-minifier
npm install -g html-minifier
html-minifier --collapse-whitespace --remove-comments index.html > index.min.html
```

**CDN Configuration**:
- Tailwind CSS already served from CDN
- Google Fonts served from CDN
- Consider CDN for images if using many

### Backend Optimization

**Database Optimization**:
```sql
-- Run before deployment
PRAGMA optimize;
VACUUM;
ANALYZE;
```

**Caching**:
```python
# Simple file-based caching
import json
import os
from time import time

def cache_response(key, data, ttl=3600):
    cache_file = f"cache/{key}.json"
    cache_data = {
        'data': data,
        'expires': time() + ttl
    }
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f)

def get_cached_response(key):
    cache_file = f"cache/{key}.json"
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
            if time() < cache_data['expires']:
                return cache_data['data']
    return None
```

## 🔄 Continuous Deployment

### Automated Deployment

**GitHub Actions** (.github/workflows/deploy.yml):
```yaml
name: Deploy CMS
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Sync content
      run: python3 sync_content.py sync --all
    
    - name: Deploy to Netlify
      uses: nwtgck/actions-netlify@v1.2
      with:
        publish-dir: './.'
        production-branch: main
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

### Content Updates

**Static Deployment**:
1. Update content locally
2. Run `python3 sync_content.py sync --all`
3. Upload updated files

**Full Stack Deployment**:
1. Update content via management interface
2. Changes are live immediately
3. Optional: Schedule automated content sync

## 📈 Monitoring & Analytics

### Analytics Setup

**Google Analytics 4**:
```html
<!-- Add to all HTML pages, before closing </head> -->
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

**Alternative Analytics**:
- Plausible Analytics (privacy-focused)
- Cloudflare Analytics (if using Cloudflare)
- Simple Analytics (GDPR compliant)

### Performance Monitoring

**Web Vitals**:
```html
<!-- Add to pages for Core Web Vitals tracking -->
<script>
  import {getCLS, getFID, getFCP, getLCP, getTTFB} from 'web-vitals';

  getCLS(console.log);
  getFID(console.log);
  getFCP(console.log);
  getLCP(console.log);
  getTTFB(console.log);
</script>
```

**Uptime Monitoring**:
- UptimeRobot (free tier available)
- Pingdom (basic monitoring)
- StatusCake (website monitoring)

## 🛠️ Post-Deployment Tasks

### Testing Checklist

**Functionality Testing**:
- ✅ All pages load correctly
- ✅ Navigation works from all pages
- ✅ Images load or show placeholders
- ✅ Search functionality works (if backend deployed)
- ✅ Mobile responsive design
- ✅ Loading speed acceptable

**SEO Testing**:
- ✅ Meta descriptions present
- ✅ Page titles unique and descriptive
- ✅ Images have alt text
- ✅ Proper heading hierarchy (H1, H2, H3)

**Browser Testing**:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

### Ongoing Maintenance

**Content Updates**:
1. Add new content via templates or GUI
2. Sync content: `python3 sync_content.py sync --all`
3. Deploy updated files

**Performance Monitoring**:
- Monitor page load speeds
- Check for broken links monthly
- Update dependencies as needed

**Security Updates**:
- Keep hosting platform updated
- Monitor for security advisories
- Regular backups of database

## 🚨 Troubleshooting Deployment

### Common Issues

**404 Errors on Netlify/Vercel**:
```toml
# netlify.toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Images Not Loading**:
- Check file paths are correct
- Verify images are uploaded
- Check case sensitivity on URLs

**Search Not Working**:
- Ensure Python backend is deployed
- Check API endpoints are accessible
- Verify database is uploaded and accessible

**Slow Loading**:
- Optimize images before upload
- Use CDN for static assets
- Enable gzip compression

---

**Last Updated**: December 10, 2024  
**Deployment Status**: Production Ready  
**Hosting Options**: Static (recommended) or Full Stack  
**Performance**: Optimized for speed and SEO