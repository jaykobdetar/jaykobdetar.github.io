/**
 * IndexedDB Initialization for Influencer News PWA
 * Handles offline storage for articles and user preferences
 */

class InfluencerNewsDB {
    constructor() {
        this.dbName = 'InfluencerNewsDB';
        this.dbVersion = 2;
        this.db = null;
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);
            
            request.onerror = () => {
                console.error('IndexedDB: Failed to open database');
                reject(request.error);
            };
            
            request.onsuccess = () => {
                this.db = request.result;
                console.log('IndexedDB: Database opened successfully');
                resolve(this.db);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                console.log('IndexedDB: Upgrading database schema');
                
                // Create object stores
                this.createObjectStores(db);
            };
        });
    }
    
    createObjectStores(db) {
        // Sync data store for background sync
        if (!db.objectStoreNames.contains('syncData')) {
            const syncStore = db.createObjectStore('syncData', { keyPath: 'key' });
            syncStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
        
        // Cached articles store
        if (!db.objectStoreNames.contains('articles')) {
            const articlesStore = db.createObjectStore('articles', { keyPath: 'id' });
            articlesStore.createIndex('slug', 'slug', { unique: true });
            articlesStore.createIndex('category', 'category_name', { unique: false });
            articlesStore.createIndex('author', 'author_name', { unique: false });
            articlesStore.createIndex('cached_at', 'cached_at', { unique: false });
        }
        
        // User preferences store
        if (!db.objectStoreNames.contains('preferences')) {
            const prefsStore = db.createObjectStore('preferences', { keyPath: 'key' });
        }
        
        
        // Search cache
        if (!db.objectStoreNames.contains('searchCache')) {
            const searchStore = db.createObjectStore('searchCache', { keyPath: 'query' });
            searchStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
    }
    
    // Article management
    async cacheArticle(article) {
        if (!this.db) await this.init();
        
        const transaction = this.db.transaction(['articles'], 'readwrite');
        const store = transaction.objectStore('articles');
        
        // Add cache timestamp
        article.cached_at = new Date().toISOString();
        
        return new Promise((resolve, reject) => {
            const request = store.put(article);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
    
    async getCachedArticle(id) {
        if (!this.db) await this.init();
        
        const transaction = this.db.transaction(['articles'], 'readonly');
        const store = transaction.objectStore('articles');
        
        return new Promise((resolve, reject) => {
            const request = store.get(id);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
    
    async getCachedArticles(limit = 20) {
        if (!this.db) await this.init();
        
        const transaction = this.db.transaction(['articles'], 'readonly');
        const store = transaction.objectStore('articles');
        
        return new Promise((resolve, reject) => {
            const request = store.getAll();
            request.onsuccess = () => {
                const articles = request.result
                    .sort((a, b) => new Date(b.cached_at) - new Date(a.cached_at))
                    .slice(0, limit);
                resolve(articles);
            };
            request.onerror = () => reject(request.error);
        });
    }
    
    // Preferences management
    async setPreference(key, value) {
        if (!this.db) await this.init();
        
        const transaction = this.db.transaction(['preferences'], 'readwrite');
        const store = transaction.objectStore('preferences');
        
        return new Promise((resolve, reject) => {
            const request = store.put({ key, value, updated_at: new Date().toISOString() });
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
    
    async getPreference(key, defaultValue = null) {
        if (!this.db) await this.init();
        
        const transaction = this.db.transaction(['preferences'], 'readonly');
        const store = transaction.objectStore('preferences');
        
        return new Promise((resolve, reject) => {
            const request = store.get(key);
            request.onsuccess = () => {
                const result = request.result;
                resolve(result ? result.value : defaultValue);
            };
            request.onerror = () => reject(request.error);
        });
    }
    
    // Search cache management
    async cacheSearchResults(query, results) {
        if (!this.db) await this.init();
        
        const transaction = this.db.transaction(['searchCache'], 'readwrite');
        const store = transaction.objectStore('searchCache');
        
        const cacheEntry = {
            query: query.toLowerCase(),
            results: results,
            timestamp: new Date().toISOString()
        };
        
        return new Promise((resolve, reject) => {
            const request = store.put(cacheEntry);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
    
    async getCachedSearchResults(query) {
        if (!this.db) await this.init();
        
        const transaction = this.db.transaction(['searchCache'], 'readonly');
        const store = transaction.objectStore('searchCache');
        
        return new Promise((resolve, reject) => {
            const request = store.get(query.toLowerCase());
            request.onsuccess = () => {
                const result = request.result;
                if (result) {
                    // Check if cache is still fresh (5 minutes)
                    const cacheAge = Date.now() - new Date(result.timestamp).getTime();
                    if (cacheAge < 5 * 60 * 1000) {
                        resolve(result.results);
                        return;
                    }
                }
                resolve(null);
            };
            request.onerror = () => reject(request.error);
        });
    }
}

// Global instance
window.influencerNewsDB = new InfluencerNewsDB();

// Initialize on load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await window.influencerNewsDB.init();
        console.log('IndexedDB: Initialization complete');
        
        
    } catch (error) {
        console.error('IndexedDB: Initialization failed', error);
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InfluencerNewsDB;
}