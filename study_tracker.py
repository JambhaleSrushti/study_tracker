import sqlite3
from datetime import date, timedelta


DB_FILE = "study_tracker.db"


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    # Study sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            duration INTEGER NOT NULL
        )
    """)

    # Old overall daily goal.
    # We keep this table because the desktop GUI still uses it.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            daily_goal_minutes INTEGER
        )
    """)

    # Check whether subjects table already existed.
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'subjects'
    """)

    subjects_table_exists = cursor.fetchone() is not None

    # Managed subjects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL COLLATE NOCASE UNIQUE,
            daily_goal_minutes INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Only the FIRST time we create the subjects table,
    # import subjects from historical study sessions.
    #
    # This is important because if a user later removes a subject,
    # we do not want it to return every time the app starts.
    if not subjects_table_exists:
        cursor.execute("""
            INSERT OR IGNORE INTO subjects (
                name,
                daily_goal_minutes
            )
            SELECT DISTINCT
                TRIM(subject),
                0
            FROM study_sessions
            WHERE TRIM(subject) != ''
        """)

    connection.commit()
    connection.close()


# =========================================================
# STUDY SESSION DATABASE FUNCTIONS
# =========================================================

def save_session_to_database(session):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO study_sessions (
            date,
            subject,
            topic,
            duration
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            session["date"],
            session["subject"],
            session["topic"],
            session["duration"]
        )
    )

    connection.commit()
    connection.close()


def load_sessions_from_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            date,
            subject,
            topic,
            duration
        FROM study_sessions
        ORDER BY date DESC, id DESC
    """)

    sessions = cursor.fetchall()

    connection.close()

    return sessions


def delete_session_by_id(session_id):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM study_sessions
        WHERE id = ?
        """,
        (session_id,)
    )

    connection.commit()
    connection.close()


def update_session_by_id(
    session_id,
    subject,
    topic,
    duration
):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE study_sessions
        SET
            subject = ?,
            topic = ?,
            duration = ?
        WHERE id = ?
        """,
        (
            subject,
            topic,
            duration,
            session_id
        )
    )

    connection.commit()
    connection.close()


# =========================================================
# OLD OVERALL DAILY GOAL
# =========================================================
# Kept because the Tkinter desktop GUI still uses it.
# The web application will now mainly use subject-wise goals.
# =========================================================

def load_daily_goal_from_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT daily_goal_minutes
        FROM settings
        WHERE id = 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return row[0]


def save_daily_goal_to_database(goal):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO settings (
            id,
            daily_goal_minutes
        )
        VALUES (1, ?)

        ON CONFLICT(id)
        DO UPDATE SET
            daily_goal_minutes = excluded.daily_goal_minutes
        """,
        (goal,)
    )

    connection.commit()
    connection.close()


# =========================================================
# STUDY SESSION SEARCH / FILTER
# =========================================================

def get_sessions_by_subject(subject):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            date,
            subject,
            topic,
            duration
        FROM study_sessions
        WHERE subject = ? COLLATE NOCASE
        ORDER BY date DESC, id DESC
        """,
        (subject,)
    )

    sessions = cursor.fetchall()

    connection.close()

    return sessions


def get_sessions_by_topic(keyword):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            date,
            subject,
            topic,
            duration
        FROM study_sessions
        WHERE topic LIKE ?
        ORDER BY date DESC, id DESC
        """,
        (f"%{keyword}%",)
    )

    sessions = cursor.fetchall()

    connection.close()

    return sessions


# =========================================================
# STATISTICS
# =========================================================

def get_today_study_minutes():
    today = date.today().isoformat()

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT SUM(duration)
        FROM study_sessions
        WHERE date = ?
        """,
        (today,)
    )

    total = cursor.fetchone()[0]

    connection.close()

    if total is None:
        return 0

    return total


