// Global Data Storage
var teachersData = [];
var studentsData = [];

var itemsPerPage = 5;
var currentStudentPage = 1;
var currentTeacherPage = 1;

// Load teachers by default
loadUsers("teachers");
document.getElementById("searchInput").addEventListener("input", applyFilters);
document.getElementById("departmentFilter").addEventListener("change", applyFilters);
document.getElementById("sectionOrDesignationFilter").addEventListener("change", applyFilters);
document.getElementById("semesterFilter").addEventListener("change", applyFilters);

// Tab Switching Logic
document.getElementById("teachersTab").addEventListener("click", function () {
    document.getElementById("departmentFilter").style.display = "block";
    document.getElementById("sectionOrDesignationFilter").style.display = "block";
    document.getElementById("semesterFilter").style.display = "none"; // Hide semester for teachers

    document.getElementById("teachersContent").classList.add("active");
    document.getElementById("studentsContent").classList.remove("active");

    this.classList.add("active");
    document.getElementById("studentsTab").classList.remove("active");

    document.getElementById("sectionOrDesignationFilter").options[0].text = "All Designations";

    currentTeacherPage = 1; // Reset pagination
    loadUsers("teachers");
});

document.getElementById("studentsTab").addEventListener("click", function () {
    document.getElementById("departmentFilter").style.display = "block";
    document.getElementById("sectionOrDesignationFilter").style.display = "block";
    document.getElementById("semesterFilter").style.display = "block"; // Show semester for students

    document.getElementById("studentsContent").classList.add("active");
    document.getElementById("teachersContent").classList.remove("active");

    this.classList.add("active");
    document.getElementById("teachersTab").classList.remove("active");

    document.getElementById("sectionOrDesignationFilter").options[0].text = "All Sections";

    currentStudentPage = 1; // Reset pagination
    loadUsers("students");
});

function setupFilters(userType) {
    const departmentFilter = document.getElementById("departmentFilter");
    const sectionOrDesignationFilter = document.getElementById("sectionOrDesignationFilter");
    const semesterFilter = document.getElementById("semesterFilter");

    const data = userType === "students" ? studentsData : teachersData;

    let departments = new Set();
    let sectionsOrDesignations = new Set();
    let semesters = new Set();

    data.forEach(user => {
        if (user.department) departments.add(user.department);
        if (userType === "students" && user.section) sectionsOrDesignations.add(user.section);
        if (userType === "teachers" && user.designation) sectionsOrDesignations.add(user.designation);
        if (userType === "students" && user.semester) semesters.add(user.semester);
    });

    // Clear previous options
    departmentFilter.innerHTML = `<option value="">All Departments</option>`;
    sectionOrDesignationFilter.innerHTML = `<option value="">${userType === "students" ? "All Sections" : "All Designations"}</option>`;

    if (userType === "students") {
        semesterFilter.innerHTML = `<option value="">All Semesters</option>`;
        semesterFilter.style.display = "block";
    } else {
        semesterFilter.style.display = "none";
    }

    // Populate filters
    departments.forEach(dept => {
        departmentFilter.innerHTML += `<option value="${dept}">${dept}</option>`;
    });

    sectionsOrDesignations.forEach(sec => {
        sectionOrDesignationFilter.innerHTML += `<option value="${sec}">${sec}</option>`;
    });

    if (userType === "students") {
        semesters.forEach(sem => {
            semesterFilter.innerHTML += `<option value="${sem}">${sem}</option>`;
        });
    }
}

function applyFilters() {

  const searchValue = document.getElementById("searchInput").value.toLowerCase();
  const departmentValue = document.getElementById("departmentFilter").value;
  const sectionOrDesignationValue = document.getElementById("sectionOrDesignationFilter").value;
  const semesterValue = document.getElementById("semesterFilter")?.value || "";

  const isStudentTabActive = document.getElementById("studentsTab").classList.contains("active");
  const allData = isStudentTabActive ? studentsData : teachersData;

  // 🔥 Apply filtering to the entire dataset, not just the current page
  const filteredData = allData.filter(user => {
    const matchesSearch =
    user.id.toString().includes(searchValue) ||
    user.name.toLowerCase().includes(searchValue) ||
    (user.id && user.id.toLowerCase().includes(searchValue)); // 🔥 Add this line


      const matchesDepartment = !departmentValue || user.department === departmentValue;
      const matchesSectionOrDesignation = !sectionOrDesignationValue ||
          (isStudentTabActive ? user.section === sectionOrDesignationValue : user.designation === sectionOrDesignationValue);
      const matchesSemester = isStudentTabActive ? (!semesterValue || user.semester.toString() === semesterValue) : true;

      return matchesSearch && matchesDepartment && matchesSectionOrDesignation && matchesSemester;
  });

  // Reset pagination after filtering
  if (isStudentTabActive) {
      currentStudentPage = 1;
  } else {
      currentTeacherPage = 1;
  }

  // 🔥 Instead of calling renderTable directly, pass filtered data to paginateTable
  paginateTable(isStudentTabActive ? "students" : "teachers", filteredData);
}




