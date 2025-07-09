var tabs = document.querySelectorAll(".profile-tab-button");
  var contents = document.querySelectorAll(".profile-tab-content");

  for (var i = 0; i < tabs.length; i++) {
    tabs[i].addEventListener("click", function () {
      for (var j = 0; j < tabs.length; j++) {
        tabs[j].classList.remove("active");
      }
      for (var k = 0; k < contents.length; k++) {
        contents[k].classList.remove("active");
      }
      this.classList.add("active");
      document.getElementById(this.getAttribute("data-tab")).classList.add("active");
    });
  }