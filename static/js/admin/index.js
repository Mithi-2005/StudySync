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

  function resetInitializationFlags() {
      console.log("🔄 Resetting initialization flags...");
      window.assessmentsInitialized = false;
      window.scheduleInitialized = false;
      window.someOtherPageInitialized = false;
  }

  function loadScripts(page) {
      console.log(`🔄 Loading script for: ${page}`);
      resetInitializationFlags();

      const oldScript = document.getElementById("dynamic-script");
      if (oldScript) {
          oldScript.remove();
          console.log("✅ Old script removed");
      }

      const newScript = document.createElement("script");
      newScript.id = "dynamic-script";
      newScript.src = `/static/js/admin/${page}.js`; // Ensure correct path
      newScript.defer = true;

      newScript.onload = function () {
          console.log(`✅ Script Loaded: ${newScript.src}`);
      };

      newScript.onerror = function () {
          console.error(`❌ Error Loading Script: ${newScript.src}`);
      };

      document.body.appendChild(newScript);
  }

  // ✅ Detect Current Page and Load Script
  console.log(`🌍 Current Path: ${window.location.pathname}`);
  
  // Extract the page name from the URL
  let currentPage = window.location.pathname.replace("/administrator/", "").replace(/\//g, "").trim();

  // Default to "dashboard" if currentPage is empty or "/"
  if (!currentPage) {
      currentPage = "dashboard";
  }

  console.log(`🔄 Current Page: ${currentPage}`); // Log currentPage for debugging
  loadScripts(currentPage); // This ensures the correct script is loaded even on direct access

  menuItems.forEach((item) => {
      item.addEventListener("click", function () {
          const page = this.getAttribute("data-page");

          fetch(`/administrator/${page}/`)
              .then((response) => response.text())
              .then((html) => {
                  const parser = new DOMParser();
                  const doc = parser.parseFromString(html, "text/html");
                  const newContent = doc.querySelector(".content").innerHTML;

                  contentArea.innerHTML = newContent;
                  console.log(`/admin/${page}`);

                  loadScripts(page);

                  window.history.pushState({}, "", `/administrator/${page}/`);

                  if (window.innerWidth <= 768) {
                      sidebar.classList.remove("open");
                      menuIcon.classList.remove("fa-xmark");
                      menuIcon.classList.add("fa-bars");
                  }
              })
              .catch((error) => console.error("Error loading page:", error));
      });
  });
//   $(document).ready(function () {
//     $(".admin-select").select2();
//   });
});
