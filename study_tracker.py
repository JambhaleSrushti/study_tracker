import sqlite3
import json
from datetime import date, timedelta

DB_FILE = "study_tracker.db"


def initialize_database():
    connection = sqlite3.connect(DB_FILE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            duration INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            daily_goal_minutes INTEGER
        )
    """)

    connection.commit()
    connection.close()

def delete_session_by_id(session_id):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM study_sessions WHERE id = ?",
        (session_id,)
    )

    connection.commit()
    connection.close()

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
        SELECT id
        FROM settings
        WHERE id = 1
        """
    )

    existing_setting = cursor.fetchone()

    if existing_setting:
        cursor.execute(
            """
            UPDATE settings
            SET daily_goal_minutes = ?
            WHERE id = 1
            """,
            (goal,)
        )
    else:
        cursor.execute(
            """
            INSERT INTO settings (id, daily_goal_minutes)
            VALUES (1, ?)
            """,
            (goal,)
        )

    connection.commit()
    connection.close()

def update_session_by_id(session_id, subject, topic, duration):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE study_sessions
        SET subject = ?, topic = ?, duration = ?
        WHERE id = ?
        """,
        (subject, topic, duration, session_id)
    )

    connection.commit()
    connection.close()

def save_session_to_database(session):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO study_sessions (date, subject, topic, duration)
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
        SELECT id, date, subject, topic, duration
        FROM study_sessions
        ORDER BY id
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


def add_study_session():
    print("\n===== ADD STUDY SESSION =====")

    subject = input("Subject: ").strip().title()
    topic = input("Topic: ").strip()
    while True:
        duration = input("Duration (minutes): ").strip()

        if duration.isdigit() and int(duration) > 0:
            duration = int(duration)
            break

        print("Please enter a valid duration in minutes.")

    session_date = date.today().isoformat()

    session = {
        "date": session_date,
        "subject": subject,
        "topic": topic,
        "duration": duration
    }

    save_session_to_database(session)

    print("\nStudy session added successfully!")


def view_study_sessions():
    print("\n===== STUDY SESSIONS =====")

    sessions = load_sessions_from_database()

    if not sessions:
        print("No study sessions added yet.")
        return

    for index, session in enumerate(sessions, start=1):
        print(
            f"{index}. "
            f"{session[1]} - "
            f"{session[2]} - "
            f"{session[3]} - "
            f"{session[4]} minutes"
        )
        

def delete_study_session():
    print("\n===== DELETE STUDY SESSION =====")

    sessions = load_sessions_from_database()

    if not sessions:
        print("No study sessions to delete.")
        return

    for index, session in enumerate(sessions, start=1):
        print(
            f"{index}. "
            f"{session[1]} - "
            f"{session[2]} - "
            f"{session[3]} - "
            f"{session[4]} minutes"
        )

    session_number = input(
        "\nEnter session number to delete: "
    ).strip()

    if not session_number.isdigit():
        print("Please enter a valid session number.")
        return

    session_number = int(session_number)

    if session_number < 1 or session_number > len(sessions):
        print("Session not found.")
        return

    selected_session = sessions[session_number - 1]
    session_id = selected_session[0]

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM study_sessions WHERE id = ?",
        (session_id,)
    )

    connection.commit()
    connection.close()


    print("\nStudy session deleted successfully!")    

def view_total_study_time():
    print("\n===== TOTAL STUDY TIME =====")

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT SUM(duration)
        FROM study_sessions
    """)

    total_minutes = cursor.fetchone()[0]

    connection.close()

    if total_minutes is None:
        total_minutes = 0

    print(f"Total study time: {total_minutes} minutes")


