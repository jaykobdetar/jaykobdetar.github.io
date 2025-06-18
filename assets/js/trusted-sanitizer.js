/**
 * Trusted Client-Side Sanitization
 * Using DOMPurify - industry standard HTML sanitization library
 * 
 * This replaces all custom escapeHtml functions with trusted sanitization
 */

// Import DOMPurify v3.1.7 (latest stable version)
// Note: In production, download and serve DOMPurify locally for better security

class TrustedSanitizer {
    constructor() {
        this.isDOMPurifyLoaded = typeof DOMPurify !== 'undefined';
        
        if (!this.isDOMPurifyLoaded) {
            console.warn('DOMPurify not loaded. Using fallback sanitization.');
        }
        
        // Configure DOMPurify with secure defaults
        if (this.isDOMPurifyLoaded) {
            this.configureDOMPurify();
        }
    }
    
    configureDOMPurify() {
        // Set secure configuration for DOMPurify
        DOMPurify.setConfig({
            // Allow only safe HTML tags
            ALLOWED_TAGS: [
                'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'mark',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'dl', 'dt', 'dd',
                'blockquote', 'pre', 'code',
                'a', 'img', 'figure', 'figcaption',
                'table', 'thead', 'tbody', 'tr', 'td', 'th',
                'div', 'span', 'section', 'article',
                'hr', 'sub', 'sup', 'small'
            ],
            
            // Allow only safe attributes
            ALLOWED_ATTR: [
                'href', 'title', 'alt', 'src', 'width', 'height',
                'class', 'id', 'colspan', 'rowspan', 'scope'
            ],
            
            // Allow only safe URL schemes
            ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
            
            // Security settings
            KEEP_CONTENT: false,  // Don't keep content of removed elements
            ADD_TAGS: [],         // Don't allow additional tags
            ADD_ATTR: [],         // Don't allow additional attributes
            FORBID_TAGS: ['script', 'object', 'embed', 'form', 'input', 'textarea', 'select', 'button'],
            FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur', 'style']
        });
    }
    
    /**
     * Sanitize HTML content using DOMPurify (trusted library)
     * @param {string} content - HTML content to sanitize
     * @param {boolean} allowHTML - Whether to allow HTML tags
     * @returns {string} Sanitized content
     */
    sanitizeHTML(content, allowHTML = true) {
        if (!content || typeof content !== 'string') {
            return '';
        }
        
        if (this.isDOMPurifyLoaded) {
            if (allowHTML) {
                return DOMPurify.sanitize(content);
            } else {
                // Strip all HTML tags
                return DOMPurify.sanitize(content, { ALLOWED_TAGS: [] });
            }
        } else {
            // Fallback to basic escaping if DOMPurify not available
            return this.fallbackSanitize(content, allowHTML);
        }
    }
    
    /**
     * Sanitize text content (no HTML allowed)
     * @param {string} content - Text content to sanitize
     * @returns {string} Sanitized text
     */
    sanitizeText(content) {
        return this.sanitizeHTML(content, false);
    }
    
    /**
     * Sanitize and validate URL
     * @param {string} url - URL to sanitize
     * @returns {string} Sanitized URL or empty string if invalid
     */
    sanitizeURL(url) {
        if (!url || typeof url !== 'string') {
            return '';
        }
        
        url = url.trim();
        
        // Block dangerous protocols
        const dangerousProtocols = ['javascript:', 'vbscript:', 'data:', 'file:'];
        const urlLower = url.toLowerCase();
        
        for (const protocol of dangerousProtocols) {
            if (urlLower.startsWith(protocol)) {
                console.warn(`Blocked dangerous URL protocol: ${protocol}`);
                return '';
            }
        }
        
        // Allow safe protocols and relative URLs
        const safeProtocols = ['http:', 'https:', 'mailto:', 'tel:'];
        const isRelative = url.startsWith('/') || url.startsWith('#');
        const hasSafeProtocol = safeProtocols.some(protocol => urlLower.startsWith(protocol));
        
        if (!isRelative && !hasSafeProtocol) {
            console.warn(`Blocked unsafe URL: ${url}`);
            return '';
        }
        
        return url;
    }
    
    /**
     * Fallback sanitization when DOMPurify is not available
     * @param {string} content - Content to sanitize
     * @param {boolean} allowHTML - Whether to allow HTML
     * @returns {string} Sanitized content
     */
    fallbackSanitize(content, allowHTML) {
        if (!allowHTML) {
            // Create a temporary div to extract text content
            const div = document.createElement('div');
            div.textContent = content;
            return div.innerHTML;
        } else {
            // Basic HTML escaping for dangerous elements
            return content
                .replace(/<script[^>]*>.*?<\/script>/gi, '')
                .replace(/javascript:/gi, '')
                .replace(/vbscript:/gi, '')
                .replace(/on\w+\s*=/gi, '')
                .replace(/<iframe[^>]*>/gi, '')
                .replace(/<object[^>]*>/gi, '')
                .replace(/<embed[^>]*>/gi, '');
        }
    }
    
    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean} Whether email is valid
     */
    validateEmail(email) {
        if (!email || typeof email !== 'string') {
            return false;
        }
        
        const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        return emailRegex.test(email.trim());
    }
    
    /**
     * Validate and sanitize slug
     * @param {string} slug - Slug to validate
     * @returns {string} Sanitized slug
     */
    sanitizeSlug(slug) {
        if (!slug || typeof slug !== 'string') {
            return '';
        }
        
        return slug
            .toLowerCase()
            .trim()
            .replace(/[^a-z0-9-]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-+|-+$/g, '');
    }
    
    /**
     * Safe innerHTML replacement
     * @param {HTMLElement} element - Target element
     * @param {string} content - HTML content to set
     */
    safeSetHTML(element, content) {
        if (!element || !content) {
            return;
        }
        
        const sanitized = this.sanitizeHTML(content);
        element.innerHTML = sanitized;
    }
    
    /**
     * Safe textContent replacement
     * @param {HTMLElement} element - Target element
     * @param {string} content - Text content to set
     */
    safeSetText(element, content) {
        if (!element || content === null || content === undefined) {
            return;
        }
        
        element.textContent = String(content);
    }
}

// Global instance
const trustedSanitizer = new TrustedSanitizer();

// Replace global escapeHtml function with trusted sanitization
window.escapeHtml = function(text) {
    return trustedSanitizer.sanitizeText(text);
};

// Safe HTML setting function
window.safeSetHTML = function(element, content) {
    return trustedSanitizer.safeSetHTML(element, content);
};

// Safe text setting function
window.safeSetText = function(element, content) {
    return trustedSanitizer.safeSetText(element, content);
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TrustedSanitizer;
}