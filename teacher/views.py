from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import json,random,string,datetime
from datetime import date
import uuid,boto3
from django.conf import settings 
from collections import defaultdict
from django.views.decorators.csrf import csrf_protect




from django.http import JsonResponse, HttpResponseForbidden
# Restrict access to teachers only
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

def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "teacher":
            return redirect("/")  # Redirect to home/login page if not a teacher
        return view_func(request, *args, **kwargs)
    return wrapper
def generate_class_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@csrf_exempt
@teacher_required
@login_required
def create_classroom(request):
    if request.method == "POST":
        class_name = request.POST['class_name']
        course_code = request.POST['course_code']
        department = request.POST['department']
        semester = request.POST['semester']
        section = request.POST['section']
        faculty_id = request.user.faculty_id
        class_code = generate_class_code()

        with connection.cursor() as cursor:
            # Step 1: Create classroom
            cursor.execute("""
                INSERT INTO classrooms (class_code, class_name, course_code, faculty_id, department, semester, section, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, [class_code, class_name, course_code, faculty_id, department, semester, section])
            
            # Step 2: Get the classroom ID
            class_id = cursor.lastrowid

            # Step 3: Get students of that dept/sem/sec
            cursor.execute("""
                SELECT reg_no FROM users
                WHERE role = 'student' AND department = %s AND semester = %s AND section = %s
            """, [department, semester, section])
            students = cursor.fetchall()  # e.g., [('2023SS0001',), ('2023SS0002',)]

            # Step 4: Insert into classroom_members for each student
            cursor.execute("""
                    INSERT INTO classroom_members (class_id, faculty_id, role, joined_by, joined_at)
                    VALUES (%s, %s, 'teacher', 'auto', NOW())
                """, [class_id, faculty_id])
            for student in students:
                reg_no = student[0]
                cursor.execute("""
                    INSERT INTO classroom_members (class_id, reg_no, role, joined_by, joined_at)
                    VALUES (%s, %s, 'student', 'auto', NOW())
                """, [class_id, reg_no])

        return redirect('/teacher/management/')

    return render(request, 'teacher/management.html')

@csrf_exempt
@teacher_required
@login_required
def classroom_detail(request, class_code):
    with connection.cursor() as cursor:
        # Fetch classroom info
        cursor.execute("""
            SELECT c.class_name, c.course_code, c.department, c.semester, c.section,
                   f.name AS faculty_name
            FROM classrooms c
            JOIN faculty f ON c.faculty_id = f.faculty_id
            WHERE c.class_code = %s
        """, [class_code])
        classroom = cursor.fetchone()

    if not classroom:
        return render(request, '404.html', status=404)

    context = {
        'class_code': class_code,
        'classroom': {
            'class_name': classroom[0],
            'course_code': classroom[1],
            'department': classroom[2],
            'semester': classroom[3],
            'section': classroom[4],
            'faculty_name': classroom[5],
        }
    }
    return render(request, 'teacher/classroom_detail.html', context)


@csrf_exempt
@login_required
@teacher_required
def delete_classroom(request, class_code):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM classrooms WHERE class_code = %s", [class_code])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'error': 'Classroom not found'}, status=404)
            
            class_id = row[0]
            cursor.execute("DELETE FROM classroom_members WHERE class_id = %s", [class_id])
            cursor.execute("DELETE FROM classrooms WHERE id = %s", [class_id])
        return JsonResponse({'message': 'Classroom deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@login_required
@teacher_required
def edit_classroom(request, class_code):
    if request.method == 'POST':
        class_name = request.POST.get('class_name')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE classrooms
                SET class_name = %s
                WHERE class_code = %s
            """, [class_name, class_code])

        return redirect('/teacher/dashboard/')  # Or wherever you want

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM classrooms WHERE class_code = %s", [class_code])
        classroom = dictfetchone(cursor)

    return render(request, 'teacher/edit_classroom.html', {'classroom': classroom})

