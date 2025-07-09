document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.querySelector(".sidebar");
  const menuToggle = document.querySelector(".menu-toggle");
  const menuIcon = menuToggle.querySelector("i");
  const contentArea = document.querySelector(".content");
  const menuItems = document.querySelectorAll(".menu-item");

  $(document).ready(function () {
    $('.fa-bell').on('click', function () {
      $('.notification-panel').toggleClass('hidden');
    });
  
    // Optional: Hide notification panel when clicking outside
    $(document).on('click', function (e) {
      if (!$(e.target).closest('.notification-panel, .fa-bell').length) {
        $('.notification-panel').addClass('hidden');
      }
    });
  });
  
  if (menuToggle) {
    menuToggle.addEventListener("click", () => {
      sidebar.classList.toggle("open");
      menuIcon.classList.toggle("fa-bars");
      menuIcon.classList.toggle("fa-xmark");
    });
  }

  function loadScripts(page) {
    const oldScript = document.getElementById("dynamic-script");
    if (oldScript) {
      oldScript.remove();
      console.log("✅ Old script removed");
    }
    const newScript = document.createElement("script");
    newScript.id = "dynamic-script";
    newScript.src = `/static/js/student/${page}.js`;
    newScript.defer = true;
    newScript.onload = function () {
      console.log(`✅ Script Loaded: ${newScript.src}`);
    };
    newScript.onerror = function () {
      console.error(`❌ Error Loading Script: ${newScript.src}`);
    };
    document.body.appendChild(newScript);
  }

  let currentPage = window.location.pathname
    .replace("/administrator/", "")
    .replace(/\//g, "")
    .trim();
    
  if (!currentPage) {
    currentPage = "dashboard";
  }
  loadScripts(currentPage);

  menuItems.forEach((item) => {
    item.addEventListener("click", function () {
      const page = this.getAttribute("data-page");

      fetch(`/${page}/`)
        .then((response) => response.text())
        .then((html) => {
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, "text/html");
          const newContent = doc.querySelector(".content").innerHTML;

          contentArea.innerHTML = newContent;

          loadScripts(page);
          setTimeout(() => {
            if (typeof initializeAssessments === "function") {
              initializeAssessments();
            }
          }, 100);
          window.history.pushState({}, "", `/${page}/`);

          if (window.innerWidth <= 768) {
            sidebar.classList.remove("open");
            menuIcon.classList.remove("fa-xmark");
            menuIcon.classList.add("fa-bars");
          }
        })
        .catch((error) => console.error("Error loading page:", error));
    });
  });

  // ===== Insert the Profile Icon Listener Below =====
  const profileIcon = document.querySelector(".fa-circle-user");

  if (profileIcon) {
    profileIcon.addEventListener("click", function () {
      fetch(`/profile/`)
        .then((response) => response.text())
        .then((html) => {
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, "text/html");
          const newContent = doc.querySelector(".content").innerHTML;

          document.querySelector(".content").innerHTML = newContent;

          loadScripts("profile");

          window.history.pushState({}, "", `/profile/`);
        })
        .catch((error) => console.error("Error loading profile page:", error));
    });
  }
  // ===== End of Profile Icon Listener =====
});
