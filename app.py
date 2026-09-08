from datetime import date

from flask import Flask, request, redirect

from study_tracker import (
    initialize_database,
    load_sessions_from_database,
    save_session_to_database,
    delete_session_by_id,
    update_session_by_id,
    load_daily_goal_from_database,
    save_daily_goal_to_database,
    get_today_study_minutes,
    get_sessions_by_subject,
    get_sessions_by_topic
)


app = Flask(__name__)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    # -----------------------------------------------------
    # ADD STUDY SESSION
    # -----------------------------------------------------

    if request.method == "POST":

        subject = request.form.get("subject", "").strip().title()
        topic = request.form.get("topic", "").strip()
        duration = request.form.get("duration", "").strip()

        if (
            subject
            and topic
            and duration.isdigit()
            and int(duration) > 0
        ):
            session = {
                "date": date.today().isoformat(),
                "subject": subject,
                "topic": topic,
                "duration": int(duration)
            }

            save_session_to_database(session)

        return redirect("/")


    # -----------------------------------------------------
    # SEARCH / FILTER
    # -----------------------------------------------------

    subject_filter = request.args.get(
        "subject",
        ""
    ).strip().title()

    topic_search = request.args.get(
        "topic",
        ""
    ).strip()


    if subject_filter:

        sessions = get_sessions_by_subject(
            subject_filter
        )

    elif topic_search:

        sessions = get_sessions_by_topic(
            topic_search
        )

    else:

        sessions = load_sessions_from_database()


    # -----------------------------------------------------
    # BUILD TABLE ROWS
    # -----------------------------------------------------

    rows = ""

    for session in sessions:

        session_id = session[0]
        session_date = session[1]
        subject = session[2]
        topic = session[3]
        duration = session[4]

        rows += f"""
        <tr>
            <td>{session_date}</td>
            <td>{subject}</td>
            <td>{topic}</td>
            <td>{duration}</td>

            <td>
                <a href="/edit/{session_id}">
                    Edit
                </a>

                &nbsp;

                <form
                    method="POST"
                    action="/delete/{session_id}"
                    style="display:inline;"
                >
                    <button type="submit">
                        Delete
                    </button>
                </form>
            </td>
        </tr>
        """


    # -----------------------------------------------------
    # DAILY GOAL
    # -----------------------------------------------------

    daily_goal = load_daily_goal_from_database()
    today_minutes = get_today_study_minutes()


    if daily_goal is None:

        goal_text = "Daily goal: Not set"

        progress_text = (
            f"Today's study: {today_minutes} minutes"
        )

    else:

        progress = (
            today_minutes / daily_goal
        ) * 100

        goal_text = (
            f"Daily goal: {daily_goal} minutes"
        )

        progress_text = (
            f"Today's study: {today_minutes} minutes "
            f"({progress:.0f}%)"
        )


    # -----------------------------------------------------
    # PAGE HTML
    # -----------------------------------------------------

    return f"""
    <!DOCTYPE html>

    <html>

        <head>
            <title>Study Tracker</title>
        </head>

        <body>

            <h1>Study Tracker</h1>

            <p>
                Track your study sessions,
                goals, progress, and consistency.
            </p>


            <hr>


            <h2>Add Study Session</h2>

            <form method="POST">

                <label>Subject:</label>

                <input
                    type="text"
                    name="subject"
                    required
                >

                <br><br>


                <label>Topic:</label>

                <input
                    type="text"
                    name="topic"
                    required
                >

                <br><br>


                <label>Duration:</label>

                <input
                    type="number"
                    name="duration"
                    min="1"
                    required
                >

                <br><br>


                <button type="submit">
                    Add Study Session
                </button>

            </form>


            <hr>


            <h2>Daily Goal</h2>

            <p>
                {goal_text}
            </p>

            <p>
                {progress_text}
            </p>


            <form
                method="POST"
                action="/goal"
            >

                <label>
                    New daily goal:
                </label>

                <input
                    type="number"
                    name="goal"
                    min="1"
                    required
                >

                <button type="submit">
                    Set Daily Goal
                </button>

            </form>


            <hr>


            <h2>Search & Filter</h2>


            <form
                method="GET"
                action="/"
            >

                <label>
                    Subject:
                </label>

                <input
                    type="text"
                    name="subject"
                >

                <button type="submit">
                    Filter Subject
                </button>

            </form>


            <br>


            <form
                method="GET"
                action="/"
            >

                <label>
                    Topic:
                </label>

                <input
                    type="text"
                    name="topic"
                >

                <button type="submit">
                    Search Topic
                </button>

            </form>


            <br>


            <a href="/">
                Show All Sessions
            </a>


            <hr>


            <h2>Study Sessions</h2>

            <table
                border="1"
                cellpadding="8"
            >

                <tr>
                    <th>Date</th>
                    <th>Subject</th>
                    <th>Topic</th>
                    <th>Duration</th>
                    <th>Actions</th>
                </tr>

                {rows}

            </table>

        </body>

    </html>
    """


# =========================================================
# SET DAILY GOAL
# =========================================================

@app.route(
    "/goal",
    methods=["POST"]
)
def set_daily_goal():

    goal = request.form.get(
        "goal",
        ""
    ).strip()

    if (
        goal.isdigit()
        and int(goal) > 0
    ):
        save_daily_goal_to_database(
            int(goal)
        )

    return redirect("/")


# =========================================================
# DELETE SESSION
# =========================================================

@app.route(
    "/delete/<int:session_id>",
    methods=["POST"]
)
def delete_session(session_id):

    delete_session_by_id(
        session_id
    )

    return redirect("/")


# =========================================================
# EDIT SESSION
# =========================================================

@app.route(
    "/edit/<int:session_id>",
    methods=["GET", "POST"]
)
def edit_session(session_id):

    # -----------------------------------------------------
    # SAVE CHANGES
    # -----------------------------------------------------

    if request.method == "POST":

        subject = request.form.get(
            "subject",
            ""
        ).strip().title()

        topic = request.form.get(
            "topic",
            ""
        ).strip()

        duration = request.form.get(
            "duration",
            ""
        ).strip()

        if (
            subject
            and topic
            and duration.isdigit()
            and int(duration) > 0
        ):

            update_session_by_id(
                session_id,
                subject,
                topic,
                int(duration)
            )

            return redirect("/")


    # -----------------------------------------------------
    # FIND SESSION
    # -----------------------------------------------------

    sessions = load_sessions_from_database()

    selected_session = None

    for session in sessions:

        if session[0] == session_id:

            selected_session = session

            break


    if selected_session is None:

        return "Study session not found."


    subject = selected_session[2]
    topic = selected_session[3]
    duration = selected_session[4]


    # -----------------------------------------------------
    # EDIT PAGE
    # -----------------------------------------------------

    return f"""
    <!DOCTYPE html>

    <html>

        <head>
            <title>Edit Study Session</title>
        </head>

        <body>

            <h1>Edit Study Session</h1>


            <form method="POST">

                <label>
                    Subject:
                </label>

                <input
                    type="text"
                    name="subject"
                    value="{subject}"
                    required
                >

                <br><br>


                <label>
                    Topic:
                </label>

                <input
                    type="text"
                    name="topic"
                    value="{topic}"
                    required
                >

                <br><br>


                <label>
                    Duration:
                </label>

                <input
                    type="number"
                    name="duration"
                    value="{duration}"
                    min="1"
                    required
                >

                <br><br>


                <button type="submit">
                    Save Changes
                </button>

                &nbsp;

                <a href="/">
                    Cancel
                </a>

            </form>

        </body>

    </html>
    """


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    initialize_database()

    app.run(debug=True)