
// =====================================
// ASSET MANAGEMENT SYSTEM
// DASHBOARD INTERACTIONS
// =====================================

document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // SIDEBAR COLLAPSE AND EXPAND
    // =====================================

    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", function () {

            if (window.innerWidth <= 768) {
                sidebar.classList.toggle("show");
            } else {
                sidebar.classList.toggle("collapsed");
            }

        });
    }

    // Close mobile sidebar when a menu link is selected
    const menuLinks = document.querySelectorAll(".menu-link");

    menuLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.innerWidth <= 768 && sidebar) {
                sidebar.classList.remove("show");
            }
        });
    });

    // =====================================
    // HIGHLIGHT ACTIVE MENU ITEM
    // =====================================

    const currentPath = window.location.pathname;

    menuLinks.forEach(function (link) {
        const linkPath = new URL(link.href, window.location.origin).pathname;

        if (linkPath === currentPath) {
            link.classList.add("active");
        }
    });

});
