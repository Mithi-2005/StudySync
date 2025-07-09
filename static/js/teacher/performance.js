document.getElementById('studentReportsTab').addEventListener('click', function() {
  setActiveTab('studentReportsTab', 'studentReportsContent');
});
document.getElementById('classOverviewTab').addEventListener('click', function() {
  setActiveTab('classOverviewTab', 'classOverviewContent');
});
document.getElementById('quizInsightsTab').addEventListener('click', function() {
  setActiveTab('quizInsightsTab', 'quizInsightsContent');
});

function setActiveTab(tabId, contentId) {
  document.querySelectorAll('.tabs button').forEach(button => button.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  document.getElementById(contentId).classList.add('active');
}

// Function to sort the table based on the selected column
function sortTable() {
  const table = document.getElementById("performanceTable");
  const rows = Array.from(table.rows).slice(1);
  const sortBy = document.getElementById("sortBy").value;

  const columnIndex = {
      "name": 0,
      "score": 1,
      "attendance": 2,
      "section": 3
  }[sortBy];

  rows.sort((a, b) => {
      let cellA = a.cells[columnIndex].innerText.trim();
      let cellB = b.cells[columnIndex].innerText.trim();

      // For score and attendance, sort in descending order
      if (sortBy === "score" || sortBy === "attendance") {
          const numA = parseFloat(cellA.replace('%', '')) || 0;
          const numB = parseFloat(cellB.replace('%', '')) || 0;
          return numB - numA; // Descending order
      }
      
      // For name and section, sort in ascending order
      return cellA.localeCompare(cellB);
  });

  rows.forEach(row => table.appendChild(row));
}

// Automatically sort by name (ascending) on page load
window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('sortBy').value = "name";  // Default sort by name
  sortTable();  // Sort the table on load
});
