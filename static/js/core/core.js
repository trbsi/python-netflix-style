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

