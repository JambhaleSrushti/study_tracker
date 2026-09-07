import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from study_tracker import (
    initialize_database,
    save_session_to_database,
    load_sessions_from_database,
    delete_session_by_id,
    update_session_by_id,
    load_daily_goal_from_database,
    save_daily_goal_to_database,
    get_today_study_minutes,
    get_sessions_by_subject
)


editing_session_id = None


# =========================================================
# SESSION TABLE
# =========================================================

def refresh_session_table(sessions=None):
    # Remove existing rows from the table
    for item in session_table.get_children():
        session_table.delete(item)

    # If no filtered sessions were provided,
    # load all sessions from SQLite
    if sessions is None:
        sessions = load_sessions_from_database()

    for session in sessions:
        session_table.insert(
            "",
            tk.END,
            iid=str(session[0]),  # SQLite ID
            values=(
                session[1],      # date
                session[2],      # subject
                session[3],      # topic
                session[4]       # duration
            )
        )


# =========================================================
# ADD SESSION
# =========================================================

def add_study_session():
    subject = subject_entry.get().strip().title()
    topic = topic_entry.get().strip()
    duration = duration_entry.get().strip()

    if not subject:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a subject."
        )
        return

    if not topic:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a topic."
        )
        return

    if not duration.isdigit() or int(duration) <= 0:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a valid duration in minutes."
        )
        return

    session = {
        "date": date.today().isoformat(),
        "subject": subject,
        "topic": topic,
        "duration": int(duration)
    }

    save_session_to_database(session)

    # Clear form
    subject_entry.delete(0, tk.END)
    topic_entry.delete(0, tk.END)
    duration_entry.delete(0, tk.END)

    refresh_session_table()
    refresh_daily_goal()

    messagebox.showinfo(
        "Success",
        "Study session added successfully!"
    )


# =========================================================
# DELETE SESSION
# =========================================================

def delete_selected_session():
    selected_items = session_table.selection()

    if not selected_items:
        messagebox.showwarning(
            "No Selection",
            "Please select a study session to delete."
        )
        return

    selected_item = selected_items[0]
    session_id = int(selected_item)

    confirmed = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this study session?"
    )

    if not confirmed:
        return

    delete_session_by_id(session_id)

    refresh_session_table()
    refresh_daily_goal()

    messagebox.showinfo(
        "Deleted",
        "Study session deleted successfully!"
    )


# =========================================================
# EDIT SESSION
# =========================================================

def edit_selected_session():
    global editing_session_id

    selected_items = session_table.selection()

    if not selected_items:
        messagebox.showwarning(
            "No Selection",
            "Please select a study session to edit."
        )
        return

    selected_item = selected_items[0]

    editing_session_id = int(selected_item)

    values = session_table.item(
        selected_item,
        "values"
    )

    # Clear existing form values
    subject_entry.delete(0, tk.END)
    topic_entry.delete(0, tk.END)
    duration_entry.delete(0, tk.END)

    # Populate selected session
    subject_entry.insert(0, values[1])
    topic_entry.insert(0, values[2])
    duration_entry.insert(0, values[3])

    save_changes_button.config(state="normal")


def save_changes():
    global editing_session_id

    if editing_session_id is None:
        return

    subject = subject_entry.get().strip().title()
    topic = topic_entry.get().strip()
    duration = duration_entry.get().strip()

    if not subject:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a subject."
        )
        return

    if not topic:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a topic."
        )
        return

    if not duration.isdigit() or int(duration) <= 0:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a valid duration in minutes."
        )
        return

    update_session_by_id(
        editing_session_id,
        subject,
        topic,
        int(duration)
    )

    editing_session_id = None

    subject_entry.delete(0, tk.END)
    topic_entry.delete(0, tk.END)
    duration_entry.delete(0, tk.END)

    save_changes_button.config(state="disabled")

    refresh_session_table()
    refresh_daily_goal()

    messagebox.showinfo(
        "Updated",
        "Study session updated successfully!"
    )


# =========================================================
# DAILY GOAL
# =========================================================

def refresh_daily_goal():
    goal = load_daily_goal_from_database()
    today_minutes = get_today_study_minutes()

    if goal is None:
        goal_label.config(
            text="Daily goal: Not set"
        )

        progress_label.config(
            text=f"Today's study: {today_minutes} minutes"
        )

        return

    progress = (today_minutes / goal) * 100

    goal_label.config(
        text=f"Daily goal: {goal} minutes"
    )

    progress_label.config(
        text=(
            f"Today's study: {today_minutes} minutes "
            f"({progress:.0f}%)"
        )
    )


def update_daily_goal():
    goal = goal_entry.get().strip()

    if not goal.isdigit() or int(goal) <= 0:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a valid daily goal in minutes."
        )
        return

    save_daily_goal_to_database(int(goal))

    goal_entry.delete(0, tk.END)

    refresh_daily_goal()

    messagebox.showinfo(
        "Success",
        "Daily study goal updated!"
    )


# =========================================================
# FILTER
# =========================================================

def filter_by_subject():
    subject = filter_subject_entry.get().strip().title()

    if not subject:
        messagebox.showwarning(
            "Missing Subject",
            "Please enter a subject to filter."
        )
        return

    sessions = get_sessions_by_subject(subject)

    refresh_session_table(sessions)


def clear_subject_filter():
    filter_subject_entry.delete(0, tk.END)

    refresh_session_table()


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

initialize_database()


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()

