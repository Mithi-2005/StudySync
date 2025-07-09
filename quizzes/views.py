from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection, transaction
from django.http import Http404, HttpResponse,JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
import uuid, math, time
from datetime import datetime
from django.utils.dateparse import parse_datetime
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from functools import wraps


def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "teacher":
            return redirect("/")  # Redirect to home/login page if not a teacher
        return view_func(request, *args, **kwargs)
    return wrapper


# -----------------------------------------------------
# TEACHER-VISIBLE VIEWS: Create, Edit, Delete, Update
# -----------------------------------------------------

@teacher_required
def create_quiz(request):
    if request.method == 'POST':
        try:
            # Generate a unique quiz code
            unique_quiz_id = uuid.uuid4().hex[:10].upper()
            total_questions = int(request.POST.get('total_questions', 0))
            time_limit = int(request.POST.get('time_limit', 60))
            start_date = parse_datetime(request.POST['start_date'])
            end_date = parse_datetime(request.POST['end_date'])

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO quizzes (
                        name, description, total_marks, start_date, end_date,
                        faculty_id, course_code, department, section,
                        semester, total_questions, time_limit, quiz_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, [
                    request.POST['name'],
                    request.POST['description'],
                    int(request.POST['total_marks']),
                    start_date,
                    end_date,
                    request.user.faculty_id,  # Using logged in teacher's identifier
                    request.POST['course_code'],
                    request.POST['department'],
                    request.POST['section'],
                    int(request.POST['semester']),
                    total_questions,
                    time_limit,
                    unique_quiz_id
                ])

            for i in range(1, total_questions + 1):
                q_text = request.POST.get(f'questions[{i}][text]')
                q_type = request.POST.get(f'questions[{i}][type]')
                marks = int(request.POST.get(f'questions[{i}][marks]', 1))

                if q_type in ['options', 'multi']:
                    option_count = int(request.POST.get(f'questions[{i}][option_count]', 4))
                    options = []
                    if q_type == 'options':
                        correct_option = request.POST.get(f'questions[{i}][correct_option]')
                    else:
                        correct_options = request.POST.getlist(f'questions[{i}][correct_option][]')

                    for j in range(1, option_count + 1):
                        option_text = request.POST.get(f'questions[{i}][option{j}]')
                        if not option_text:
                            continue
                        if q_type == 'options':
                            is_correct = (str(j) == correct_option)
                        else:
                            is_correct = (str(j) in correct_options)
                        options.append({'text': option_text, 'is_correct': is_correct})

                    insert_question({
                        'quiz_id': unique_quiz_id,
                        'question_text': q_text,
                        'question_type': q_type,
                        'options': options,
                        'marks': marks
                    })

                else:
                    correct_answer = request.POST.get(f'questions[{i}][correct_answer]')
                    insert_question({
                        'quiz_id': unique_quiz_id,
                        'question_text': q_text,
                        'question_type': q_type,
                        'correct_answer': correct_answer,
                        'marks': marks
                    })

            messages.success(request, 'Quiz created successfully!')
            return redirect('/teacher/quizzes')

        except Exception as e:
            messages.error(request, f'Error creating quiz: {str(e)}')

    return render(request, 'teacher/create_quiz.html',{'faculty_id': request.user.faculty_id})


