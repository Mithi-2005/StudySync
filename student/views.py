import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password,make_password
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import json
from django.http import JsonResponse
from collections import defaultdict
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings as dset

def google_login(request):
    auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth'
        '?response_type=code'
        f'&client_id={dset.GOOGLE_CLIENT_ID}'
        f'&redirect_uri={dset.GOOGLE_REDIRECT_URI}'
        '&scope=email%20profile'
        '&access_type=offline'
        '&prompt=select_account'
    )
    return redirect(auth_url)


# def google_callback(request):
#     code = request.GET.get('code')
#     if not code:
#         messages.error(request, 'Authorization failed.')
#         return redirect('login')

#     # Get access token
#     token_res = requests.post(
#         'https://oauth2.googleapis.com/token',
#         data={
#             'code': code,
#             'client_id': dset.GOOGLE_CLIENT_ID,
#             'client_secret': dset.GOOGLE_CLIENT_SECRET,
#             'redirect_uri': dset.GOOGLE_REDIRECT_URI,
#             'grant_type': 'authorization_code'
#         }
#     )
#     token_json = token_res.json()
#     access_token = token_json.get('access_token')

#     # Get user info from Google
#     userinfo_res = requests.get(
#         'https://www.googleapis.com/oauth2/v2/userinfo',
#         headers={'Authorization': f'Bearer {access_token}'}
#     )
#     userinfo = userinfo_res.json()

#     email = userinfo.get('email')
#     name = userinfo.get('name')

#     # 🔍 Check if this email exists in your `students` table and get the role
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT id, name, role FROM users WHERE email = %s", [email])
#         row = cursor.fetchone()

#     if row:
#         student_id, student_name, role = row

#         # Store in session
#         request.session['id'] = student_id
#         request.session['name'] = student_name
#         request.session['role'] = role

#         messages.success(request, f"Welcome, {student_name}!")

#         # Redirect based on role
#         if role == 'student':
#             return redirect('index')
#         elif role == 'teacher':
#             return redirect('index')
#         elif role == 'admin':
#             return redirect('index')
#         else:
#             messages.error(request, "Unknown role. Please contact admin.")
#             return redirect('login')
#     else:
#         messages.error(request, "No account found for this email.")
#         return redirect('login')
    
def google_callback(request):
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Authorization failed.')
        return redirect('login')

    # Get access token
    token_res = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': dset.GOOGLE_CLIENT_ID,
            'client_secret': dset.GOOGLE_CLIENT_SECRET,
            'redirect_uri': dset.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
    )
    token_json = token_res.json()
    access_token = token_json.get('access_token')

    # Get user info from Google
    userinfo_res = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    userinfo = userinfo_res.json()

    email = userinfo.get('email')
    name = userinfo.get('name')

    # Check if student exists in your own DB
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, role FROM users WHERE email = %s", [email])
        row = cursor.fetchone()

    if row:
        student_id, student_name, role = row

        # 🔐 Create a Django user object if not exists
        user, created = User.objects.get_or_create(username=email, defaults={'first_name': student_name, 'email': email})
        
        # ✅ Log in the user using Django's system
        login(request, user)

        # Store additional info in session (optional)
        request.session['student_id'] = student_id
        request.session['student_name'] = student_name
        request.session['role'] = role

        messages.success(request, f"Welcome, {student_name}")

        # Redirect based on role
        if role == "student":
            return redirect('index')
        elif role == "teacher":
            return redirect('index')
        elif role == "admin":
            return redirect('index')
        else:
            return redirect('home')
    else:
        messages.error(request, "No account found for this email.")
        return redirect('login')

def dictfetchone(cursor):
    "Return one row from a cursor as a dict"
    row = cursor.fetchone()
    if row is None:
        return None
    desc = cursor.description
    return {desc[i][0]: row[i] for i in range(len(row))}
def dictfetchall(cursor):
    "Returns all rows from a cursor as a list of dicts"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

