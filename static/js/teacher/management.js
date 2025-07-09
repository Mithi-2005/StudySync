 // Popup Controls
 function openPopup() {
    document.getElementById("createPopup").classList.add("active");
    loadDepartments()
  }

  function closePopup() {
    document.getElementById("createPopup").classList.remove("active");
  }

  // Close when clicking outside content
  document
    .getElementById("createPopup")
    .addEventListener("click", function (e) {
      if (e.target === this) closePopup();
    });

  // Simple animation on scroll
    var elements = document.querySelectorAll("[data-aos]");

    function checkPosition() {
      elements.forEach((element) => {
        const position = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;

        if (position < windowHeight - 100) {
          element.classList.add("aos-animate");
        }
      });
    }

    window.addEventListener("scroll", checkPosition);
    window.addEventListener("resize", checkPosition);
    checkPosition();
    function copyToClipboard(event, text, button) {
      event.stopPropagation(); // Prevent event bubbling to parent elements
      event.preventDefault(); // Prevent default behavior
      
      navigator.clipboard.writeText(text).then(() => {
        // Visual feedback
        const icon = button.querySelector('.copy-icon');
        button.classList.add('copied');
        icon.innerHTML = `<path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;
        
        // Reset after 2 seconds
        setTimeout(() => {
          button.classList.remove('copied');
          icon.innerHTML = `<path d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>`;
        }, 2000);
      }).catch(err => {
        console.error('Failed to copy: ', err);
      });
    }
    function loadDepartments() {
      fetch("/administrator/get-departments/")
          .then(response => response.json())
          .then(data => {
              let deptDropdown = document.getElementsByName("department");
              console.log(deptDropdown)
              deptDropdown[0].innerHTML = '<option value="" selected disabled>Select Department</option>';              
              if (Array.isArray(data.departments)) {
                  data.departments.forEach(dept => {
                      deptDropdown[0].innerHTML += `<option value="${dept.code}">${dept.code}</option>`;
                  });
              }
          })
          .catch(error => console.error("Error loading departments:", error));
    }

    function loadSemesters() {
      let department = document.getElementById("department").value;
      let semDropdown = document.getElementById("semester");
      
      // Reset dependent dropdowns
      document.getElementById("section").innerHTML = '<option value="" selected disabled>Select Section</option>';
      document.getElementById("course_code").innerHTML = '<option value="" selected disabled>Select Course</option>';
      
      if (!department) return;
    
      fetch(`/administrator/get-semesters/?department=${department}`)
          .then(response => response.json())
          .then(data => {
              semDropdown.innerHTML = '<option value="" selected disabled>Select Semester</option>' +
                  data.semesters.map(sem => `<option value="${sem}">${sem}</option>`).join("");
          })
          .catch(error => console.error("Error loading semesters:", error));
    }
    function loadSections() {
      let department = document.getElementById("department").value;
      let semester = document.getElementById("semester").value;
      let secDropdown = document.getElementById("section");
      
      // Reset courses dropdown
      document.getElementById("course_code").innerHTML = '<option value="" selected disabled>Select Course</option>';
      
      if (!department || !semester) return;
    
      fetch(`/administrator/get-sections/?department=${department}&semester=${semester}`)
          .then(response => response.json())
          .then(data => {
              secDropdown.innerHTML = '<option value="" selected disabled>Select Section</option>' +
                  data.sections.map(sec => `<option value="${sec}">${sec}</option>`).join("");
          })
          .catch(error => console.error("Error loading sections:", error));
    }
    function loadCourses() {
      let department = document.getElementById("department").value;
      let semester = document.getElementById("semester").value;
      let section = document.getElementById("section").value;
      let CoDropdown = document.getElementById("course_code");
      
      // Reset courses dropdown
      
      if (!department || !semester) return;
    
      fetch(`/administrator/get-courses-json?department=${department}&section=${section}&semester=${semester}`)
          .then(response => response.json())
          .then(data => {
              CoDropdown.innerHTML = '<option value="" selected disabled>Select Section</option>' +
                  data.courses.map(cou => `<option value="${cou.code}">${cou.name}</option>`).join("");
          })
          .catch(error => console.error("Error loading sections:", error));
    }
    function toggleMenu(event,button) {
      event.preventDefault();
      event.stopPropagation();
      
      const menu = button.closest('.action-menu');
      menu.classList.toggle('active');
      
      // Close when clicking outside
      document.addEventListener('click', function closeMenu(e) {
        if (!menu.contains(e.target)) {
          menu.classList.remove('active');
          document.removeEventListener('click', closeMenu);
        }
      });
    }
    
    // Delete confirmation
    function confirmDelete(event,classCode) {
      event.preventDefault();
      event.stopPropagation();
      const dialog = document.createElement('div');
      dialog.className = 'delete-confirm';
      dialog.innerHTML = `
        <div class="confirm-box">
          <h3>Delete Classroom?</h3>
          <p>Are you sure you want to delete this classroom? This action cannot be undone.</p>
          <div class="confirm-actions">
            <button class="confirm-btn cancel-btn" onclick="this.closest('.delete-confirm').remove()">Cancel</button>
            <button class="confirm-btn proceed-btn" onclick="deleteClassroom('${classCode}')">Delete</button>
          </div>
        </div>
      `;
      document.body.appendChild(dialog);
      setTimeout(() => dialog.classList.add('active'), 10);
    }
    
    function deleteClassroom(classCode) {
      fetch(`/teacher/classroom/${classCode}/delete/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': '{{ csrf_token }}',
          'Content-Type': 'application/json'
        }
      }).then(response => {
        if (response.ok) {
          // Remove classroom card
          const card = document.querySelector(`.classroom-card[data-code="${classCode}"]`);
          if (card) card.remove();
          
          // Show success toast
          showToast('Classroom deleted successfully');
        }
      });
      
      // Remove confirmation dialog
      document.querySelector('.delete-confirm').remove();
    }
    
    // Toast creation function
    function showToast(message, type = 'success') {
      const toast = document.createElement('div');
      toast.className = `toast ${type}`;
      toast.innerHTML = `
        <svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          ${type === 'success' ? 
            '<path d="M20 6L9 17l-5-5"/>' : 
            '<path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>'}
        </svg>
        <span>${message}</span>
      `;
      
      document.getElementById('toastContainer').appendChild(toast);
      
      // Animation timing
      setTimeout(() => toast.classList.add('visible'), 50);
      setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    }
    
    function gotoClass(id) {
      window.open(`/teacher/classroom/${id}/`, '_blank');
    }
    function openEditPopup(event,name,code) {
      event.preventDefault();
      event.stopPropagation();
      const popup = document.getElementById('editClassPopup');
      popup.classList.add('active');
      document.body.style.overflow = 'hidden';
      
      // Fill form with classroom data
      const form = document.querySelector('.edit-class-form');
      if (name) {
        document.getElementById('edit_class_name').value = name;
        form.action = `/teacher/classroom/${code}/edit/`;
      }
      
      // Reset any previous validation
      form.classList.remove('was-validated');
    }
  
    // Function to close edit popup
    function closeEditPopup() {
      const popup = document.getElementById('editClassPopup');
      popup.classList.remove('active');
      document.body.style.overflow = 'auto';
    }
  
    // Close when clicking outside
    document.getElementById('editClassPopup').addEventListener('click', function(e) {
      if (e.target === this) {
        closeEditPopup();
      }
    });
  
    // Close with Escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && document.getElementById('editClassPopup').classList.contains('active')) {
        closeEditPopup();
      }
    });
  
    function updateClassroomCard(newName) {
      // Implement this based on your app structure
      // Example:
      const currentCard = document.querySelector(`.classroom-card h3`);
      if (currentCard) {
        currentCard.textContent = newName;
      }
    }

    document.querySelector('.edit-class-form')?.addEventListener('submit', async function(e) {
      e.preventDefault();
      const form = this;
  form.classList.add('was-validated');
  
  if (!form.checkValidity()) {
    e.preventDefault();
    e.stopPropagation();
    return;
  }
      
      try {
        const formData = new FormData(this);
        const response = await fetch(this.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': '{{ csrf_token }}'
          }
        });
    
        if (response.ok) {
          // Show success toast
          showToast('Classroom updated successfully!', 'success');
          
          // Close the popup after a short delay
          setTimeout(() => {
            closeEditPopup();
            
           
              // If we're on the dashboard, you might want to update the card
              // You would need to implement this based on your app structure
              updateClassroomCard(formData.get('class_name'));
          }, 500);
        } else {
          showToast('Failed to update classroom', 'error');
        }
      } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred', 'error');
      }
    });