def get_total_study_minutes():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT SUM(duration)
        FROM study_sessions
    """)

    total = cursor.fetchone()[0]

    connection.close()

    if total is None:
        return 0

    return total


def get_current_streak():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT date
        FROM study_sessions
    """)

    rows = cursor.fetchall()

    connection.close()

    study_dates = {
        row[0]
        for row in rows
    }

    if not study_dates:
        return 0

    today = date.today()
    yesterday = today - timedelta(days=1)

    if today.isoformat() in study_dates:
        current_date = today

    elif yesterday.isoformat() in study_dates:
        current_date = yesterday

    else:
        return 0

    streak = 0

    while current_date.isoformat() in study_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak


def get_weekly_study_minutes():
    today = date.today()

    week_start = (
        today
        - timedelta(days=today.weekday())
    )

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT SUM(duration)
        FROM study_sessions
        WHERE date BETWEEN ? AND ?
        """,
        (
            week_start.isoformat(),
            today.isoformat()
        )
    )

    total = cursor.fetchone()[0]

    connection.close()

    if total is None:
        return 0

    return total


def get_monthly_study_minutes():
    today = date.today()

    month_start = today.replace(
        day=1
    )

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT SUM(duration)
        FROM study_sessions
        WHERE date BETWEEN ? AND ?
        """,
        (
            month_start.isoformat(),
            today.isoformat()
        )
    )

    total = cursor.fetchone()[0]

    connection.close()

    if total is None:
        return 0

    return total


# =========================================================
# MANAGED SUBJECTS
# =========================================================

def get_subjects():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            daily_goal_minutes
        FROM subjects
        ORDER BY name
    """)

    subjects = cursor.fetchall()

    connection.close()

    return subjects


def add_subject(name):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO subjects (
            name,
            daily_goal_minutes
        )
        VALUES (?, 0)
        """,
        (name,)
    )

    connection.commit()
    connection.close()


def update_subject_goal(
    subject_id,
    daily_goal_minutes
):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE subjects
        SET daily_goal_minutes = ?
        WHERE id = ?
        """,
        (
            daily_goal_minutes,
            subject_id
        )
    )

    connection.commit()
    connection.close()


def delete_subject(subject_id):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM subjects
        WHERE id = ?
        """,
        (subject_id,)
    )

    connection.commit()
    connection.close()


# =========================================================
# SIMPLE COMMAND-LINE VERSION
# =========================================================

def display_sessions():
    sessions = load_sessions_from_database()

    if not sessions:
        print("\nNo study sessions found.")
        return

    print("\nStudy Sessions")
    print("-" * 75)

    for session in sessions:
        print(
            f"ID: {session[0]} | "
            f"Date: {session[1]} | "
            f"Subject: {session[2]} | "
            f"Topic: {session[3]} | "
            f"Duration: {session[4]} min"
        )


def cli_add_session():
    subject = input(
        "Subject: "
    ).strip().title()

    topic = input(
        "Topic: "
    ).strip()

    duration = input(
        "Duration in minutes: "
    ).strip()

    if (
        not subject
        or not topic
        or not duration.isdigit()
        or int(duration) <= 0
    ):
        print("Invalid study session.")
        return

    session = {
        "date": date.today().isoformat(),
        "subject": subject,
        "topic": topic,
        "duration": int(duration)
    }

    save_session_to_database(session)

    print("Study session added.")


def main():
    while True:
        print("\nStudy Tracker")
        print("1. Add study session")
        print("2. View study sessions")
        print("3. Show statistics")
        print("4. Exit")

        choice = input(
            "Choose an option: "
        ).strip()

        if choice == "1":
            cli_add_session()

        elif choice == "2":
            display_sessions()

        elif choice == "3":
            print(
                "\nTotal:",
                get_total_study_minutes(),
                "minutes"
            )

            print(
                "This week:",
                get_weekly_study_minutes(),
                "minutes"
            )

            print(
                "This month:",
                get_monthly_study_minutes(),
                "minutes"
            )

            print(
                "Current streak:",
                get_current_streak(),
                "days"
            )

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print(
                "Please choose a valid option."
            )


if __name__ == "__main__":
    initialize_database()
    main()