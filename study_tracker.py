study_sessions = []


def add_study_session():
    print("\n===== ADD STUDY SESSION =====")

    subject = input("Subject: ")
    topic = input("Topic: ")
    duration = input("Duration (minutes): ")

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


def main():
    while True:
        print("\n===== STUDY TRACKER =====")
        print("1. Add study session")
        print("2. View study sessions")
        print("3. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            add_study_session()

        elif choice == "2":
            view_study_sessions()

        elif choice == "3":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option. Please choose 1, 2, or 3.")


main()