@csrf_exempt
@login_required
@teacher_required
def create_post(request, class_code):
    faculty_id = request.user.faculty_id

    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        post_type = request.POST['post_type']
        attachment_title = request.POST['attachment_title']

        # === Handle File Uploads to S3 ===
        files = request.FILES.getlist('attachments')
        file_urls = []

        if files:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )

            for file in files:
                ext = file.name.split('.')[-1]
                s3_key = f'classroom_attachments/{uuid.uuid4()}.{ext}'
                s3.upload_fileobj(
                    file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    s3_key,
                    ExtraArgs={'ContentType': file.content_type}
                )
                url = f"http://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
                file_urls.append(url)

        # Convert to JSON string
        attachment_json = json.dumps(file_urls)

        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM classrooms WHERE class_code = %s", [class_code])
            classroom = cursor.fetchone()

            if classroom:
                class_id = classroom[0]
                cursor.execute("""
                    INSERT INTO classroom_posts 
                    (class_id, faculty_id, title, content, attachment_url, post_type, created_at,attachment_title)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(),%s)
                """, [class_id, faculty_id, title, content, attachment_json, post_type,attachment_title])

        return redirect(f'/teacher/classroom/{class_code}/')

    return render(request, 'teacher/createpost.html', {'class_code': class_code})


@csrf_exempt
@login_required
@csrf_exempt
def submit_comment(request, class_code, post_id):
    if request.method == "POST":
        comment = request.POST.get("content")
        parent_id = request.POST.get("parent_comment_id") or None

        role = request.user.role  # 'student' or 'teacher'
        reg_no = request.user.reg_no if role == 'student' else None
        faculty_id = request.user.faculty_id if role == 'teacher' else None

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO classroom_comments (post_id, reg_no, faculty_id, role, comment, parent_id, commented_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, [post_id, reg_no, faculty_id, role, comment, parent_id])

        return redirect(f'/teacher/classroom/{class_code}/')


@login_required
@teacher_required

def classroom_feed(request, class_code):
    with connection.cursor() as cursor:
        # Get classroom id
        cursor.execute("SELECT id, class_name FROM classrooms WHERE class_code = %s", [class_code])
        classroom = cursor.fetchone()
        if not classroom:
            return render(request, "404.html")

        class_id = classroom[0]
        class_name = classroom[1]

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

