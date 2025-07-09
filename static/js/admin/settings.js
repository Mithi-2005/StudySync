
  // document.addEventListener("DOMContentLoaded", function () {
    var buttons = {
        "account-btn": "account-settings",
        "notifications-btn": "notification-settings",
        "about-btn": "about-settings",
      };
  
      // Get all buttons and containers
      var allButtons = document.querySelectorAll(".toggle-btn");
      var allSections = document.querySelectorAll(".form-container");
  
      // Add click events to buttons
      allButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
          // Remove 'active' class from all buttons
          allButtons.forEach(b => b.classList.remove("active"));
  
          // Hide all sections
          allSections.forEach(section => section.style.display = "none");
  
          // Activate clicked button
          btn.classList.add("active");
  
          // Show corresponding section
          const sectionId = buttons[btn.id];
          document.getElementById(sectionId).style.display = "block";
        });
      });
    // });
  
    document.getElementById('toggle-password').addEventListener('change', function () {
      const passwordField = document.getElementById('acc_password');
      passwordField.type = this.checked ? 'text' : 'password';
    });
  // Load country, dial code, and initialize defaults
  function loadCountryData() {
    fetch("https://restcountries.com/v2/all")
      .then(response => response.json())
      .then(countries => {
        countries.sort((a, b) => a.name.localeCompare(b.name));
  
        const countryCodeOptions = [];
        const countryOptions = [];
  
        countries.forEach(country => {
          const countryName = country.name;
          const dialCode = (country.callingCodes && country.callingCodes[0]) || "";
  
          if (dialCode) {
            countryCodeOptions.push({
              value: dialCode,
              label: `${countryName} (+${dialCode})`
            });
          }
  
          countryOptions.push({
            value: countryName,
            label: countryName
          });
        });
  
        countryCodeOptions.sort((a, b) => a.label.localeCompare(b.label));
        countryOptions.sort((a, b) => a.label.localeCompare(b.label));
  
        populateDropdown("acc_mobile_code", countryCodeOptions, "Select Code");
        populateDropdown("acc_country", countryOptions, "Select Country");
  
        // Set defaults to India
        const countrySelect = document.getElementById("acc_country");
        const mobileCodeSelect = document.getElementById("acc_mobile_code");
  
        if (countrySelect) countrySelect.value = "India";
        if (mobileCodeSelect) mobileCodeSelect.value = "91";
  
        const stateSelect = document.getElementById("acc_state");
        if (countrySelect && stateSelect) {
          loadStates(countrySelect.value, stateSelect);
        }
      })
      .catch(error => console.error("Error loading country data:", error));
  }
  
  // Populate dropdowns with given options
  function populateDropdown(selectId, optionsArray, defaultLabel) {
    const selectElem = document.getElementById(selectId);
    if (!selectElem) return;
  
    selectElem.innerHTML = "";
    const defaultOpt = document.createElement("option");
    defaultOpt.value = "";
    defaultOpt.textContent = defaultLabel;
    selectElem.appendChild(defaultOpt);
  
    optionsArray.forEach(optObj => {
      const opt = document.createElement("option");
      opt.value = optObj.value;
      opt.textContent = optObj.label;
      selectElem.appendChild(opt);
    });
  }
  
  // Load states based on selected country
  function loadStates(countryName, stateSelectElement) {
    stateSelectElement.innerHTML = "";
    const defaultOpt = document.createElement("option");
    defaultOpt.value = "";
    defaultOpt.textContent = "Select State";
    stateSelectElement.appendChild(defaultOpt);
  
    fetch("https://countriesnow.space/api/v0.1/countries/states", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ country: countryName })
    })
      .then(response => response.json())
      .then(result => {
        if (result.data?.states?.length) {
          result.data.states
            .sort((a, b) => a.name.localeCompare(b.name))
            .forEach(stateObj => {
              const opt = document.createElement("option");
              opt.value = stateObj.name;
              opt.textContent = stateObj.name;
              stateSelectElement.appendChild(opt);
            });
        }
      })
      .catch(error => console.error("Error loading states:", error));
  }
  
  // Load cities based on selected state
  function loadCities(countryName, stateName, citySelectElement) {
    citySelectElement.innerHTML = "";
    const defaultOpt = document.createElement("option");
    defaultOpt.value = "";
    defaultOpt.textContent = "Select City";
    citySelectElement.appendChild(defaultOpt);
  
    fetch("https://countriesnow.space/api/v0.1/countries/state/cities", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ country: countryName, state: stateName })
    })
      .then(response => response.json())
      .then(result => {
        if (result.data?.length) {
          result.data
            .sort((a, b) => a.localeCompare(b))
            .forEach(city => {
              const opt = document.createElement("option");
              opt.value = city;
              opt.textContent = city;
              citySelectElement.appendChild(opt);
            });
        }
      })
      .catch(error => console.error("Error loading cities:", error));
  }
  
  // Hook up change listeners for country and state
  (function setupLocationListeners() {
    const countrySelect = document.getElementById("acc_country");
    const stateSelect = document.getElementById("acc_state");
    const citySelect = document.getElementById("acc_city");
  
    if (countrySelect && stateSelect && citySelect) {
      countrySelect.addEventListener("change", () => {
        const country = countrySelect.value;
        if (country) {
          loadStates(country, stateSelect);
          citySelect.innerHTML = `<option value="">Select City</option>`;
        }
      });
  
      stateSelect.addEventListener("change", () => {
        const country = countrySelect.value;
        const state = stateSelect.value;
        if (country && state) {
          loadCities(country, state, citySelect);
        }
      });
    }
  })();
  