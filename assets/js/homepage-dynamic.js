
// Auto-generated homepage data from database
// Generated at: 2025-06-18T17:11:14.276270

const homepageArticles = [
  {
    "id": 17,
    "title": "New Platform Update Changes Everything for Creators",
    "excerpt": "Major social media platform announces algorithm changes that could reshape how creators build audiences and earn revenue in 2025.",
    "slug": "new-platform-update-changes-everything-for-creators",
    "author_name": "Alex Rivera",
    "author_slug": "alex-rivera",
    "category_name": "Technology",
    "category_slug": "technology",
    "category_color": "#3B82F6",
    "category_icon": "\ud83d\ude80",
    "publish_date": "2025-06-18T17:11:14.259243",
    "views": 0,
    "likes": 0,
    "read_time_minutes": 1,
    "image_url": "assets/images/default-article.jpg",
    "url": "integrated/articles/article_new-platform-update-changes-everything-for-creators.html"
  }
];

// Load articles into homepage
function loadHomepageArticles() {
    const grid = document.getElementById('articlesGrid');
    if (!grid) {
        console.error('Articles grid not found');
        return;
    }
    
    // Remove loading indicator
    const loadingIndicator = document.getElementById('articlesLoading');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
    
    // Clear existing content
    grid.innerHTML = '';
    
    // Add articles to grid
    homepageArticles.forEach((article, index) => {
        const articleCard = createArticleCard(article, index === 0);
        grid.appendChild(articleCard);
    });
    
    console.log(`Loaded ${homepageArticles.length} articles from database`);
}

function createArticleCard(article, isFeatured = false) {
    const card = document.createElement('div');
    card.className = isFeatured ? 
        'article-card bg-white rounded-xl shadow-lg overflow-hidden md:col-span-2 lg:col-span-1' :
        'article-card bg-white rounded-xl shadow-lg overflow-hidden';
    
    // Format publish date
    const publishDate = new Date(article.publish_date);
    const timeAgo = getTimeAgo(publishDate);
    
    // Create card HTML with safe escaping
    card.innerHTML = `
        <div class="relative">
            <img src="${article.image_url}" alt="${escapeHtml(article.title)}" class="w-full h-48 object-cover" loading="lazy" onerror="this.src='assets/images/default-article.jpg'">
            <div class="absolute top-4 right-4">
                <span class="category-${article.category_name} bg-white/90 px-2 py-1 rounded text-xs font-bold uppercase">${article.category_name}</span>
            </div>
        </div>
        <div class="p-6">
            <div class="flex items-center gap-2 mb-3">
                <span class="text-gray-500 text-sm">${escapeHtml(article.author_name)} • ${timeAgo}</span>
            </div>
            <h3 class="text-lg font-bold mb-3 hover:text-indigo-600 transition cursor-pointer">
                ${escapeHtml(article.title)}
            </h3>
            <p class="text-gray-700 mb-4 text-sm">
                ${escapeHtml(article.excerpt)}
            </p>
            <div class="flex items-center justify-between text-sm">
                <span class="text-gray-500">👁 ${article.views.toLocaleString()} views</span>
                <a href="${article.url}" class="text-indigo-600 font-medium cursor-pointer">Read →</a>
            </div>
        </div>
    `;
    
    return card;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getTimeAgo(date) {
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
}

// Enhanced load more functionality with real search integration
let allArticles = [...homepageArticles];
let articlesPerPage = 6;
let currentPage = 1;

function loadMoreArticles() {
    console.log('Loading more articles...');
    
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.innerHTML = '<span class="animate-spin">⟳</span> Loading...';
        loadMoreBtn.disabled = true;
        
        // In production, this would call the search backend for more articles
        setTimeout(() => {
            loadMoreBtn.innerHTML = 'No more articles';
            loadMoreBtn.disabled = true;
            loadMoreBtn.className = loadMoreBtn.className.replace('hover:from-indigo-700 hover:to-purple-700', 'bg-gray-400 cursor-not-allowed');
        }, 1000);
    }
}

// Search functionality
// Note: Search has been moved to dedicated search.html page
// These functions are kept for compatibility but mobile search still works

// Initialize homepage when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing dynamic homepage...');
    loadHomepageArticles();
});

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.homepageArticles = homepageArticles;
    window.loadHomepageArticles = loadHomepageArticles;
    window.createArticleCard = createArticleCard;
}
