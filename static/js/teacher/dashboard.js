console.log("Charts Initialized");
// document.addEventListener("DOMContentLoaded", function () {
function intializeCharts() {
    new Chart(document.getElementById("quizChart"), {
      type: "bar",
      data: {
        labels: [
          "Section A",
          "Section B",
          "Section C",
          "Section D",
          "Section E",
          "Section F",
        ],
        datasets: [
          {
            label: "Completed Quizzes",
            data: [30, 25, 28, 32, 29, 27],
            backgroundColor: "#3D3B8E",
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });

    // Assignments Chart: Section-wise attempted vs missed assignments
    new Chart(document.getElementById("assignmentChart"), {
      type: "bar",
      data: {
        labels: [
          "Section A",
          "Section B",
          "Section C",
          "Section D",
          "Section E",
          "Section F",
        ],
        datasets: [
          {
            label: "Attempted",
            data: [25, 22, 28, 30, 27, 24],
            backgroundColor: "#3D3B8E",
          },
          {
            label: "Missed",
            data: [5, 8, 2, 4, 3, 6],
            backgroundColor: "#E74C3C",
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }
// });
intializeCharts()