function paginateTable(userType, filteredData = null) {
  const allData = userType === "students" ? studentsData : teachersData;
  const data = filteredData || allData; // Use filtered data if available
  const currentPage = userType === "students" ? currentStudentPage : currentTeacherPage;
  const totalPages = Math.ceil(data.length / itemsPerPage);

  // 🔥 Ensure pagination buttons are updated correctly
  updatePaginationButtons(userType, totalPages);

  // Clear table before inserting paginated rows
  const tableBody = document.getElementById(userType === "students" ? "studentsTableBody" : "teachersTableBody");
  tableBody.innerHTML = "";

  // Display only the items for the current page
  data.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage).forEach(user => {
      let row = `<tr id="${userType}-${user.id}">
          <td>${user.id}</td>
          <td>${user.name}</td>
          <td>${user.department}</td>
          <td>${user.section || user.designation}</td>
          ${userType === "students" ? `<td>${user.semester}</td>` : ""}
          <td>
              <button class="edit" data-id="${user.id}" data-role="${userType}">Edit</button>
              <button class="delete" data-id="${user.id}" data-role="${userType}">Remove</button>
          </td>
      </tr>`;
      tableBody.innerHTML += row;
  });
}



function updatePaginationButtons(userType, totalPages) {
  const paginationContainer = document.getElementById(userType === "students" ? "studentsPaginationContainer" : "teachersPaginationContainer");
  let currentPage = userType === "students" ? currentStudentPage : currentTeacherPage;

  // Ensure pagination resets if the new total pages are less than the current page
  if (currentPage > totalPages) {
      currentPage = totalPages > 0 ? totalPages : 1;
      if (userType === "students") currentStudentPage = currentPage;
      else currentTeacherPage = currentPage;
  }

  paginationContainer.innerHTML = `
      <button id="${userType}PrevPage" ${currentPage <= 1 ? "disabled" : ""}>Previous</button>
      <span>Page ${currentPage} of ${totalPages || 1}</span>
      <button id="${userType}NextPage" ${currentPage >= totalPages ? "disabled" : ""}>Next</button>
  `;

  document.getElementById(`${userType}PrevPage`).addEventListener("click", () => {
      if (userType === "students") currentStudentPage--;
      else currentTeacherPage--;
      paginateTable(userType);
  });

  document.getElementById(`${userType}NextPage`).addEventListener("click", () => {
      if (userType === "students") currentStudentPage++;
      else currentTeacherPage++;
      paginateTable(userType);
  });
}



function loadUsers(userType) {
    let url = userType === "teachers" ? "/administrator/get_teachers/" : "/administrator/get_students/";

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (userType === "teachers") {
                teachersData = data.users;
            } else {
                studentsData = data.users;
            }
            
            renderTable(userType, data.users);
            
            setupFilters(userType);
            applyFilters();
        });
}

function renderTable(userType, data) {
    const tableBody = document.getElementById(userType === "teachers" ? "teachersTableBody" : "studentsTableBody");
    tableBody.innerHTML = "";  

    data.forEach(user => {
        if (!user.id) {
            console.warn("Skipping user with missing ID:", user);
            return; // Skip users with no ID
        }

        let row = `<tr id="${userType}-${user.id}">
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.department}</td>
            <td>${user.section || user.designation}</td>
            ${userType === "students" ? `<td>${user.semester}</td>` : ""}
            <td>
                <button class="edit" data-id="${user.id}" data-role="${userType}">Edit</button>
                <button class="delete" data-id="${user.id}" data-role="${userType}">Remove</button>
            </td>
        </tr>`;

        tableBody.insertAdjacentHTML("beforeend", row);
    });

    paginateTable(userType);

}


