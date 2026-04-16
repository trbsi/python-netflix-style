function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

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

