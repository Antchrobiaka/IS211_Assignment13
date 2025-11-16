# app.py
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

DATABASE = 'hw13.db'
SECRET_KEY = 'devkey-change-this'  # for teaching assignment it's okay; change in real projects

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY=SECRET_KEY)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# simple login_required decorator-like function
def require_login():
    if not session.get('logged_in'):
        flash("Please log in first.", "warning")
        return False
    return True

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid credentials"
            flash(error, 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not require_login():
        return redirect(url_for('login'))
    db = get_db()
    students = db.execute("SELECT id, first, last FROM students ORDER BY id").fetchall()
    quizzes = db.execute("SELECT id, subject, num_questions, quiz_date FROM quizzes ORDER BY id").fetchall()
    # results count per student optionally
    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not require_login():
        return redirect(url_for('login'))
    if request.method == 'POST':
        first = request.form.get('first', '').strip()
        last = request.form.get('last', '').strip()
        if not first or not last:
            flash("First and last name are required.", "danger")
            return render_template('add_student.html', first=first, last=last)
        db = get_db()
        db.execute("INSERT INTO students (first, last) VALUES (?, ?)", (first, last))
        db.commit()
        flash("Student added.", "success")
        return redirect(url_for('dashboard'))
    return render_template('add_student.html')

@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not require_login():
        return redirect(url_for('login'))
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        num_questions = request.form.get('num_questions', '').strip()
        quiz_date = request.form.get('quiz_date', '').strip()  # expect YYYY-MM-DD from <input type="date">
        # Basic validation
        errors = []
        if not subject:
            errors.append("Subject required.")
        try:
            nq = int(num_questions)
            if nq < 0:
                errors.append("Number of questions must be >= 0.")
        except:
            errors.append("Number of questions must be an integer.")
        # ensure date present & parseable
        try:
            datetime.strptime(quiz_date, '%Y-%m-%d')
        except:
            errors.append("Quiz date must be provided in YYYY-MM-DD format.")

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('add_quiz.html', subject=subject, num_questions=num_questions, quiz_date=quiz_date)

        db = get_db()
        db.execute("INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)",
                   (subject, nq, quiz_date))
        db.commit()
        flash("Quiz added.", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_quiz.html')

@app.route('/student/<int:student_id>')
def student_results(student_id):
    if not require_login():
        return redirect(url_for('login'))
    db = get_db()
    student = db.execute("SELECT id, first, last FROM students WHERE id = ?", (student_id,)).fetchone()
    if student is None:
        flash("Student not found.", "danger")
        return redirect(url_for('dashboard'))
    # join to show quiz id, score (optional: include subject and date)
    rows = db.execute("""
        SELECT r.id as result_id, r.quiz_id, r.score, q.subject, q.quiz_date
        FROM results r
        JOIN quizzes q ON r.quiz_id = q.id
        WHERE r.student_id = ?
        ORDER BY q.quiz_date
    """, (student_id,)).fetchall()
    return render_template('student_results.html', student=student, results=rows)

@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not require_login():
        return redirect(url_for('login'))
    db = get_db()
    students = db.execute("SELECT id, first, last FROM students ORDER BY id").fetchall()
    quizzes = db.execute("SELECT id, subject, quiz_date FROM quizzes ORDER BY id").fetchall()

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        quiz_id = request.form.get('quiz_id')
        score = request.form.get('score', '').strip()

        errors = []
        try:
            sid = int(student_id)
        except:
            errors.append("Invalid student selection.")
        try:
            qid = int(quiz_id)
        except:
            errors.append("Invalid quiz selection.")
        try:
            s = int(score)
            if s < 0 or s > 100:
                errors.append("Score must be between 0 and 100.")
        except:
            errors.append("Score must be an integer between 0 and 100.")

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('add_result.html', students=students, quizzes=quizzes,
                                   form_student=student_id, form_quiz=quiz_id, form_score=score)

        # insert, handling UNIQUE constraint
        try:
            db.execute("INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)",
                       (sid, qid, s))
            db.commit()
            flash("Result added.", "success")
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError as e:
            flash("Failed to add result (maybe duplicate or bad reference).", "danger")
            return render_template('add_result.html', students=students, quizzes=quizzes,
                                   form_student=student_id, form_quiz=quiz_id, form_score=score)

    return render_template('add_result.html', students=students, quizzes=quizzes)

# Optional deletion routes (extra credit)
@app.route('/student/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    if not require_login():
        return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    flash("Student deleted (and their results).", "info")
    return redirect(url_for('dashboard'))

@app.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
def delete_quiz(quiz_id):
    if not require_login():
        return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    db.commit()
    flash("Quiz deleted (and associated results).", "info")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