document.addEventListener("click", function (event) {
  if (event.target.classList.contains("edit")) {
      let userId = event.target.getAttribute("data-id");
      let userRole = event.target.getAttribute("data-role");

      if (!userId || !userRole) {
          console.error("User ID or role is missing!");
          return;
      }

      fetch(`/administrator/get-user/${userRole}/${userId}`)
          .then(response => response.json())
          .then(data => {
              console.log("Fetched User Data:", data); // Debugging Output

              // Populate modal fields
              document.getElementById("editUserId").value = data.id;
              document.getElementById("editName").value = data.name;
              document.getElementById("editEmail").value = data.email;
              document.getElementById("editDepartment").value = data.department;
              document.getElementById("editRole").value = userRole;

              // Fill additional details
              document.getElementById("editMobile").value = data.mobile || "";
              document.getElementById("editAddress").value = data.address || "";
              document.getElementById("editCity").value = data.city || "";
              document.getElementById("editState").value = data.state || "";
              document.getElementById("editCountry").value = data.country || "";
              document.getElementById("editPincode").value = data.pincode || "";

              // If student, show semester and section
              if (data.semester) {
                document.getElementById("studentFields").style.display = "flex";
                  document.getElementById("editSemester").value = data.semester || "";
                  document.getElementById("editSection").value = data.section || "";
              }

              // Display the modal
              document.getElementById("editModal").style.display = "flex";
          })
          .catch(error => {
              console.error("Error fetching user data:", error);
              alert("Failed to fetch user data!");
          });
  }
});
document.addEventListener("click", function (event) {
  if (event.target.classList.contains("delete")) {
    let userId = event.target.getAttribute("data-id");
    let userRole = event.target.getAttribute("data-role");

    if (confirm("Are you sure you want to delete this user permanently?")) {
        fetch(`/administrator/delete-user/${userRole}/${userId}/`, {
            method: "DELETE"
        })
        .then(response => response.json())
        .then(data => {
            let deleteMsg = document.getElementById("deleteMessage");

            if (data.status === "success") {
                deleteMsg.classList.remove("hidden");
                deleteMsg.style.display = "block";

                setTimeout(() => {
                    deleteMsg.style.display = "none";
                    location.reload();
                }, 2000);
            } else {
                alert("❌ " + (data.message || "Failed to delete user."));
            }
        })
        .catch(error => {
            console.error("Error deleting user:", error);
            alert("❌ Error deleting user. Please try again!");
        });
    }
}
});

// Handle modal close
document.querySelectorAll(".close").forEach(button => {
  button.addEventListener("click", function () {
      document.getElementById("editModal").style.display = "none";
  });
});

// Handle form submission for updating user
document.getElementById("editForm").addEventListener("submit", function (event) {
    event.preventDefault();

    let userId = document.getElementById("editUserId").value;
    let userRole = document.getElementById("editRole").value;
    let formData = new FormData(this);

    fetch(`/administrator/update-user/${userRole}/${userId}/`, {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let successMsg = document.getElementById("successMessage");
        let errorMsg = document.getElementById("errorMessage");

        if (data.status === "success") {
            successMsg.classList.remove("hidden");
            successMsg.style.display = "block";

            setTimeout(() => {
                successMsg.style.display = "none";
                document.getElementById("editModal").style.display = "none";
                location.reload();
            }, 2000);
        } else {
            errorMsg.classList.remove("hidden");
            errorMsg.textContent = "❌ " + (data.message || "Failed to update user.");
            errorMsg.style.display = "block";

            setTimeout(() => {
                errorMsg.style.display = "none";
            }, 3000);
        }
    })
    .catch(error => {
        console.error("Error updating user:", error);
        let errorMsg = document.getElementById("errorMessage");
        errorMsg.textContent = "❌ Error updating user. Please try again!";
        errorMsg.classList.remove("hidden");
        errorMsg.style.display = "block";

        setTimeout(() => {
            errorMsg.style.display = "none";
        }, 3000);
    });
});




// // Handle Delete button click
// document.querySelectorAll(".delete").forEach(button => {
//     button.addEventListener("click", function () {
//         console.log("Clicked")
        
//     });
// });
