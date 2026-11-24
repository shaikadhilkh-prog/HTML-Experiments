
from flask import (
    Flask, request, redirect, url_for,
    session, flash, render_template_string
)
import sqlite3
import re
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from functools import wraps

app = Flask(__name__)

# Secret key for session management
app.secret_key = "change-this-to-a-long-random-secret-key"

DATABASE = "users.db"


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# HTML template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Authentication</title>
    <style>
        body {
            font-family: Arial;
            background: #f1f5f9;
            text-align: center;
            padding: 50px;
        }

        .container {
            background: white;
            padding: 30px;
            width: 320px;
            margin: auto;
            border-radius: 10px;
            box-shadow: 0 0 10px #ccc;
        }

        input {
            width: 90%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        button {
            width: 98%;
            padding: 12px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        a {
            color: #2563eb;
            text-decoration: none;
        }

        .message {
            color: red;
            margin: 10px;
        }
    </style>
</head>
<body>

<div class="container">

    <h2>{{ title }}</h2>

    {% with messages = get_flashed_messages() %}
        {% for message in messages %}
            <p class="message">{{ message }}</p>
        {% endfor %}
    {% endwith %}

    {{ content|safe }}

</div>

</body>
</html>
"""


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# Home page
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():

    content = """
    <form method="POST">
        <input type="text" name="name"
               placeholder="Full Name" required>

        <input type="email" name="email"
               placeholder="Email" required>

        <input type="password" name="password"
               placeholder="Password" required minlength="8">

        <button type="submit">Register</button>
    </form>

    <p>Already registered?
    <a href="/login">Login</a></p>
    """

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        # Input validation
        if not name or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return redirect(url_for("register"))

        # Hash password
        hashed_password = generate_password_hash(password)

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )

            conn.commit()
            flash("Registration successful! Please login.")

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email already registered.")

        finally:
            conn.close()

    return render_template_string(
        HTML, title="User Registration", content=content
    )


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    content = """
    <form method="POST">
        <input type="email" name="email"
               placeholder="Email" required>

        <input type="password" name="password"
               placeholder="Password" required>

        <button type="submit">Login</button>
    </form>

    <p>New user?
    <a href="/register">Register</a></p>
    """

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            flash("Login successful!")
            return redirect(url_for("dashboard"))

        else:
            flash("Invalid email or password.")

    return render_template_string(
        HTML, title="User Login", content=content
    )


# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():

    content = f"""
    <h3>Welcome, {session['user_name']}!</h3>
    <p>You have successfully logged in.</p>

    <a href="/logout">
        <button>Logout</button>
    </a>
    """

    return render_template_string(
        HTML, title="Dashboard", content=content
    )


# Logout
@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")

    return redirect(url_for("login"))


# Run application
if __name__ == "__main__":
    create_table()
    app.run(debug=True)