def insert_question(data):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO questions (
                quiz_id, question_text, question_type,
                correct_answer, marks
            ) VALUES (%s, %s, %s, %s, %s)
        """, [
            data['quiz_id'],
            data['question_text'],
            data['question_type'],
            data.get('correct_answer'),
            data['marks']
        ])
        question_id = cursor.lastrowid

        if data['question_type'] in ['options', 'multi']:
            for option in data['options']:
                cursor.execute("""
                    INSERT INTO options (
                        question_id, option_text, is_correct
                    ) VALUES (%s, %s, %s)
                """, [
                    question_id,
                    option['text'],
                    option['is_correct']
                ])


@teacher_required
def edit_quiz(request, quiz_id):
    print("Editing quiz with ID:", quiz_id)
    try:
        if request.method == 'POST':
            print("Received POST request to edit quiz")
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE quizzes SET
                        name = %s,
                        description = %s,
                        total_marks = %s,
                        start_date = %s,
                        end_date = %s,
                        faculty_id = %s,
                        course_code = %s,
                        department = %s,
                        section = %s,
                        semester = %s,
                        total_questions = %s
                    WHERE quiz_id = %s
                """, [
                    request.POST['name'],
                    request.POST['description'],
                    int(request.POST['total_marks']),
                    request.POST['start_date'],
                    request.POST['end_date'],
                    request.user.faculty_id,  # Teacher's identifier
                    request.POST['course_code'],
                    request.POST['department'],
                    request.POST['section'],
                    int(request.POST['semester']),
                    int(request.POST['total_questions']),
                    quiz_id
                ])
            messages.success(request, 'Quiz updated successfully!!')
            return redirect('teachers:quiz')

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM quizzes WHERE quiz_id = %s", [quiz_id])
            quiz = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
        if not quiz:
            raise Http404("Quiz does not exist")
        quiz = dict(zip(columns, quiz))
        # Fetch associated questions using the unique quiz_id
        print("Fetched quiz data:", quiz)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM questions WHERE quiz_id = %s", [quiz_id])
            question_rows = cursor.fetchall()
            question_cols = [col[0] for col in cursor.description]
            questions = []
            print("Fetched question rows:", question_rows)
            for question_row in question_rows:
                question = dict(zip(question_cols, question_row))
                if question['question_type'] in ['options', 'multi']:
                    cursor.execute("SELECT * FROM options WHERE question_id = %s", [question['id']])
                    option_rows = cursor.fetchall()
                    option_cols = [col[0] for col in cursor.description]
                    question['options'] = [dict(zip(option_cols, opt_row)) for opt_row in option_rows]
                    print("Fetched options for question:", question['options'])
                else:
                    question['options'] = []
                questions.append(question)
        print("Final questions list:", questions)
        return render(request, 'teacher/edit_quiz.html', {'quiz': quiz, 'questions': questions})
    
    except Exception as e:
        messages.error(request, f'Error editing quiz: {str(e)}')
        print(f"Error: {str(e)}")
        return redirect('teachers:quiz')