def view_study_time_by_subject():
    print("\n===== STUDY TIME BY SUBJECT =====")

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT subject, SUM(duration)
        FROM study_sessions
        GROUP BY subject
        ORDER BY subject
    """)

    results = cursor.fetchall()

    connection.close()

    if not results:
        print("No study sessions added yet.")
        return

    for subject, total_minutes in results:
        print(f"{subject}: {total_minutes} minutes")

def view_daily_goal_progress():
    print("\n===== DAILY STUDY GOAL =====")

    daily_goal_minutes = load_daily_goal_from_database()

    if daily_goal_minutes is None:
        print("Daily study goal has not been set yet.")
        return

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

    today_minutes = cursor.fetchone()[0]

    connection.close()

    if today_minutes is None:
        today_minutes = 0

    progress = (today_minutes / daily_goal_minutes) * 100

    print(f"Daily goal: {daily_goal_minutes} minutes")
    print(f"Today's study: {today_minutes} minutes")
    print(f"Progress: {progress:.0f}%")

    if today_minutes >= daily_goal_minutes:
        print("Daily goal completed!")
    else:
        remaining = daily_goal_minutes - today_minutes
        print(f"{remaining} minutes remaining.")
        
def view_study_streak():
    print("\n===== STUDY STREAK =====")

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT date
        FROM study_sessions
        ORDER BY date DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    study_dates = set()

    for row in rows:
        study_dates.add(row[0])

    if not study_dates:
        print("Current streak: 0 days")
        return

    today = date.today()
    yesterday = today - timedelta(days=1)

    if today.isoformat() in study_dates:
        current_date = today
    elif yesterday.isoformat() in study_dates:
        current_date = yesterday
    else:
        print("Current streak: 0 days")
        return

    streak = 0

    while current_date.isoformat() in study_dates:
        streak += 1
        current_date -= timedelta(days=1)

    if streak == 1:
        print("Current streak: 1 day")
    else:
        print(f"Current streak: {streak} days")

def filter_sessions_by_subject():
    print("\n===== FILTER BY SUBJECT =====")

    subject_to_find = input("Enter subject: ").strip().title()

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, date, subject, topic, duration
        FROM study_sessions
        WHERE subject = ?
        ORDER BY date
        """,
        (subject_to_find,)
    )

    matching_sessions = cursor.fetchall()

    connection.close()

    if not matching_sessions:
        print(f"No study sessions found for {subject_to_find}.")
        return

    for index, session in enumerate(matching_sessions, start=1):
        print(
            f"{index}. "
            f"{session[1]} - "
            f"{session[2]} - "
            f"{session[3]} - "
            f"{session[4]} minutes"
        )

def filter_sessions_by_date():
    print("\n===== FILTER BY DATE =====")

    date_to_find = input("Enter date (YYYY-MM-DD): ").strip()

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, date, subject, topic, duration
        FROM study_sessions
        WHERE date = ?
        ORDER BY id
        """,
        (date_to_find,)
    )

    matching_sessions = cursor.fetchall()

    connection.close()

    if not matching_sessions:
        print(f"No study sessions found for {date_to_find}.")
        return

    for index, session in enumerate(matching_sessions, start=1):
        print(
            f"{index}. "
            f"{session[1]} - "
            f"{session[2]} - "
            f"{session[3]} - "
            f"{session[4]} minutes"
        )

def view_sorted_sessions():
    print("\n===== SORT STUDY SESSIONS =====")

    print("1. Oldest first")
    print("2. Newest first")

    choice = input("Choose sort order: ").strip()

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    if choice == "1":
        cursor.execute("""
            SELECT id, date, subject, topic, duration
            FROM study_sessions
            ORDER BY date ASC, id ASC
        """)

    elif choice == "2":
        cursor.execute("""
            SELECT id, date, subject, topic, duration
            FROM study_sessions
            ORDER BY date DESC, id DESC
        """)

    else:
        print("Invalid option.")
        connection.close()
        return

    sorted_sessions = cursor.fetchall()

    connection.close()

    if not sorted_sessions:
        print("No study sessions added yet.")
        return

    print("\n===== SORTED STUDY SESSIONS =====")

    for index, session in enumerate(sorted_sessions, start=1):
        print(
            f"{index}. "
            f"{session[1]} - "
            f"{session[2]} - "
            f"{session[3]} - "
            f"{session[4]} minutes"
        )

def search_sessions_by_topic():
    print("\n===== SEARCH BY TOPIC =====")

    topic_to_find = input("Enter topic keyword: ").strip()

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, date, subject, topic, duration
        FROM study_sessions
        WHERE topic LIKE ?
        ORDER BY date
        """,
        (f"%{topic_to_find}%",)
    )

    matching_sessions = cursor.fetchall()

    connection.close()

    if not matching_sessions:
        print(f"No study sessions found matching '{topic_to_find}'.")
        return

    for index, session in enumerate(matching_sessions, start=1):
        print(
            f"{index}. "
            f"{session[1]} - "
            f"{session[2]} - "
            f"{session[3]} - "
            f"{session[4]} minutes"
        )

