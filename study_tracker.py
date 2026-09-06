import json
from datetime import date, timedelta

DATA_FILE = "study_sessions.json"
DAILY_GOAL_MINUTES = 120

def load_sessions():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


study_sessions = load_sessions()

def save_sessions():
    with open(DATA_FILE, "w") as file:
        json.dump(study_sessions, file, indent=4)

def add_study_session():
    print("\n===== ADD STUDY SESSION =====")

    subject = input("Subject: ").strip().title()
    topic = input("Topic: ").strip()
    while True:
        duration = input("Duration (minutes): ")

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

    study_sessions.append(session)
    save_sessions()

    print("\nStudy session added successfully!")


def view_study_sessions():
    print("\n===== STUDY SESSIONS =====")

    if not study_sessions:
        print("No study sessions added yet.")
        return

    for index, session in enumerate(study_sessions, start=1):
        print(
            f"{index}. "
            f"{session['date']} - "
            f"{session['subject']} - "
            f"{session['topic']} - "
            f"{session['duration']} minutes"
        )

def delete_study_session():
    print("\n===== DELETE STUDY SESSION =====")

    if not study_sessions:
        print("No study sessions to delete.")
        return

    view_study_sessions()

    session_number = input("\nEnter session number to delete: ")

    if not session_number.isdigit():
        print("Please enter a valid number.")
        return

    session_number = int(session_number)

    if session_number < 1 or session_number > len(study_sessions):
        print("Session not found.")
        return

    deleted_session = study_sessions.pop(session_number - 1)
    save_sessions()

    print(
        f"\nDeleted: {deleted_session['subject']} - "
        f"{deleted_session['topic']}"
    )

def view_total_study_time():
    print("\n===== TOTAL STUDY TIME =====")

    if not study_sessions:
        print("No study sessions added yet.")
        return

    total_minutes = 0

    for session in study_sessions:
        total_minutes += session["duration"]

    print(f"Total study time: {total_minutes} minutes")

def view_study_time_by_subject():
    print("\n===== STUDY TIME BY SUBJECT =====")

    if not study_sessions:
        print("No study sessions added yet.")
        return

    subject_totals = {}

    for session in study_sessions:
        subject = session["subject"]
        duration = session["duration"]

        if subject in subject_totals:
            subject_totals[subject] += duration
        else:
            subject_totals[subject] = duration

    for subject, total in subject_totals.items():
        print(f"{subject}: {total} minutes")
        
def view_daily_goal_progress():
    print("\n===== DAILY STUDY GOAL =====")

    today = date.today().isoformat()
    today_minutes = 0

    for session in study_sessions:
        if session["date"] == today:
            today_minutes += session["duration"]

    progress = (today_minutes / DAILY_GOAL_MINUTES) * 100

    print(f"Daily goal: {DAILY_GOAL_MINUTES} minutes")
    print(f"Today's study: {today_minutes} minutes")
    print(f"Progress: {progress:.0f}%")

    if today_minutes >= DAILY_GOAL_MINUTES:
        print("Daily goal completed!")
    else:
        remaining = DAILY_GOAL_MINUTES - today_minutes
        print(f"{remaining} minutes remaining.")

def view_study_streak():
    print("\n===== STUDY STREAK =====")

    if not study_sessions:
        print("Current streak: 0 days")
        return

    study_dates = set()

    for session in study_sessions:
        study_dates.add(session["date"])

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

    print(f"Current streak: {streak} days")

def filter_sessions_by_subject():
    print("\n===== FILTER BY SUBJECT =====")

    if not study_sessions:
        print("No study sessions added yet.")
        return

    subject_to_find = input("Enter subject: ").strip().title()

    matching_sessions = []

    for session in study_sessions:
        if session["subject"] == subject_to_find:
            matching_sessions.append(session)

    if not matching_sessions:
        print(f"No study sessions found for {subject_to_find}.")
        return

    for index, session in enumerate(matching_sessions, start=1):
        print(
            f"{index}. "
            f"{session['date']} - "
            f"{session['subject']} - "
            f"{session['topic']} - "
            f"{session['duration']} minutes"
        )

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
        print("9. Exit")

        choice = input("\nChoose an option: ")

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
            print("\nGoodbye!")
            break      

        else:
            print("\nInvalid option. Please choose 1 to 9.")

main()