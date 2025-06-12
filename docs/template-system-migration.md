# 🔄 Template System Migration Guide

## Overview

The documentation has been updated to reflect the new granular template system that uses dynamic field placeholders instead of hardcoded examples.

## What Changed

### Before: Hardcoded Examples
The old template system included complete examples with specific data:
- Static article examples (TikTok Creator Fund story)
- Hardcoded author profiles (Sarah Johnson example)
- Fixed category examples (Creator Economy)
- Static trending topics (Virtual Collaborations)

### After: Dynamic Field Placeholders
The new system uses dynamic placeholders that are populated by your content management system:
- `{{article.title}}`, `{{article.content}}`, etc.
- `{{author.name}}`, `{{author.bio}}`, etc.
- `{{category.name}}`, `{{category.description}}`, etc.
- `{{trending.title}}`, `{{trending.heat_score}}`, etc.

## Updated Template Files

### 📄 Article Template (`docs/templates/article_template.txt`)
**Old**: Complete TikTok Creator Fund example with 140+ lines of content
**New**: Dynamic placeholders with formatting guidelines and usage instructions

**Key Changes**:
- Header fields now use `{{article.*}}` placeholders
- Content section uses `{{article.content}}` with formatting guide
- Removed hardcoded example, added template usage instructions

### 👤 Author Template (`docs/templates/author_template.txt`)
**Old**: Sarah Johnson example with full biography
**New**: Dynamic placeholders with content guidelines

**Key Changes**:
- Profile fields now use `{{author.*}}` placeholders
- Extended bio uses `{{author.extended_bio}}`
- Removed hardcoded example, added field documentation

### 📂 Category Template (`docs/templates/category_template.txt`)
**Old**: Creator Economy example with detailed description
**New**: Dynamic placeholders with content structure

**Key Changes**:
- Category fields now use `{{category.*}}` placeholders
- Description uses `{{category.extended_description}}`
- Added available color options and usage notes

### 🔥 Trending Template (`docs/templates/trending_template.txt`)
**Old**: Virtual Collaborations example with full analysis
**New**: Dynamic placeholders with analysis framework

**Key Changes**:
- Trending fields now use `{{trending.*}}` placeholders
- Analysis content uses `{{trending.analysis}}`
- Added heat score ranges and field documentation
- Marked deprecated fields for reference

## Updated Documentation

### Content Management Guide (`docs/content-management.md`)
- Updated template descriptions to reflect dynamic system
- Changed workflow instructions from "copy templates" to "use dynamic templates"
- Updated content creation process for new system

### Article Format Guide (`docs/article_format_guide.md`)
- Completely restructured for dynamic template system
- Replaced hardcoded examples with template references
- Updated usage instructions for new content management tools
- Added dynamic field documentation

## Migration Benefits

### For Developers
1. **Template Flexibility**: No need to modify templates for different content
2. **Maintainability**: Single template structure for all content of same type
3. **Scalability**: Easy to add new fields without changing examples
4. **Consistency**: All content follows same dynamic structure

### For Content Creators
1. **Clear Structure**: Templates show exactly what fields are available
2. **No Confusion**: No mixing of examples with actual template structure
3. **Better Documentation**: Clear separation of template format and usage guidelines
4. **Field Reference**: Complete list of available dynamic fields

## Dynamic Field Reference

### Article Fields
```
{{article.title}}           - Article headline
{{article.slug}}            - URL-friendly identifier
{{article.author.name}}     - Author's name
{{article.category.slug}}   - Category identifier
{{article.status}}          - Publication status
{{article.featured}}        - Homepage feature flag
{{article.trending}}        - Trending section flag
{{article.image_url}}       - Featured image URL
{{article.content}}         - Main article content
{{article.tags}}            - Comma-separated tags
{{article.excerpt}}         - Brief summary
{{article.publish_date}}    - Publication date
{{article.read_time}}       - Estimated reading time
```

### Author Fields
```
{{author.name}}             - Full name
{{author.slug}}             - URL identifier
{{author.title}}            - Job title/position
{{author.bio}}              - Brief description
{{author.image_url}}        - Profile image URL
{{author.location}}         - Geographic location
{{author.expertise}}        - Comma-separated skills
{{author.twitter}}          - Twitter handle/URL
{{author.linkedin}}         - LinkedIn profile URL
{{author.extended_bio}}     - Detailed biography
```

### Category Fields
```
{{category.name}}           - Display name
{{category.slug}}           - URL identifier
{{category.icon}}           - Emoji representation
{{category.color}}          - Theme color
{{category.description}}    - Brief description
{{category.is_featured}}    - Feature flag
{{category.sort_order}}     - Display order
{{category.extended_description}} - Detailed content
```

### Trending Fields
```
{{trending.title}}          - Topic title
{{trending.slug}}           - URL identifier
{{trending.category_id}}    - Related category
{{trending.icon}}           - Emoji icon
{{trending.heat_score}}     - Trending intensity (0-10000)
{{trending.is_active}}      - Active status
{{trending.momentum}}       - Rate of change
{{trending.analysis}}       - Detailed analysis content
```

## Implementation Notes

### Template Processing
- Templates are processed by the content management system
- Dynamic fields are replaced with actual content from the database
- Missing fields use default values or remain empty as appropriate

### Content Management
- Use `python3 scripts/sync_content.py` for content synchronization
- Use `python3 scripts/content_manager.py` for GUI management
- Templates serve as structure reference, not direct input files

### Backward Compatibility
- Old hardcoded examples have been removed
- Deprecated fields in trending template are documented for reference
- Migration guide provides field mapping for existing content

## Best Practices

### Template Usage
1. **Reference Only**: Use templates as structure reference, not input files
2. **Field Validation**: Ensure all required dynamic fields are populated
3. **Content Guidelines**: Follow formatting guidelines in template comments
4. **System Integration**: Use content management tools for template processing

### Content Creation
1. **Dynamic First**: Always use dynamic field system for new content
2. **Consistent Structure**: Follow template field order and naming
3. **Complete Data**: Populate all available fields for best results
4. **Testing**: Verify template processing before publishing

---

**Migration Date**: December 2024  
**Status**: Complete  
**Next Steps**: Content creators should familiarize themselves with dynamic field system and updated documentation