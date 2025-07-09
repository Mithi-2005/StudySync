from django.shortcuts import render, redirect
from django.db import connection  
from django.contrib import messages
from django.contrib.auth.hashers import make_password  # ✅ Import Django's password hasher
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings

def send_login_details(email, name, reg_no, password):
    subject = "Your StudySync Login Details"
    message = f"""
    Hello {name},

    Welcome to StudySync! Below are your login details:

    📌 **Registration No:** {reg_no}
    🔑 **Password:** {password}

    🔗 **Login Here:** http://yourwebsite.com/login/

    Please change your password after logging in.

    Regards,  
    StudySync Team
    """
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return True  # Email sent successfully
    except Exception as e:
        print(f"Error sending email: {e}")
        return False  # Email failed to send
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect

def signup(request):
    if request.method == "POST":
        name = str(request.POST["name"]).upper()
        email = request.POST["email"]
        password = request.POST["password"]
        dob = request.POST["dob"]
        gender = request.POST["gender"]
        mobile = "+" + str(request.POST["mobile_code"]) + " " + str(request.POST["mobile"])
        address = request.POST["address"]
        city = request.POST["city"]
        state = request.POST["state"]
        country = request.POST["country"]
        pincode = request.POST["pincode"]
        hashed_password = make_password(password)

        # Determine if the form is for Student or Faculty based on unique fields
        if "reg_no" in request.POST:  # Student Form Submitted
            reg_no = request.POST["reg_no"]
            section = request.POST["section"]
            department = request.POST["department"]
            admission_year = datetime.now().year
            semester = 1  # Default semester for a new student

            try:
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO users (reg_no, name, email, password, role, dob, gender, mobile, 
                                       address, city, state, country, pincode, semester, section, 
                                       department, admission_year, created_at)
                    VALUES (%s, %s, %s, %s, 'student', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """
                    cursor.execute(sql, (reg_no, name, email, hashed_password, dob, gender, mobile,
                                         address, city, state, country, pincode, semester, section,
                                         department, admission_year))
                    
                    messages.success(request, "Student added successfully!")
                    send_login_details(email, name, reg_no, password)

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")

        elif "faculty_id" in request.POST:  # Faculty Form Submitted
            faculty_id = request.POST["faculty_id"]
            department = request.POST["department"]
            designation = request.POST["designation"]
            joining_year = request.POST["joining_year"]

            try:
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO faculty (faculty_id, name, email, password, dob, gender, mobile, 
                                         address, city, state, country, pincode, department, 
                                         designation, joining_year, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """
                    cursor.execute(sql, (faculty_id, name, email, hashed_password, dob, gender, mobile,
                                         address, city, state, country, pincode, department,
                                         designation, joining_year))
                    
                    messages.success(request, "Faculty added successfully!")
                    send_login_details(email, name, faculty_id, password)

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")

        return redirect("/administrator/adduser")  # Redirect back to form page

    return render(request, "admin/adduser.html")


def generate_student_reg_no(request):
    current_year = datetime.now().year
    latest_reg_no = None

    # Fetch the latest student reg_no from the database
    with connection.cursor() as cursor:
        cursor.execute("SELECT reg_no FROM users WHERE reg_no LIKE %s ORDER BY reg_no DESC LIMIT 1", [f"{current_year}SS%"])
        row = cursor.fetchone()
        if row:
            latest_reg_no = row[0]

    if latest_reg_no:
        last_number = int(latest_reg_no[6:])  # Extracts the last 4-digit student number
        new_number = last_number + 1
    else:
        new_number = 1  # If no student exists, start from 0001

    new_reg_no = f"{current_year}SS{new_number:04d}"  # Format as YYYYSS0001, YYYYSS0002, etc.

    return JsonResponse({"reg_no": new_reg_no})
def generate_faculty_id(request):
    latest_faculty_id = None

    # Fetch the latest faculty ID from the database
    with connection.cursor() as cursor:
        cursor.execute("SELECT faculty_id FROM faculty WHERE faculty_id LIKE 'FAC%' ORDER BY faculty_id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            latest_faculty_id = row[0]

    if latest_faculty_id:
        last_number = int(latest_faculty_id[3:])  # Extract numeric part after 'FAC'
        new_number = last_number + 1
    else:
        new_number = 1  # If no faculty exists, start from FAC001

    new_faculty_id = f"FAC{new_number:03d}"  # Format as FAC001, FAC002, FAC003...

    return JsonResponse({"faculty_id": new_faculty_id})
def get_courses(request):
    # Query to fetch course details
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, course_code, course_name FROM courses")
        courses = cursor.fetchall()

    # Format the results into a list of dictionaries
    course_list = [
        {"id": course[0], "course_code": course[1], "course_name": course[2]}
        for course in courses
    ]

    # Return the list as JSON
    return JsonResponse({"courses": course_list})
def get_faculty(request):
    # Query to fetch faculty details
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, faculty_id, name FROM faculty")
        faculty = cursor.fetchall()

    # Format the results into a list of dictionaries
    faculty_list = [
        {"id": f[0], "faculty_id": f[1], "name": f[2]}
        for f in faculty
    ]

    # Return the list as JSON
    return JsonResponse({"faculty": faculty_list})
# ✅ Fetch all departments
def get_departments(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT department_code, department_name FROM departments")
        departments = [{"code": row[0], "name": row[1]} for row in cursor.fetchall()]
    return JsonResponse({"departments": departments})

# ✅ Fetch semesters based on selected department
def get_semesters(request):
    department = request.GET.get("department")
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT semester FROM users WHERE department = %s", [department])
        semesters = [row[0] for row in cursor.fetchall()]
    return JsonResponse({"semesters": semesters})

# ✅ Fetch sections based on department & semester
def get_sections(request):
    department = request.GET.get("department")
    semester = request.GET.get("semester")
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT section FROM users WHERE department = %s AND semester = %s", [department, semester])
        sections = [row[0] for row in cursor.fetchall()]
    return JsonResponse({"sections": sections})

# ✅ Fetch timetable based on department, semester, and section
def get_timetable(request):
    department = request.GET.get("department")
    semester = request.GET.get("semester")
    section = request.GET.get("section")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, day, period, course_code, faculty_id, room_no, time_slot 
            FROM timetable 
            WHERE department = %s AND semester = %s AND section = %s
            ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'), period
        """, [department, semester, section])
        timetable = [
            {"id": row[0], "day": row[1], "period": row[2], "subject": row[3], "faculty_id": row[4], "room_no": row[5], "time_slot": row[6]}
            for row in cursor.fetchall()
        ]
    
    return JsonResponse({"timetable": timetable})

# ✅ Add new timetable slot
@csrf_exempt
def add_timetable(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO timetable (department, semester, section, day, period, course_code, faculty_id, room_no, time_slot) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data["department"], data["semester"], data["section"],
                    data["day"], data["period"], data["subject"],
                    data["faculty_id"], data["room_no"], data["time_slot"]
                ])
            return JsonResponse({"success": True, "message": "Slot added successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
def get_slot(request, slot_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM timetable WHERE id = %s
        """, [slot_id])
        result = cursor.fetchone()
        
        if result:
            slot_data = {
                'id': result[0],
                'department': result[1],
                'semester': result[2],
                'section': result[3],
                'day': result[4],
                'period': result[5],
                'subject': result[6],
                'faculty_id': result[7],
                'room_no': result[8],
                'time_slot': result[9]
            }
            return JsonResponse(slot_data)
        else:
            return JsonResponse({"error": "Slot not found"}, status=404)

def update_slot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        
        slot_id = data.get('id')
        department = data.get('department')
        semester = data.get('semester')
        section = data.get('section')
        day = data.get('day')
        period = data.get('period')
        subject = data.get('subject')
        faculty_id = data.get('faculty_id')
        room_no = data.get('room_no')
        time_slot = data.get('time_slot')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE timetable 
                SET department = %s, semester = %s, section = %s, day = %s, period = %s, 
                    course_code = %s, faculty_id = %s, room_no = %s, time_slot = %s
                WHERE id = %s
            """, [department, semester, section, day, period, subject, faculty_id, room_no, time_slot, slot_id])
            
            if cursor.rowcount > 0:
                return JsonResponse({"success": True, "message": "Slot updated successfully"})
            else:
                return JsonResponse({"error": "Failed to update slot"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def delete_timetable(request, id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM timetable WHERE id = %s", [id])
        return JsonResponse({"success": True, "message": "Slot deleted successfully"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})



# ✅ Fetch courses based on department and semester
# ✅ Fetch all courses
def get_all_courses(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT course_code, course_name, credits FROM courses")
        courses = [{"code": row[0], "name": row[1], "credits": row[2]} for row in cursor.fetchall()]
    return JsonResponse({"courses": courses})



@csrf_exempt
def enroll_students(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            department = data.get("department")
            semester = data.get("semester")
            section = data.get("section")
            course_code = data.get("course_code")

            if not all([department, semester, section, course_code]):
                return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

            with connection.cursor() as cursor:
                # Fetch students who belong to the selected department, semester, and section
                cursor.execute(
                    "SELECT reg_no FROM users WHERE department=%s AND semester=%s AND section=%s",
                    [department, semester, section]
                )
                students = cursor.fetchall()

                if not students:
                    return JsonResponse({"status": "error", "message": "No students found"}, status=404)

                # Insert enrollments into the course_enrollments table
                enrolled_at = datetime.now()
                enrollments = [
                    (reg_no[0], course_code, department, semester, section, enrolled_at)
                    for reg_no in students
                ]

                cursor.executemany(
                    "INSERT INTO course_enrollments (reg_no, course_code, department, semester, section, enrolled_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    enrollments
                )

            return JsonResponse({"status": "success", "message": f"{len(students)} students enrolled successfully"})

        except Exception as e:
            print("Error: ",e)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@csrf_exempt
def get_teachers(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT faculty_id, name, department, designation FROM faculty")
        teachers = cursor.fetchall()
    
    teacher_list = [
        {"id": t[0], "name": t[1], "department": t[2], "designation": t[3]} 
        for t in teachers
    ]
    
    return JsonResponse({"users": teacher_list})

@csrf_exempt
def get_students(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT reg_no, name, department, section, semester FROM users WHERE role = 'student'")
        students = cursor.fetchall()
    
    student_list = [
        {"id": s[0], "name": s[1], "department": s[2], "section": s[3], "semester": s[4]} 
        for s in students
    ]
    
    return JsonResponse({"users": student_list})
def get_user(request, role, user_id):
    table = "faculty" if role == "teachers" else "users"
    id_field = "faculty_id" if role == "teachers" else "reg_no"

    query = f"SELECT * FROM {table} WHERE {id_field} = %s"

    with connection.cursor() as cursor:
        cursor.execute(query, [user_id])
        user = cursor.fetchone()

        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        # Convert fetched row to dictionary
        columns = [col[0] for col in cursor.description]
        user_data = dict(zip(columns, user))

    # Prepare response based on role
    if role == "teachers":
        data = {
            "id": user_data["faculty_id"],
            "name": user_data["name"],
            "email": user_data["email"],
            "department": user_data["department"],
            "designation": user_data["designation"],
            "mobile": user_data["mobile"],
            "address": user_data["address"],
            "city": user_data["city"],
            "state": user_data["state"],
            "country": user_data["country"],
            "pincode": user_data["pincode"]
        }
    else:  # Student
        data = {
            "id": user_data["reg_no"],
            "name": user_data["name"],
            "email": user_data["email"],
            "department": user_data["department"],
            "semester": user_data["semester"],
            "section": user_data["section"],
            "mobile": user_data["mobile"],
            "address": user_data["address"],
            "city": user_data["city"],
            "state": user_data["state"],
            "country": user_data["country"],
            "pincode": user_data["pincode"]
        }

    return JsonResponse(data)
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_user(request, role, user_id):
    if request.method == "POST":
        data = request.POST
        
        if role == "teachers":
            table = "faculty"
            query = f"""
                UPDATE {table} 
                SET name = %s, email = %s, department = %s,
                    mobile = %s, address = %s, city = %s, state = %s, country = %s, pincode = %s
                WHERE faculty_id = %s
            """
            params = [
                data["name"], data["email"], data["department"], 
                data.get("mobile", ""), data.get("address", ""), data.get("city", ""), 
                data.get("state", ""), data.get("country", ""), data.get("pincode", ""), user_id
            ]
        else:  # Student or Admin
            table = "users"
            query = f"""
                UPDATE {table} 
                SET name = %s, email = %s, department = %s,
                    semester = %s, section = %s, mobile = %s, address = %s, 
                    city = %s, state = %s, country = %s, pincode = %s
                WHERE reg_no = %s
            """
            params = [
                data["name"], data["email"], data["department"], 
                data.get("semester", None), data.get("section", None), 
                data.get("mobile", ""), data.get("address", ""), 
                data.get("city", ""), data.get("state", ""), 
                data.get("country", ""), data.get("pincode", ""), user_id
            ]

        with connection.cursor() as cursor:
            cursor.execute(query, params)

        return JsonResponse({"status": "success", "message": "User updated successfully!"})
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

@csrf_exempt
def delete_user(request, role, user_id):
    if request.method == "DELETE":
        table = "faculty" if role == "teachers" else "users"
        id_field = "faculty_id" if role == "teachers" else "reg_no"

        query = f"DELETE FROM {table} WHERE {id_field} = %s"

        with connection.cursor() as cursor:
            cursor.execute(query, [user_id])

        return JsonResponse({"status": "success", "message": "User deleted successfully!"})

def get_courses_json(request):
    department = request.GET.get("department")
    section = request.GET.get("section")
    semester = request.GET.get("semester")

    if not all([department, section, semester]):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT ce.course_code, c.course_name
            FROM course_enrollments ce
            JOIN courses c ON ce.course_code = c.course_code
            WHERE ce.department = %s AND ce.section = %s AND ce.semester = %s
        """, [department, section, semester])
        results = cursor.fetchall()

    courses = [{"code": row[0], "name": row[1]} for row in results]
    return JsonResponse({"courses": courses})

def dashboard(request):
    return render(request, "admin/index.html")
def register(request):
    return render(request, "admin/register.html")
def home(request):
    return render(request, "admin/dashboard.html")
def manage(request):
    return render(request, "admin/manage.html")
def timetable(request):
    return render(request,"admin/timetable.html")
def settingsp(request):
    return render(request,"admin/settings.html")

