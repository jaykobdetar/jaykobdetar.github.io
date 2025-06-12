# 📝 Article Formatting Guide

## Dynamic Template System

This guide covers the new granular template system that uses dynamic field placeholders instead of hardcoded examples.

### Template Structure

All templates now use `{{variable}}` placeholders that are replaced with actual content from your content management system.

## 📄 Dynamic Article Template Format

The new template system uses dynamic placeholders. Reference the `docs/templates/article_template.txt` for the complete structure:

```
Title: {{article.title}}
Slug: {{article.slug}}
Author: {{article.author.name}}
Category: {{article.category.slug}}
Status: {{article.status}}
Featured: {{article.featured}}
Trending: {{article.trending}}
Image: {{article.image_url}}
Tags: {{article.tags}}
Excerpt: {{article.excerpt}}
Publish_Date: {{article.publish_date}}

---

{{article.content}}
```

### Content Formatting Guidelines

Use these formatting options in your `{{article.content}}`:

**Section Headings**: Use `##` for main sections
**Information Boxes**: Use `[INFO] Your message here`
**Quotes**: Use `> Quote text - Author`
**Lists**: Standard markdown bullet and numbered lists
**Emphasis**: Use `**bold**` and `*italic*` formatting

## 🎯 Dynamic Author System

Authors are now managed through the database system with dynamic fields:

- `{{author.name}}` - Full author name
- `{{author.title}}` - Job title/position
- `{{author.bio}}` - Brief description
- `{{author.expertise}}` - Comma-separated expertise areas
- `{{author.location}}` - Geographic location
- Social links: `{{author.twitter}}`, `{{author.linkedin}}`

Refer to `docs/templates/author_template.txt` for complete author field structure.

## 📂 Dynamic Category System

Categories use dynamic fields with customizable colors:

- `{{category.name}}` - Display name
- `{{category.slug}}` - URL identifier
- `{{category.color}}` - Theme color
- `{{category.icon}}` - Emoji representation
- `{{category.description}}` - Brief description

Available colors: blue, green, red, purple, orange, pink, yellow, indigo, teal, gray

Refer to `docs/templates/category_template.txt` for complete structure.

## 🖼️ Images

Use high-quality images from Unsplash or other sources. Recommended format:
```
https://images.unsplash.com/photo-[ID]?w=600&h=300&fit=crop
```

## 🏷️ Tags

Add relevant tags separated by commas:
```
Tags: MrBeast, creator fund, YouTube, philanthropy, business
```

## 🚀 Content Management Instructions

1. **Use the new content management tools:**
   ```bash
   # Sync all content
   python3 scripts/sync_content.py
   
   # Use GUI manager
   python3 scripts/content_manager.py
   ```

2. **Template Integration:**
   - Replace `{{variable}}` placeholders with actual content
   - Use database-driven content management
   - Generate HTML from template system

3. **The system automatically:**
   - ✅ Generates pages from dynamic templates
   - ✅ Updates all content relationships
   - ✅ Maintains consistent formatting
   - ✅ Handles metadata and SEO fields
   - ✅ Manages content linking and navigation

## 📊 What Gets Generated

For each article, the script creates:

- **Individual article page** with full content
- **Homepage card** with excerpt and image
- **Search index entry** for findability
- **Realistic metrics** (views, comments, read time)
- **Proper navigation** between all pages
- **Author attribution** with bio and image

## ⚡ Advanced Formatting

### Information Boxes
```
[INFO] This creates a highlighted information box with an icon.
```

### Blockquotes with Attribution
```
> Your quote text here. - Author Name
```

### Section Headers
```
## Main Section
### Subsection (optional)
```

## 🔧 Troubleshooting

**"Invalid format" error:**
- Make sure you have the `---` separator line
- Check that all required fields are present

**Images not showing:**
- Verify the image URL is accessible
- Use direct image links (not webpage links)

**Author not found:**
- Check spelling against available authors list
- Custom names work but won't have detailed bios

## 📝 Template Reference

Refer to the dynamic templates in `docs/templates/` for complete structure:

- `article_template.txt` - Complete article structure with all dynamic fields
- `author_template.txt` - Author profile template
- `category_template.txt` - Category definition template  
- `trending_template.txt` - Trending topic template

### Key Dynamic Fields:

**Articles**: `{{article.title}}`, `{{article.content}}`, `{{article.author.name}}`
**Authors**: `{{author.name}}`, `{{author.bio}}`, `{{author.expertise}}`
**Categories**: `{{category.name}}`, `{{category.color}}`, `{{category.description}}`
**Trending**: `{{trending.title}}`, `{{trending.heat_score}}`, `{{trending.analysis}}`

## 🎉 Ready to Manage Content!

Use the new content management system:
```bash
# Sync all content types
python3 scripts/sync_content.py

# Use GUI for visual management
python3 scripts/content_manager.py
```

Your content will be automatically generated from dynamic templates with professional styling and proper relationships!