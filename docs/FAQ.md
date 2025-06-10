# Frequently Asked Questions

## General Questions

### What is Influencer News CMS?
Influencer News CMS is a desktop content management system specifically designed for creating and managing static news websites focused on the influencer and creator economy. It provides a GUI interface for managing articles, authors, categories, and trending topics.

### Do I need any programming knowledge?
No programming knowledge is required! The system uses simple text files with a specific format, and the GUI handles all the technical aspects of HTML generation and website management.

### What platforms does it work on?
The system works on Windows, macOS, and Linux. It requires Python 3.7 or higher, which includes the tkinter GUI library.

## Installation & Setup

### What do I need to install?
Only Python 3.7 or higher is required. The system uses built-in Python libraries only, so no additional packages need to be installed.

### How do I get started?
1. Download/clone the project
2. Run `python3 integration_manager.py`
3. Click "Setup" buttons to create sample files
4. Edit the samples or create your own content
5. Use "Integrate" to process your content

### The GUI won't start. What's wrong?
- Ensure Python 3.7+ is installed: `python3 --version`
- Test tkinter availability: `python3 -m tkinter`
- Try running: `python3 integration_manager.py` (note the "3")
- Check that you're in the correct directory

## Content Creation

### What file format do I use?
All content uses `.txt` files with a specific format:
- Metadata fields at the top
- A `---` separator line
- Content in markdown format below

### Can I use HTML in my content?
Basic HTML is supported in the markdown content area, but the system primarily uses markdown formatting for safety and simplicity.

### How do I add images?
Use image URLs in the `Image:` field. Recommended sources:
- Unsplash: `https://images.unsplash.com/photo-123?w=600&h=400&fit=crop`
- Other public CDNs or your own hosting

### What's the difference between Bio and extended biography for authors?
- `Bio`: Short description used in article bylines and listing pages
- Extended biography: Full content after the `---` separator, used on individual author profile pages

## Integration Process

### What does "integration" mean?
Integration converts your `.txt` source files into professional HTML pages, updates navigation, and links everything together into a complete website.

### Why do I need to integrate files?
Raw `.txt` files can't be viewed as web pages. Integration generates the HTML, CSS styling, navigation links, and cross-references needed for a functional website.

### Can I integrate the same file multiple times?
No, the system tracks processed files in JSON databases to prevent duplicates. If you want to update content, edit the source file and re-integrate, or remove the old version first.

### What's the difference between individual and batch integration?
- **Individual**: Process one content type at a time (Articles, Authors, etc.)
- **Batch**: Process all content types in sequence
- **Selective**: Choose specific files to integrate from the available options

## Content Management

### How do I update existing content?
1. Edit the source `.txt` file in the `content/` directory
2. Remove the old version using the Content Management tab
3. Re-integrate the updated file

### How do I remove content?
Use the Content Management or Content Browser tabs in the integration manager:
- Remove by ID or filename
- Use selective removal for multiple items
- Clean orphaned files periodically

### What are orphaned files?
Orphaned files are HTML pages in the `integrated/` directory that don't have corresponding entries in the JSON databases. This can happen if files are manually deleted or if integration fails.

### When should I run the sync utility?
Run `python3 sync_site.py` when:
- Content appears out of sync with the website
- After manually editing database files
- After bulk content operations
- As a general "fix everything" tool

## File Structure & Organization

### Can I change the folder structure?
The basic structure (`content/` → `integrated/`) is required for the system to work. You can rename individual files, but keep them in the correct subdirectories.

### What are the JSON files in the data/ directory?
These are the databases that track processed content:
- `articles_db.json` - Article tracking and metadata
- `authors_db.json` - Author profile information
- `categories_db.json` - Category definitions and settings
- `trending_db.json` - Trending topic data and metrics

### Can I edit the JSON files directly?
While possible, it's not recommended. Use the GUI tools instead. If you must edit them directly, run `python3 sync_site.py` afterward to ensure consistency.

## Cross-Linking & References

