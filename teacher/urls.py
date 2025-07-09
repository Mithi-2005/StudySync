from django.urls import path
from . import views
app_name = "teachers"

urlpatterns=[
    path("",views.dashboard,name="home"),
    path("dashboard/",views.dashboard,name="index"),
    path("profile/", views.lecturer_profile, name="profile"),
    path("attendance_entry/",views.attendance_entry,name="attendance_entry"),
    path("quizzes/",views.quizzes,name="quiz"),
    path("performance/",views.performance,name="performance"),
    path("attendance/",views.attendance,name="attendance"),
    path("save_attendance/", views.save_attendance, name="save_attendance"),
    path("schedule/",views.schedule,name="schedule"),
    path("management/",views.management,name="management"),
    path("get_quizzes/",views.get_faculty_quizzes,name="faculty_quizzes"),
    path("settings/", views.settings_page, name="settings"),
    path("create_classroom/",views.create_classroom,name="create"),
    path("get_teacher_schedule/",views.get_teacher_schedule,name="get_timetable"),
    path('classroom/<str:class_code>/', views.classroom_feed, name='classroom_detail'),
    path('classroom/<str:class_code>/post/', views.create_post, name='create_post'),
    path('classroom/<str:class_code>/post/<int:post_id>/comment/', views.submit_comment, name='add_comment'),
    path('classroom/<str:class_code>/delete/', views.delete_classroom, name='delete_classroom'),
    path('classroom/<str:class_code>/edit/', views.edit_classroom, name='edit_classroom'),
    path('classroom/<str:class_code>/post/update/<int:post_id>/', views.update_post, name='update_post'),
    path('classroom/<str:class_code>/post/delete/<int:post_id>/', views.delete_post, name='delete_post'),

]