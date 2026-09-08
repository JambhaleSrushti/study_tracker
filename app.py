from datetime import date

from flask import Flask, request, redirect

from study_tracker import (
    initialize_database,
    load_sessions_from_database,
    save_session_to_database,
    delete_session_by_id
)


app = Flask(__name__)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    # -----------------------------------------
    # ADD NEW STUDY SESSION
    # -----------------------------------------

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


    # -----------------------------------------
    # LOAD EXISTING SESSIONS
    # -----------------------------------------

    sessions = load_sessions_from_database()

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
                <form
                    method="POST"
                    action="/delete/{session_id}"
                >
                    <button type="submit">
                        Delete
                    </button>
                </form>
            </td>
        </tr>
        """


    # -----------------------------------------
    # PAGE HTML
    # -----------------------------------------

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
                    <th>Action</th>
                </tr>

                {rows}

            </table>

        </body>

    </html>
    """


# =========================================================
# DELETE SESSION
# =========================================================

@app.route(
    "/delete/<int:session_id>",
    methods=["POST"]
)
def delete_session(session_id):

    delete_session_by_id(session_id)

    return redirect("/")


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    initialize_database()

    app.run(debug=True)