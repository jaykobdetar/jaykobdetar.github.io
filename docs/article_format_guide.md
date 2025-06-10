# 📝 Article Formatting Guide

## Quick Setup Instructions

1. **Save your HTML files with these exact names:**
   - `index.html` (homepage)
   - `search.html` (search page) 
   - `article.html` (article template)
   - `authors.html` (authors page)
   - `404.html` (404/no results page)

2. **Save the Python script as:** `integrate_articles.py`

3. **Create your articles in the `articles/` folder** (script creates this automatically)

## 📄 Article Text File Format

Create `.txt` files in the `articles/` folder using this exact format:

```
Title: Your Article Title Here
Author: Sarah Chen
Category: business
Image: https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=600&h=300&fit=crop
Tags: keyword1, keyword2, keyword3
Excerpt: Brief description that appears on homepage and search results. Keep under 200 characters for best display.

---

Your opening paragraph goes here. This should hook the reader and introduce the topic compellingly.

## First Section Heading

Write your content here. You can have multiple paragraphs in each section.

This is another paragraph in the same section.

## Special Formatting Options

### Information Boxes
[INFO] Use this format for important information that needs to be highlighted with a blue background.

### Bullet Lists
Create lists like this:

- First point
- Second point  
- Third point with more details

### Quotes
> This is how you create a blockquote. It will be beautifully styled. - Quote Author

## More Content Sections

Continue adding sections with ## headings. Each section will be properly formatted with HTML styling.

## Conclusion

End with a strong conclusion that provides value to readers.
```

## 🎯 Available Authors

Choose from these pre-configured authors (case-insensitive):

- **Sarah Chen** - Senior Business Reporter (Business, Creator Economy)
- **Michael Torres** - Entertainment Editor (Celebrity News, Entertainment)  
- **Alex Rivera** - Tech Correspondent (Algorithms, Platform Updates)
- **Jessica Kim** - Beauty & Fashion Editor (Beauty, Fashion, Collabs)
- **David Park** - Markets & Economics Editor (Market Analysis, Data)

*You can also use any custom author name - the script will create a basic profile automatically.*

## 📂 Categories

Choose from these categories (affects color styling):

- `business` (green)
- `entertainment` (orange)
- `tech` (blue) 
- `fashion` (pink)
- `charity` (purple)
- `beauty` (pink)

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

## 🚀 Usage Instructions

1. **Create your article file:**
   ```
   articles/my_new_article.txt
   ```

2. **Run the integration script:**
   ```bash
   python integrate_articles.py
   ```

3. **The script will automatically:**
   - ✅ Create individual article pages (`article_1.html`, etc.)
   - ✅ Update homepage with latest articles
   - ✅ Update search page with new content
   - ✅ Generate realistic view counts and metrics
   - ✅ Calculate reading time
   - ✅ Create proper links between pages

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

## 📝 Example Article File

Save this as `articles/sample_news.txt`:

```
Title: New Platform Update Changes Everything for Creators
Author: Alex Rivera  
Category: tech
Image: https://images.unsplash.com/photo-1607827448387-a67db1383b59?w=600&h=300&fit=crop
Tags: platform update, algorithm, creators, monetization
Excerpt: Major social media platform announces algorithm changes that could reshape how creators build audiences and earn revenue.

---

In a surprise announcement today, one of the world's largest social media platforms revealed significant changes to its recommendation algorithm that could fundamentally alter the creator landscape.

## What's Changing

The new algorithm will prioritize several key factors:

- Longer engagement times over quick views
- Community interaction and responses  
- Original content over reposts
- Consistent posting schedules

[INFO] These changes go into effect starting next month, giving creators time to adapt their strategies.

## Impact on Creators

> This could be the biggest shift we've seen since the platform launched. Creators need to think long-term now. - Industry Expert

Early testing shows creators who focus on community building are seeing significant growth, while those relying on viral trends are experiencing decreased reach.

## Looking Forward

The platform's commitment to rewarding quality content over viral moments represents a maturation of the creator economy that could benefit serious content creators in the long run.
```

## 🎉 Ready to Publish!

Once you've created your article file, just run:
```bash
python integrate_articles.py
```

Your new article will be automatically integrated into the entire website with professional styling and proper navigation!