@login_required
def student_join_classroom(request):
    if request.method == "POST":
        data = json.loads(request.body)
        class_code = data.get("class_code")
        print("Hello",class_code)
        reg_no = request.user.reg_no

        with connection.cursor() as cursor:
            # Check if classroom exists
            cursor.execute("SELECT id FROM classrooms WHERE class_code = %s", [class_code])
            classroom = cursor.fetchone()

            if not classroom:
                return JsonResponse({"error": "Classroom not found"}, status=404)

            class_id = classroom[0]

            # Check if student is already in the class
            cursor.execute("""
                SELECT id FROM classroom_members 
                WHERE class_id = %s AND reg_no = %s
            """, [class_id, reg_no])
            already_joined = cursor.fetchone()

            if already_joined:
                return JsonResponse({"error": "Already joined the classroom"}, status=400)

            # Add student to classroom
            cursor.execute("""
                INSERT INTO classroom_members (class_id, reg_no, role, joined_at,joined_by)
                VALUES (%s, %s, 'student', NOW(),'manual')
            """, [class_id, reg_no])

            return JsonResponse({"success": "Joined classroom successfully"}, status=200)

    return redirect('classrooms')
def get_student_timetable(request):
    print("User:", request.user)  # Debugging

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # Correctly access the student's attributes
    department = request.user.department
    semester = request.user.semester
    section = request.user.section

    query = """
    SELECT t.day, t.period, t.course_code, c.course_name, t.faculty_id, t.room_no, t.time_slot
    FROM timetable t
    JOIN courses c ON t.course_code = c.course_code
    WHERE t.department = %s AND t.semester = %s AND t.section = %s
    ORDER BY FIELD(t.day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'), t.period
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [department, semester, section])
        timetable_data = cursor.fetchall()

    # Format the response
    formatted_timetable = []
    for row in timetable_data:
        formatted_timetable.append({
            "day": row[0],
            "period": row[1],
            "course_code": row[2],
            "course_name": row[3],  
            "faculty_id": row[4],
            "room_no": row[5],
            "time_slot": row[6],
        })

    return JsonResponse({"timetable": formatted_timetable})

def get_total_quizzes_scheduled(user):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM quizzes 
            WHERE department = %s AND section = %s AND semester = %s
        """, [user.department, user.section, user.semester])
        total_quizzes = cursor.fetchone()[0]
    return total_quizzes

def get_quizzes_attended(user):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM quiz_attempts 
            WHERE user_id = %s
        """, [user.reg_no])
        quizzes_attended = cursor.fetchone()[0]
    return quizzes_attended

def get_quizzes_accuracy(user):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT AVG((marks_obtained / total_marks) * 100) 
            FROM quiz_attempts 
            WHERE user_id = %s
        """, [user.reg_no])
        accuracy = cursor.fetchone()[0]
        if(accuracy is not None):
            accuracy=round(accuracy, 2)
        else:
            accuracy=0.0
        return accuracy

