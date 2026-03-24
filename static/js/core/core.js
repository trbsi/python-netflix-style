function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// 18+ popup
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

// thumbnail effect variant
(function () {
  let variant = localStorage.getItem("ab_variant");

  if (!variant) {
    variant = Math.random() < 0.5 ? "A" : "B";
    localStorage.setItem("ab_variant", variant);
  }

  document.documentElement.setAttribute("data-variant", variant);
})();
