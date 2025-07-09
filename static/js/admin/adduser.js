
// Toggle between Student and Lecturer forms
var studentBtn = document.getElementById("student-btn");
var lecturerBtn = document.getElementById("lecturer-btn");
var studentForm = document.getElementById("student-form");
var lecturerForm = document.getElementById("lecturer-form");

studentBtn.addEventListener("click", function() {
  studentForm.style.display = "block";
  lecturerForm.style.display = "none";
  studentBtn.classList.add("active");
  lecturerBtn.classList.remove("active");
});

lecturerBtn.addEventListener("click", function() {
  studentForm.style.display = "none";
  lecturerForm.style.display = "block";
  lecturerBtn.classList.add("active");
  studentBtn.classList.remove("active");
});

document.addEventListener("DOMContentLoaded", function () {
  handleHashChange(); // Call function on page load

  // Listen for hash changes (in case user navigates manually)
  window.addEventListener("hashchange", handleHashChange);
});

function handleHashChange() {
  const hash = window.location.hash;

  if (hash === "#lecturer-form") {
    lecturerBtn.addEventListener("click");
  } else {
    studentBtn.addEventListener("click"); // Default form
  }
}

function fetchRegNo() {
  fetch("/administrator/get_reg_no/")
      .then(response => response.json())
      .then(data => {
          if (data.reg_no) {
              document.getElementById("student_reg_no").value = data.reg_no; // Fill input field
          }
      })
      .catch(error => console.error("Error fetching reg_no:", error));
}
fetchRegNo();
function fetchfacID() {
  fetch("/administrator/get_fac_id/")
      .then(response => response.json())
      .then(data => {
          if (data.faculty_id) {
              document.getElementById("lecturer_faculty_id").value = data.faculty_id; // Fill input field
          }
      })
      .catch(error => console.error("Error fetching reg_no:", error));
}
fetchfacID();
function generatePassword(length = 10) {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+";
  let password = "";
  for (let i = 0; i < length; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  document.getElementById("student_password").value = password; // Auto-fill input
  document.getElementById("lecturer_password").value = password; // Auto-fill input
}
generatePassword()
function loadDepartments() {
  fetch("/administrator/get-departments/")
      .then(response => response.json())
      .then(data => {
          let deptDropdown = document.getElementsByName("department");
          deptDropdown[0].innerHTML = '<option value="" selected disabled>Select Department</option>';
          deptDropdown[1].innerHTML = '<option value="" selected disabled>Select Department</option>';
          
          if (Array.isArray(data.departments)) {
              data.departments.forEach(dept => {
                  deptDropdown[0].innerHTML += `<option value="${dept.code}">${dept.code}</option>`;
                  deptDropdown[1].innerHTML += `<option value="${dept.code}">${dept.code}</option>`;
              });
          }
      })
      .catch(error => console.error("Error loading departments:", error));
}
loadDepartments()
function showTeacherForm() {
  studentForm.style.display = "none";
  lecturerForm.style.display = "block";
  lecturerBtn.classList.add("active");
  studentBtn.classList.remove("active");
}

// Function to show student form
function showStudentForm() {
  studentForm.style.display = "block";
  lecturerForm.style.display = "none";
  studentBtn.classList.add("active");
  lecturerBtn.classList.remove("active");
}

// Load country data using REST Countries v2 API
function loadCountryData() {
  fetch("https://restcountries.com/v2/all")
    .then(function(response) {
      return response.json();
    })
    .then(function(countries) {
      countries.sort(function(a, b) {
        return a.name.localeCompare(b.name);
      });
      
      var countryCodeOptions = [];
      var countryOptions = [];
      
      countries.forEach(function(country) {
        var countryName = country.name;
        var dialCode = "";
        if (country.callingCodes && country.callingCodes.length > 0 && country.callingCodes[0] !== "") {
          dialCode = country.callingCodes[0];
        }
        if (dialCode) {
          countryCodeOptions.push({
            value: dialCode,
            label: countryName + " (+" + dialCode + ")"
          });
        }
        countryOptions.push({
          value: countryName,
          label: countryName
        });
      });
      
      countryCodeOptions.sort(function(a, b) {
        return a.label.localeCompare(b.label);
      });
      countryOptions.sort(function(a, b) {
        return a.label.localeCompare(b.label);
      });
      
      // Populate mobile code dropdowns for Student and Lecturer
      populateDropdown("student_mobile_code", countryCodeOptions, "Select Code");
      populateDropdown("lecturer_mobile_code", countryCodeOptions, "Select Code");
      // Populate country dropdowns for Student and Lecturer
      populateDropdown("student_country", countryOptions, "Select Country");
      populateDropdown("lecturer_country", countryOptions, "Select Country");
      
      // Set default selections to India (for country dropdown) and dial code "91" (for mobile code)
      var studentCountrySelect = document.getElementById("student_country");
      var lecturerCountrySelect = document.getElementById("lecturer_country");
      var studentMobileCodeSelect = document.getElementById("student_mobile_code");
      var lecturerMobileCodeSelect = document.getElementById("lecturer_mobile_code");
      
      if(studentCountrySelect) {
        studentCountrySelect.value = "India";
      }
      if(lecturerCountrySelect) {
        lecturerCountrySelect.value = "India";
      }
      if(studentMobileCodeSelect) {
        studentMobileCodeSelect.value = "91";
      }
      if(lecturerMobileCodeSelect) {
        lecturerMobileCodeSelect.value = "91";
      }
      
      // After setting defaults, load the states for India in both forms
      var studentStateSelect = document.getElementById("student_state");
      var lecturerStateSelect = document.getElementById("lecturer_state");
      if(studentCountrySelect.value && studentStateSelect) {
        loadStates(studentCountrySelect.value, studentStateSelect);
      }
      if(lecturerCountrySelect.value && lecturerStateSelect) {
        loadStates(lecturerCountrySelect.value, lecturerStateSelect);
      }
    })
    .catch(function(error) {
      console.error("Error loading country data:", error);
    });
}
loadCountryData();

// Populate a dropdown with plain HTML options
function populateDropdown(selectId, optionsArray, defaultLabel) {
  var selectElem = document.getElementById(selectId);
  if (!selectElem) return;
  selectElem.innerHTML = "";
  var defaultOpt = document.createElement("option");
  defaultOpt.value = "";
  defaultOpt.textContent = defaultLabel;
  selectElem.appendChild(defaultOpt);
  optionsArray.forEach(function(optObj) {
    var opt = document.createElement("option");
    opt.value = optObj.value;
    opt.textContent = optObj.label;
    selectElem.appendChild(opt);
  });
}

// Function to load states using the CountriesNow API
function loadStates(countryName, stateSelectElement) {
  stateSelectElement.innerHTML = "";
  var defaultOpt = document.createElement("option");
  defaultOpt.value = "";
  defaultOpt.textContent = "Select State";
  stateSelectElement.appendChild(defaultOpt);
  
  fetch("https://countriesnow.space/api/v0.1/countries/states", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ country: countryName })
  })
    .then(function(response) {
      return response.json();
    })
    .then(function(result) {
      if (result.data && result.data.states && result.data.states.length) {
        var states = result.data.states.sort(function(a, b) {
          return a.name.localeCompare(b.name);
        });
        states.forEach(function(stateObj) {
          var opt = document.createElement("option");
          opt.value = stateObj.name;
          opt.textContent = stateObj.name;
          stateSelectElement.appendChild(opt);
        });
      }
    })
    .catch(function(error) {
      console.error("Error loading states:", error);
    });
}