@teacher_required
def delete_question(request, question_id, quiz_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM questions WHERE id = %s", [question_id])
                if cursor.rowcount == 0:
                    raise Http404("Question not found")
                messages.success(request, "Question deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting question: {str(e)}")
    return redirect('edit_quiz', quiz_id=quiz_id)

@teacher_required
@teacher_required
def delete_quiz(request, quiz_id):
    try:
        with connection.cursor() as cursor:
            # Step 1: Delete quiz attempt answers related to this quiz's questions
            cursor.execute("""
                DELETE qa FROM quiz_attempt_answers qa
                INNER JOIN questions q ON qa.question_id = q.id
                WHERE q.quiz_id = %s
            """, [quiz_id])

            # Step 2: Delete quiz attempts related to this quiz
            cursor.execute("""
                DELETE FROM quiz_attempts WHERE quiz_id = %s
            """, [quiz_id])

            # Step 3: Delete options related to the quiz's questions
            cursor.execute("""
                DELETE o FROM options o
                INNER JOIN questions q ON o.question_id = q.id
                WHERE q.quiz_id = %s
            """, [quiz_id])

            # Step 4: Delete questions of the quiz
            cursor.execute("""
                DELETE FROM questions WHERE quiz_id = %s
            """, [quiz_id])

            # Step 5: Delete the quiz itself
            cursor.execute("""
                DELETE FROM quizzes WHERE quiz_id = %s
            """, [quiz_id])

            if cursor.rowcount == 0:
                raise Http404("Quiz does not exist")

            messages.success(request, 'Quiz deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting quiz: {str(e)}')

    return JsonResponse({'success': True})



@teacher_required
def update_quiz_questions(request, quiz_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                question_ids = [key.split('_')[-1] for key in request.POST if key.startswith('question_id_')]
                for i in question_ids:
                    q_id = request.POST.get(f'question_id_{i}')
                    question_text = request.POST.get(f'question_text_{i}')
                    question_type = request.POST.get(f'question_type_{i}')
                    marks = int(request.POST.get(f'marks_{i}', 1))

                    if question_type in ['options', 'multi']:
                        cursor.execute("""
                            UPDATE questions
                            SET question_text = %s, question_type = %s, marks = %s, correct_answer = NULL
                            WHERE id = %s
                        """, [question_text, question_type, marks, q_id])

                        cursor.execute("DELETE FROM options WHERE question_id = %s", [q_id])

                        # Count options based on how many exist in the POST
                        option_keys = [key for key in request.POST if key.startswith(f'option_text_{i}_')]
                        option_indices = sorted([int(key.split('_')[-1]) for key in option_keys])

                        for j in option_indices:
                            text = request.POST.get(f'option_text_{i}_{j}')
                            if question_type == 'multi':
                                is_correct = f'is_correct_{i}_{j}' in request.POST
                            elif question_type == 'options':
                                correct_index = request.POST.get(f'is_correct_{i}')
                                print(f"Correct index for question {i}: {correct_index}")
                                is_correct = str(j) == str(correct_index)
                            else:
                                is_correct = False

                            cursor.execute("""
                                INSERT INTO options (question_id, option_text, is_correct)
                                VALUES (%s, %s, %s)
                            """, [q_id, text, is_correct])

                    else:  # For 'blank' type
                        correct_answer = request.POST.get(f'correct_answer_{i}')
                        cursor.execute("""
                            UPDATE questions
                            SET question_text = %s, question_type = %s, correct_answer = %s, marks = %s
                            WHERE id = %s
                        """, [question_text, question_type, correct_answer, marks, q_id])

            messages.success(request, "Questions updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating questions: {str(e)}")
    return redirect('quizzes:edit_quiz', quiz_id=quiz_id)



@login_required
def quiz_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT quiz_id, name, course_code, semester, section, start_date, end_date, total_marks 
            FROM quizzes
        """)
        quizzes = [
            {
                'quiz_id': row[0],
                'id': row[0],
                'name': row[1],
                'course_code': row[2],
                'semester': row[3],
                'section': row[4],
                'start_date': row[5],
                'end_date': row[6],
                'total_marks': row[7],
            }
            for row in cursor.fetchall()
        ]
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})


@login_required
def quiz_detail(request, quiz_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM quizzes WHERE quiz_id = %s", [quiz_id])
        columns = [col[0] for col in cursor.description]
        quiz = cursor.fetchone()
        if not quiz:
            return render(request, 'quiz/quiz_detail.html', {'error': 'Quiz not found'})
        quiz_data = dict(zip(columns, quiz))
        cursor.execute("SELECT * FROM questions WHERE quiz_id = %s", [quiz_id])
        question_rows = cursor.fetchall()
        question_cols = [col[0] for col in cursor.description]
        questions = [dict(zip(question_cols, row)) for row in question_rows]
        for question in questions:
            cursor.execute("SELECT * FROM options WHERE question_id = %s", [question['id']])
            option_rows = cursor.fetchall()
            option_cols = [col[0] for col in cursor.description]
            options = [dict(zip(option_cols, row)) for row in option_rows]
            question['options'] = options
    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz_data,
        'questions': questions
    })
    
@login_required
def get_quiz_by_id(quiz_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM quizzes WHERE quiz_id = %s", [quiz_id])
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))
        return None

@login_required
def attempt_quiz(request, quiz_id):
    user_id = request.user.reg_no

    # Fetch quiz details
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT name, time_limit, total_marks, start_date, end_date FROM quizzes WHERE quiz_id = %s",
            [quiz_id]
        )
        quiz_data = cursor.fetchone()

        if not quiz_data:
            messages.error(request, "Quiz not found.")
            return redirect('student:dashboard')

        quiz_name, time_limit, total_marks, start_date, end_date = quiz_data

        # Handle naive datetime
        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
        if timezone.is_naive(end_date):
            end_date = timezone.make_aware(end_date, timezone.get_current_timezone())

        now = timezone.localtime(timezone.now())
        if now < start_date:
            messages.warning(request, "Quiz hasn't started yet.")
            return redirect('student:dashboard')
        if now > end_date:
            messages.warning(request, "Quiz has expired.")
            return redirect('student:dashboard')

    # POST: Submitting the quiz
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT id, start_time FROM quiz_attempts 
                   WHERE user_id = %s AND quiz_id = %s AND status = 'In-Progress'""",
                [user_id, quiz_id]
            )
            attempt = cursor.fetchone()

            if not attempt:
                messages.error(request, "No active attempt found.")
                return redirect('/')

            attempt_id, start_time = attempt
            if timezone.is_naive(start_time):
                start_time = timezone.make_aware(start_time, timezone.get_current_timezone())

            current_time = timezone.localtime(timezone.now())
            time_spent = int((current_time - start_time).total_seconds())

            if time_spent > (time_limit * 60) + 5:
                messages.warning(request, "Time limit exceeded.")
                return redirect('student:dashboard')

            # Extract and check answers
            answers = {}
            for key in request.POST:
                if key.startswith('question_'):
                    qid = key.split('_')[1]
                    answers[qid] = request.POST.getlist(key)

            correct, wrong, unattempted = 0, 0, 0

            cursor.execute(
                "SELECT id, question_type, correct_answer FROM questions WHERE quiz_id = %s",
                [quiz_id]
            )
            questions = cursor.fetchall()
            total_questions = len(questions)
            marks_per_question = total_marks / total_questions if total_questions else 0

            for qid, q_type, correct_answer in questions:
                qid = str(qid)
                user_ans = answers.get(qid)

                if not user_ans or not any(user_ans):
                    unattempted += 1
                    continue

                if q_type == 'blank':
                    if user_ans[0].strip().lower() == correct_answer.strip().lower():
                        correct += 1
                    else:
                        wrong += 1
                else:
                    cursor.execute(
                        "SELECT option_text FROM options WHERE question_id = %s AND is_correct = TRUE",
                        [qid]
                    )
                    correct_options = sorted([row[0] for row in cursor.fetchall()])
                    user_selected = sorted([ans.strip() for ans in user_ans])
                    if correct_options == user_selected:
                        correct += 1
                    else:
                        wrong += 1

            marks_obtained = round(correct * marks_per_question, 2)
            accuracy = round((correct / total_questions) * 100, 2) if total_questions else 0

            cursor.execute(
                """UPDATE quiz_attempts
                   SET marks_obtained = %s,
                       correct_questions = %s,
                       wrong_questions = %s,
                       time_spent = %s,
                       accuracy = %s,
                       status = 'Completed'
                   WHERE id = %s""",
                [marks_obtained, correct, total_questions - correct, time_spent, accuracy, attempt_id]
            )

        messages.success(request, "Quiz submitted successfully!")
        return redirect('student:quiz_results', quiz_id=quiz_id)

    # GET: Attempting the quiz
    else:
        with connection.cursor() as cursor:
            # Check if quiz is already completed or in-progress
            cursor.execute(
                "SELECT id, status, start_time FROM quiz_attempts WHERE user_id = %s AND quiz_id = %s",
                [user_id, quiz_id]
            )
            existing_attempt = cursor.fetchone()

            if existing_attempt:
                attempt_id, status, start_time = existing_attempt
                if status == 'Completed':
                    messages.info(request, "You've already completed this quiz.")
                    return redirect('/quiz_list')
                elif timezone.is_naive(start_time):
                    start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
            else:
                # No attempt yet, create one
                start_time = timezone.localtime(timezone.now())
                cursor.execute(
                    """INSERT INTO quiz_attempts (quiz_id, user_id, attempt_date, total_marks, status, start_time)
                       VALUES (%s, %s, NOW(), %s, 'In-Progress', %s);""",
                    [quiz_id, user_id, total_marks, start_time]
                )
                cursor.execute("SELECT LAST_INSERT_ID();")
                attempt_id = cursor.fetchone()[0]

            # Time calculation
            elapsed = (timezone.localtime(timezone.now()) - start_time).total_seconds()
            remaining_time = (time_limit * 60) - elapsed

            if remaining_time <= 0:
                cursor.execute("UPDATE quiz_attempts SET status = 'Completed' WHERE id = %s", [attempt_id])
                messages.warning(request, "Time expired for this quiz.")
                return redirect('/')

            # Load questions
            cursor.execute(
                "SELECT id, question_text, question_type FROM questions WHERE quiz_id = %s",
                [quiz_id]
            )
            questions = []
            for q in cursor.fetchall():
                question = {
                    'id': q[0],
                    'text': q[1],
                    'type': q[2],
                    'options': []
                }
                if q[2] != 'blank':
                    cursor.execute(
                        "SELECT option_text FROM options WHERE question_id = %s",
                        [q[0]]
                    )
                    question['options'] = [row[0] for row in cursor.fetchall()]
                questions.append(question)

        return render(request, 'student/attempt_quiz.html', {
            'quiz': {
                'id': quiz_id,
                'name': quiz_name,
                'time_limit': time_limit,
                'total_marks': total_marks
            },
            'questions': questions,
            'remaining_time': int(remaining_time),
            'start_time': start_time.timestamp(),
            'quiz_id': quiz_id
        })


@transaction.atomic
@login_required
def start_quiz(request, quiz_id):
    if request.method == 'POST':
        user_id = request.user.reg_no
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT quiz_id, total_marks FROM quizzes WHERE quiz_id = %s",
                [quiz_id]
            )
            quiz = cursor.fetchone()
            if not quiz:
                raise Http404("Quiz not found")
            total_marks = quiz[1]
            cursor.execute(
                "SELECT id, status FROM quiz_attempts WHERE user_id = %s AND quiz_id = %s AND status IN ('In-Progress', 'Completed') LIMIT 1",
                [user_id, quiz_id]
            )
            existing_attempt = cursor.fetchone()
            if existing_attempt:
                if existing_attempt[1] == 'In-Progress':
                    return redirect('quizzes:attempt_quiz', quiz_id=quiz_id)
                messages.warning(request, 'You already attempted this quiz')
                return redirect('/quiz_list')
            now = timezone.localtime(timezone.now())
            cursor.execute(
                """INSERT INTO quiz_attempts 
                   (quiz_id, user_id, attempt_date, total_marks, marks_obtained, status, start_time)
                   VALUES (%s, %s, NOW(), %s, 0, 'In-Progress', %s)""",
                [quiz_id, user_id, total_marks, now]
            )
        return redirect('quizzes:attempt_quiz', quiz_id=quiz_id)
    return redirect('quiz_overview', quiz_id=quiz_id)

