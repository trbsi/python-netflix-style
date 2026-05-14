let deferredPrompt;

const HIDE_KEY = "installPromptDismissedAt";
const HIDE_DAYS = 5;

/* ----------- HELPERS ----------- */

function shouldShowPrompt() {
    const dismissedAt = localStorage.getItem(HIDE_KEY);
    if (!dismissedAt) return true;

    const days = (Date.now() - parseInt(dismissedAt)) / (1000 * 60 * 60 * 24);
    return days >= HIDE_DAYS;
}

function isIOS() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent);
}

/* ----------- ANDROID INSTALL ----------- */
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();

    if (!shouldShowPrompt()) return;

    deferredPrompt = e;
    document.getElementById('androidInstallPrompt').style.display = 'block';
});

document.getElementById('androidInstallBtn').addEventListener('click', async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();

    const {outcome} = await deferredPrompt.userChoice;

    deferredPrompt = null;
    document.getElementById('androidInstallPrompt').style.display = 'none';
});

/* ----------- CLOSE BUTTON ----------- */

document.getElementById('androidCloseBtn')?.addEventListener('click', () => {
    localStorage.setItem(HIDE_KEY, Date.now().toString());
    document.getElementById('androidInstallPrompt').style.display = 'none';
});

/* ----------- IOS PROMPT ----------- */

document.getElementById('iosClose')?.addEventListener('click', () => {
    localStorage.setItem(HIDE_KEY, Date.now().toString());
    document.getElementById('iosInstallPrompt').style.display = 'none';
});

/* ----------- INIT ----------- */

document.addEventListener("DOMContentLoaded", function () {
    // iOS manual banner
    if (isIOS() && shouldShowPrompt() && !isInstalledPWA()) {
        document.getElementById('iosInstallPrompt').style.display = 'block';
    }

    // Push notification prompt
    if (shouldShowPushPrompt()) {
        document.getElementById('pushPrompt').style.display = 'block';
    }
});

/* ----------- PUSH PROMPT ----------- */

const PUSH_HIDE_KEY = 'pushPromptDismissedAt';
const PUSH_HIDE_DAYS = 3;

function shouldShowPushPrompt() {
    return false; //NOT IMPLEMENTED
    //debugPushPrompt('isInstalledPWA', isInstalledPWA());
    if (!isInstalledPWA()) return false;
    if (!isUserAuthenticated || hasPushSubscription) return false;
    if (!('Notification' in window)) return false;
    if (Notification.permission === 'denied') return false;

    const dismissedAt = localStorage.getItem(PUSH_HIDE_KEY);
    if (!dismissedAt) return true;

    const days = (Date.now() - parseInt(dismissedAt)) / (1000 * 60 * 60 * 24);
    return days >= PUSH_HIDE_DAYS;
}

function isInstalledPWA() {
    return window.matchMedia('(display-mode: standalone)').matches
        || window.navigator.standalone === true; // iOS Safari
}

function debugPushPrompt(key, value) {
    let el = document.getElementById('push-debug-body');
    if (!el) {
        const bar = document.createElement('div');
        bar.style.cssText = 'position:fixed;bottom:0;left:0;right:0;z-index:99999;font-family:monospace;font-size:12px;background:#1a1a1a;color:#e0e0e0;border-top:2px solid #333';
        bar.innerHTML = '<div id="push-debug-body" style="padding:6px 12px;display:flex;flex-wrap:wrap;gap:6px 20px;"></div>';
        document.body.appendChild(bar);
        el = document.getElementById('push-debug-body');
    }

    const color = '#eb5757';
    const span = document.createElement('span');
    span.innerHTML = `<span style="color:#aaa">${key}:</span> <b style="color:${color}">${value}</b>`;
    el.appendChild(span);
}

document.getElementById('pushClose')?.addEventListener('click', () => {
    localStorage.setItem(PUSH_HIDE_KEY, Date.now().toString());
    document.getElementById('pushPrompt').style.display = 'none';
});

document.getElementById('pushEnableBtn')?.addEventListener('click', async () => {
    document.getElementById('pushPrompt').style.display = 'none';
    await requestNotificationPermission();
});

/* ----------------- PUSH NOTIFICATION -------------- */
async function requestNotificationPermission() {
    if (!isUserAuthenticated) {
        return;
    }

    const permission = await Notification.requestPermission();
    if (permission !== 'granted') return;

    await subscribeToPush();
}

async function subscribeToPush() {
    const registration = await navigator.serviceWorker.ready;

    const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
    });

    // Send subscription to your Laravel backend
    const response = await fetch(createWebTokenEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
        },
        body: JSON.stringify(subscription),
    });

    const data = await response.json();
}

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = atob(base64);
    return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)));
}
