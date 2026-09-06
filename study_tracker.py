study_sessions = []


def add_study_session():
    print("\n===== ADD STUDY SESSION =====")

    subject = input("Subject: ")
    topic = input("Topic: ")
    while True:
        duration = input("Duration (minutes): ")

        if duration.isdigit() and int(duration) > 0:
            duration = int(duration)
            break

    print("Please enter a valid duration in minutes.")

    session = {
        "subject": subject,
        "topic": topic,
        "duration": duration
    }

    study_sessions.append(session)

    print("\nStudy session added successfully!")


def view_study_sessions():
    print("\n===== STUDY SESSIONS =====")

    if not study_sessions:
        print("No study sessions added yet.")
        return

    for index, session in enumerate(study_sessions, start=1):
        print(
            f"{index}. "
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

def main():
    while True:
        print("1. Add study session")
        print("2. View study sessions")
        print("3. Delete study session")
        print("4. View total study time")
        print("5. Exit")

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
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option. Please choose 1, 2, 3, 4, or 5.")

main()