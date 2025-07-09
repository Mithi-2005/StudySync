async function initializeAssessments() {
    console.log("✅ Assessments Page Loaded");
    if (window.assessmentsInitialized) return;
    window.assessmentsInitialized = true;
  
    // Common Elements
    const tabs = {
      quizzes: {
        tab: document.getElementById("quizzesTab"),
        content: document.getElementById("quizzesContent"),
      },
      assignments: {
        tab: document.getElementById("assignmentsTab"),
        content: document.getElementById("assignmentsContent"),
      },
    };
  
    // Quiz System Elements
    const quizElements = {
      table: document.getElementById("quizTable")?.querySelector("tbody"),
      filter: document.getElementById("quizFilter"),
      modal: document.getElementById("createQuizModal"),
      createBtn: document.getElementById("showCreateQuiz"),
      closeBtn: document.getElementById("closeQuizModal"),
      typeCards: document.querySelectorAll(".quiz-type-card"),
      onlineOptions: document.querySelector(".offline-options"),
      quizForm: document.querySelector(".quiz-form"),
      saveBtn: document.getElementById("createQuizBtn"),
      titleInput: document.getElementById("quizTitle"),
      descInput: document.getElementById("quizDescription"),
      startInput: document.getElementById("quizStartDate"),
      dueInput: document.getElementById("quizDueDate"),
      questionsInput: document.getElementById("offlineQuizQuestions"),
    };
  
    // Assignment System Elements (Updated)
    const assignmentElements = {
      modal: document.getElementById("createAssignmentModal"),
      createBtn: document.getElementById("createAssignmentBtn"),
      saveBtn: document.getElementById("saveAssignmentChanges"), // Fixed reference
      closeBtn: document.getElementById("closeAssignmentModal"),
      table: document.querySelector("#assignmentTable tbody"),
      openBtn: document.getElementById("showCreateAssignment"),
      fileInput: document.getElementById("assignmentFile"),
      fileInfo: document.querySelector(".file-info"),
      titleInput: document.getElementById("assignmentTitle"),
      descInput: document.getElementById("assignmentDescription"),
      startInput: document.getElementById("assignmentStartDate"),
      dueInput: document.getElementById("assignmentDueDate"),
    };
  
    // State
    let quizList = [];
    let isEditingQuiz = false;
    let editingQuizIndex = null;
    let assignmentList = [];
    let isEditingAssignment = false;
    let editingAssignmentIndex = null;
    let currentQuizType = "online";
  
    // Tab Switching
    function switchToQuizzes() {
      tabs.quizzes.tab?.classList.add("active");
      tabs.assignments.tab?.classList.remove("active");
      tabs.quizzes.content?.classList.add("active");
      tabs.assignments.content?.classList.remove("active");
    }
  
    function switchToAssignments() {
      tabs.assignments.tab?.classList.add("active");
      tabs.quizzes.tab?.classList.remove("active");
      tabs.assignments.content?.classList.add("active");
      tabs.quizzes.content?.classList.remove("active");
    }
  
    tabs.quizzes.tab?.addEventListener("click", switchToQuizzes);
    tabs.assignments.tab?.addEventListener("click", switchToAssignments);
    
    // Quiz Modal Handling
    function handleQuizModal() {
      function openModal() {
        quizElements.modal.style.display = "block";
        resetQuizModal();
      }
  
      function closeModal() {
        quizElements.modal.style.display = "none";
        resetQuizModal();
      }
  
      quizElements.createBtn?.addEventListener("click", openModal);
      quizElements.closeBtn?.addEventListener("click", closeModal);
      window.addEventListener("click", (e) => {
        if (e.target === quizElements.modal) closeModal();
      });
    }
  
    // Quiz Type Cards Handling
    function handleQuizTypeCards() {
      quizElements.typeCards?.forEach((card) => {
        card.addEventListener("click", () => {
          quizElements.typeCards?.forEach((c) => c.classList.remove("active"));
          card.classList.add("active");
          currentQuizType = card.dataset.type;
          quizElements.onlineOptions.style.display =
            currentQuizType === "offline" ? "block" : "none";
        });
      });
    }
  
    // Quiz CRUD Operations
    function resetQuizModal() {
      quizElements.titleInput.value = "";
      quizElements.descInput.value = "";
      quizElements.startInput.value = "";
      quizElements.dueInput.value = "";
      quizElements.questionsInput.value = "";
      quizElements.saveBtn.textContent = "Create Quiz";
      isEditingQuiz = false;
      editingQuizIndex = null;
      currentQuizType = "online";
  
      quizElements.typeCards?.forEach((c) => c.classList.remove("active"));
      const onlineCard = document.querySelector('[data-type="online"]');
      onlineCard?.classList.add("active");
      quizElements.onlineOptions.style.display = "none";
    }
  
    function getQuizStatus(startDate, dueDate, today) {
      if (today >= startDate && today <= dueDate) return "Active";
      return today > dueDate ? "Expired" : "Upcoming";
    }
   
  
  
    function createQuiz() {
      const quiz = {
        title: quizElements.titleInput.value.trim(),
        description: quizElements.descInput.value.trim(),
        start_date: quizElements.startInput.value,
        end_date: quizElements.dueInput.value,
        questions: parseInt(quizElements.questionsInput.value),
      };
  
      console.log(quiz);
  
      if (!quiz.title || !quiz.start_date || !quiz.end_date) {
        alert("Please fill all required fields");
        return;
      }
  
      if (currentQuizType === "offline" && !quiz.questions) {
        alert("Please enter number of questions");
        return;
      }
      fetch("/quizzes/go/create/", {
        method: "POST",
        body: new URLSearchParams(quiz),
        headers: {
          "X-CSRFToken": "{{ csrf_token }}",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            window.location.href = data.redirect_url; // Redirect to the quiz detail page
          } else {
            alert("Error creating quiz: " + data.error);
          }
        })
        .catch((error) => {
          console.error("AJAX Error:", error);
          alert("An error occurred: " + error.message);
        });
      loadStudentQuizzes();
      quizElements.modal.style.display = "none";
      resetQuizModal();
    }
  
    function editQuiz(index) {
      const quiz = quizList[index];
      isEditingQuiz = true;
      editingQuizIndex = index;
  
      quizElements.titleInput.value = quiz.title;
      quizElements.descInput.value = quiz.description || "";
      quizElements.startInput.value = quiz.start;
      quizElements.dueInput.value = quiz.due;
      quizElements.saveBtn.textContent = "Save Changes";
  
      currentQuizType = quiz.type;
      quizElements.typeCards?.forEach((c) => {
        c.classList.toggle("active", c.dataset.type === quiz.type);
      });
      quizElements.onlineOptions.style.display =
        quiz.type === "offline" ? "block" : "none";
  
      if (quiz.type === "offline") {
        quizElements.questionsInput.value = quiz.questions || "";
      }
  
      quizElements.modal.style.display = "block";
    }
  
  
    // Assignment CRUD Operations
    function resetAssignmentModal() {
      assignmentElements.titleInput.value = "";
      assignmentElements.descInput.value = "";
      assignmentElements.startInput.value = "";
      assignmentElements.dueInput.value = "";
      assignmentElements.fileInput.value = "";
      assignmentElements.fileInfo.textContent = "";
  
      // Fixed null checks
      if (assignmentElements.saveBtn)
        assignmentElements.saveBtn.style.display = "none";
      if (assignmentElements.createBtn)
        assignmentElements.createBtn.style.display = "block";
  
      isEditingAssignment = false;
      editingAssignmentIndex = null;
    }
  
    function getAssignmentStatus(startDate, dueDate, today) {
      return today > new Date(dueDate) ? "Expired" : "Active";
    }
  
    function renderAssignmentTable() {
      if (!assignmentElements.table) return;
  
      assignmentElements.table.innerHTML =
        assignmentList
          .map((assignment, index) => {
            const status = getAssignmentStatus(
              new Date(assignment.startDate),
              new Date(assignment.dueDate),
              new Date()
            );
            // In renderAssignmentTable() function, update the buttons HTML
            return `
  <tr>
    <td>${assignment.title}</td>
    <td>${assignment.startDate}</td>
    <td>${assignment.dueDate}</td>
    <td>${
      assignment.fileName
        ? `<a href="uploads/${assignment.fileName}" target="_blank">${assignment.fileName}</a>`
        : "No file"
    }</td>
    <td class="status-${status.toLowerCase()}">${status}</td>
    <td>
      <button class="edit edit-assignment" data-index="${index}">Edit</button>
      <button class="delete delete-assignment" data-index="${index}">Delete</button>
    </td>
  </tr>
  `;
          })
          .join("") || `<tr><td colspan="6">No assignments available</td></tr>`;
  
      assignmentElements.table
        .querySelectorAll(".edit-assignment")
        .forEach((btn) => {
          btn.addEventListener("click", () =>
            editAssignment(parseInt(btn.dataset.index))
          );
        });
      assignmentElements.table
        .querySelectorAll(".delete-assignment")
        .forEach((btn) => {
          btn.addEventListener("click", () =>
            deleteAssignment(parseInt(btn.dataset.index))
          );
        });
    }
  
    function handleAssignmentModal() {
      // Add this to the handleAssignmentModal function
      document.querySelector(".browse-link")?.addEventListener("click", () => {
        assignmentElements.fileInput.click();
      });
      function openModal() {
        assignmentElements.modal.style.display = "block";
        resetAssignmentModal();
      }
  
      function closeModal() {
        assignmentElements.modal.style.display = "none";
        resetAssignmentModal();
      }
  
      assignmentElements.openBtn?.addEventListener("click", openModal);
      assignmentElements.closeBtn?.addEventListener("click", closeModal);
      window.addEventListener("click", (e) => {
        if (e.target === assignmentElements.modal) closeModal();
      });
  
      assignmentElements.fileInput?.addEventListener("change", () => {
        const file = assignmentElements.fileInput.files[0];
        if (file) {
          assignmentElements.fileInfo.textContent = `Selected file: ${file.name}`;
        }
      });
      // Add to handleAssignmentModal function
      const dropZone = document.getElementById("assignmentDropzone");
      const fileInput = assignmentElements.fileInput;
  
      // Prevent default drag behaviors
      ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
      });
  
      // Highlight drop zone when dragging
      ["dragenter", "dragover"].forEach((eventName) => {
        dropZone.addEventListener(eventName, highlight, false);
      });
  
      ["dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, unhighlight, false);
      });
  
      // Handle dropped files
      dropZone.addEventListener("drop", handleDrop, false);
  
      function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
      }
  
      function highlight(e) {
        dropZone.classList.add("dragover");
      }
  
      function unhighlight(e) {
        dropZone.classList.remove("dragover");
      }
  
      function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        updateFileDisplay(files[0]);
      }
  
      function updateFileDisplay(file) {
        assignmentElements.fileInfo.textContent = `Selected file: ${file.name}`;
        assignmentElements.fileInfo.style.display = "block";
      }
  
      // Update existing change listener
      assignmentElements.fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) updateFileDisplay(file);
      });
    }
  
    function createAssignment() {
      const assignment = {
        title: assignmentElements.titleInput.value.trim(),
        description: assignmentElements.descInput.value.trim(),
        startDate: assignmentElements.startInput.value,
        dueDate: assignmentElements.dueInput.value,
        fileName: assignmentElements.fileInput.files[0]?.name || "",
      };
  
      if (!assignment.title || !assignment.startDate || !assignment.dueDate) {
        alert("Please fill all required fields");
        return;
      }
  
      if (isEditingAssignment) {
        assignmentList[editingAssignmentIndex] = assignment;
      } else {
        assignmentList.push(assignment);
      }
  
      renderAssignmentTable();
      assignmentElements.modal.style.display = "none";
      resetAssignmentModal();
    }
  
    function editAssignment(index) {
      const assignment = assignmentList[index];
      isEditingAssignment = true;
      editingAssignmentIndex = index;
  
      assignmentElements.titleInput.value = assignment.title;
      assignmentElements.descInput.value = assignment.description || "";
      assignmentElements.startInput.value = assignment.startDate;
      assignmentElements.dueInput.value = assignment.dueDate;
      assignmentElements.fileInfo.textContent = assignment.fileName
        ? `Current file: ${assignment.fileName}`
        : "No file uploaded";
  
      assignmentElements.createBtn.style.display = "none";
      assignmentElements.saveBtn.style.display = "block";
      assignmentElements.modal.style.display = "block";
    }
  
    function deleteAssignment(index) {
      if (confirm("Are you sure you want to delete this assignment?")) {
        assignmentList.splice(index, 1);
        renderAssignmentTable();
      }
    }
  
    // Event Listeners
    quizElements.filter?.addEventListener("change", loadStudentQuizzes);
    quizElements.saveBtn?.addEventListener("click", createQuiz);
    assignmentElements.createBtn?.addEventListener("click", createAssignment);
    assignmentElements.saveBtn?.addEventListener("click", createAssignment);
  
    // Initialization
    handleQuizModal();
    handleQuizTypeCards();
    handleAssignmentModal();
    renderAssignmentTable();
  }
  function go_create_quiz(e) {
    e.preventDefault();
    var quizForm = document.getElementById("quiz-form");
  
    const formData = new FormData(quizForm);
  }
  
  // Initialize the application
 
  // Global variables to store pending quiz id and index
  var pendingDeleteQuizId = null;
  var pendingDeleteIndex = null;
  
  // Function to show the delete confirmation modal
  function showDeleteModal(quizId, index) {
      pendingDeleteQuizId = quizId;
      pendingDeleteIndex = index;
      document.getElementById('deleteConfirmationModal').style.display = 'flex';
  }
  
  // Function to hide the modal
  function hideDeleteModal() {
      document.getElementById('deleteConfirmationModal').style.display = 'none';
      pendingDeleteQuizId = null;
      pendingDeleteIndex = null;
  }
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  
  var csrftoken = getCookie('csrftoken');
  
  
  // Set up event listeners on modal buttons
      var cancelBtn = document.getElementById('cancelDeleteBtn');
      var confirmBtn = document.getElementById('confirmDeleteBtn');
      var modal = document.getElementById('deleteConfirmationModal');
  
      function confirmDelete() {
          // Make sure we have a pending quiz ID
          if (pendingDeleteQuizId) {
              // Perform AJAX deletion
              fetch("/quizzes/delete/" + pendingDeleteQuizId + "/", {
                  method: "POST",
                  headers: {
                      "X-CSRFToken": csrftoken, // CSRF token must be provided
                  },
              })
              .then(response => response.json())
              .then(data => {
                  if (data.success) {
                      // For example, reload the page or re-fetch quizzes from the backend
                      window.location.reload();
                  } else {
                      alert("Error deleting quiz: " + data.error);
                  }
              })
              .catch(error => {
                  console.error("Deletion Error:", error);
                  alert("An error occurred during deletion.");
              });
          }
          hideDeleteModal();
      };
  
      // Close modal if clicking outside content
      modal.addEventListener('click', function(e) {
          if (e.target === modal) {
              hideDeleteModal();
          }
      });
  
     initializeAssessments();
     async function loadStudentQuizzes() {
      console.log("Loading quizzes...");
  
      const tableBody = document.getElementById("quizTableBody");
      tableBody.innerHTML = ""; // Clear existing
  
      try {
          const res = await fetch("/get_avl_quizzes/");
          const quizzes = await res.json();
  
          // Log the response for debugging
          console.log("Quizzes fetched:", quizzes);
  
          if (!Array.isArray(quizzes)) throw new Error("Invalid data");
  
          // Check if there are no quizzes
          if (quizzes.length === 0) {
              const noQuizRow = document.createElement("tr");
              noQuizRow.innerHTML = `
                  <td colspan="8" class="text-center py-4 text-gray-500">No quizzes available</td>
              `;
              tableBody.appendChild(noQuizRow);
          } else {
              quizzes.forEach((quiz, index) => {
                  const row = document.createElement("tr");
                  row.innerHTML = `
                      <td class="px-4 py-3">${quiz.id}</td>
                      <td class="px-4 py-3">${quiz.title}</td>
                      <td class="px-4 py-3">${quiz.section}-${quiz.semester}-${quiz.department}</td>
                      <td class="px-4 py-3">${quiz.course_code}</td>
                      <td class="px-4 py-3">${quiz.start_date}</td>
                      <td class="px-4 py-3">${quiz.due_date}</td>
                      <td class="status-${quiz.status.toLowerCase()}">${quiz.status}</td>
                      <td class="px-4 py-3 text-right">
                          <a href="/quizzes/${quiz.id}/overview" style="text-decoration: none;">
                              <button class="edit" data-index="${index}">Attempt</button>
                          </a>
                      </td>
                  `;
                  tableBody.appendChild(row);
              });
          }
      } catch (err) {
          console.error("Failed to load quizzes:", err);
          tableBody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-red-500">Failed to load quizzes</td></tr>`;
      }
  }
  
  loadStudentQuizzes();
  async function loadAttemptedQuizzes() {
    console.log("Loading attempted quizzes...");

    const tableBody = document.getElementById("attemptedQuizTableBody");
    tableBody.innerHTML = ""; // Clear existing

    try {
        const res = await fetch("/get_attempted_quizzes/");
        const quizzes = await res.json();

        // Log the response for debugging
        console.log("Attempted Quizzes fetched:", quizzes);

        if (!Array.isArray(quizzes)) throw new Error("Invalid data");

        quizzes.forEach((quiz, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td class="px-4 py-3">${quiz.quiz_name}</td>
                <td class="px-4 py-3">${quiz.marks_scored} / ${quiz.total_marks}</td>
                <td class="px-4 py-3">${quiz.correct}</td>
                <td class="px-4 py-3">${quiz.wrong}</td>
                <td class="px-4 py-3">${quiz.unattempted}</td>
                <td class="px-4 py-3">${quiz.accuracy}%</td>
                <td class="px-4 py-3 text-right">
                    <a href="/quizzes/${quiz.quiz_id}/summary" style="text-decoration: none;">
                        <button class="view-summary">Summary</button>
                    </a>
                </td>
            `;
            tableBody.appendChild(row);
        });

        if (quizzes.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-red-500">No attempted quizzes found</td></tr>`;
        }

    } catch (err) {
        console.error("Failed to load attempted quizzes:", err);
        tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-red-500">Failed to load attempted quizzes</td></tr>`;
    }
}

loadAttemptedQuizzes();
  