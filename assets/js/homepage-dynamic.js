// Homepage dynamic content loader
// Loads articles dynamically from database-generated content

let homepageArticles = [];

// Load articles into homepage
function loadHomepageArticles() {
    const grid = document.getElementById('articlesGrid');
    if (!grid) {
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

// Load more functionality
function loadMoreArticles() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.innerHTML = 'No more articles';
        loadMoreBtn.disabled = true;
        loadMoreBtn.className = loadMoreBtn.className.replace('hover:from-indigo-700 hover:to-purple-700', 'bg-gray-400 cursor-not-allowed');
    }
}

// Initialize homepage when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    loadHomepageArticles();
});

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.homepageArticles = homepageArticles;
    window.loadHomepageArticles = loadHomepageArticles;
    window.createArticleCard = createArticleCard;
}