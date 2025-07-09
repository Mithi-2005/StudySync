// Function to Load Departments
function loadDepartments() {
    fetch("/administrator/get-departments/")
        .then(response => response.json())
        .then(data => {
            let deptDropdown = document.getElementById("department");
            deptDropdown.innerHTML = '<option value="" selected disabled>Select Department</option>';
            
            if (Array.isArray(data.departments)) {
                data.departments.forEach(dept => {
                    deptDropdown.innerHTML += `<option value="${dept.code}">${dept.code}</option>`;
                });
            }
        })
        .catch(error => console.error("Error loading departments:", error));
}

// Function to Fetch Semesters Based on Department
function loadSemesters() {
    let department = document.getElementById("department").value;
    if (!department) return;

    fetch(`/administrator/get-semesters/?department=${department}`)
        .then(response => response.json())
        .then(data => {
            let semDropdown = document.getElementById("semester");
            semDropdown.innerHTML = '<option value="">Select Semester</option>';
            data.semesters.forEach(sem => {
                semDropdown.innerHTML += `<option value="${sem}">${sem}</option>`;
            });
        })
        .catch(error => console.error("Error loading semesters:", error));
    }

// Function to Fetch Sections Based on Semester
function loadSections() {
    let department = document.getElementById("department").value;
    let semester = document.getElementById("semester").value;
    if (!department || !semester) return;

    fetch(`/administrator/get-sections/?department=${department}&semester=${semester}`)
        .then(response => response.json())
        .then(data => {
            let secDropdown = document.getElementById("section");
            secDropdown.innerHTML = '<option value="">Select Section</option>';
            data.sections.forEach(sec => {
                secDropdown.innerHTML += `<option value="${sec}">${sec}</option>`;
            });
        })
        .catch(error => console.error("Error loading sections:", error));
}

// Function to Load Timetable
function loadTimetable() {
    let department = document.getElementById("department").value;
    let semester = document.getElementById("semester").value;
    let section = document.getElementById("section").value;
    
    if (!department || !semester || !section) {
        alert("Please select all filters!");
        return;
    }

    fetch(`/administrator/get-timetable/?department=${department}&semester=${semester}&section=${section}`)
        .then(response => response.json())
        .then(data => {
            let tbody = document.getElementById("timetable-body");
            tbody.innerHTML = "";

            if (!data.timetable || data.timetable.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7">No timetable available</td></tr>`;
                return;
            }

            data.timetable.forEach(row => {
                tbody.innerHTML += `
                    <tr>
                        <td>${row.day}</td>
                        <td>${row.period}</td>
                        <td>${row.subject}</td>
                        <td>${row.faculty_id}</td>
                        <td>${row.room_no}</td>
                        <td>${row.time_slot}</td>
                        <td>
                            <button onclick="editSlot(${row.id})">Edit</button>
                            <button onclick="deleteSlot(${row.id})">Delete</button>
                        </td>
                    </tr>
                `;
            });
        })
        .catch(error => console.error("Error loading timetable:", error));
}

// Function to Load Courses (Subjects)
function loadCourses() {
    let subjectDropdown = document.getElementById("slot-subject");

    // Clear existing options before adding new ones
    subjectDropdown.innerHTML = '<option value="" selected disabled>Select Subject</option>';  

    fetch("/administrator/get-courses/")
        .then(response => response.json())
        .then(data => {
            data.courses.forEach(course => {
                subjectDropdown.innerHTML += `<option value="${course.course_code}">${course.course_code} - ${course.course_name}</option>`;
            });

            // Initialize or Reinitialize Select2 for search functionality
            if ($.fn.select2 && !$(subjectDropdown).hasClass("select2-hidden-accessible")) {
                $(subjectDropdown).select2({
                    placeholder: "Select a subject",
                    allowClear: true
                });
            }
        })
        .catch(error => console.error("Error loading courses:", error));
}