def get_assignments_submitted(user):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM assignment_submissions 
            WHERE reg_no = %s AND status = 'Submitted'
        """, [user.reg_no])
        assignments_submitted = cursor.fetchone()[0]  # Fetch single count value
    return assignments_submitted



def user_logout(request):
    logout(request)  # Clears session and logs out user
    return redirect("/")

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import check_password

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        print(f"🔹 Login attempt - Email: {email}, Role: {role}")

        # Define table and ID field mappings
        table_mapping = {
            "student": ("users", "reg_no"),
            "teacher": ("faculty", "faculty_id"),
            "admin": ("admin", "admin_id"),
        }

        if role not in table_mapping:
            messages.error(request, "❌ Invalid role selected.")
            return redirect("login/")

        table_name, id_field = table_mapping[role]

        # Fetch user data
        with connection.cursor() as cursor:
            if role == "student":
                cursor.execute(
                    f"SELECT id, {id_field}, name, email, password, department, semester, section FROM {table_name} WHERE email=%s",
                    [email],
                )
            elif role == "teacher":
                cursor.execute(
                    f"SELECT id, {id_field}, name, email, password, department FROM {table_name} WHERE email=%s",
                    [email],
                )
            elif role == "admin":
                cursor.execute(
                    f"SELECT id, {id_field}, name, email, password FROM {table_name} WHERE email=%s",
                    [email],
                )

            user = cursor.fetchone()
            print(f"🔹 Fetched user: {user}")

        if not user:
            messages.error(request, "❌ Invalid email or password.")
            print("❌ Error: No user found with this email.")
            return redirect("login/")

        if check_password(password, user[4]):  # Password verification
            print("✅ Password verified")

            # Store session data
            request.session["user_id"] = user[0]  # Store user ID
            request.session["role"] = role  # Store role

            print("🔹 Session Data after Login:", request.session)

            # Redirect paths
            redirect_paths = {
                "student": "/dashboard/",
                "teacher": "/teacher/dashboard/",
                "admin": "/administrator/dashboard/",
            }
            return redirect(redirect_paths[role])
        
        else:
            messages.error(request, "❌ Invalid email or password.")
            print("❌ Error: Password incorrect.")
            return redirect("login/")

    return render(request, "login.html")
@login_required
def quiz_data_api(request):
    user = request.user

    # Fetch quiz data logic (same as before)
    quiz_data = get_quiz_data(user.reg_no)
    print("Quiz Data:", quiz_data)  # Debugging line to check fetched data

    # Process data into correct format
    formatted_data = [
        {
            'quiz_name': quiz['quiz_name'],
            'correct': float(quiz['correct']),
            'attempted': float(quiz['attempted']),
            'wrong': abs(float(quiz['wrong'])),
        }
        for quiz in quiz_data
    ]

    return JsonResponse(formatted_data, safe=False)
@login_required
def assignment_data_api(request):
    user = request.user

    # Fetch and process assignment data
    assignment_data = get_assignment_data(user.reg_no)

    return JsonResponse(assignment_data, safe=False)

def home(request):
     if request.user.is_authenticated :
         redirect_paths = {
                "student": "/dashboard/",
                "teacher": "/teacher/dashboard/",
                "admin": "/administrator/dashboard/"
            }
         return redirect(redirect_paths[request.user.role])
     return render(request,"login.html")
@login_required
def dashboard(request):
    user = request.user

    # Fetching the recent quiz attempts for the dashboard
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                qa.id AS attempt_id,
                q.name AS quiz_name,
                qa.marks_obtained,
                qa.accuracy,
                qa.time_spent,
                qa.status,
                qa.attempt_date,
                qa.total_marks
            FROM 
                quiz_attempts qa
            JOIN 
                quizzes q ON qa.quiz_id = q.quiz_id
            WHERE 
                qa.user_id = %s
            ORDER BY 
                qa.attempt_date DESC
        """, [user.reg_no])

        quiz_attempts = cursor.fetchall()

    # Formatting the quiz attempt data
    quiz_attempts_data = [
        {
            'attempt_id': attempt[0],
            'quiz_name': attempt[1],
            'marks_obtained': attempt[2],
            'accuracy': attempt[3],
            'time_spent': attempt[4],
            'status': attempt[5],
            'attempt_date': attempt[6],
            'total_marks': attempt[7],
        }
        for attempt in quiz_attempts
    ]

    # Fetching the metrics
    total_quizzes = get_total_quizzes_scheduled(user)
    quizzes_attended = get_quizzes_attended(user)
    quizzes_accuracy = get_quizzes_accuracy(user)
    assignments_submitted = get_assignments_submitted(user)
    total_assignments = get_total_assignments_scheduled(user)
    assignments_missed = get_assignments_missed(user)
    recent_assignments = get_recent_assignments(user)    
    # Fetch assignment data (submitted, missed)
    assignment_data = get_assignment_data(user.reg_no)
    print("HI",assignment_data)

    return render(request, 'student/dashboard.html', {
        'quiz_attempts': quiz_attempts_data,
        'total_quizzes': total_quizzes,
        'quizzes_attended': quizzes_attended,
        'quizzes_accuracy': quizzes_accuracy,
        'assignments_submitted': assignments_submitted,
        "total_assignments": total_assignments,
        "assignments_missed": assignments_missed,
        "recent_assignments": recent_assignments,
        "assignment_data":json.dumps(assignment_data),
    })
def get_total_assignments_scheduled(user):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM assignments 
            WHERE department = %s AND semester = %s AND section = %s
        """, [user.department, user.semester, user.section])
        total_assignments = cursor.fetchone()[0]
    return total_assignments

def get_assignments_missed(user):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM assignments a
            LEFT JOIN assignment_submissions s 
            ON a.assignment_id = s.assignment_id AND s.reg_no = %s
            WHERE s.assignment_id IS NULL 
            AND a.department = %s 
            AND a.semester = %s 
            AND a.section = %s
        """, [user.reg_no, user.department, user.semester, user.section])
        assignments_missed = cursor.fetchone()[0]
    return assignments_missed

