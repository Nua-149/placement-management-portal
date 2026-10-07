from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

app.secret_key = "placement-portal-secret-key"


def get_db_connection():
    conn = sqlite3.connect("database/placement.db")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():

    conn = get_db_connection()

    student_exists = conn.execute(
        "SELECT id FROM students WHERE email = ?",
        ("student@example.com",)
    ).fetchone()

    if student_exists is None:

        conn.execute(
            """
            INSERT INTO students
            (name, email, branch, cgpa, graduation_year, backlogs)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Demo Student",
                "student@example.com",
                "CSE",
                8.2,
                2027,
                0
            )
        )

    drive_count = conn.execute(
        "SELECT COUNT(*) FROM placement_drives"
    ).fetchone()[0]

    if drive_count == 0:

        conn.execute(
            """
            INSERT INTO placement_drives
            (company, role, min_cgpa, branches, graduation_year, backlogs_allowed)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "ABC Technologies",
                "Software Developer",
                7.5,
                "CSE,ISE",
                2027,
                0
            )
        )

        conn.execute(
            """
            INSERT INTO placement_drives
            (company, role, min_cgpa, branches, graduation_year, backlogs_allowed)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "XYZ Cloud",
                "Cloud Intern",
                8.0,
                "CSE,ISE",
                2027,
                0
            )
        )

    conn.commit()
    conn.close()
# Temporary student data

student = {
    "name": "Demo Student",
    "email": "student@example.com",
    "branch": "CSE",
    "cgpa": 8.2,
    "graduation_year": 2027,
    "backlogs": 0
}


# Temporary placement drives

placement_drives = [
    {
        "id": 1,
        "company": "ABC Technologies",
        "role": "Software Developer",
        "min_cgpa": 7.5,
        "branches": ["CSE", "ISE"],
        "graduation_year": 2027,
        "backlogs_allowed": 0
    },

    {
        "id": 2,
        "company": "XYZ Cloud",
        "role": "Cloud Intern",
        "min_cgpa": 8.0,
        "branches": ["CSE", "ISE"],
        "graduation_year": 2027,
        "backlogs_allowed": 0
    }
]
# Temporary application storage


# Temporary users
users = {
    "student@example.com": {
        "password": "student123",
        "role": "student"
    },

    "admin@example.com": {
        "password": "admin123",
        "role": "admin"
    }
}


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = users.get(email)

        if user and user["password"] == password:

            session["email"] = email
            session["role"] = user["role"]

            if user["role"] == "student":
                return redirect(url_for("student_dashboard"))

            else:
                return redirect(url_for("admin_dashboard"))

        return "Invalid email or password"

    return render_template("login.html")


@app.route("/student")
def student_dashboard():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    return render_template("student_dashboard.html")


@app.route("/admin")
def admin_dashboard():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    return render_template("admin_dashboard.html")

@app.route("/profile")
def profile():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student_from_db = conn.execute(
        "SELECT * FROM students WHERE email = ?",
        ("student@example.com",)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        student=student_from_db
    )


@app.route("/drives")
def drives():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    drives_from_db = conn.execute(
        "SELECT * FROM placement_drives"
    ).fetchall()

    conn.close()

    drives_from_db = [
        dict(drive) for drive in drives_from_db
    ]

    for drive in drives_from_db:
        drive["branches"] = drive["branches"].split(",")

    return render_template(
        "drives.html",
        drives=drives_from_db,
        student=student
    )

@app.route("/apply/<int:drive_id>")
def apply(drive_id):

    if session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    selected_drive = conn.execute(
        "SELECT * FROM placement_drives WHERE id = ?",
        (drive_id,)
    ).fetchone()

    student_from_db = conn.execute(
        "SELECT * FROM students WHERE email = ?",
        ("student@example.com",)
    ).fetchone()

    if selected_drive is None:
        conn.close()
        return "Placement drive not found"

    eligible = True

    if student_from_db["cgpa"] < selected_drive["min_cgpa"]:
        eligible = False

    branches = selected_drive["branches"].split(",")

    if student_from_db["branch"] not in branches:
        eligible = False

    if student_from_db["graduation_year"] != selected_drive["graduation_year"]:
        eligible = False

    if student_from_db["backlogs"] > selected_drive["backlogs_allowed"]:
        eligible = False

    if eligible:

        existing_application = conn.execute(
            """
            SELECT id
            FROM applications
            WHERE student_id = ?
            AND drive_id = ?
            """,
            (
                student_from_db["id"],
                selected_drive["id"]
            )
        ).fetchone()

        if existing_application is not None:

            conn.close()

            return f"""
            <h1>Already Applied</h1>

            <p>
                You have already applied to
                {selected_drive["company"]}.
            </p>

            <a href="/applications">
                View My Applications
            </a>
            """

        conn.execute(
            """
            INSERT INTO applications
            (student_id, drive_id, status)
            VALUES (?, ?, ?)
            """,
            (
                student_from_db["id"],
                selected_drive["id"],
                "Applied"
            )
        )

        conn.commit()
        conn.close()

        return f"""
        <h1>Application Successful!</h1>

        <p>
            You are eligible for
            {selected_drive["company"]}.
        </p>

        <p>
            Role: {selected_drive["role"]}
        </p>

        <p>
            Your application has been submitted.
        </p>

        <a href="/applications">
            View Applications
        </a>
        """

    else:

        conn.close()

        return f"""
        <h1>Not Eligible</h1>

        <p>
            You do not meet the eligibility requirements for
            {selected_drive["company"]}.
        </p>

        <a href="/drives">
            Back to Placement Drives
        </a>
        """


@app.route("/applications")
def applications():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student_applications = conn.execute(
        """
        SELECT
            applications.id,
            students.name AS student_name,
            students.email AS student_email,
            placement_drives.company,
            placement_drives.role,
            applications.status
        FROM applications
        JOIN students
            ON applications.student_id = students.id
        JOIN placement_drives
            ON applications.drive_id = placement_drives.id
        WHERE students.email = ?
        """,
        ("student@example.com",)
    ).fetchall()

    conn.close()

    return render_template(
        "applications.html",
        applications=student_applications
    )

@app.route("/admin/applications")
def admin_applications():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()

    admin_applications_list = conn.execute(
        """
        SELECT
            applications.id,
            students.name AS student_name,
            students.email AS student_email,
            placement_drives.company,
            placement_drives.role,
            applications.status
        FROM applications
        JOIN students
            ON applications.student_id = students.id
        JOIN placement_drives
            ON applications.drive_id = placement_drives.id
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_applications.html",
        applications=admin_applications_list
    )

@app.route("/admin/update-status/<student_email>/<company>", methods=["POST"])
def update_application_status(student_email, company):

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    new_status = request.form["status"]

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE applications
        SET status = ?
        WHERE student_id = (
            SELECT id
            FROM students
            WHERE email = ?
        )
        AND drive_id = (
            SELECT id
            FROM placement_drives
            WHERE company = ?
        )
        """,
        (
            new_status,
            student_email,
            company
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_applications"))

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)