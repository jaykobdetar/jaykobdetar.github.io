/**
 * Clean Search Integration for Influencer News CMS
 * Uses the local search API server at localhost:8080
 */

class SearchAPI {
    constructor() {
        this.apiBaseURL = 'http://localhost:8080/api';
        this.isSearching = false;
    }

    /**
     * Perform search using the local API server
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Promise<Object>} Search results
     */
    async search(query, options = {}) {
        if (this.isSearching) {
            console.log('Search already in progress');
            return null;
        }

        const { limit = 20, offset = 0 } = options;
        this.isSearching = true;

        try {
            const url = `${this.apiBaseURL}/search?q=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`;
            console.log('Searching:', url);
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const results = await response.json();
            console.log('Search results:', results);
            
            return results;
        } catch (error) {
            console.error('Search API error:', error);
            throw error;
        } finally {
            this.isSearching = false;
        }
    }

    /**
     * Get search suggestions (autocomplete)
     * @param {string} query - Partial query
     * @returns {Promise<Array>} Suggestions array
     */
    async getSuggestions(query) {
        if (!query || query.length < 2) return [];

        try {
            const url = `${this.apiBaseURL}/suggestions?q=${encodeURIComponent(query)}`;
            const response = await fetch(url);
            if (!response.ok) return [];
            
            const suggestions = await response.json();
            return suggestions.suggestions || [];
        } catch (error) {
            console.error('Suggestions API error:', error);
            return [];
        }
    }
}

// Create global search API instance
window.searchAPI = new SearchAPI();