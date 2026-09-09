from datetime import date

from flask import (
    Flask,
    request,
    redirect,
    render_template,
    url_for
)

from study_tracker import (
    initialize_database,
    load_sessions_from_database,
    save_session_to_database,
    delete_session_by_id,
    update_session_by_id,
    get_today_study_minutes,
    get_sessions_by_subject,
    get_sessions_by_topic,
    get_total_study_minutes,
    get_current_streak,
    get_weekly_study_minutes,
    get_monthly_study_minutes,
    get_subjects,
    add_subject,
    update_subject_goal,
    delete_subject
)


app = Flask(__name__)


# =========================================================
# HOME PAGE
# =========================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    subjects = get_subjects()

    # -----------------------------------------------------
    # ADD STUDY SESSION
    # -----------------------------------------------------

    if request.method == "POST":

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        topic = request.form.get(
            "topic",
            ""
        ).strip()

        duration = request.form.get(
            "duration",
            ""
        ).strip()

        available_subjects = {
            item[1]
            for item in subjects
        }

        if (
            subject in available_subjects
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

            save_session_to_database(
                session
            )

        return redirect(
            url_for("home")
        )


    # -----------------------------------------------------
    # SEARCH / FILTER
    # -----------------------------------------------------

    subject_filter = request.args.get(
        "subject",
        ""
    ).strip()

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
    # SUBJECT-WISE DAILY GOALS
    # -----------------------------------------------------

    total_daily_goal = sum(
        subject[2] or 0
        for subject in subjects
    )

    today_minutes = get_today_study_minutes()

    overall_progress = None

    if total_daily_goal > 0:

        overall_progress = (
            today_minutes
            / total_daily_goal
        ) * 100


    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    total_minutes = (
        get_total_study_minutes()
    )

    current_streak = (
        get_current_streak()
    )

    weekly_minutes = (
        get_weekly_study_minutes()
    )

    monthly_minutes = (
        get_monthly_study_minutes()
    )


    # -----------------------------------------------------
    # RENDER PAGE
    # -----------------------------------------------------

    return render_template(
        "index.html",
        sessions=sessions,
        subjects=subjects,
        total_daily_goal=total_daily_goal,
        today_minutes=today_minutes,
        overall_progress=overall_progress,
        total_minutes=total_minutes,
        current_streak=current_streak,
        weekly_minutes=weekly_minutes,
        monthly_minutes=monthly_minutes,
        subject_filter=subject_filter,
        topic_search=topic_search
    )


# =========================================================
# ADD SUBJECT
# =========================================================

@app.route(
    "/subjects/add",
    methods=["POST"]
)
def create_subject():

    name = request.form.get(
        "subject_name",
        ""
    ).strip().title()

    if name:

        add_subject(
            name
        )

    return redirect(
        url_for("home")
    )


# =========================================================
# UPDATE SUBJECT DAILY GOAL
# =========================================================

@app.route(
    "/subjects/<int:subject_id>/goal",
    methods=["POST"]
)
def change_subject_goal(subject_id):

    goal = request.form.get(
        "goal",
        ""
    ).strip()

    if (
        goal.isdigit()
        and int(goal) >= 0
    ):

        update_subject_goal(
            subject_id,
            int(goal)
        )

    return redirect(
        url_for("home")
    )


# =========================================================
# REMOVE MANAGED SUBJECT
# =========================================================

@app.route(
    "/subjects/<int:subject_id>/delete",
    methods=["POST"]
)
def remove_subject(subject_id):

    delete_subject(
        subject_id
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# DELETE STUDY SESSION
# =========================================================

@app.route(
    "/delete/<int:session_id>",
    methods=["POST"]
)
def delete_session(session_id):

    delete_session_by_id(
        session_id
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# EDIT STUDY SESSION
# =========================================================

@app.route(
    "/edit/<int:session_id>",
    methods=["GET", "POST"]
)
def edit_session(session_id):

    sessions = (
        load_sessions_from_database()
    )

    selected_session = None

    for session in sessions:

        if session[0] == session_id:

            selected_session = session
            break


    if selected_session is None:

        return (
            "Study session not found.",
            404
        )


    subjects = get_subjects()

    managed_subject_names = {
        subject[1]
        for subject in subjects
    }


    # Allow the historical subject to remain
    # selectable even if it was removed from
    # the managed subjects list.
    allowed_subjects = set(
        managed_subject_names
    )

    allowed_subjects.add(
        selected_session[2]
    )


    if request.method == "POST":

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        topic = request.form.get(
            "topic",
            ""
        ).strip()

        duration = request.form.get(
            "duration",
            ""
        ).strip()

        if (
            subject in allowed_subjects
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

            return redirect(
                url_for("home")
            )


    return render_template(
        "edit.html",
        session=selected_session,
        subjects=subjects,
        managed_subject_names=managed_subject_names
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    initialize_database()

    app.run(
        debug=True
    )