def view_weekly_statistics():
    print("\n===== WEEKLY STATISTICS =====")

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*), COUNT(DISTINCT date), SUM(duration)
        FROM study_sessions
        WHERE date BETWEEN ? AND ?
        """,
        (
            week_start.isoformat(),
            today.isoformat()
        )
    )

    result = cursor.fetchone()
    connection.close()

    session_count = result[0]
    study_days = result[1]
    total_minutes = result[2]

    if total_minutes is None:
        total_minutes = 0

    print(f"Week: {week_start} to {today}")
    print(f"Study sessions: {session_count}")
    print(f"Study days: {study_days}")
    print(f"Total study time: {total_minutes} minutes")

def view_monthly_statistics():
    print("\n===== MONTHLY STATISTICS =====")

    today = date.today()

    month_start = today.replace(day=1)

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*), COUNT(DISTINCT date), SUM(duration)
        FROM study_sessions
        WHERE date BETWEEN ? AND ?
        """,
        (
            month_start.isoformat(),
            today.isoformat()
        )
    )

    result = cursor.fetchone()
    connection.close()

    session_count = result[0]
    study_days = result[1]
    total_minutes = result[2]

    if total_minutes is None:
        total_minutes = 0

    print(f"Month: {today.strftime('%B %Y')}")
    print(f"Study sessions: {session_count}")
    print(f"Study days: {study_days}")
    print(f"Total study time: {total_minutes} minutes")

def edit_study_session():
    print("\n===== EDIT STUDY SESSION =====")

    sessions = load_sessions_from_database()

    if not sessions:
        print("No study sessions to edit.")
        return

    for index, session in enumerate(sessions, start=1):
        print(
            f"{index}. "
            f"{session[1]} - "
            f"{session[2]} - "
            f"{session[3]} - "
            f"{session[4]} minutes"
        )

    session_number = input(
        "\nEnter session number to edit: "
    ).strip()

    if not session_number.isdigit():
        print("Please enter a valid session number.")
        return

    session_number = int(session_number)

    if session_number < 1 or session_number > len(sessions):
        print("Session not found.")
        return

    selected_session = sessions[session_number - 1]
    session_id = selected_session[0]

    print("\nWhat would you like to edit?")
    print("1. Subject")
    print("2. Topic")
    print("3. Duration")

    choice = input("Choose an option: ").strip()

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    if choice == "1":
        new_subject = input("Enter new subject: ").strip().title()

        if not new_subject:
            print("Subject cannot be empty.")
            connection.close()
            return

        cursor.execute(
            """
            UPDATE study_sessions
            SET subject = ?
            WHERE id = ?
            """,
            (new_subject, session_id)
        )

    elif choice == "2":
        new_topic = input("Enter new topic: ").strip()

        if not new_topic:
            print("Topic cannot be empty.")
            connection.close()
            return

        cursor.execute(
            """
            UPDATE study_sessions
            SET topic = ?
            WHERE id = ?
            """,
            (new_topic, session_id)
        )

    elif choice == "3":
        while True:
            new_duration = input(
                "Enter new duration (minutes): "
            ).strip()

            if new_duration.isdigit() and int(new_duration) > 0:
                new_duration = int(new_duration)
                break

            print("Please enter a valid duration in minutes.")

        cursor.execute(
            """
            UPDATE study_sessions
            SET duration = ?
            WHERE id = ?
            """,
            (new_duration, session_id)
        )

    else:
        print("Invalid option.")
        connection.close()
        return

    connection.commit()
    connection.close()


    print("\nStudy session updated successfully!")

