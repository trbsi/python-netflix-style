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

function shouldShowIOSPrompt() {
    const t = localStorage.getItem("iosInstallDismissed");
    if (!t) return true;

    const days = (Date.now() - parseInt(t)) / (1000 * 60 * 60 * 24);
    return days >= 5;
}

function isIOS() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent);
}

/* ----------- ANDROID INSTALL ----------- */

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();

    if (!shouldShowPrompt()) return;

    deferredPrompt = e;
    document.getElementById('installPrompt').style.display = 'block';
});

document.getElementById('installBtn')?.addEventListener('click', async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    await deferredPrompt.userChoice;

    deferredPrompt = null;
    document.getElementById('installPrompt').style.display = 'none';
});

/* ----------- CLOSE BUTTON ----------- */

document.getElementById('closeBtn')?.addEventListener('click', () => {
    localStorage.setItem(HIDE_KEY, Date.now().toString());
    document.getElementById('installPrompt').style.display = 'none';
});

/* ----------- IOS PROMPT ----------- */

document.getElementById('iosClose')?.addEventListener('click', () => {
    localStorage.setItem("iosInstallDismissed", Date.now().toString());
    document.getElementById('iosInstallPrompt').style.display = 'none';
});

/* ----------- INIT ----------- */

document.addEventListener("DOMContentLoaded", function () {

    // iOS manual banner
    if (isIOS() && shouldShowIOSPrompt()) {
        document.getElementById('iosInstallPrompt').style.display = 'block';
    }

});