var dayButtons = document.querySelectorAll(".day-btn");
var mobileTimetable = document.getElementById("mobile-timetable");
var days = [];
var timeSlots = [];
var schedule = {};

fetch('/teacher/get_teacher_schedule/')
  .then(response => {
    if (!response.ok) throw new Error("Failed to fetch schedule");
    return response.json();
  })
  .then(data => {
    days = JSON.parse(data.days_json);
    timeSlots = JSON.parse(data.time_slots);
    schedule = JSON.parse(data.schedule_json);

    console.log("✅ Days:", days);
    console.log("🕐 Time Slots:", timeSlots);
    console.log("📅 Schedule:", schedule);

    // You can now use these in your loadDay function or UI
    loadDay(days[(new Date().getDay() + 6) % 7]); // auto-load today
  })
  .catch(err => {
    console.error("❌ Error loading schedule:", err);
  });

function loadDay(day) {
  mobileTimetable.innerHTML = "";
  const dayClasses = schedule[day];

  if (!dayClasses) {
    mobileTimetable.innerHTML = "<p>No data found for this day.</p>";
    return;
  }

  timeSlots.forEach((time) => {
    const slot = dayClasses[time];

    // Create the wrapper
    const wrapper = document.createElement("div");
    wrapper.className = `mobile-slot ${slot ? "" : "empty"}`;

    // Set inner HTML with corrected structure
    wrapper.innerHTML = `
    <div class="slot-main">
      <div class="slot-header">
        <span class="slot-time">${time}</span>
      </div>
      <div class="slot-room-wrapper">
        <span class="slot-room">${slot ? (slot.room || "Free") : "Free"}</span>
      </div>
    </div>
    <div class="slot-details">
       ${
      slot
        ? `<strong>${slot.subject}</strong><br/>
           Dept: ${slot.department}<br/>
           Sec: ${slot.section}, Sem: ${slot.semester}`
        : `<em>No Class</em>`
    }
    </div>
  `;

    // Add event listener for expanding/collapsing details
    wrapper.addEventListener("click", () => {
      wrapper.classList.toggle("active");
    });

    // Append to mobile timetable
    mobileTimetable.appendChild(wrapper);
  });
}

// Day button click handler
dayButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    dayButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    loadDay(btn.dataset.day);
  });
});

// Load today's day by default
const todayIndex = new Date().getDay(); // Sunday=0
const today = days[(todayIndex + 6) % 7]; // Shift to Monday-start
document.querySelector(`[data-day="${today}"]`)?.click();
