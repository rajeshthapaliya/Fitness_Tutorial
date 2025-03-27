from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a strong secret key

DATABASE = "users.db"

# Ensure the database exists
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )"""
        )
        db.commit()

# Initialize the database
init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            session["role"] = user["role"]
            flash("Login successful!", "success")
            return redirect(url_for("videos"))
        else:
            flash("Invalid credentials. Try again.", "danger")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        hashed_password = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            db.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists. Try a different one.", "danger")

    return render_template("register.html")

@app.route("/videos")
def videos():
    if "user" not in session:
        return redirect(url_for("login"))

    # Workouts for each day
    weekly_workouts = {
        "Sunday": [
            {"title": "Legs Workout: Squats & Lunges", "url": "https://www.youtube.com/watch?v=aclHkVaku9U"},
        ],
        "Monday": [
            {"title": "Biceps Workout: Dumbbell Curls & Pull-ups", "url": "https://www.youtube.com/watch?v=av7-8igSXTs"},
        ],
        "Tuesday": [
            {"title": "Chest Workout: Push-ups & Bench Press", "url": "https://www.youtube.com/watch?v=IODxDxX7oi4"},
        ],
        "Wednesday": [
            {"title": "Back Workout: Deadlifts & Rows", "url": "https://www.youtube.com/watch?v=ytGaGIn3SjE"},
        ],
        "Thursday": [
            {"title": "Shoulders Workout: Overhead Press & Lateral Raises", "url": "https://www.youtube.com/watch?v=B-aVuyhvLHU"},
        ],
        "Friday": [
            {"title": "Triceps Workout: Dips & Close-Grip Bench Press", "url": "https://www.youtube.com/watch?v=6kALZikXxLc"},
        ],
        "Saturday": [
            {"title": "Abs Workout: Planks & Crunches", "url": "https://www.youtube.com/watch?v=1f8yoFFnXSE"},
        ],
    }

    return render_template("videos.html", tutorials=weekly_workouts)


@app.route("/admin")
def admin():
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for("videos"))

    return "Welcome, Admin! Here you can manage users."

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("role", None)
    flash("You have logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
