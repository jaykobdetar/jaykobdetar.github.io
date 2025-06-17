/**
 * Mobile Touch Enhancement for Influencer News
 * Provides touch gestures, haptic feedback, and mobile-optimized interactions
 */

class MobileTouchEnhancer {
    constructor() {
        this.isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        this.touchStartTime = 0;
        this.touchStartPos = { x: 0, y: 0 };
        this.tapThreshold = 10; // pixels
        this.swipeThreshold = 50; // pixels
        this.longPressDelay = 500; // milliseconds
        
        this.init();
    }
    
    init() {
        if (!this.isTouch) return;
        
        this.setupTouchTargets();
        this.setupSwipeGestures();
        this.setupLongPress();
        this.setupTouchFeedback();
        this.setupPullToRefresh();
        this.optimizeTapTargets();
        
        console.log('✓ Mobile touch enhancements initialized');
    }
    
    setupTouchTargets() {
        // Ensure all interactive elements have adequate touch targets
        const minTouchSize = 44; // iOS/Android recommended minimum
        
        const interactiveElements = document.querySelectorAll(
            'button, a, input[type="button"], input[type="submit"], .mobile-nav-item, .article-card'
        );
        
        interactiveElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            
            // Add padding if element is too small
            if (rect.width < minTouchSize || rect.height < minTouchSize) {
                element.style.minHeight = `${minTouchSize}px`;
                element.style.minWidth = `${minTouchSize}px`;
                element.style.display = 'flex';
                element.style.alignItems = 'center';
                element.style.justifyContent = 'center';
            }
        });
    }
    
    setupSwipeGestures() {
        // Add swipe support for article cards and image galleries
        const swipeableElements = document.querySelectorAll('.article-card, .related-card, picture');
        
        swipeableElements.forEach(element => {
            let startX = 0;
            let startY = 0;
            let startTime = 0;
            
            element.addEventListener('touchstart', (e) => {
                const touch = e.touches[0];
                startX = touch.clientX;
                startY = touch.clientY;
                startTime = Date.now();
                
                // Add visual feedback
                element.style.transition = 'transform 0.1s ease';
                element.style.transform = 'scale(0.98)';
            }, { passive: true });
            
            element.addEventListener('touchmove', (e) => {
                if (e.touches.length > 1) return; // Ignore multi-touch
                
                const touch = e.touches[0];
                const deltaX = touch.clientX - startX;
                const deltaY = touch.clientY - startY;
                
                // Prevent default scroll if horizontal swipe is detected
                if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
                    e.preventDefault();
                    
                    // Visual feedback for swipe
                    const swipeProgress = Math.min(Math.abs(deltaX) / 100, 1);
                    element.style.transform = `translateX(${deltaX * 0.3}px) scale(${0.98 + swipeProgress * 0.02})`;
                }
            }, { passive: false });
            
            element.addEventListener('touchend', (e) => {
                const touch = e.changedTouches[0];
                const deltaX = touch.clientX - startX;
                const deltaY = touch.clientY - startY;
                const deltaTime = Date.now() - startTime;
                
                // Reset visual feedback
                element.style.transition = 'transform 0.3s ease';
                element.style.transform = '';
                
                // Detect swipe gestures
                if (deltaTime < 300 && Math.abs(deltaX) > this.swipeThreshold && Math.abs(deltaX) > Math.abs(deltaY)) {
                    if (deltaX > 0) {
                        this.handleSwipeRight(element);
                    } else {
                        this.handleSwipeLeft(element);
                    }
                }
                
                // Cleanup
                setTimeout(() => {
                    element.style.transition = '';
                }, 300);
            }, { passive: true });
        });
    }
    
    handleSwipeLeft(element) {
        // Handle left swipe (e.g., next article, share action)
        if (element.classList.contains('article-card')) {
            this.showQuickActions(element, 'left');
        }
    }
    
    handleSwipeRight(element) {
        // Handle right swipe (e.g., bookmark, like action)
        if (element.classList.contains('article-card')) {
            this.showQuickActions(element, 'right');
        }
    }
    
    showQuickActions(element, direction) {
        // Create quick action overlay
        const actionsOverlay = document.createElement('div');
        actionsOverlay.className = 'quick-actions-overlay';
        actionsOverlay.style.cssText = `
            position: absolute;
            top: 0;
            ${direction}: 0;
            width: 80px;
            height: 100%;
            background: linear-gradient(90deg, 
                ${direction === 'left' ? 'rgba(59, 130, 246, 0.9), rgba(59, 130, 246, 0.7)' : 'rgba(16, 185, 129, 0.9), rgba(16, 185, 129, 0.7)'}
            );
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            z-index: 10;
            border-radius: 0.75rem;
        `;
        
        // Add action icon
        actionsOverlay.innerHTML = direction === 'left' ? '📤' : '❤️';
        
        // Position relative to parent
        element.style.position = 'relative';
        element.appendChild(actionsOverlay);
        
        // Animate in
        actionsOverlay.style.opacity = '0';
        actionsOverlay.style.transform = `translateX(${direction === 'left' ? '-20px' : '20px'})`;
        
        requestAnimationFrame(() => {
            actionsOverlay.style.transition = 'all 0.3s ease';
            actionsOverlay.style.opacity = '1';
            actionsOverlay.style.transform = 'translateX(0)';
        });
        
        // Auto remove after delay
        setTimeout(() => {
            actionsOverlay.style.opacity = '0';
            actionsOverlay.style.transform = `translateX(${direction === 'left' ? '-20px' : '20px'})`;
            setTimeout(() => {
                if (actionsOverlay.parentNode) {
                    actionsOverlay.parentNode.removeChild(actionsOverlay);
                }
            }, 300);
        }, 2000);
        
        // Add haptic feedback if available
        this.hapticFeedback('light');
    }
    
    setupLongPress() {
        const longPressElements = document.querySelectorAll('.article-card, .mobile-nav-item, 'picture');
        
        longPressElements.forEach(element => {
            let longPressTimer = null;
            let isLongPress = false;
            
            element.addEventListener('touchstart', (e) => {
                isLongPress = false;
                longPressTimer = setTimeout(() => {
                    isLongPress = true;
                    this.handleLongPress(element, e);
                }, this.longPressDelay);
            }, { passive: true });
            
            element.addEventListener('touchmove', () => {
                if (longPressTimer) {
                    clearTimeout(longPressTimer);
                    longPressTimer = null;
                }
            }, { passive: true });
            
            element.addEventListener('touchend', () => {
                if (longPressTimer) {
                    clearTimeout(longPressTimer);
                    longPressTimer = null;
                }
            }, { passive: true });
            
            // Prevent context menu on long press
            element.addEventListener('contextmenu', (e) => {
                if (isLongPress) {
                    e.preventDefault();
                }
            });
        });
    }
    
    handleLongPress(element, event) {
        // Show context menu or additional options
        this.hapticFeedback('medium');
        
        if (element.classList.contains('article-card')) {
            this.showArticleContextMenu(element, event);
        } else if (element.tagName === 'PICTURE' || element.querySelector('img')) {
            this.showImageContextMenu(element, event);
        }
    }
    
    showArticleContextMenu(element, event) {
        const contextMenu = document.createElement('div');
        contextMenu.className = 'context-menu';
        contextMenu.style.cssText = `
            position: fixed;
            top: ${event.touches[0].clientY}px;
            left: ${event.touches[0].clientX}px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            padding: 8px;
            z-index: 1000;
            min-width: 200px;
            transform: scale(0.8);
            opacity: 0;
            transition: all 0.2s ease;
        `;
        
        contextMenu.innerHTML = `
            <div class="context-menu-item" style="padding: 12px; cursor: pointer; border-radius: 8px;" onmousedown="this.style.background='#f3f4f6'">
                📖 Read Later
            </div>
            <div class="context-menu-item" style="padding: 12px; cursor: pointer; border-radius: 8px;" onmousedown="this.style.background='#f3f4f6'">
                📤 Share Article
            </div>
            <div class="context-menu-item" style="padding: 12px; cursor: pointer; border-radius: 8px;" onmousedown="this.style.background='#f3f4f6'">
                ❤️ Like
            </div>
            <div class="context-menu-item" style="padding: 12px; cursor: pointer; border-radius: 8px;" onmousedown="this.style.background='#f3f4f6'">
                🔗 Copy Link
            </div>
        `;
        
        document.body.appendChild(contextMenu);
        
        // Animate in
        requestAnimationFrame(() => {
            contextMenu.style.transform = 'scale(1)';
            contextMenu.style.opacity = '1';
        });
        
        // Auto remove after delay or on touch outside
        const removeMenu = () => {
            contextMenu.style.transform = 'scale(0.8)';
            contextMenu.style.opacity = '0';
            setTimeout(() => {
                if (contextMenu.parentNode) {
                    contextMenu.parentNode.removeChild(contextMenu);
                }
            }, 200);
        };
        
        setTimeout(removeMenu, 3000);
        
        // Remove on touch outside
        document.addEventListener('touchstart', function onTouch(e) {
            if (!contextMenu.contains(e.target)) {
                removeMenu();
                document.removeEventListener('touchstart', onTouch);
            }
        });
    }
    
    showImageContextMenu(element, event) {
        // Implement image-specific context menu
        console.log('Image long press detected');
    }
    
    setupTouchFeedback() {
        // Add visual feedback for touch interactions
        const touchElements = document.querySelectorAll('button, a, .mobile-nav-item, .article-card');
        
        touchElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                element.style.transform = 'scale(0.95)';
                element.style.transition = 'transform 0.1s ease';
            }, { passive: true });
            
            element.addEventListener('touchend', () => {
                element.style.transform = '';
                element.style.transition = 'transform 0.2s ease';
            }, { passive: true });
            
            element.addEventListener('touchcancel', () => {
                element.style.transform = '';
                element.style.transition = 'transform 0.2s ease';
            }, { passive: true });
        });
    }
    
    setupPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let isPulling = false;
        let pullToRefreshElement = null;
        
        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
                isPulling = true;
            }
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (!isPulling) return;
            
            currentY = e.touches[0].clientY;
            const pullDistance = currentY - startY;
            
            if (pullDistance > 0 && window.scrollY === 0) {
                if (!pullToRefreshElement) {
                    pullToRefreshElement = this.createPullToRefreshIndicator();
                }
                
                const progress = Math.min(pullDistance / 100, 1);
                pullToRefreshElement.style.transform = `translateY(${pullDistance * 0.5}px)`;
                pullToRefreshElement.style.opacity = progress;
                
                if (progress >= 1) {
                    pullToRefreshElement.classList.add('ready');
                    pullToRefreshElement.innerHTML = '🔄 Release to refresh';
                } else {
                    pullToRefreshElement.classList.remove('ready');
                    pullToRefreshElement.innerHTML = '⬇️ Pull to refresh';
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', () => {
            if (isPulling && pullToRefreshElement) {
                if (pullToRefreshElement.classList.contains('ready')) {
                    this.triggerRefresh();
                }
                
                pullToRefreshElement.style.transform = '';
                pullToRefreshElement.style.opacity = '0';
                setTimeout(() => {
                    if (pullToRefreshElement && pullToRefreshElement.parentNode) {
                        pullToRefreshElement.parentNode.removeChild(pullToRefreshElement);
                        pullToRefreshElement = null;
                    }
                }, 300);
            }
            isPulling = false;
        }, { passive: true });
    }
    
    createPullToRefreshIndicator() {
        const indicator = document.createElement('div');
        indicator.style.cssText = `
            position: fixed;
            top: -50px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(59, 130, 246, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            z-index: 1000;
            opacity: 0;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        `;
        indicator.innerHTML = '⬇️ Pull to refresh';
        document.body.appendChild(indicator);
        return indicator;
    }
    
    triggerRefresh() {
        this.hapticFeedback('medium');
        
        // Show loading state
        const loadingIndicator = document.createElement('div');
        loadingIndicator.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(16, 185, 129, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            z-index: 1000;
            backdrop-filter: blur(10px);
        `;
        loadingIndicator.innerHTML = '🔄 Refreshing...';
        document.body.appendChild(loadingIndicator);
        
        // Simulate refresh (in real app, this would reload content)
        setTimeout(() => {
            loadingIndicator.innerHTML = '✅ Updated!';
            setTimeout(() => {
                if (loadingIndicator.parentNode) {
                    loadingIndicator.parentNode.removeChild(loadingIndicator);
                }
            }, 1000);
        }, 1500);
    }
    
    optimizeTapTargets() {
        // Optimize tap targets for mobile
        const style = document.createElement('style');
        style.textContent = `
            @media (max-width: 768px) {
                /* Ensure minimum touch target sizes */
                button, a, input[type="button"], input[type="submit"] {
                    min-height: 44px !important;
                    min-width: 44px !important;
                    padding: 8px 12px !important;
                }
                
                /* Optimize link spacing */
                .nav-link {
                    padding: 12px 16px !important;
                    margin: 4px 0 !important;
                }
                
                /* Touch-friendly form controls */
                input, select, textarea {
                    font-size: 16px !important; /* Prevent zoom on iOS */
                    padding: 12px !important;
                }
                
                /* Article card touch optimization */
                .article-card {
                    margin-bottom: 16px !important;
                    touch-action: manipulation;
                }
                
                /* Improve text selection on mobile */
                .article-content p,
                .article-content h1,
                .article-content h2,
                .article-content h3 {
                    -webkit-user-select: text;
                    user-select: text;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    hapticFeedback(intensity = 'light') {
        // Provide haptic feedback if available
        if ('vibrate' in navigator) {
            const patterns = {
                light: [10],
                medium: [20],
                heavy: [30]
            };
            navigator.vibrate(patterns[intensity] || patterns.light);
        }
    }
}

// Initialize mobile touch enhancements when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        new MobileTouchEnhancer();
    }
});

// Export for use in other scripts
window.MobileTouchEnhancer = MobileTouchEnhancer;