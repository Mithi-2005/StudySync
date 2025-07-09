// Global variable to store responses data for client-side searching
var responsesData = [];

async function initializeAssessments() {
  console.log("✅ Assessments Page Loaded");
  if (window.assessmentsInitialized) return;
  window.assessmentsInitialized = true;

  // Common Elements (quizzes section remains unchanged)
  const tabs = {
    quizzes: {
      tab: document.getElementById("quizzesTab"),
      content: document.getElementById("quizzesContent"),
    },
    responses: { // Changed from assignments to responses
      tab: document.getElementById("responsesTab"),
      content: document.getElementById("responsesContent"),
    },
  };

  // Quiz System Elements (unchanged)
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

  // State for quizzes
  let quizList = [];
  let isEditingQuiz = false;
  let editingQuizIndex = null;
  let currentQuizType = "online";

  // Tab Switching
  function switchToQuizzes() {
    tabs.quizzes.tab?.classList.add("active");
    tabs.responses.tab?.classList.remove("active");
    tabs.quizzes.content?.classList.add("active");
    tabs.responses.content?.classList.remove("active");
  }

  function switchToResponses() {
    tabs.responses.tab?.classList.add("active");
    tabs.quizzes.tab?.classList.remove("active");
    tabs.responses.content?.classList.add("active");
    tabs.quizzes.content?.classList.remove("active");
    loadQuizFilterOptions();
    loadAttemptedQuizzes(); // Load all responses by default
  }

  tabs.quizzes.tab?.addEventListener("click", switchToQuizzes);
  tabs.responses.tab?.addEventListener("click", switchToResponses);

  // Quiz Modal Handling (unchanged)
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

  // Quiz Type Cards Handling (unchanged)
  function handleQuizTypeCards() {
    quizElements.typeCards?.forEach((card) => {
      card.addEventListener("click", () => {
        quizElements.typeCards?.forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        currentQuizType = card.dataset.type;
        if (quizElements.onlineOptions) {
          quizElements.onlineOptions.style.display =
            currentQuizType === "offline" ? "block" : "none";
        }
      });
    });
  }

  // Quiz CRUD Operations (unchanged)
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
    if (quizElements.onlineOptions) {
      quizElements.onlineOptions.style.display = "none";
    }
  }

  // Helper to get quiz status for display (if needed)
  function getQuizStatus(startDate, dueDate, today) {
    if (today >= startDate && today <= dueDate) return "Active";
    return today > dueDate ? "Expired" : "Upcoming";
  }

  // Load quizzes for the quizzes table
  async function loadFacultyQuizzes() {
    const tableBody = document.getElementById("quizTableBody");
    tableBody.innerHTML = "";
    try {
      const res = await fetch("/teacher/get_quizzes/");
      const quizzes = await res.json();
      if (!Array.isArray(quizzes)) throw new Error("Invalid data");
      quizList = quizzes; // store quizzes for later use if needed
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
           <a href="/quizzes/edit/${quiz.id}" style="text-decoration: none;">
             <button class="edit" data-index="${index}">Edit</button>
           </a>
           <button class="delete" data-index="${index}" onclick="showDeleteModal('${quiz.id}', ${index})">Delete</button>
         </td>
        `;
        tableBody.appendChild(row);
      });
    } catch (err) {
      console.error("Failed to load quizzes:", err);
      tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-red-500">Failed to load quizzes</td></tr>`;
    }
  }
  loadFacultyQuizzes();

  // Quiz create operation (unchanged)
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
          window.location.href = data.redirect_url;
        } else {
          alert("Error creating quiz: " + data.error);
        }
      })
      .catch((error) => {
        console.error("AJAX Error:", error);
        alert("An error occurred: " + error.message);
      });
    loadFacultyQuizzes();
    quizElements.modal.style.display = "none";
    resetQuizModal();
  }

  // Event Listeners for quizzes
  quizElements.filter?.addEventListener("change", loadFacultyQuizzes);
  quizElements.saveBtn?.addEventListener("click", createQuiz);

  // Initialization
  handleQuizModal();
  handleQuizTypeCards();
}

