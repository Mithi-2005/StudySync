// document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('attendance-chart').getContext('2d');

    // Extract data from the table
    const rows = document.querySelectorAll('tbody tr');
    const labels = [];
    const percentages = [];

    rows.forEach(row => {
        const subject = row.children[1].textContent;  // Subject name
        const attendance = parseFloat(row.children[5].textContent);  // Attendance percentage
        labels.push(subject);
        percentages.push(attendance);
    });

    // Calculate overall average
    const avgAttendance = (percentages.reduce((sum, val) => sum + val, 0) / percentages.length).toFixed(2);
    document.getElementById('average-attendance').textContent = avgAttendance;

    // Chart.js configuration
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Attendance %',
                data: percentages,
                backgroundColor: [
                    '#3498db', '#e74c3c', '#f1c40f', '#2ecc71', '#9b59b6', '#1abc9c', '#34495e', '#e67e22', '#95a5a6'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 20,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.label}: ${context.raw}%`;
                        }
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
// });