@login_required
def quiz_overview(request, quiz_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT quiz_id, name, description, course_code, department, "
                "semester, time_limit, total_marks, end_date "
                "FROM quizzes WHERE quiz_id = %s",
                [quiz_id]
            )
            row = cursor.fetchone()
            if not row:
                raise Http404("Quiz not found")
            
            quiz = {
                'quiz_id': row[0],
                'name': row[1],
                'description': row[2],
                'course_code': row[3],
                'department': row[4],
                'semester': row[5],
                'time_limit': row[6],
                'total_marks': row[7],
                'end_date': row[8]
            }
    except Exception as e:
        messages.error(request, f"Error loading quiz: {str(e)}")
        return redirect('teachers:quiz')
    
    return render(request, 'student/quiz_overview.html', {'quiz': quiz})

@transaction.atomic
@login_required
def submit_quiz(request, quiz_id):
    user_id = request.user.reg_no
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT quiz_id, total_marks FROM quizzes WHERE quiz_id = %s",
            [quiz_id]
        )
        quiz = cursor.fetchone()
        if not quiz:
            raise Http404("Quiz not found")
        total_marks = quiz[1]
        cursor.execute(
            """SELECT id, start_time FROM quiz_attempts 
               WHERE user_id = %s AND quiz_id = %s AND status = 'In-Progress'""",
            [user_id, quiz_id]
        )
        attempt = cursor.fetchone()
        if not attempt:
            raise Http404("No active quiz attempt found")
        attempt_id, start_time = attempt
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
        current_time = timezone.localtime(timezone.now())
        time_spent = int((current_time - start_time).total_seconds())
        answers = {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                qid = key.split('_')[1]
                answers[qid] = request.POST.getlist(key)
        correct = 0
        wrong = 0
        unattempted = 0
        cursor.execute(
            "SELECT id, question_type, correct_answer FROM questions WHERE quiz_id = %s",
            [quiz_id]
        )
        questions = cursor.fetchall()
        total_questions = len(questions)
        marks_per_question = total_marks / total_questions if total_questions else 0
        for q in questions:
            qid, q_type, correct_answer = str(q[0]), q[1], q[2]
            user_ans = answers.get(qid)
            is_correct = False
            if not user_ans or not any(user_ans):
                unattempted += 1
            else:
                if q_type == 'blank':
                    if user_ans[0].strip().lower() == correct_answer.strip().lower():
                        is_correct = True
                else:
                    cursor.execute(
                        """SELECT option_text FROM options 
                           WHERE question_id = %s AND is_correct = TRUE""",
                        [qid]
                    )
                    correct_options = sorted([row[0] for row in cursor.fetchall()])
                    user_selected = sorted([ans.strip() for ans in user_ans])
                    if correct_options == user_selected:
                        is_correct = True
            if is_correct:
                correct += 1
            else:
                wrong += 1
            cursor.execute(
                """INSERT INTO quiz_attempt_answers (attempt_id, question_id, selected_option_ids, text_answer, is_correct)
                   VALUES (%s, %s, %s, %s, %s)""",
                [attempt_id, qid, ','.join(user_ans), user_ans[0] if q_type == 'blank' else None, 1 if is_correct else 0]
            )
        marks_obtained = round(correct * marks_per_question, 2)
        accuracy = round((correct / total_questions) * 100, 2) if total_questions else 0
        cursor.execute(
            """UPDATE quiz_attempts SET
               marks_obtained = %s, correct_questions = %s, wrong_questions = %s, time_spent = %s,
               accuracy = %s, status = 'Completed'
               WHERE id = %s""",
            [marks_obtained, correct, total_questions - correct, time_spent, accuracy, attempt_id]
        )
    return redirect('quizzes:quiz_result', quiz_id=quiz_id)

@login_required
def quiz_result(request, quiz_id):
    user_id = request.user.reg_no
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT qa.id, q.name, qa.marks_obtained, qa.total_marks, qa.accuracy,
                   qa.time_spent, qa.correct_questions, qa.wrong_questions, qa.unattempted
            FROM quiz_attempts qa
            JOIN quizzes q ON qa.quiz_id = q.quiz_id
            WHERE qa.quiz_id = %s AND qa.user_id = %s AND qa.status = 'Completed'
            ORDER BY qa.attempt_date DESC
            LIMIT 1
            """,
            [quiz_id, user_id]
        )
        result = cursor.fetchone()
        if not result:
            messages.error(request, "Result not found")
            return redirect("teachers:quiz")
        attempt_id, quiz_name, marks_obtained, total_marks, accuracy, time_spent, correct, wrong, unattempted = result
        minutes = time_spent // 60
        seconds = time_spent % 60
        time_spent_formatted = f"{minutes}m {seconds}s"
        context = {
            "quiz_name": quiz_name,
            "marks_obtained": marks_obtained,
            "total_marks": total_marks,
            "accuracy": accuracy,
            "time_spent": time_spent_formatted,
            "correct": correct,
            "wrong": wrong,
            "unattempted": unattempted,
            "percentage": round((marks_obtained / total_marks) * 100, 2) if total_marks else 0,
            'quiz_id': quiz_id,
        }
    return render(request, 'student/quiz_result.html', context)


@login_required
def quiz_summary(request, quiz_id):
    user_id = request.user.reg_no
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name as quiz_name, total_marks
            FROM quizzes
            WHERE quiz_id = %s
        """, [quiz_id])
        quiz = cursor.fetchone()
        if not quiz:
            return render(request, 'student/quiz_summary.html', {'error': 'Quiz not found.'})
        quiz_name, total_marks = quiz
        cursor.execute("""
            SELECT id, marks_obtained
            FROM quiz_attempts
            WHERE quiz_id = %s AND user_id = %s
            ORDER BY attempt_date DESC
            LIMIT 1
        """, [quiz_id, user_id])
        attempt = cursor.fetchone()
        if not attempt:
            return render(request, 'quiz/quiz_summary.html', {'error': 'No attempt found for this user.'})
        attempt_id = attempt[0]
        marks_obtained = float(attempt[1])
        cursor.execute("""
            SELECT id, question_text, question_type, correct_answer, marks
            FROM questions
            WHERE quiz_id = %s
        """, [quiz_id])
        questions = cursor.fetchall()
        summary = []
        correct_count = 0
        wrong_count = 0
        unattempted_count = 0
        for q_id, q_text, q_type, correct_text_answer, q_marks in questions:
            print(f"Processing question ID: {q_id}, Type: {q_type}, Marks: {q_marks}")
            cursor.execute("""
                SELECT selected_option_ids, text_answer
                FROM quiz_attempt_answers
                WHERE question_id = %s AND attempt_id = %s
            """, [q_id, attempt_id])
            answer_data = cursor.fetchone()
            selected_values = []
            student_text_answer = None
            marks_for_question = 0
            is_correct = False
            attempted = True
            if answer_data:
                selected_option_ids, student_text_answer = answer_data
                if not selected_option_ids and not student_text_answer:
                    attempted = False
            else:
                attempted = False
            if not attempted:
                unattempted_count += 1
                summary.append({
                    'question_text': q_text,
                    'text_answer': None,
                    'correct_answer': correct_text_answer if q_type in ['text', 'blank'] else None,
                    'options': [],
                    'marks_awarded': 0,
                    'total_marks': q_marks,
                    'attempted': False
                })
                continue
            if selected_option_ids:
                selected_values = [opt.strip() for opt in selected_option_ids.split(',')]
            if q_type in ['text', 'blank']:
                is_correct = student_text_answer.strip().lower() == correct_text_answer.strip().lower()
                if is_correct:
                    marks_for_question = q_marks
                    correct_count += 1
                else:
                    wrong_count += 1
                summary.append({
                    'question_text': q_text,
                    'text_answer': student_text_answer,
                    'correct_answer': correct_text_answer,
                    'options': [],
                    'marks_awarded': marks_for_question,
                    'total_marks': q_marks,
                    'attempted': True
                })
            else:
                cursor.execute("""
                    SELECT option_text, is_correct
                    FROM options
                    WHERE question_id = %s
                """, [q_id])
                options_data = cursor.fetchall()
                options = []
                correct_options = {opt.strip() for opt, correct in options_data if correct}
                selected_set = set(selected_values)
                is_correct = correct_options == selected_set
                if is_correct:
                    marks_for_question = q_marks
                    correct_count += 1
                else:
                    wrong_count += 1
                for option_text, correct in options_data:
                    is_selected = option_text.strip() in selected_values
                    icon = ''
                    if correct:
                        icon = '✅'
                    if is_selected and not correct:
                        icon = '❌'
                    options.append({
                        'text': option_text,
                        'is_selected': is_selected,
                        'is_correct': bool(correct),
                        'icon': icon
                    })
                summary.append({
                    'question_text': q_text,
                    'text_answer': None,
                    'correct_answer': None,
                    'options': options,
                    'marks_awarded': marks_for_question,
                    'total_marks': q_marks,
                    'attempted': True
                })
        percentage = (marks_obtained / total_marks) * 100 if total_marks > 0 else 0
        circumference = 2 * math.pi * 64  # ~402.12
        offset = circumference * (1 - (percentage / 100))
        print(f"Offset: {offset}, Percentage: {percentage}")
        print(summary)
    return render(request, 'student/quiz_summary.html', {
        'quiz_name': quiz_name,
        'quiz_id': quiz_id,
        'total_marks': total_marks,
        'marks_obtained': marks_obtained,
        'offset': offset,
        'percentage': percentage,
        'summary': summary,
        'correct_count': correct_count,
        'wrong_count': wrong_count,
        'unattempted_count': unattempted_count
    })