def set_daily_goal():
    global daily_goal_minutes

    print("\n===== SET DAILY STUDY GOAL =====")

    while True:
        goal = input("Enter daily goal in minutes: ").strip()

        if goal.isdigit() and int(goal) > 0:
            daily_goal_minutes = int(goal)
            save_daily_goal(daily_goal_minutes)

            print(
                f"\nDaily study goal set to "
                f"{daily_goal_minutes} minutes."
            )
            return

        print("Please enter a valid number of minutes.")

def view_database_sessions():
    print("\n===== SQLITE STUDY SESSIONS =====")

    sessions = load_sessions_from_database()

    if not sessions:
        print("No study sessions found in the database.")
        return

    for session in sessions:
        print(
            f"{session[0]}. "
            f"{session[1]} - "
            f"{session[2]} - "
            f"{session[3]} - "
            f"{session[4]} minutes"
        )

def set_daily_goal():
    print("\n===== SET DAILY STUDY GOAL =====")

    while True:
        goal = input("Enter daily goal in minutes: ").strip()

        if goal.isdigit() and int(goal) > 0:
            goal = int(goal)

            save_daily_goal_to_database(goal)

            print(f"\nDaily study goal set to {goal} minutes.")
            return

        print("Please enter a valid number of minutes.")

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

def get_sessions_by_subject(subject):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, date, subject, topic, duration
        FROM study_sessions
        WHERE subject = ?
        ORDER BY date
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
        SELECT id, date, subject, topic, duration
        FROM study_sessions
        WHERE topic LIKE ?
        ORDER BY date
        """,
        (f"%{keyword}%",)
    )

    sessions = cursor.fetchall()

    connection.close()

    return sessions

def main():
    while True:
        print("1. Add study session")
        print("2. View study sessions")
        print("3. Delete study session")
        print("4. View total study time")
        print("5. View study time by subject")
        print("6. View daily goal progress")
        print("7. View study streak")
        print("8. Filter sessions by subject")
        print("9. Filter sessions by date")
        print("10. Sort study sessions")
        print("11. Search sessions by topic")
        print("12. View weekly statistics")
        print("13. View monthly statistics")
        print("14. Edit study session")
        print("15. Set daily study goal")
        print("16. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            add_study_session()

        elif choice == "2":
            view_study_sessions()

        elif choice == "3":
            delete_study_session()

        elif choice == "4":
            view_total_study_time()

        elif choice == "5":
            view_study_time_by_subject()

        elif choice == "6":
            view_daily_goal_progress()

        elif choice == "7":
            view_study_streak()

        elif choice == "8":
            filter_sessions_by_subject()

        elif choice == "9":
            filter_sessions_by_date()

        elif choice == "10":
            view_sorted_sessions()

        elif choice == "11":
            search_sessions_by_topic()

        elif choice == "12":
            view_weekly_statistics()

        elif choice == "13":
            view_monthly_statistics()

        elif choice == "14":
            edit_study_session()

        elif choice == "15":
            set_daily_goal()

        elif choice == "16":
            print("\nGoodbye!")
            break      

        else:
            print("\nInvalid option. Please choose 1 to 16.")

if __name__ == "__main__":
    initialize_database()
    main()