window.title("Study Tracker")
window.geometry("1000x750")
window.minsize(850, 650)


# =========================================================
# TITLE
# =========================================================

title_label = ttk.Label(
    window,
    text="Study Tracker",
    font=("Arial", 22)
)

title_label.pack(pady=20)


# =========================================================
# ADD / EDIT FORM
# =========================================================

form_frame = ttk.LabelFrame(
    window,
    text="Study Session"
)

form_frame.pack(
    padx=20,
    pady=10,
    fill="x"
)


ttk.Label(
    form_frame,
    text="Subject:"
).grid(
    row=0,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)


subject_entry = ttk.Entry(
    form_frame,
    width=30
)

subject_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=10
)


ttk.Label(
    form_frame,
    text="Topic:"
).grid(
    row=1,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)


topic_entry = ttk.Entry(
    form_frame,
    width=30
)

topic_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=10
)


ttk.Label(
    form_frame,
    text="Duration (minutes):"
).grid(
    row=2,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)


duration_entry = ttk.Entry(
    form_frame,
    width=30
)

duration_entry.grid(
    row=2,
    column=1,
    padx=10,
    pady=10
)


form_button_frame = ttk.Frame(form_frame)

form_button_frame.grid(
    row=0,
    column=2,
    rowspan=3,
    padx=20,
    pady=10
)


add_button = ttk.Button(
    form_button_frame,
    text="Add Study Session",
    command=add_study_session
)

add_button.pack(
    pady=5,
    fill="x"
)


save_changes_button = ttk.Button(
    form_button_frame,
    text="Save Changes",
    command=save_changes,
    state="disabled"
)

save_changes_button.pack(
    pady=5,
    fill="x"
)


# =========================================================
# DAILY GOAL
# =========================================================

goal_frame = ttk.LabelFrame(
    window,
    text="Daily Goal"
)

goal_frame.pack(
    padx=20,
    pady=10,
    fill="x"
)


goal_label = ttk.Label(
    goal_frame,
    text="Daily goal: Not set"
)

goal_label.grid(
    row=0,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)


progress_label = ttk.Label(
    goal_frame,
    text="Today's study: 0 minutes"
)

progress_label.grid(
    row=0,
    column=1,
    padx=20,
    pady=10,
    sticky="w"
)


ttk.Label(
    goal_frame,
    text="New goal:"
).grid(
    row=1,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)


goal_entry = ttk.Entry(
    goal_frame,
    width=15
)

goal_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=10,
    sticky="w"
)


goal_button = ttk.Button(
    goal_frame,
    text="Set Daily Goal",
    command=update_daily_goal
)

goal_button.grid(
    row=1,
    column=2,
    padx=10,
    pady=10
)


# =========================================================
# FILTER
# =========================================================

filter_frame = ttk.LabelFrame(
    window,
    text="Filter Sessions"
)

filter_frame.pack(
    padx=20,
    pady=10,
    fill="x"
)


ttk.Label(
    filter_frame,
    text="Subject:"
).grid(
    row=0,
    column=0,
    padx=10,
    pady=10
)


filter_subject_entry = ttk.Entry(
    filter_frame,
    width=25
)

filter_subject_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=10
)


filter_button = ttk.Button(
    filter_frame,
    text="Filter",
    command=filter_by_subject
)

filter_button.grid(
    row=0,
    column=2,
    padx=10,
    pady=10
)


show_all_button = ttk.Button(
    filter_frame,
    text="Show All",
    command=clear_subject_filter
)

show_all_button.grid(
    row=0,
    column=3,
    padx=10,
    pady=10
)


# =========================================================
# STUDY SESSION TABLE
# =========================================================

table_label = ttk.Label(
    window,
    text="Study Sessions",
    font=("Arial", 14)
)

table_label.pack(
    pady=(10, 5)
)


table_frame = ttk.Frame(window)

table_frame.pack(
    padx=20,
    pady=10,
    fill="both",
    expand=True
)


columns = (
    "date",
    "subject",
    "topic",
    "duration"
)


session_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="browse"
)


session_table.heading(
    "date",
    text="Date"
)

session_table.heading(
    "subject",
    text="Subject"
)

session_table.heading(
    "topic",
    text="Topic"
)

session_table.heading(
    "duration",
    text="Duration"
)


session_table.column(
    "date",
    width=120
)

session_table.column(
    "subject",
    width=200
)

session_table.column(
    "topic",
    width=300
)

session_table.column(
    "duration",
    width=100
)


# Vertical scrollbar

table_scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=session_table.yview
)

session_table.configure(
    yscrollcommand=table_scrollbar.set
)


session_table.pack(
    side="left",
    fill="both",
    expand=True
)

table_scrollbar.pack(
    side="right",
    fill="y"
)


# =========================================================
# TABLE ACTION BUTTONS
# =========================================================

action_frame = ttk.Frame(window)

action_frame.pack(
    pady=(0, 15)
)


edit_button = ttk.Button(
    action_frame,
    text="Edit Selected Session",
    command=edit_selected_session
)

edit_button.pack(
    side="left",
    padx=5
)


delete_button = ttk.Button(
    action_frame,
    text="Delete Selected Session",
    command=delete_selected_session
)

delete_button.pack(
    side="left",
    padx=5
)


# =========================================================
# INITIAL DATA LOAD
# =========================================================

refresh_session_table()
refresh_daily_goal()


# =========================================================
# START GUI
# =========================================================

window.mainloop()