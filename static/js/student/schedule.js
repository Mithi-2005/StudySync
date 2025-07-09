async function initializeSchedule() {
    console.log("✅ Schedules Page Loaded");

    // Get timetable containers
    var timetableBody = document.getElementById("timetable-body");
    var mobileTimetable = document.getElementById("mobile-timetable");
    if (!timetableBody || !mobileTimetable) {
        console.error("❌ Timetable elements not found!");
        return;
    }

    // Fetch timetable data from backend
    let timetableData = [];
    try {
        const response = await fetch("/get_timetable/", { method: "GET" });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        timetableData = data.timetable;
    } catch (error) {
        console.error("❌ Error fetching timetable:", error);
        return;
    }

    // Process timetable data into a structured format
    const structuredTimetable = {};
    timetableData.forEach(slot => {
        if (!structuredTimetable[slot.time_slot]) {
            structuredTimetable[slot.time_slot] = { time: slot.time_slot };
        }
        structuredTimetable[slot.time_slot][slot.day] = {
            course_code: slot.course_code,
            course_name: slot.course_name,  // Store course name
            room_no: slot.room_no
        };
    });

    // Convert object to array
    const timetableArray = Object.values(structuredTimetable);

    // Function to load laptop view
    function loadLaptopView() {
        timetableBody.innerHTML = "";
        timetableArray.forEach(row => {
            let rowHTML = `<div class="row"><div class="slot"><strong>${row.time}</strong></div>`;
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].forEach(day => {
                let subjectData = row[day];
                let displayText = subjectData ? `${subjectData.course_code} (${subjectData.room_no})` : "-";
                let tooltipText = subjectData ? `${subjectData.course_name}` : "";  // Show course name in tooltip

                rowHTML += `
                    <div class="slot">
                        <span class="subject-name">${displayText}</span>
                        ${tooltipText ? `<div class="tooltip">${tooltipText}</div>` : ""}
                    </div>`;
            });
            timetableBody.innerHTML += `<div class="timetable-body">${rowHTML}</div></div>`;
        });
    }

  


    function loadMobileView(selectedDay = "Monday") {
        mobileTimetable.innerHTML = "";
        timetableArray.forEach(row => {
            let subject = row[selectedDay];
    
            if (subject) {
                let displayText = `${subject.course_code} - ${subject.course_name}`;
                let roomText = subject.room_no ? `Room: ${subject.room_no}` : "Room: N/A";
    
                mobileTimetable.innerHTML += `
                    <div class="course-card">
                        <div class="course-info">
                            <h3>${displayText}</h3>
                            <p>${roomText}</p>
                        </div>
                        <div class="course-time"><h4>${row.time}</h4></div>
                    </div>`;
            }
        });
    
        // Highlight the active day
        document.querySelectorAll(".day-btn").forEach(btn => {
            btn.classList.toggle("active", btn.getAttribute("data-day") === selectedDay);
        });
    }
    
    // Attach event listeners for day selection
    setTimeout(() => {
        document.querySelectorAll(".day-btn").forEach(btn => {
            btn.addEventListener("click", () => loadMobileView(btn.getAttribute("data-day")));
        });
    }, 500);

    // Load timetable views
    loadLaptopView();
    loadMobileView(new Date().toLocaleString("en-US", { weekday: "long" }));

    console.log("✅ Timetable Rendering Completed");
}
initializeSchedule();