def get_recent_assignments(user):
    print(user.department)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.assignment_id, a.name, a.due_date, 
                   COALESCE(s.status, 'Not Submitted') AS status
            FROM assignments a
            LEFT JOIN assignment_submissions s 
            ON a.assignment_id = s.assignment_id AND s.reg_no = %s
            WHERE a.department = %s AND a.semester = %s AND a.section = %s
            ORDER BY a.due_date DESC LIMIT 5
        """, [user.reg_no, user.department, user.semester, user.section])
        recent_assignments = cursor.fetchall()
    
    formatted_assignments = [
        {
            "id": row[0],
            "title": row[1],
            "due_date": row[2].strftime("%Y-%m-%d"), 
            "status": row[3]
        }
        for row in recent_assignments
    ]
    return formatted_assignments

def get_assignment_data(user_reg_no):
    # Fetch data for assignments (Submitted, Missed)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM assignment_submissions 
            WHERE reg_no = %s AND status = 'Submitted'
        """, [user_reg_no])
        assignments_submitted = cursor.fetchone()[0]
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM assignment_submissions 
            WHERE reg_no = %s AND status = 'Pending'
        """, [user_reg_no])
        assignments_pending = cursor.fetchone()[0]
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM assignment_submissions 
            WHERE reg_no = %s AND status = 'Late'
        """, [user_reg_no])
        assignments_late = cursor.fetchone()[0]
    assignments = [
        {"pending": assignments_pending, "submitted": assignments_submitted, "late": assignments_late},
        # Add data dynamically based on actual assignment submissions
    ]
    
    # Extract the submitted and missed data for the chart

    
    return assignments
from django.db import connection

def get_quiz_data(user_reg_no):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                q.name AS quiz_name,
                SUM(CASE WHEN qa.status = 'Completed' THEN qa.correct_questions ELSE 0 END) AS correct,
                SUM(CASE WHEN qa.status = 'Completed' THEN (qa.correct_questions+qa.wrong_questions+qa.unattempted) ELSE 0 END) AS attempted,
                SUM(CASE WHEN qa.status = 'Completed' THEN (qa.wrong_questions) ELSE 0 END) AS wrong
            FROM 
                quiz_attempts qa
            JOIN 
                quizzes q ON qa.quiz_id = q.quiz_id
            WHERE 
                qa.user_id = %s
            GROUP BY 
                q.name
            ORDER BY 
                q.name
        """, [user_reg_no])
        
        quiz_data = cursor.fetchall()
    
    # Prepare the data for the chart
    quizzes = []
    for quiz in quiz_data:
        quizzes.append({
            'quiz_name': quiz[0],
            'correct': quiz[1],
            'attempted': quiz[2],
            'wrong': quiz[3],
        })
    
    return quizzes


def student_courses_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # If user is not logged in

    email = request.user.email  # Get email from logged-in user

    # Fetch reg_no from users table
    with connection.cursor() as cursor:
        cursor.execute("SELECT reg_no FROM users WHERE email = %s", [email])
        reg_no_row = cursor.fetchone()

    if not reg_no_row:
        return redirect('login')  # No student found

    reg_no = reg_no_row[0]

    # Fetch enrolled courses
    with connection.cursor() as cursor:
        query = """
            SELECT c.course_name, c.course_code, c.credits
            FROM courses c
            JOIN course_enrollments ce ON c.course_code = ce.course_code
            WHERE ce.reg_no = %s
        """
        cursor.execute(query, [reg_no])
        results = cursor.fetchall()

        courses = []
        for course in results:
            courses.append({
                'course_name': course[0],
                'course_code': course[1],
                'credits': course[2],
            })

        return render(request, 'student/courses.html', {'courses': courses})



@login_required()
def course(request):
    return render(request,"student/courses.html")

@login_required
def attend(request):
    reg_no = request.user.reg_no  # Assuming you're storing student reg_no in session
    attendance_data = []

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.course_name,
                a.course_code,
                COUNT(*) AS total_classes,
                SUM(CASE WHEN a.status = 'P' THEN 1 ELSE 0 END) AS attended,
                SUM(CASE WHEN a.status = 'A' THEN 1 ELSE 0 END) AS absent
            FROM attendance a
            JOIN courses c ON a.course_code = c.course_code
            WHERE a.reg_no = %s
            GROUP BY a.course_code
        """, [reg_no])
        
        rows = cursor.fetchall()
        for course_name, course_code, total, attended, absent in rows:
            percentage = int((attended / total) * 100) if total > 0 else 0
            attendance_data.append({
                "course_name": course_name,
                "course_code": course_code,
                "total": total,
                "attended": attended,
                "absent": absent,
                "percentage": percentage,
                "progress_level": "high" if percentage >= 85 else "medium" if percentage >= 75 else "low"
            })

    return render(request, "student/attend.html", {
        "attendance_data": attendance_data
    })

@login_required()
def profile(request):
    return render(request,"student/profile.html")

@login_required()
def results(request):
    return render(request,"student/results.html")

