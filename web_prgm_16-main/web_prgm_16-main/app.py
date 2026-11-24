
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database connection
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create table
def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# READ - Display records
@app.route('/')
def index():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template('index.html', students=students)

# CREATE - Add record
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    email = request.form['email']
    course = request.form['course']

    conn = get_db()
    conn.execute(
        "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
        (name, email, course)
    )
    conn.commit()
    conn.close()

    return redirect('/')

# UPDATE - Edit record
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        conn.execute(
            "UPDATE students SET name=?, email=?, course=? WHERE id=?",
            (name, email, course, id)
        )
        conn.commit()
        conn.close()
        return redirect('/')

    student = conn.execute(
        "SELECT * FROM students WHERE id=?", (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found", 404

    return render_template('edit.html', student=student)

# DELETE - Remove record
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
