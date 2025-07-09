const presentCount = document.getElementById('present-count');
const absentCount = document.getElementById('absent-count');
const totalCount = document.getElementById('total-count');

function updateSummary() {
  const students = document.querySelectorAll('.student');
  let present = 0;
  let absent = 0;

  students.forEach(student => {
    if (student.classList.contains('present')) {
      present++;
    } else if (student.classList.contains('absent')) {
      absent++;
    }
  });

  presentCount.textContent = present;
  absentCount.textContent = absent;
  totalCount.textContent = students.length;
}

function setDefaultStatus(status) {
  var students = document.querySelectorAll('.student');

  students.forEach(student => {
    const statusCell = student.querySelector('.status');
    student.classList.remove('present', 'absent');

    if (status === 'P') {
      student.classList.add('present');
      statusCell.textContent = 'P';
    } else {
      student.classList.add('absent');
      statusCell.textContent = 'A';
    }
  });

  updateSummary();
}

// This function is triggered directly from HTML onchange
function handleDefaultStatusChange(value) {
  setDefaultStatus(value);
}

// Attach row click handlers
function bindRowClickEvents() {
  const students = document.querySelectorAll('.student');

  students.forEach(student => {
    student.onclick = function () {
      const statusCell = student.querySelector('.status');

      if (student.classList.contains('present')) {
        student.classList.remove('present');
        student.classList.add('absent');
        statusCell.textContent = 'A';
      } else {
        student.classList.remove('absent');
        student.classList.add('present');
        statusCell.textContent = 'P';
      }

      updateSummary();
    };
  });
}

function submitAttendance() {
  const students = [];
  document.querySelectorAll(".student").forEach(row => {
      const reg_no = row.children[1].textContent.trim();
      const status = row.querySelector(".status").textContent.trim();
      students.push({ reg_no, status });
  });

  // Get data from the hidden div
  const meta = document.getElementById("attendance-data");
  const data = {
      code: meta.dataset.code,
      section: meta.dataset.section,
      semester: meta.dataset.semester,
      date: meta.dataset.date,
      type: meta.dataset.type,
      students: students
  };

  fetch("/teacher/save_attendance/", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(response => {
      alert(response.message || "Attendance saved successfully!");
  })
  .catch(error => {
      alert("Error saving attendance");
      console.error(error);
  });
}


// Initialize
// setDefaultStatus('present');
bindRowClickEvents();
updateSummary();