@login_required
def student_classroom_feed(request, class_code):
    reg_no = request.user.reg_no  # Assuming `request.user` is the student

    with connection.cursor() as cursor:
        # ✅ Check if student is part of the classroom
        cursor.execute("""
            SELECT c.id, c.class_name 
            FROM classrooms c
            JOIN classroom_members cm ON c.id = cm.class_id
            WHERE c.class_code = %s AND cm.reg_no = %s
        """, [class_code, reg_no])
        classroom = cursor.fetchone()

        if not classroom:
            return render(request, "404.html")

        class_id = classroom[0]
        class_name = classroom[1]

        # ✅ Fetch posts
         # Fetch posts
        cursor.execute("""
            SELECT cp.id, cp.title, cp.content, cp.attachment_url, cp.post_type, cp.created_at, f.name ,cp.attachment_title
            FROM classroom_posts cp
            JOIN faculty f ON cp.faculty_id = f.faculty_id
            WHERE cp.class_id = %s
            ORDER BY cp.created_at DESC
        """, [class_id])
        posts = cursor.fetchall()

        # Fetch comments
        cursor.execute("SELECT * FROM classroom_comments ORDER BY commented_at ASC")
        comments = dictfetchall(cursor)

        # Nest replies
        comment_map = {c['id']: {**c, 'replies': []} for c in comments}
        nested_comments = []
        for comment in comment_map.values():
            if comment['parent_id']:
                parent = comment_map.get(comment['parent_id'])
                if parent:
                    parent['replies'].append(comment)
            else:
                nested_comments.append(comment)

        # Comment counts
        comment_counts = defaultdict(int)
        for comment in nested_comments:
            comment_counts[comment['post_id']] += 1

        # Append comment count to posts
        nposts = []
        for post in posts:
            post = list(post)
            post_id = post[0]
            try:
                # Safely parse the attachment_url as JSON
                post[3] = json.loads(post[3]) if post[3] else []
            except json.JSONDecodeError:
                print(f"Invalid JSON format in post ID {post_id}: {post[3]}")
                post[3] = []  # Fallback if JSON is invalid
            post.append(comment_counts.get(post_id, 0))
            nposts.append(post)

        # Debugging: Check the media posts data
        media_posts1 = []
        for post in posts:
            post=list(post)
            print(type(post[3]))
            post[3]=eval(post[3])
            media_posts1.append(post)
        
        media_posts = [post for post in media_posts1 if post[3]]
        print("Media Posts:", media_posts)  # Debugging line to check if media posts are correctly parsed

        # ✅ Fetch members of the classroom
        cursor.execute("""
        SELECT 
            COALESCE(u.name, f.name) AS name,
            COALESCE(u.email, f.email) AS email,
            cm.role,
            cm.joined_at AS joined,
            COALESCE(u.id, f.id) AS id
        FROM classroom_members cm
        LEFT JOIN users u ON cm.reg_no = u.reg_no
        LEFT JOIN faculty f ON cm.faculty_id = f.faculty_id
        WHERE cm.class_id = %s
    """, [class_id])
        members = dictfetchall(cursor)

    return render(request, 'teacher/classroom_feed.html', {
        'posts': nposts,
        'nested_comments': nested_comments,
        'comment_counts': comment_counts,
        'class_code': class_code,
        'class_name': class_name,
        'media_posts': media_posts,
        'members': members,
    })


