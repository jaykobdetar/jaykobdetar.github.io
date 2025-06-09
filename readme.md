# 📰 Influencer News - Modern News Website Template

A beautifully designed, fully responsive news website template with automated content management system. Built with modern web technologies and following 2025 design trends.

> **⚠️ Disclaimer**: This is a demonstration project and template, not a real news website. All content and articles are fictional examples for showcase purposes.

![Website Preview](screenshots/homepage-preview.png)

## ✨ Features

### 🎨 Modern Design
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Contemporary UI**: Follows 2025 web design trends with gradients, animations, and micro-interactions
- **Professional Layout**: Clean typography, proper spacing, and visual hierarchy
- **Dark/Light Elements**: Sophisticated color schemes and contrast

### 📱 User Experience
- **Sticky Navigation**: Always-accessible header with search functionality
- **Live Breaking News Ticker**: Animated news updates
- **Reading Progress Bar**: Visual indicator for article progress
- **Social Sharing**: Integrated sharing buttons with floating sidebar
- **Interactive Comments**: Realistic comment system with engagement features

### ⚙️ Automated Content Management
- **Python Integration Script**: Automatically converts text files to full articles
- **Dynamic Page Updates**: Homepage and search pages update automatically
- **Article Database**: JSON-based content management
- **Author Management**: Pre-configured author profiles with expertise areas
- **SEO Optimization**: Proper meta tags, structured data, and link management

### 📄 Complete Page System
- **Homepage**: Featured articles, trending topics, newsletter signup
- **Search & Browse**: Advanced filtering, real-time search suggestions
- **Individual Articles**: Full article pages with comments and related content
- **Authors Page**: Team profiles with social links and article counts
- **404/Error Pages**: Custom error handling with helpful suggestions

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Web browser
- Text editor

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/influencer-news-template.git
   cd influencer-news-template
   ```

2. **Set up the articles directory**
   ```bash
   mkdir articles
   ```

3. **Create your first article**
   ```bash
   cp articles/sample_article.txt articles/my_first_article.txt
   # Edit the file with your content
   ```

4. **Run the integration script**
   ```bash
   python integrate_articles.py
   ```

5. **Open the website**
   ```bash
   # Open index.html in your browser
   ```

## 📝 Creating Articles

Articles are created using simple text files with a specific format:

```
Title: Your Amazing Article Title
Author: Sarah Chen
Category: business
Image: https://images.unsplash.com/photo-example
Tags: keyword1, keyword2, keyword3
Excerpt: Brief description for homepage and search results.

---

Your article content goes here. You can use markdown-style formatting.

## Section Headings

Regular paragraphs with proper formatting.

### Lists
- Bullet point one
- Bullet point two
- Bullet point three

### Quotes
> This is a blockquote with proper attribution. - Quote Author

### Information Boxes
[INFO] This creates a highlighted information box for important details.
```

See [Article Format Guide](docs/article_format_guide.md) for complete documentation.

## 🗂️ Project Structure

```
influencer-news-template/
├── 📄 index.html              # Homepage
├── 🔍 search.html             # Search & browse page
├── 📰 article.html            # Article template
├── 👥 authors.html            # Editorial team page
├── ❌ 404.html                # Error page
├── 🐍 integrate_articles.py   # Main automation script
├── 🔗 link_verification.py    # Link checking utility
├── 📊 articles_db.json        # Article database
├── 📁 articles/               # Article text files
│   └── sample_article.txt
├── 📚 docs/                   # Documentation
│   ├── article_format_guide.md
│   └── SITEMAP.md
└── 🖼️ screenshots/           # Demo images
```

## 🛠️ Available Scripts

### `integrate_articles.py`
Main script that processes articles and updates the website:
- Converts text files to HTML articles
- Updates homepage with latest content
- Refreshes search index
- Generates realistic metrics
- Creates proper navigation links

### `link_verification.py`
Utility script for maintaining website health:
- Checks for broken links
- Fixes navigation issues
- Updates cross-references
- Generates sitemap

## 🎨 Customization

### Colors & Branding
Edit the CSS custom properties in the HTML files to match your brand:
- Primary colors: Indigo/Purple gradient theme
- Secondary colors: Category-specific color coding
- Typography: Inter + Playfair Display font combination

### Authors
Add or modify authors in `integrate_articles.py`:
```python
self.authors = {
    'your name': {
        'name': 'Your Name',
        'title': 'Your Title',
        'image': 'your-image-url',
        'bio': 'Your bio here',
        'expertise': ['Skill 1', 'Skill 2']
    }
}
```

### Categories
Supported categories with color themes:
- `business` (green)
- `entertainment` (orange)
- `tech` (blue)
- `fashion` (pink)
- `charity` (purple)

## 📱 Responsive Design

The template is built mobile-first and includes:
- **Breakpoints**: Tailwind CSS responsive utilities
- **Navigation**: Collapsible mobile menu
- **Images**: Responsive with proper aspect ratios
- **Typography**: Scalable font sizes
- **Touch Interactions**: Mobile-optimized buttons and links

## 🌐 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 📈 Performance Features

- **Optimized Images**: Proper sizing and compression
- **Minimal JavaScript**: Vanilla JS for core functionality
- **CSS Framework**: Tailwind CSS for minimal bundle size
- **Semantic HTML**: Proper document structure
- **SEO Ready**: Meta tags, structured data, sitemap

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 TODO / Roadmap

- [ ] Add dark mode toggle
- [ ] Implement PWA capabilities
- [ ] Add real-time search
- [ ] Create admin dashboard
- [ ] Add newsletter integration
- [ ] Implement comment system backend
- [ ] Add analytics dashboard
- [ ] Create mobile app version

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Design Inspiration**: Modern news websites like The Verge, TechCrunch, and Fast Company
- **Images**: Unsplash for high-quality stock photography
- **Icons**: Heroicons for beautiful SVG icons
- **Fonts**: Google Fonts for typography
- **CSS Framework**: Tailwind CSS for rapid styling

## 📞 Support

If you have questions or need help with the template:

- 📖 Check the [Documentation](docs/)
- 🐛 [Open an Issue](../../issues)
- 💬 [Start a Discussion](../../discussions)

## 🌟 Show Your Support

If this template helped you, please give it a ⭐ on GitHub!

---

**Made with ❤️ for the developer community**

*This template demonstrates modern web development practices and can serve as a starting point for news websites, blogs, or content management systems.*