// Global functions for deletion and overview actions (unchanged)
function showDeleteModal(quizId, index) {
  window.pendingDeleteQuizId = quizId;
  window.pendingDeleteIndex = index;
  document.getElementById("deleteConfirmationModal").style.display = "flex";
}

function hideDeleteModal() {
  document.getElementById("deleteConfirmationModal").style.display = "none";
  window.pendingDeleteQuizId = null;
  window.pendingDeleteIndex = null;
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

var csrftoken = getCookie("csrftoken");
var modal = document.getElementById("deleteConfirmationModal");

function confirmDelete() {
  if (window.pendingDeleteQuizId) {
    fetch("/quizzes/delete/" + window.pendingDeleteQuizId + "/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          window.location.reload();
        } else {
          alert("Error deleting quiz: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Deletion Error:", error);
        alert("An error occurred during deletion.");
      });
  }
  hideDeleteModal();
}

modal.addEventListener("click", function(e) {
  if (e.target === modal) {
    hideDeleteModal();
  }
});

// Global function to view the overview of a student's quiz response
function viewOverview(responseId) {
  window.location.href = "/responses/overview/" + responseId + "/";
}

// Load quiz filter options in the responses view
async function loadQuizFilterOptions() {
  const filter = document.getElementById('responsesFilter');
  try {
    const res = await fetch('/teacher/get_quizzes/');
    const quizzes = await res.json();
    // Reset options and add default
    filter.innerHTML = '<option value="all">All Quizzes</option>';
    quizzes.forEach(quiz => {
      const option = document.createElement('option');
      option.value = quiz.id;
      option.textContent = quiz.title;
      filter.appendChild(option);
    });
  } catch (err) {
    console.error('Failed to load quizzes for filter:', err);
  }
}

// Load attempted quizzes/responses with an optional filter (quizId)
async function loadAttemptedQuizzes(quizId = 'all') {
  console.log("Loading attempted quizzes...");
  const tableBody = document.getElementById("responsesBody");
  tableBody.innerHTML = ""; // Clear existing rows

  try {
    let url = "/quizzes/get_responses/";
    if (quizId !== 'all') {
      url += `?quiz_id=${quizId}`;
    }
    const res = await fetch(url);
    const data = await res.json();

    console.log("Attempted Quizzes fetched:", data.responses);

    if (!Array.isArray(data.responses)) throw new Error("Invalid data");

    // Store responses in global variable for use in search filtering
    responsesData = data.responses;
    renderResponses();
  } catch (err) {
    console.error("Failed to load attempted quizzes:", err);
    tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-red-500">Failed to load attempted quizzes</td></tr>`;
  }
}

// Render responses taking into account the search filter (by Reg No)
function renderResponses() {
  const tableBody = document.getElementById("responsesBody");
  const searchValue = document.getElementById("searchInput").value.toLowerCase();
  // Filter responsesData based on Reg No matching the search value
  const filteredResponses = responsesData.filter(response => 
    response.reg_no.toLowerCase().includes(searchValue)
  );
  tableBody.innerHTML = ""; // Clear table

  if (filteredResponses.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-red-500">No attempted quizzes found</td></tr>`;
    return;
  }

  filteredResponses.forEach((quiz) => {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td class="px-4 py-3">${quiz.quiz_name}</td>
        <td class="px-4 py-3">${quiz.reg_no}</td>
        <td class="px-4 py-3">${quiz.name}</td>
        <td class="px-4 py-3">${quiz.marks}</td>
        <td class="px-4 py-3">${quiz.accuracy}</td>
        <td class="px-4 py-3 text-right">
            <a href="/quizzes/${quiz.quiz_id}/${quiz.reg_no}/summary" style="text-decoration: none;">
                <button class="view-summary">Summary</button>
            </a>
        </td>
    `;
    tableBody.appendChild(row);
  });
}

// Update responses filter when the dropdown value changes
document.getElementById('responsesFilter').addEventListener('change', function() {
  loadAttemptedQuizzes(this.value);
});

// Listen for search input changes to apply filtering by Reg No
document.getElementById("searchInput").addEventListener("input", function() {
  renderResponses();
});

// Initialize the assessments page
initializeAssessments();
