from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('contacts.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create database table
def create_table():
    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# Home page
@app.route('/')
def index():
    return render_template('index.html')


# Handle form submission
@app.route('/submit', methods=['POST'])
def submit():

    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    conn = get_db_connection()

    conn.execute(
        'INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)',
        (name, email, message)
    )

    conn.commit()
    conn.close()

    return '''
        <h2>Thank You!</h2>
        <p>Your message has been submitted successfully.</p>
        <a href="/">Go Back</a>
    '''


if __name__ == '__main__':
    create_table()
    app.run(debug=True)