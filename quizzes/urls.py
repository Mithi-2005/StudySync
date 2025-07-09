# quizzes/urls.py

from django.urls import path
from . import views

app_name = 'quizzes'  # Optional but useful for namespacing

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('create/', views.create_quiz, name='create_quiz'),
    path('go/create/', views.go_create_quiz, name='create_quiz_page'),
    path('create-quiz-details/', views.create_quiz_details, name='create_quiz_page'),
    path('edit/<str:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('delete/<str:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('detail/<str:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('delete-question/<int:question_id>/<str:quiz_id>/', views.delete_question, name='delete_question'),
    path('<str:quiz_id>/update-questions/', views.update_quiz_questions, name='update_quiz_questions'),
    path('<str:quiz_id>/overview/', views.quiz_overview, name='quiz_overview'),
    path('<str:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('<str:quiz_id>/attempt/', views.attempt_quiz, name='attempt_quiz'),
    path('<str:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('<str:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('<str:quiz_id>/summary/', views.quiz_summary, name='quiz_summary'),
    path('<str:quiz_id>/<str:reg_no>/summary/', views.student_summary, name='student_summary'),
    path('get_responses/', views.get_all_quiz_responses, name='get_quiz_responses'),
    path('get_departments/', views.get_departments),
    path('get_semesters/', views.get_semesters),
    path('get_courses/', views.get_courses),
    path('get_sections/', views.get_sections),
]
