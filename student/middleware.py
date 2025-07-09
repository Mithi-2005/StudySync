from django.contrib.auth.models import AnonymousUser
from django.db import connection

class CustomUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Middleware running...")  # Debugging

        user_id = request.session.get("user_id")
        role = request.session.get("role")

        print(f"Session user_id: {user_id}")  
        print(f"Session role: {role}")  

        if user_id and role:
            # Fetch user details from the database based on role
            with connection.cursor() as cursor:
                if role == "student":
                    cursor.execute("""
                        SELECT id, reg_no, name, email, department, semester, section
                        FROM users WHERE id = %s
                    """, [user_id])
                    user_data = cursor.fetchone()
                    user_keys = ["id", "reg_no", "name", "email", "department", "semester", "section"]

                elif role == "teacher":
                    cursor.execute("""
                        SELECT id, faculty_id, name, email, department
                        FROM faculty WHERE id = %s
                    """, [user_id])
                    user_data = cursor.fetchone()
                    user_keys = ["id", "faculty_id", "name", "email", "department"]

                elif role == "admin":
                    cursor.execute("""
                        SELECT id, admin_id, name, email
                        FROM admin WHERE id = %s
                    """, [user_id])
                    user_data = cursor.fetchone()
                    user_keys = ["id", "admin_id", "name", "email"]

                else:
                    request.user = AnonymousUser()
                    return self.get_response(request)

            if user_data:
                class CustomUser:
                    def __init__(self, **kwargs):
                        for key, value in kwargs.items():
                            setattr(self, key, value)
                        self.role = role
                        self.is_authenticated = True

                # Attach custom user object to request
                user_dict = dict(zip(user_keys, user_data))
                request.user = CustomUser(**user_dict)

                print(f"Custom user created: {getattr(request.user, 'reg_no', getattr(request.user, 'faculty_id', 'N/A'))}")  
            else:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        return self.get_response(request)
