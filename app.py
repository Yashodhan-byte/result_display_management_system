from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to create a database connection
def get_db_connection():
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host="localhost",  # Update if needed
            user="root",  # Update with your MySQL username
            password="Yashodh@N245",  # Update with your MySQL password
            database="student_management"  # Update with your database name
        )
        
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()

        if conn is None:
            return "Database connection failed", 500

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teachers WHERE email = %s", (email,))
        admin = cursor.fetchone()

        if admin and check_password_hash(admin[2], password):  # Assuming password is stored hashed in the 3rd column
            return redirect(url_for('index'))
        else:
            return "Invalid credentials", 401
    return render_template('admin_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500

        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO teachers (email, password) VALUES (%s, %s)", (email, hashed_password))
            conn.commit()
            return redirect(url_for('admin_login'))
        except Error as e:
            print(f"The error '{e}' occurred")
            return "Registration failed", 400
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/get_student_result', methods=['POST'])
def get_student_result():
    data = request.json
    hall_ticket = data.get('hallTicket')
    student_year = data.get('studentYear')
    student_semester = data.get('studentSemester')

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE hall_ticket = %s", (hall_ticket,))
    student = cursor.fetchone()

    if student:
        cursor.execute("SELECT subject, marks_obtained FROM marks WHERE hall_ticket = %s AND semester = %s", 
                       (hall_ticket, student_semester))
        marks = cursor.fetchall()

        total_marks = sum(mark[1] for mark in marks)
        average_marks = total_marks / len(marks) if marks else 0

        return jsonify({
            'name': student[1],  # Assuming name is in the 2nd column
            'total': total_marks,
            'average': average_marks,
            'marks': marks
        })
    else:
        return jsonify({'error': 'Student not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
