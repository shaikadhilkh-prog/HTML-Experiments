
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database connection
def get_db():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create database table
def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Display and search employees
@app.route("/")
def index():
    search = request.args.get("search", "").strip()

    conn = get_db()

    if search:
        if search.isdigit():
            employees = conn.execute(
                "SELECT * FROM employees WHERE id=? OR name LIKE ?",
                (int(search), "%" + search + "%")
            ).fetchall()
        else:
            employees = conn.execute(
                "SELECT * FROM employees WHERE name LIKE ?",
                ("%" + search + "%",)
            ).fetchall()
    else:
        employees = conn.execute(
            "SELECT * FROM employees"
        ).fetchall()

    conn.close()

    return render_template("index.html", employees=employees)

# Add employee
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    email = request.form["email"]
    department = request.form["department"]
    salary = request.form["salary"]

    conn = get_db()
    conn.execute("""
        INSERT INTO employees (name, email, department, salary)
        VALUES (?, ?, ?, ?)
    """, (name, email, department, salary))

    conn.commit()
    conn.close()

    return redirect("/")

# Update employee
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
            UPDATE employees
            SET name=?, email=?, department=?, salary=?
            WHERE id=?
        """, (
            request.form["name"],
            request.form["email"],
            request.form["department"],
            request.form["salary"],
            id
        ))

        conn.commit()
        conn.close()
        return redirect("/")

    employee = conn.execute(
        "SELECT * FROM employees WHERE id=?", (id,)
    ).fetchone()

    conn.close()

    if employee is None:
        return "Employee not found", 404

    return render_template("edit.html", employee=employee)

# Delete employee
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM employees WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    create_table()
    app.run(debug=True)
