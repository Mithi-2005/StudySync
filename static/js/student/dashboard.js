console.log("📊 Dashboard Charts Initializing...");

  Promise.all([
    fetch('/quizdata/').then((res) => res.json()),
   fetch('/assignmentdata/').then((res) => res.json()),

  ])
    .then(([quizData, assignmentData]) => {
      if (!Array.isArray(quizData) || quizData.length === 0) {
        console.warn("⚠️ No quiz data found.");
      }
      if (!Array.isArray(assignmentData) || assignmentData.length === 0) {
        console.warn("⚠️ No assignment data found.");
      }

      initializeCharts(quizData, assignmentData);
    })
    .catch((err) => {
      console.error("❌ Failed to fetch dashboard data:", err);
    });

function initializeCharts(quizData, assignmentData) {
  const trendCanvas = document.getElementById("trendChart");
  const salesCanvas = document.getElementById("salesChart");

  if (trendCanvas && quizData && quizData.length > 0) {
    const ctx1 = trendCanvas.getContext("2d");

    const quizNames = quizData.map((quiz) => quiz.quiz_name);
    const correctData = quizData.map((quiz) => quiz.correct);
    const attemptedData = quizData.map((quiz) => quiz.attempted);
    const missedData = quizData.map((quiz) => quiz.wrong);

    new Chart(ctx1, {
      type: "bar",
      data: {
        labels: quizNames,
        datasets: [
          {
            label: "Attempted",
            data: attemptedData,
            backgroundColor: "#6fa8dc",
          },
          {
            label: "Correct",
            data: correctData,
            backgroundColor: "#93c47d",
          },
          {
            label: "Wrong",
            data: missedData,
            backgroundColor: "#e06666",
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

  if (salesCanvas && assignmentData && assignmentData.length > 0) {
    const ctx2 = salesCanvas.getContext("2d");

    const submitted = assignmentData[0].submitted || 0;
    const missed = assignmentData[0].late || 0;
    const pending = assignmentData[0].pending || 0;

    new Chart(ctx2, {
      type: "doughnut",
      data: {
        labels: ["Submitted", "Missed", "Pending"],
        datasets: [
          {
            data: [submitted, missed, pending],
            backgroundColor: ["#42A5F5", "#EF5350", "#FFCA28"],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "bottom",
          },
        },
      },
    });
  }
}