// Function to Load Faculty
function loadFaculty() {
    let facultyDropdown = document.getElementById("slot-faculty");

    // Clear existing options before adding new ones
    facultyDropdown.innerHTML = '<option value="" selected disabled>Select Faculty</option>';  

    fetch("/administrator/get-faculty/")
        .then(response => response.json())
        .then(data => {
            data.faculty.forEach(faculty => {
                facultyDropdown.innerHTML += `<option value="${faculty.faculty_id}">${faculty.faculty_id} - ${faculty.name}</option>`;
            });

            // Initialize or Reinitialize Select2 for search functionality
            if ($.fn.select2 && !$(facultyDropdown).hasClass("select2-hidden-accessible")) {
                $(facultyDropdown).select2({
                    placeholder: "Select a faculty",
                    allowClear: true
                });
            }
        })
        .catch(error => console.error("Error loading faculty:", error));
}

// Function to Open Popup for Adding Slot
function openAddSlotPopup() {
    document.getElementById("addSlotPopup").style.display = "block";

    // Load courses and faculty only once when opening the popup
    loadCourses();
    loadFaculty();
}

// Function to Close Popup
function closePopup() {
    document.getElementById("addSlotPopup").style.display = "none";
}

// Function to Get CSRF Token
function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}

// Function to Delete Slot
function deleteSlot(id) {
    if (!confirm("Are you sure you want to delete this slot?")) return;

    fetch(`/administrator/delete-timetable/${id}/`, { 
        method: "DELETE",
        headers: { 'X-CSRFToken': getCSRFToken() }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Slot deleted successfully!");
            loadTimetable();
        } else {
            alert("Error deleting slot!");
        }
    })
    .catch(error => console.error("Error deleting slot:", error));
}

// Function to Edit Slot
function editSlot(id) {
    fetch(`/administrator/edit-timetable/${id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            openAddSlotPopup();

            setTimeout(() => {
                document.getElementById("slot-id").value = id;
                document.getElementById("slot-day").value = data.day;
                document.getElementById("slot-period").value = data.period;
                document.getElementById("slot-subject").value = data.subject;
                document.getElementById("slot-faculty").value = data.faculty_id;
                document.getElementById("slot-room").value = data.room_no;
                document.getElementById("slot-time").value = data.time_slot;
                document.getElementById("save-slot-btn").innerText="Update"
                document.getElementById("save-slot-btn").setAttribute("onclickw",`updateSlot(${id})`)
            }, 100);
        })
        .catch(error => console.error("Error fetching slot data:", error));
}

// Function to Update Slot
function updateSlot(id) {
    let slotData = {
        id: id,
        department: document.getElementById("department").value,
        semester: document.getElementById("semester").value,
        section: document.getElementById("section").value,
        day: document.getElementById("slot-day").value,
        period: document.getElementById("slot-period").value,
        subject: document.getElementById("slot-subject").value,
        faculty_id: document.getElementById("slot-faculty").value,
        room_no: document.getElementById("slot-room").value,
        time_slot: document.getElementById("slot-time").value
    };

    fetch('/administrator/update-timetable/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(slotData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Slot updated successfully!");
            closePopup();
            loadTimetable();
        } else {
            alert("Error updating slot: " + data.error);
        }
    })
    .catch(error => console.error("Error updating slot:", error));
}
function addSlot() {
    let department = document.getElementById("department").value;
    let semester = document.getElementById("semester").value;
    let section = document.getElementById("section").value;
    let day = document.getElementById("slot-day").value;
    let period = document.getElementById("slot-period").value;
    let subject = document.getElementById("slot-subject").value;
    let faculty_id = document.getElementById("slot-faculty").value;
    let room_no = document.getElementById("slot-room").value;
    let time_slot = document.getElementById("slot-time").value;

    if (!department || !semester || !section || !day || !period || !subject || !faculty_id || !room_no || !time_slot) {
        alert("All fields are required!");
        return;
    }

    // Send the data to the backend
    fetch("/administrator/add-timetable/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            department,
            semester,
            section,
            day,
            period,
            subject,
            faculty_id,
            room_no,
            time_slot
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Slot added successfully!");
            closePopup();
            loadTimetable();
        } else {
            alert("Error adding slot!");
        }
    })
    .catch(error => console.error("Error adding slot:", error));
}
loadDepartments()