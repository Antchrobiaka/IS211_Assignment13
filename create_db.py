import sqlite3
DB = 'hw13.db'
SCHEMA = 'schema.sql'

def create_and_seed():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    with open(SCHEMA, 'r') as f:
        c.executescript(f.read())

    # Insert John Smith (if not exists)
    c.execute("SELECT id FROM students WHERE first = ? AND last = ?", ("John", "Smith"))
    if c.fetchone() is None:
        c.execute("INSERT INTO students (first, last) VALUES (?, ?)", ("John", "Smith"))
        john_id = c.lastrowid
    else:
        c.execute("SELECT id FROM students WHERE first = ? AND last = ?", ("John", "Smith"))
        john_id = c.fetchone()[0]

    # Insert one quiz "Python Basics", 5 questions, date 2015-02-05 (ISO format)
    quiz_date = "2015-02-05"
    c.execute("SELECT id FROM quizzes WHERE subject = ? AND quiz_date = ?", ("Python Basics", quiz_date))
    row = c.fetchone()
    if row is None:
        c.execute("INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)",
                  ("Python Basics", 5, quiz_date))
        quiz_id = c.lastrowid
    else:
        quiz_id = row[0]
    c.execute("SELECT id FROM results WHERE student_id = ? AND quiz_id = ?", (john_id, quiz_id))
    if c.fetchone() is None:
        c.execute("INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)",
                  (john_id, quiz_id, 85))

    conn.commit()
    conn.close()
    print(f"Database '{DB}' created/updated and seeded.")

if __name__ == '__main__':create_and_seed()