@login_required()
def classroom(request):
   student_id = request.user.reg_no

   with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.id,
                c.class_code,
                c.class_name,
                c.course_code,
                c.department,
                c.semester,
                c.section,
                c.created_at,
                f.name AS faculty_name,
                COUNT(cm2.id) AS student_count
            FROM classroom_members cm
            JOIN classrooms c ON cm.class_id = c.id
            JOIN faculty f ON c.faculty_id = f.faculty_id
            LEFT JOIN classroom_members cm2 ON cm2.class_id = c.id
            WHERE cm.reg_no = %s
            GROUP BY 
                c.id, c.class_code, c.class_name, c.course_code,
                c.department, c.semester, c.section, c.created_at, f.name
            ORDER BY c.created_at DESC
        """, [student_id])
        classrooms = cursor.fetchall()

   context = {
        'classrooms': classrooms
    }
   return render(request, "student/classroom.html", context)
   

STATES = ['Andhra Pradesh', 'Tamil Nadu', 'Telangana', 'Karnataka', 'Kerala']

@login_required
def student_settings(request):
    user_email = request.user.email

    if request.method == 'POST':
        # Get form data
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        pincode = request.POST.get('pincode')
        new_password = request.POST.get('new_password')

        # Handle password change
        if new_password:
            try:
                user = request.user
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully")
            except Exception as e:
                messages.error(request, f"Error updating password: {str(e)}")

        # Update profile info
        try:
            with connection.cursor() as cursor:
                query = '''
                    UPDATE users
                    SET mobile = %s, address = %s, city = %s, 
                        state = %s, country = %s, pincode = %s
                    WHERE email = %s
                '''
                cursor.execute(query, [
                    mobile, address, city, 
                    state, country, pincode, 
                    user_email
                ])
                messages.success(request, "Profile updated successfully")
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")

        # Use one of these redirect options:
        # Option 1 (if namespace is registered):
        return redirect('students:settings')
        
        # Option 2 (direct path):
        # return redirect('/settings/account/')
        
        # Option 3 (if URL name exists in root urls):
        # return redirect('settings')

    # Fetch student data
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", [user_email])
            columns = [col[0] for col in cursor.description]
            student_data = cursor.fetchone()
        student = dict(zip(columns, student_data)) if student_data else {}
    except Exception as e:
        student = {}
        messages.error(request, f"Error fetching data: {str(e)}")

    return render(request, 'student/settings.html', {
        'student': student,
        'states': STATES
    })

@login_required()
def schedule(request):
    return render(request,"student/schedule.html")
@login_required()
def quiz_list(request):
    return render(request,"student/quiz_list.html")
def settings(request):
    return render(request,"student/settings.html")
@login_required
def get_student_quizzes(request):
    # Assuming the student details are stored in the request or session
    student_department = request.user.department
    student_section = request.user.section
    student_semester = request.user.semester

    if not student_department or not student_section or not student_semester:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    with connection.cursor() as cursor:
        query = """
            SELECT 
    quiz_id,
    name,
    section,
    semester,
    department,
    course_code,
    start_date,
    end_date,
    CASE
        WHEN NOW() < start_date THEN 'Upcoming'
        WHEN NOW() BETWEEN start_date AND end_date THEN 'Active'
        ELSE 'Expired'
    END AS status
FROM quizzes
WHERE department = %s
  AND section = %s
  AND semester = %s
  AND (
      (NOW() < start_date) -- Upcoming quizzes
      OR (NOW() BETWEEN start_date AND end_date) -- Active quizzes
  )
  AND quiz_id NOT IN (
      SELECT DISTINCT quiz_id
      FROM quiz_attempts
      WHERE user_id = %s -- Assuming you filter attempts by student_id
  )
ORDER BY start_date DESC;

        """
        cursor.execute(query, [student_department, student_section, student_semester,request.user.reg_no])
        rows = cursor.fetchall()

    quizzes = []
    for row in rows:
        quizzes.append({
            'id': row[0],
            'title': row[1],
            'section': row[2],
            'semester': row[3],
            'department': row[4],
            'course_code': row[5],
            'start_date': row[6],
            'due_date': row[7],
            'status': row[8],
        })

    return JsonResponse(quizzes, safe=False)
@login_required
def get_attempted_quizzes(request):
    student_id = request.user.reg_no 
    print(student_id)# Or whatever identifies the student
    
    # SQL query to get attempted quizzes with marks and other details
    query = """
        SELECT 
            q.quiz_id AS quiz_id,
            q.name AS quiz_name,
            qa.marks_obtained,
            qa.total_marks,
            qa.correct_questions,
            qa.wrong_questions,
            qa.unattempted,
            qa.accuracy,
            (qa.marks_obtained / qa.total_marks) * 100 AS accuracy_percentage,
            CONCAT('/quizzes/', q.quiz_id, '/summary/') AS summary_url
        FROM quiz_attempts qa
        JOIN quizzes q ON qa.quiz_id = q.quiz_id
        WHERE qa.user_id = %s
            AND qa.status = 'Completed'
        ORDER BY qa.attempt_date DESC;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [student_id])
        rows = cursor.fetchall()

    # Format the rows into a list of dictionaries for easy use in the frontend
    attempted_quizzes = []
    for row in rows:
        attempted_quizzes.append({
            'quiz_id': row[0],
            'quiz_name': row[1],
            'marks_scored': row[2],
            'total_marks': row[3],
            'correct': row[4],
            'wrong': row[5],
            'unattempted': row[6],
            'accuracy': round(row[7], 2),
            'summary_url': row[8]
        })
    
    return JsonResponse(attempted_quizzes, safe=False)