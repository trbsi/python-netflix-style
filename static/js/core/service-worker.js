/*
* !!! IMPORTANT !!!
* It has to be in root of public directory because of scope, otherwise it will not work properly
* e.g. push notifications will not work properly
* */
self.addEventListener('install', (event) => {
    // Activate immediately
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    // Take control of all pages immediately
    event.waitUntil(self.clients.claim());
});

// IMPORTANT: no caching, no intercepting HTML, no fetch handler
// This is intentional