function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            const [key, value] = cookie.trim().split('=');
            if (key === name) cookieValue = decodeURIComponent(value);
        });
    }
    return cookieValue;
}

/* ------------- 18+ POPUP -----------*/
$(document).ready(function () {
    if (localStorage.getItem("peachka18") !== "true") {
        var ageModal = new bootstrap.Modal(document.getElementById('ageModal'));
        ageModal.show();
    }

    $("#enterSite").click(function () {
        localStorage.setItem("peachka18", "true");
        $("#ageModal").modal("hide");
    });

    $("#leaveSite").click(function () {
        window.location.href = "https://google.com";
    });
});

/* ------------ SET LANGUAGE -------------- */

// doing it via JS because frontpage is cached and csrf token is also cached
function setLanguage(lang) {
    fetch('/i18n/setlang/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `language=${lang}&next=${window.location.pathname}`
    }).then(() => location.reload());
}

/* ----------- PAGINATION ------------ */
$(document).ready(function () {
    function goToPage() {
        let pageNumber = $("#pageInput").val().trim();
        let maxPage = parseInt($("#pageInput").attr("max")) || 1;
        let minPage = parseInt($("#pageInput").attr("min")) || 1;

        if (!pageNumber) return;

        pageNumber = Math.max(
            minPage,
            Math.min(maxPage, parseInt(pageNumber, 10))
        );

        window.location.search = "?page=" + pageNumber;
    }

    // Enter key
    $("#pageInput").on("keypress", function (e) {
        if (e.which === 13) {
            e.preventDefault();
            goToPage();
        }
    });

    // Blur
    $("#pageInput").on("blur", function () {
        goToPage();
    });

});

/* ---------- Yandex.Metrika counter ---------- */
// https://metrika.yandex.ru
(function(m,e,t,r,i,k,a){
    m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
    m[i].l=1*new Date();
    for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
    k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=108760122', 'ym');

ym(108760122, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
