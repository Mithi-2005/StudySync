function getCSRFToken() {
  return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
}



// Load Departments
function loadDepartments() {
  fetch("/administrator/get-departments/")
      .then(response => response.json())
      .then(data => {
          let deptDropdown = document.getElementById("enroll-department");
          deptDropdown.innerHTML = '<option value="" selected disabled>Select Department</option>';
          
          if (Array.isArray(data.departments)) {
              deptDropdown.innerHTML += data.departments.map(dept =>
                  `<option value="${dept.code}">${dept.code}</option>`
              ).join("");
          }
      })
      .catch(error => console.error("Error loading departments:", error));
}

// Load Semesters Based on Department
function loadSemesters() {
  let department = document.getElementById("enroll-department").value;
  let semDropdown = document.getElementById("enroll-semester");
  
  // Reset dependent dropdowns
  document.getElementById("enroll-section").innerHTML = '<option value="" selected disabled>Select Section</option>';
  document.getElementById("enroll-course").innerHTML = '<option value="" selected disabled>Select Course</option>';
  
  if (!department) return;

  fetch(`/administrator/get-semesters/?department=${department}`)
      .then(response => response.json())
      .then(data => {
          semDropdown.innerHTML = '<option value="" selected disabled>Select Semester</option>' +
              data.semesters.map(sem => `<option value="${sem}">${sem}</option>`).join("");
      })
      .catch(error => console.error("Error loading semesters:", error));
}

// Load Sections Based on Semester
function loadSections() {
  let department = document.getElementById("enroll-department").value;
  let semester = document.getElementById("enroll-semester").value;
  let secDropdown = document.getElementById("enroll-section");
  
  // Reset courses dropdown
  document.getElementById("enroll-course").innerHTML = '<option value="" selected disabled>Select Course</option>';
  
  if (!department || !semester) return;

  fetch(`/administrator/get-sections/?department=${department}&semester=${semester}`)
      .then(response => response.json())
      .then(data => {
          secDropdown.innerHTML = '<option value="" selected disabled>Select Section</option>' +
              data.sections.map(sec => `<option value="${sec}">${sec}</option>`).join("");
      })
      .catch(error => console.error("Error loading sections:", error));
}

// Load Courses Based on Department, Semester & Section
function loadCourses() {
  let department = document.getElementById("enroll-department").value;
  let semester = document.getElementById("enroll-semester").value;
  let section = document.getElementById("enroll-section").value;
  let subjectDropdown = $("#enroll-course"); // jQuery selector for Bootstrap Select

  if (!department || !semester || !section) return;

  fetch(`/administrator/get-courses/?department=${department}&semester=${semester}&section=${section}`)
      .then(response => response.json())
      .then(data => {
          subjectDropdown.empty(); // Clear existing options
          subjectDropdown.append('<option value="" selected disabled>Select Course</option>');

          data.courses.forEach(course => {
              subjectDropdown.append(`<option value="${course.course_code}">${course.course_code} - ${course.course_name}</option>`);
          });

          subjectDropdown.selectpicker("refresh"); // 🔥 Important: Refresh Bootstrap Select
      })
      .catch(error => console.error("Error loading courses:", error));
}
function enrollStudents() {
  var department = document.getElementById('enroll-department').value;
  var semester = document.getElementById('enroll-semester').value;
  var section = document.getElementById('enroll-section').value;
  var course_code = document.getElementById('enroll-course').value;

  if (!department || !semester || !section || !course_code) {
      showMessage("Please select all fields before enrolling students.", "error");
      return;
  }

  fetch("/administrator/enroll-students/", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ department, semester, section, course_code }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === "success") {
      showSuccessMessage(data.message);
  } else {
      showErrorMessage(data.message);
  }
  })
  .catch(error => {
      console.error("Error enrolling students:", error);
      showMessage("Error enrolling students.", "error");
  });
}

function showSuccessMessage(message) {
  let messageBox = document.getElementById("message-box");
  messageBox.innerHTML = `<div class="success-message">${message}</div>`;
  messageBox.style.display = "block";

  setTimeout(() => {
      messageBox.style.display = "none";
  }, 3000);  // Hide after 3 seconds
}

function showErrorMessage(message) {
  let messageBox = document.getElementById("message-box");
  messageBox.innerHTML = `<div class="error-message">${message}</div>`;
  messageBox.style.display = "block";

  setTimeout(() => {
      messageBox.style.display = "none";
  }, 3000);  // Hide after 3 seconds
}



loadDepartments(); // Load departments on page load