@csrf_exempt
@login_required
@teacher_required
def update_post(request,class_code, post_id):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            print("Hello1")
            new_content = request.POST['post_content'].strip()
            new_title = request.POST['post_title'].strip()
            print("Hello1")

            if not new_content:
                return JsonResponse({'status': 'error', 'message': 'Empty content'})

            with connection.cursor() as cursor:
                # Check ownership
                cursor.execute("SELECT faculty_id FROM classroom_posts WHERE id = %s", [post_id])
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({'status': 'error', 'message': 'Post not found'})
                if row[0] != request.user.faculty_id:
                    return HttpResponseForbidden("You are not allowed to edit this post.")

                # Update
                cursor.execute("UPDATE classroom_posts SET content = %s,title=%s WHERE id = %s", [new_content,new_title, post_id])
                return JsonResponse({'status': 'success', 'message': 'Post updated successfully'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
@csrf_exempt
@login_required
@teacher_required
def delete_post(request,class_code, post_id):
    print(request.method)
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                # Check ownership
                cursor.execute("SELECT faculty_id FROM classroom_posts WHERE id = %s", [post_id])
                row = cursor.fetchone()

                if not row:
                    return JsonResponse({'status': 'error', 'message': 'Post not found'})
                if row[0] != request.user.faculty_id:
                    
                    return HttpResponseForbidden("You are not allowed to delete this post.")

                # Delete
                cursor.execute("DELETE FROM classroom_posts WHERE id = %s", [post_id])
                return JsonResponse({'status': 'success', 'message': 'Post deleted successfully'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
@login_required
@teacher_required
def dashboard(request):
    return render(request, "teacher/dashboard.html")

@login_required
@teacher_required
def quizzes(request):
    return render(request, "teacher/quizzes.html")

@login_required
@teacher_required
def performance(request):
    return render(request, "teacher/performance.html")


@login_required
@teacher_required
def schedule(request):
    faculty_id = request.user.faculty_id # assuming this is stored in session
    if not faculty_id:
            return redirect("login")  # or show unauthorized

    cursor = connection.cursor()

    # 1. Get all relevant timetable entries for the faculty
    # 1. Get all relevant timetable entries for the faculty
    cursor.execute("""
    SELECT day, time_slot, period, course_code, room_no, semester, department, section
    FROM timetable
    WHERE faculty_id = %s
    """, [faculty_id])
    timetable_rows = cursor.fetchall()

    # 2. Get distinct time_slots (dynamically)
    cursor.execute("""
        SELECT DISTINCT time_slot
        FROM timetable
        WHERE faculty_id = %s
        ORDER BY time_slot
    """, [faculty_id])
    time_slot_rows = cursor.fetchall()
    time_slots = [row[0] for row in time_slot_rows]

    # 3. Get course code to name mapping
    cursor.execute("SELECT course_code, course_name FROM courses")
    course_map = {row[0]: row[1] for row in cursor.fetchall()}

    # 4. Build a structure: schedule[day][time_slot] = {subject, room, semester, faculty}
    schedule = {}
    for day, time_slot, period, course_code, room_no, semester, department, section in timetable_rows:
        if day not in schedule:
            schedule[day] = {}
        schedule[day][time_slot] = {
            "subject": course_map.get(course_code, course_code),
            "room": room_no,
            "semester": semester,
            "department": department,
            "section": section,
            "faculty": "You"  # can remove later if not needed
        }


    # 5. Fill any missing slots with None
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for day in days:
        if day not in schedule:
            schedule[day] = {}
        for slot in time_slots:
            schedule[day].setdefault(slot, None)

    # 6. Format for laptop view: list of rows with time + classes per day
    table_data = []
    for time in time_slots:
        row = {"time": time, "classes": [schedule[day][time] for day in days]}
        table_data.append(row)

    context = {
        "days": days,
        "days_json": json.dumps(days),
        "time_slots": json.dumps(time_slots),
        "schedule_json": json.dumps(schedule),
        "table_data": table_data,
    }
    print(json.dumps(schedule))

    return render(request, "teacher/schedule.html", context)
@login_required
@teacher_required
def get_teacher_schedule(request):
    faculty_id=request.user.faculty_id
    cursor = connection.cursor()

    # 1. Get all relevant timetable entries for the faculty
    # 1. Get all relevant timetable entries for the faculty
    cursor.execute("""
    SELECT day, time_slot, period, course_code, room_no, semester, department, section
    FROM timetable
    WHERE faculty_id = %s
    """, [faculty_id])
    timetable_rows = cursor.fetchall()

    # 2. Get distinct time_slots (dynamically)
    cursor.execute("""
        SELECT DISTINCT time_slot
        FROM timetable
        WHERE faculty_id = %s
        ORDER BY time_slot
    """, [faculty_id])
    time_slot_rows = cursor.fetchall()
    time_slots = [row[0] for row in time_slot_rows]

    # 3. Get course code to name mapping
    cursor.execute("SELECT course_code, course_name FROM courses")
    course_map = {row[0]: row[1] for row in cursor.fetchall()}

    # 4. Build a structure: schedule[day][time_slot] = {subject, room, semester, faculty}
    schedule = {}
    for day, time_slot, period, course_code, room_no, semester, department, section in timetable_rows:
        if day not in schedule:
            schedule[day] = {}
        schedule[day][time_slot] = {
            "subject": course_map.get(course_code, course_code),
            "room": room_no,
            "semester": semester,
            "department": department,
            "section": section,
            "faculty": "You"  # can remove later if not needed
        }


    # 5. Fill any missing slots with None
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for day in days:
        if day not in schedule:
            schedule[day] = {}
        for slot in time_slots:
            schedule[day].setdefault(slot, None)


    context = {
        "days_json": json.dumps(days),
        "time_slots": json.dumps(time_slots),
        "schedule_json": json.dumps(schedule),
    }

    return JsonResponse(context)

@login_required
@teacher_required
def attendance(request):
     # Date filter
    faculty_id = request.user.faculty_id  # Assuming session contains this
    selected_date = request.GET.get("date")
    selected_type = request.GET.get("type", "manual")

    if selected_date:
        try:
            date_obj = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
        except ValueError:
            date_obj = datetime.date.today()
    else:
        date_obj = datetime.date.today()

    if date_obj > datetime.date.today():
        date_obj = datetime.date.today()

    day_of_week = date_obj.strftime("%A")

    cursor = connection.cursor()
    cursor.execute("""
    SELECT 
        c.course_name,
        t.course_code,
        t.section,
        t.semester,
        t.period AS hour
    FROM timetable t
    JOIN courses c ON t.course_code = c.course_code
    WHERE t.faculty_id = %s AND t.day = %s
    ORDER BY t.period
""", (faculty_id, day_of_week))

    today_courses = cursor.fetchall()
    cursor.close()
    print(today_courses)
    return render(request, "teacher/attendance.html", {
        "today": datetime.date.today().strftime("%Y-%m-%d"),
        "selected_date": date_obj.strftime("%Y-%m-%d"),
        "selected_type": selected_type,
        "today_courses": today_courses
    })
@login_required
@teacher_required
def management(request):
    faculty_id = request.user.faculty_id  # Assuming session contains this

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
                COUNT(cm.id) AS student_count
            FROM classrooms c
            LEFT JOIN classroom_members cm ON c.id = cm.class_id
            WHERE c.faculty_id = %s
            GROUP BY 
                c.id, c.class_code, c.class_name, c.course_code, 
                c.department, c.semester, c.section, c.created_at
            ORDER BY c.created_at DESC
        """, [faculty_id])
        classrooms = cursor.fetchall()

    context = {
        'classrooms': classrooms
    }
    return render(request, "teacher/management.html", context)

@login_required
def lecturer_profile(request):
    # Check if user is a teacher (using your custom middleware attributes)
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        raise PermissionDenied("You don't have permission to view this page")
    
    # Fetch complete lecturer data from database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, faculty_id, name, email, dob, gender, mobile, address,
                   city, state, country, pincode, department, designation,
                   joining_year
            FROM faculty 
            WHERE id = %s
        """, [request.user.id])  # Using id from your middleware user object
        
        row = cursor.fetchone()
        if row is None:
            raise PermissionDenied("Lecturer profile not found.")

        columns = [col[0] for col in cursor.description]
        lecturer_data = dict(zip(columns, row))
    
    # Map database fields to template variables
    context = {
        'lecturer': {
            # Basic Info
            'name': lecturer_data.get('name'),
            'email': lecturer_data.get('email'),
            'address': lecturer_data.get('address'),
            'city': lecturer_data.get('city'),
            'state': lecturer_data.get('state'),
            'zipcode': lecturer_data.get('pincode'),
            'dob': lecturer_data.get('dob'),
            'gender': lecturer_data.get('gender'),
            'mobile': lecturer_data.get('mobile'),
            'country': lecturer_data.get('country'),

            # Academic Info
            'employee_id': lecturer_data.get('faculty_id'),  # faculty_id in DB -> employee_id in template
            'department': lecturer_data.get('department'),
            'designation': lecturer_data.get('designation'),
            'joining_year': lecturer_data.get('joining_year'),

            # Extra Info (placeholder values)
            'qualification': "Not Available",  # Add to faculty table if needed
            'experience': "Not Available",     # Add to faculty table if needed
            'rank': "Not Available"             # Add to faculty table if needed
        }
    }
    
    return render(request, 'teacher/profile.html', context)


def settings_page(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    role = getattr(request.user, 'role', None)
    user_id = getattr(request.user, 'id', None)

    if request.method == 'POST' and role == 'teacher':
        # Get form data
        dob = request.POST.get('dob')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        pincode = request.POST.get('pincode')

        # Update faculty data
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE faculty
                SET dob = %s, mobile = %s, address = %s, city = %s,
                    state = %s, country = %s, pincode = %s
                WHERE id = %s
            """, [dob, mobile, address, city, state, country, pincode, user_id])

        return redirect('teachers:settings')

    user_details = {}
    if role == 'teacher':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, email, faculty_id, department, dob, gender, mobile, 
                       address, country, state, city, pincode, joining_year
                FROM faculty WHERE id = %s
            """, [user_id])
            result = cursor.fetchone()
            if result:
                fields = ["name", "email", "faculty_id", "department", "dob", "gender", 
                          "mobile", "address", "country", "state", "city", "pincode", "joining_year"]
                user_details = dict(zip(fields, result))

    states = ["Andhra Pradesh", "Telangana", "Tamil Nadu", "Karnataka", "Kerala"]  # Add more as needed
    countries = ["India", "Nepal", "Japan", "China", "Nigeria", "Pakistan", "Bangladesh"]
    
    return render(request, 'teacher/settings.html', {
        "faculty": user_details, 
        "states": states,
        "countries": countries
    })

@login_required
@teacher_required
def profile(request):
    return render(request, "teacher/profile.html")
@login_required
@teacher_required
def attendance_entry(request):
    course_code = request.GET.get('code')
    section = request.GET.get('section')
    semester = request.GET.get('sem')
    selected_type = request.GET.get('type')
    selected_date = request.GET.get('date', date.today().isoformat())

    students = []
    course_details = {}

    if course_code and section and semester:
        with connection.cursor() as cursor:
            # Get attendance status (if exists)
            cursor.execute("""
                SELECT reg_no, status 
                FROM attendance 
                WHERE course_code = %s AND section = %s AND semester = %s AND date = %s
            """, [course_code, section, semester, selected_date])
            attendance_data = {row[0]: row[1] for row in cursor.fetchall()}

            # Get students and attach their status
            cursor.execute("""
                SELECT reg_no, name, section 
                FROM users 
                WHERE semester = %s AND section = %s AND department = (
                    SELECT department FROM timetable 
                    WHERE course_code = %s LIMIT 1
                )
                ORDER BY reg_no
            """, [semester, section, course_code])
            raw_students = cursor.fetchall()

            # Merge attendance status (default to 'P')
            students = [(s[0], s[1], s[2], attendance_data.get(s[0], 'P')) for s in raw_students]

            # Get course details
            cursor.execute("""
                SELECT c.course_name, c.course_code, f.name, t.semester 
                FROM timetable t
                JOIN courses c ON t.course_code = c.course_code
                JOIN faculty f ON t.faculty_id = f.faculty_id
                WHERE t.course_code = %s
                LIMIT 1
            """, [course_code])
            result = cursor.fetchone()
            if result:
                course_details = {
                    'course_name': result[0],
                    'course_code': result[1],
                    'faculty_name': result[2],
                    'semester': result[3]
                }

    return render(request, "teacher/attendance_entry.html", {
        'students': students,  # Now includes status
        'course_details': course_details,
        'selected_date': selected_date,
        'section': section,
        'selected_type': selected_type
    })


@csrf_exempt
@login_required
@teacher_required
def save_attendance(request):
    if request.method == "POST":
        data = json.loads(request.body)
        code = data.get("code")
        section = data.get("section")
        semester = data.get("semester")
        date = data.get("date")
        attendance_type = data.get("type")
        students = data.get("students")
        print(students,attendance_type,code,section,semester,date)  

        try:
            with connection.cursor() as cursor:
                for student in students:
                    cursor.execute("""
                        INSERT INTO attendance (reg_no, course_code, date, status, section, semester, type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE status = VALUES(status)
                    """, (
                        student["reg_no"],
                        code,
                        date,
                        student["status"],
                        section,
                        semester,
                        attendance_type
                    ))
            return JsonResponse({"message": "Attendance saved successfully."})
        except Exception as e:
            print(f"Error saving attendance: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)

@teacher_required
@csrf_exempt
def get_faculty_quizzes(request):
    faculty_id = request.user.faculty_id

    if not faculty_id:
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
            WHERE faculty_id = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, [faculty_id])
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