@csrf_exempt
@teacher_required
@login_required
def go_create_quiz(request):
    if request.method == "POST":
        quizData={
            'title':request.POST.get("title"),
            'description':request.POST.get("description"),
            'start_date':request.POST.get("start_date"),
            'end_date':request.POST.get("end_date"),
            'question_count':request.POST.get("questions"),
            'faculty_id':request.user.faculty_id,
        }
        request.session['quiz_data'] = quizData
        print("Quiz data stored in session:", quizData)
        print(request.session['quiz_data'])
        return JsonResponse({
            'success': True,
            'redirect_url': '/quizzes/create-quiz-details/'  # Redirect to the next page
        })
    return JsonResponse({'success': False, 'error': 'Error creating quiz'})    
@teacher_required
def create_quiz_details(request):
    quiz_data = request.session.get('quiz_data', None)
    print("Quiz data from session:", quiz_data)
    if not quiz_data:
        return redirect('/')  

    if request.method == "POST":
        return redirect('/quizzes/') 

    context = quiz_data.copy()
    context['faculty_id'] = request.user.faculty_id
    return render(request, 'teacher/create_quiz.html', context)
@teacher_required
def get_departments(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT department FROM timetable WHERE faculty_id = %s", [request.user.faculty_id])
        departments = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'departments': departments})

