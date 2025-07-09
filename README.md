# StudySync

**StudySync** is a full-stack Django-based platform for managing academic activities for students, teachers, and administrators. It provides features such as classroom management, quiz and assignment handling, attendance tracking, scheduling, and more, with dedicated interfaces for each user role.

---

## Features

### Student
- Traditional Email login
- Dashboard with schedule, results, and upcoming quizzes/assignments
- Join classrooms via code
- Quizzes
  - View available quizzes
  - Attempt quizzes within deadlines
  - Review quiz results
- Attendance tracking
- Profile and settings management

### Teacher
- Dashboard with class and performance overview
- Create, edit, and manage classrooms
- Post announcements and materials (with AWS S3 support for attachments)
- Create, edit, and manage quizzes (with multiple question types)
- Track and manage attendance
- View and analyze student performance
- Profile and settings management

### Administrator
- Add and manage students and faculty
- Assign roles and generate registration numbers/faculty IDs
- Manage courses, departments, and timetables
- Enroll students and faculty in courses
- System-wide settings and user management

### Quizzes
- Teachers can create, edit, and delete quizzes
- Students can view, attempt, and review quizzes
- Automatic grading and result summary
- Quiz analytics for teachers

---
## Tech Stack

- **Backend**: Django, MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Storage**: AWS S3 (for media and attachments)
- **Authentication**: Django's built-in auth system with role-based access
- **Deployment**: (Add if applicable, e.g., Render, Heroku, EC2)
---

## Project Flow

### 1. Authentication & Role-based Access
- **Login:** Users (students, teachers, administrators) log in using their email and password via the login page.
- **Role Detection:** Upon login, the system determines the user's role and redirects them to their respective dashboard (Student, Teacher, or Administrator).

### 2. Student Flow
- **Dashboard:** Students see their schedule, upcoming quizzes, assignments, and results.
- **Classroom Join:** Students can join classrooms using a class code provided by teachers.
- **Quizzes & Assignments:** Students can view, attempt, and review quizzes and assignments assigned to their classrooms.
- **Attendance:** Students can mark or view their attendance records.
- **Profile & Settings:** Students can update their profile and account settings.

### 3. Teacher Flow
- **Dashboard:** Teachers see an overview of their classes, schedules, and student performance.
- **Classroom Management:** Teachers can create, edit, and manage classrooms, and automatically enroll students based on department, semester, and section.
- **Posts & Materials:** Teachers can post announcements and upload materials (with AWS S3 support for attachments) to their classrooms.
- **Quiz Management:** Teachers can create, edit, and manage quizzes with various question types, and view analytics on student performance.
- **Attendance:** Teachers can take and manage attendance for their classes.
- **Profile & Settings:** Teachers can update their profile and account settings.

### 4. Administrator Flow
- **Dashboard:** Administrators have access to system-wide statistics and management tools.
- **User Management:** Admins can add students and faculty, assign roles, and generate registration numbers or faculty IDs.
- **Course & Timetable Management:** Admins can manage courses, departments, timetables, and enrollments.
- **Settings:** Admins can configure system-wide settings and manage all users.

### 5. Quizzes
- **Creation:** Teachers create quizzes and assign them to specific classrooms.
- **Participation:** Students attempt quizzes within the allowed time window.
- **Grading & Results:** The system automatically grades quizzes and provides instant feedback and analytics to both students and teachers.

### 6. Static & Media Files
- **Static Files:** CSS, JS, and images are served from the `static/` directory.
- **Media Uploads:** Attachments and materials are uploaded to AWS S3, with links managed in the platform.

---

## Project Structure

- `student/` – Student-facing views, URLs, and logic
- `teacher/` – Teacher-facing views, URLs, and logic
- `administrator/` – Admin-facing views, URLs, and logic
- `quizzes/` – Quiz management logic and endpoints
- `static/` – Static assets (CSS, JS, images)
- `templates/` – HTML templates for all user roles
- `study_sync/` – Project settings and root URLs

---

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mithi-2005/StudySync
   cd study_sync
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *(If `requirements.txt` is missing, generate it with `pip freeze > requirements.txt` after installing your packages.)*

4. **Set up environment variables**

   Create a `.env` file in the root directory with the following variables:
   ```
   SECRET_KEY=your-django-secret-key
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=3306
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_STORAGE_BUCKET_NAME=your_bucket
   AWS_S3_CUSTOM_DOMAIN=your_s3_domain
   SESSION_COOKIE_AGE=3600
   SESSION_SAVE_EVERY_REQUEST=True
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.yourprovider.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_USE_SSL=False
   EMAIL_HOST_USER=your_email
   EMAIL_HOST_PASSWORD=your_email_password
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the app**
   - Student: `/`
   - Teacher: `/teacher/`
   - Administrator: `/administrator/`
   - Quizzes: `/quizzes/`

---

## Static & Media Files

- Place static files in the `static/` directory.
- AWS S3 is used for file uploads (attachments, etc.)—configure your AWS credentials in `.env`.

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a new Pull Request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or support, contact kvmithilesh2005@gmail.com. 
