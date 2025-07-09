var tabButtons = document.querySelectorAll(".lecturer-profile-tab-button");
  var tabContents = document.querySelectorAll(".lecturer-profile-tab-content");

  tabButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var tab = this.getAttribute("data-tab");

      tabButtons.forEach(function (b) {
        b.classList.remove("active");
      });
      tabContents.forEach(function (c) {
        c.classList.remove("active");
      });

      this.classList.add("active");
      document.querySelector('[data-content="' + tab + '"]').classList.add("active");
    });
  });
  