### How do author names need to match?
The `Author:` field in articles must exactly match the `Name:` field in author files, including capitalization and spacing. Example:
- Author file: `Name: Sarah Chen`
- Article file: `Author: Sarah Chen` ✓
- Article file: `Author: sarah chen` ✗

### How do category references work?
Articles and trending topics reference categories by their `slug` value, not the display name:
- Category file: `Slug: creator-economy`
- Article file: `Category: creator-economy` ✓
- Article file: `Category: Creator Economy` ✗

### What happens if I reference a non-existent author or category?
The integration will fail with an error message indicating the missing reference. Create the author or category file first, then integrate the referencing content.

## Website & Output

### Where is my generated website?
The main website files are:
- `index.html` - Homepage
- `search.html` - Search page  
- `authors.html` - Authors listing
- `integrated/categories.html` - Categories overview
- `integrated/trending.html` - Trending topics overview
- Individual content pages in `integrated/` subdirectories

### How do I publish my website?
The generated HTML files can be uploaded to any web hosting service. Popular options:
- GitHub Pages (free)
- Netlify (free tier available)
- Traditional web hosting
- CDN services

### Can I customize the appearance?
The system uses Tailwind CSS for styling. Advanced users can modify the HTML generation code in the integrator files to customize layouts and styling.

### Is the website mobile-friendly?
Yes, all generated pages use responsive design with Tailwind CSS and are optimized for mobile devices.

## Troubleshooting

### "Missing required field" error
- Check that all required fields are present in your file
- Ensure field names are spelled correctly (case-sensitive)
- Verify that field values are not empty

### "Invalid format" error
- Ensure the `---` separator line exists
- Check for special characters that might break parsing
- Verify the file is saved as plain text (.txt)

### Content appears but navigation is broken
- Run `python3 sync_site.py` to fix navigation
- Check that all referenced authors and categories exist
- Verify relative paths in generated HTML

### Integration succeeds but content doesn't appear
- Check the generated files in `integrated/` directories
- Run the sync utility: `python3 sync_site.py`
- Verify cross-references (author names, category slugs)

### GUI becomes unresponsive
- Large content sets may take time to process
- Check the log panel for progress updates
- Restart the application if it truly hangs

## Performance & Limits

### How many articles can the system handle?
The system has been tested with hundreds of articles. Performance depends on your computer's specs and the complexity of cross-linking.

### Why is integration slow?
Integration involves:
- File parsing and validation
- HTML generation with styling
- Cross-reference resolution
- Database updates
- Navigation rebuilding

### Can I speed up the process?
- Use selective integration for large batches
- Ensure authors and categories exist before integrating articles
- Close other applications to free up system resources

## Advanced Usage

### Can I add new content types?
Yes, but it requires programming knowledge. See the CONTRIBUTING.md guide for details on extending the system.

### How do I backup my content?
Back up these directories:
- `content/` - Your source files
- `data/` - The JSON databases
- Optionally `integrated/` - Generated content (can be regenerated)

### Can I use version control?
Yes! The source files in `content/` and `data/` work well with Git. Consider adding `integrated/` to `.gitignore` since it can be regenerated.

### How do I migrate content between systems?
Copy the `content/` and `data/` directories to the new system, then run integration to regenerate the website files.

## Getting Help

### Where can I get more help?
- **Documentation**: Check the comprehensive guides in the project
- **GitHub Issues**: Report bugs or ask questions
- **GitHub Discussions**: Community discussions and feature requests
- **Help Button**: In the integration manager GUI

### How do I report a bug?
1. Check if the issue already exists in GitHub Issues
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - System information
   - Error messages or screenshots

### How do I request a feature?
Use GitHub Issues with the "enhancement" label, including:
- Description of the desired feature
- Use case and benefits
- Any implementation suggestions

## Contributing

### How can I contribute?
- Report bugs and suggest features
- Improve documentation
- Submit code contributions
- Help other users in discussions

### Do I need programming skills to contribute?
Not necessarily! Documentation improvements, bug reports, feature suggestions, and user support are all valuable contributions.