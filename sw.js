/**
 * Service Worker for Influencer News PWA
 * Provides offline functionality, caching, and background sync
 */

const CACHE_NAME = 'influencer-news-v1.2';
const STATIC_CACHE = 'static-cache-v1.2';
const DYNAMIC_CACHE = 'dynamic-cache-v1.2';

// Static assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/search.html',
  '/authors.html',
  '/integrated/categories.html',
  '/integrated/trending.html',
  '/assets/css/styles.min.css',
  '/assets/js/mobile-touch.js',
  '/manifest.json'
];

// Dynamic assets to cache on request
const CACHE_STRATEGIES = {
  // Cache first for static assets
  cacheFirst: [
    /\.css$/,
    /\.js$/,
    /\.woff2?$/,
    /\.png$/,
    /\.jpg$/,
    /\.jpeg$/,
    /\.webp$/,
    /\.avif$/
  ],
  
  // Network first for API calls and dynamic content
  networkFirst: [
    /\/search/,
    /\/api\//,
    /\.json$/
  ],
  
  // Stale while revalidate for HTML pages
  staleWhileRevalidate: [
    /\.html$/,
    /\/$/
  ]
};

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('Service Worker: Static assets cached');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Service Worker: Failed to cache static assets', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => {
              return cacheName !== STATIC_CACHE && 
                     cacheName !== DYNAMIC_CACHE &&
                     cacheName !== CACHE_NAME;
            })
            .map(cacheName => {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return;
  }
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  event.respondWith(
    getCachedResponse(request)
  );
});

async function getCachedResponse(request) {
  const url = new URL(request.url);
  const pathname = url.pathname;
  
  try {
    // Determine caching strategy
    const strategy = getCachingStrategy(pathname);
    
    switch (strategy) {
      case 'cacheFirst':
        return await cacheFirstStrategy(request);
      
      case 'networkFirst':
        return await networkFirstStrategy(request);
      
      case 'staleWhileRevalidate':
        return await staleWhileRevalidateStrategy(request);
      
      default:
        return await networkFirstStrategy(request);
    }
  } catch (error) {
    console.error('Service Worker: Fetch error', error);
    return await getOfflineFallback(request);
  }
}

function getCachingStrategy(pathname) {
  for (const [strategy, patterns] of Object.entries(CACHE_STRATEGIES)) {
    if (patterns.some(pattern => pattern.test(pathname))) {
      return strategy;
    }
  }
  return 'networkFirst';
}

async function cacheFirstStrategy(request) {
  const cache = await caches.open(STATIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    throw error;
  }
}

async function networkFirstStrategy(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

async function staleWhileRevalidateStrategy(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  // Return cached response immediately if available
  const fetchPromise = fetch(request)
    .then(networkResponse => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    })
    .catch(() => {
      // Network failed, return cached response if available
      return cachedResponse;
    });
  
  return cachedResponse || await fetchPromise;
}

async function getOfflineFallback(request) {
  const url = new URL(request.url);
  
  // For HTML requests, return cached index.html or offline page
  if (request.headers.get('accept').includes('text/html')) {
    const cache = await caches.open(STATIC_CACHE);
    return await cache.match('/index.html') || 
           await cache.match('/offline.html') ||
           new Response('Offline - Please check your connection', {
             status: 503,
             headers: { 'Content-Type': 'text/plain' }
           });
  }
  
  // For image requests, return placeholder
  if (request.headers.get('accept').includes('image/')) {
    return new Response(
      '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="#f3f4f6"/><text x="200" y="150" text-anchor="middle" fill="#9ca3af" font-family="Arial" font-size="16">Image Offline</text></svg>',
      { 
        headers: { 'Content-Type': 'image/svg+xml' } 
      }
    );
  }
  
  // For other requests, return generic offline response
  return new Response('Resource not available offline', {
    status: 503,
    headers: { 'Content-Type': 'text/plain' }
  });
}

// Background sync for analytics and form submissions
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(handleBackgroundSync());
  }
});

async function handleBackgroundSync() {
  try {
    // Sync any pending analytics data
    await syncAnalytics();
    
    // Sync any saved articles or user preferences
    await syncUserData();
    
    console.log('Service Worker: Background sync completed');
  } catch (error) {
    console.error('Service Worker: Background sync failed', error);
  }
}

async function syncAnalytics() {
  // Implementation for syncing analytics data when back online
  const pendingAnalytics = await getStoredData('pendingAnalytics');
  
  if (pendingAnalytics && pendingAnalytics.length > 0) {
    for (const data of pendingAnalytics) {
      try {
        await fetch('/api/analytics', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
      } catch (error) {
        console.error('Failed to sync analytics data', error);
      }
    }
    
    // Clear synced data
    await clearStoredData('pendingAnalytics');
  }
}

async function syncUserData() {
  // Implementation for syncing user preferences, saved articles, etc.
  console.log('Syncing user data...');
}

// Utility functions for IndexedDB storage
async function getStoredData(key) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('InfluencerNewsDB', 1);
    
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['syncData'], 'readonly');
      const store = transaction.objectStore('syncData');
      const getRequest = store.get(key);
      
      getRequest.onsuccess = () => {
        resolve(getRequest.result ? getRequest.result.data : null);
      };
      
      getRequest.onerror = () => {
        reject(getRequest.error);
      };
    };
    
    request.onerror = () => {
      reject(request.error);
    };
  });
}

async function clearStoredData(key) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('InfluencerNewsDB', 1);
    
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['syncData'], 'readwrite');
      const store = transaction.objectStore('syncData');
      const deleteRequest = store.delete(key);
      
      deleteRequest.onsuccess = () => {
        resolve();
      };
      
      deleteRequest.onerror = () => {
        reject(deleteRequest.error);
      };
    };
    
    request.onerror = () => {
      reject(request.error);
    };
  });
}

// Push notification handling
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'New content available!',
    icon: '/assets/icons/icon-192x192.png',
    badge: '/assets/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '2'
    },
    actions: [
      {
        action: 'explore',
        title: 'Read Now',
        icon: '/assets/icons/action-read.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/assets/icons/action-close.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Influencer News', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('Service Worker: Loaded successfully');