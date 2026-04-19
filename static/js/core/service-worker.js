const CACHE_NAME = "app-cache-v1";
const urlsToCache = [
    "/",
];

/* ------------ CORE LOGIC FOR APP INSTALL ------------- */

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});


/* ----------------- SHOWING PROMPT --------------- */
let deferredPrompt;
const HIDE_KEY = "installPromptDismissedAt";
const HIDE_DAYS = 5;

// Show install prompt when available
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();

    if (!shouldShowPrompt()) return;

    deferredPrompt = e;
    document.getElementById('installPrompt').style.display = 'block';
});

document.addEventListener("DOMContentLoaded", function () {
    if (isIOS() && shouldShowIOSPrompt()) {
        document.getElementById('iosInstallPrompt').style.display = 'block';
    }
});

// Install button click
document.getElementById('installBtn').addEventListener('click', async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const result = await deferredPrompt.userChoice;

    console.log('User choice:', result.outcome);
    deferredPrompt = null;

    document.getElementById('installPrompt').style.display = 'none';
});

// Close button
document.getElementById('closeBtn').addEventListener('click', () => {
    localStorage.setItem(HIDE_KEY, Date.now().toString());
    document.getElementById('installPrompt').style.display = 'none';
});

// Optional: hide if already installed
window.addEventListener('appinstalled', () => {
    document.getElementById('installPrompt').style.display = 'none';
});

if (isIOS()) {
    document.getElementById('iosInstallPrompt').style.display = 'block';
}

document.getElementById('iosClose').addEventListener('click', () => {
    localStorage.setItem("iosInstallDismissed", Date.now());
    document.getElementById('iosInstallPrompt').style.display = 'none';
});

function shouldShowIOSPrompt() {
    const t = localStorage.getItem("iosInstallDismissed");
    if (!t) return true;

    const days = (Date.now() - parseInt(t)) / (1000 * 60 * 60 * 24);
    return days >= 5;
}

function shouldShowPrompt() {
    const dismissedAt = localStorage.getItem(HIDE_KEY);
    if (!dismissedAt) return true;

    const now = Date.now();
    const diff = now - parseInt(dismissedAt, 10);
    const days = diff / (1000 * 60 * 60 * 24);

    return days >= HIDE_DAYS;
}

function isIOS() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent);
}