@teacher_required
def get_semesters(request):
    dept = request.GET.get("department")
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT semester FROM timetable WHERE department = %s and faculty_id=%s", [dept, request.user.faculty_id])
        semesters = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'semesters': semesters})


def get_courses(request):
    dept = request.GET.get("department")
    sem = request.GET.get("semester")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT course_code FROM timetable
            WHERE department = %s AND semester = %s AND faculty_id = %s
        """, [dept, sem,request.user.faculty_id])
        courses = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'courses': courses})


def get_sections(request):
    dept = request.GET.get("department")
    sem = request.GET.get("semester")
    course = request.GET.get("course")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT section FROM timetable
            WHERE department = %s AND semester = %s AND course_code = %s AND faculty_id = %s
        """, [dept, sem, course, request.user.faculty_id])
        sections = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'sections': sections})

@teacher_required
def get_all_quiz_responses(request):
    faculty_id = request.user.faculty_id
    if not faculty_id:
        return JsonResponse({"error": "Faculty ID not provided"}, status=400)

    # Grab the quiz_id from the query parameters. Default to "all"
    quiz_id = request.GET.get("quiz_id", "all")

    with connection.cursor() as cursor:
        # If a specific quiz_id is provided, add an extra WHERE clause to filter.
        if quiz_id == "all":
            cursor.execute("""
                SELECT
                    s.reg_no,
                    s.name,
                    qa.marks_obtained,
                    qa.total_marks,
                    qa.accuracy,
                    qa.quiz_id,
                    qa.id AS response_id,
                    q.name
                FROM quiz_attempts qa
                INNER JOIN quizzes q ON qa.quiz_id = q.quiz_id
                INNER JOIN users s ON qa.user_id = s.reg_no
                WHERE q.faculty_id = %s
            """, [faculty_id])
        else:
            cursor.execute("""
                SELECT
                    s.reg_no,
                    s.name,
                    qa.marks_obtained,
                    qa.total_marks,
                    qa.accuracy,
                    qa.quiz_id,
                    qa.id AS response_id,
                    q.name
                FROM quiz_attempts qa
                INNER JOIN quizzes q ON qa.quiz_id = q.quiz_id
                INNER JOIN users s ON qa.user_id = s.reg_no
                WHERE q.faculty_id = %s AND q.quiz_id = %s
            """, [faculty_id, quiz_id])
        rows = cursor.fetchall()

    responses = []
    for row in rows:
        responses.append({
            "reg_no": row[0],
            "name": row[1],
            "marks": f"{row[2]}/{row[3]}",
            "accuracy": f"{row[4]}%",
            "quiz_id": row[5],
            "response_id": row[6],
            "quiz_name": row[7],
        })

    return JsonResponse({"responses": responses})