// Function to load cities using the CountriesNow API
function loadCities(countryName, stateName, citySelectElement) {
  citySelectElement.innerHTML = "";
  var defaultOpt = document.createElement("option");
  defaultOpt.value = "";
  defaultOpt.textContent = "Select City";
  citySelectElement.appendChild(defaultOpt);
  
  fetch("https://countriesnow.space/api/v0.1/countries/state/cities", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ country: countryName, state: stateName })
  })
    .then(function(response) {
      return response.json();
    })
    .then(function(result) {
      if (result.data && result.data.length) {
        var cities = result.data.sort(function(a, b) {
          return a.localeCompare(b);
        });
        cities.forEach(function(city) {
          var opt = document.createElement("option");
          opt.value = city;
          opt.textContent = city;
          citySelectElement.appendChild(opt);
        });
      }
    })
    .catch(function(error) {
      console.error("Error loading cities:", error);
    });
}

// Setup event listeners for country and state changes for both Student and Lecturer forms
["student", "lecturer"].forEach(function(role) {
  var countrySelect = document.getElementById(role + "_country");
  var stateSelect = document.getElementById(role + "_state");
  var citySelect = document.getElementById(role + "_city");
  
  if (countrySelect && stateSelect && citySelect) {
    countrySelect.addEventListener("change", function() {
      var selectedCountry = countrySelect.value;
      if (selectedCountry) {
        loadStates(selectedCountry, stateSelect);
        citySelect.innerHTML = "";
        var defaultCity = document.createElement("option");
        defaultCity.value = "";
        defaultCity.textContent = "Select City";
        citySelect.appendChild(defaultCity);
      } else {
        stateSelect.innerHTML = "";
        var defaultState = document.createElement("option");
        defaultState.value = "";
        defaultState.textContent = "Select State";
        stateSelect.appendChild(defaultState);
        citySelect.innerHTML = "";
        var defaultCity = document.createElement("option");
        defaultCity.value = "";
        defaultCity.textContent = "Select City";
        citySelect.appendChild(defaultCity);
      }
    });
    
    stateSelect.addEventListener("change", function() {
      var selectedCountry = countrySelect.value;
      var selectedState = stateSelect.value;
      if (selectedCountry && selectedState) {
        loadCities(selectedCountry, selectedState, citySelect);
      } else {
        citySelect.innerHTML = "";
        var defaultCity = document.createElement("option");
        defaultCity.value = "";
        defaultCity.textContent = "Select City";
        citySelect.appendChild(defaultCity);
      }
    });
  }
});