@login_required
@teacher_required
def student_summary(request, quiz_id,reg_no):
    user_id = reg_no
    student_name=" "
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name 
            FROM users
            WHERE reg_no = %s
            """, [user_id])
        st = cursor.fetchone()
        student_name = st[0] if st else None
        cursor.execute("""
            SELECT name as quiz_name ,total_marks
            FROM quizzes
            WHERE quiz_id = %s
            """, [quiz_id])
        quiz = cursor.fetchone()
        if not quiz:
            return render(request, 'teacher/student_summary.html', {'error': 'Quiz not found.'})
        quiz_name, total_marks = quiz
        cursor.execute("""
            SELECT id, marks_obtained
            FROM quiz_attempts
            WHERE quiz_id = %s AND user_id = %s
            ORDER BY attempt_date DESC
            LIMIT 1
        """, [quiz_id, user_id])
        attempt = cursor.fetchone()
        if not attempt:
            return render(request, 'teacher/quizzes.html', {'error': 'No attempt found for this user.'})
        attempt_id = attempt[0]
        marks_obtained = float(attempt[1])
        cursor.execute("""
            SELECT id, question_text, question_type, correct_answer, marks
            FROM questions
            WHERE quiz_id = %s
        """, [quiz_id])
        questions = cursor.fetchall()
        summary = []
        correct_count = 0
        wrong_count = 0
        unattempted_count = 0
        for q_id, q_text, q_type, correct_text_answer, q_marks in questions:
            print(f"Processing question ID: {q_id}, Type: {q_type}, Marks: {q_marks}")
            cursor.execute("""
                SELECT selected_option_ids, text_answer
                FROM quiz_attempt_answers
                WHERE question_id = %s AND attempt_id = %s
            """, [q_id, attempt_id])
            answer_data = cursor.fetchone()
            selected_values = []
            student_text_answer = None
            marks_for_question = 0
            is_correct = False
            attempted = True
            if answer_data:
                selected_option_ids, student_text_answer = answer_data
                if not selected_option_ids and not student_text_answer:
                    attempted = False
            else:
                attempted = False
            if not attempted:
                unattempted_count += 1
                summary.append({
                    'question_text': q_text,
                    'text_answer': None,
                    'correct_answer': correct_text_answer if q_type in ['text', 'blank'] else None,
                    'options': [],
                    'marks_awarded': 0,
                    'total_marks': q_marks,
                    'attempted': False
                })
                continue
            if selected_option_ids:
                selected_values = [opt.strip() for opt in selected_option_ids.split(',')]
            if q_type in ['text', 'blank']:
                is_correct = student_text_answer.strip().lower() == correct_text_answer.strip().lower()
                if is_correct:
                    marks_for_question = q_marks
                    correct_count += 1
                else:
                    wrong_count += 1
                summary.append({
                    'question_text': q_text,
                    'text_answer': student_text_answer,
                    'correct_answer': correct_text_answer,
                    'options': [],
                    'marks_awarded': marks_for_question,
                    'total_marks': q_marks,
                    'attempted': True
                })
            else:
                cursor.execute("""
                    SELECT option_text, is_correct
                    FROM options
                    WHERE question_id = %s
                """, [q_id])
                options_data = cursor.fetchall()
                options = []
                correct_options = {opt.strip() for opt, correct in options_data if correct}
                selected_set = set(selected_values)
                is_correct = correct_options == selected_set
                if is_correct:
                    marks_for_question = q_marks
                    correct_count += 1
                else:
                    wrong_count += 1
                for option_text, correct in options_data:
                    is_selected = option_text.strip() in selected_values
                    icon = ''
                    if correct:
                        icon = '✅'
                    if is_selected and not correct:
                        icon = '❌'
                    options.append({
                        'text': option_text,
                        'is_selected': is_selected,
                        'is_correct': bool(correct),
                        'icon': icon
                    })
                summary.append({
                    'question_text': q_text,
                    'text_answer': None,
                    'correct_answer': None,
                    'options': options,
                    'marks_awarded': marks_for_question,
                    'total_marks': q_marks,
                    'attempted': True
                })
        percentage = (marks_obtained / total_marks) * 100 if total_marks > 0 else 0
        circumference = 2 * math.pi * 64  # ~402.12
        offset = circumference * (1 - (percentage / 100))
        print(f"Offset: {offset}, Percentage: {percentage}")
        print(summary)
    return render(request, 'teacher/student_summary.html', {
        'quiz_name': quiz_name,
        'quiz_id': quiz_id,
        'total_marks': total_marks,
        'marks_obtained': marks_obtained,
        'offset':offset,
        "student_name": student_name, 
        'percentage': percentage,
        'summary': summary,
        'correct_count': correct_count,
        'wrong_count': wrong_count,
        'unattempted_count': unattempted_count,
        'reg_no': reg_no,
    })