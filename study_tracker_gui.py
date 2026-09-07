import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from study_tracker import (
    initialize_database,
    save_session_to_database,
    load_sessions_from_database,
    delete_session_by_id
)

def refresh_session_table():
    for item in session_table.get_children():
        session_table.delete(item)

    sessions = load_sessions_from_database()

    for session in sessions:
        session_table.insert(
            "",
            tk.END,
            iid=str(session[0]),
            values=(
                session[1],
                session[2],
                session[3],
                session[4]
            )
        )

def add_study_session():
    subject = subject_entry.get().strip().title()
    topic = topic_entry.get().strip()
    duration = duration_entry.get().strip()

    if not subject:
        messagebox.showerror("Invalid Input", "Please enter a subject.")
        return

    if not topic:
        messagebox.showerror("Invalid Input", "Please enter a topic.")
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
    refresh_session_table()

    messagebox.showinfo(
        "Success",
        "Study session added successfully!"
    )

    subject_entry.delete(0, tk.END)
    topic_entry.delete(0, tk.END)
    duration_entry.delete(0, tk.END)


initialize_database()

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

    messagebox.showinfo(
        "Deleted",
        "Study session deleted successfully!"
    )

window = tk.Tk()
window.title("Study Tracker")
window.geometry("850x550")


title_label = ttk.Label(
    window,
    text="Study Tracker",
    font=("Arial", 20)
)
title_label.pack(pady=20)


form_frame = ttk.Frame(window)
form_frame.pack(pady=10)


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

subject_entry = ttk.Entry(form_frame, width=30)
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

topic_entry = ttk.Entry(form_frame, width=30)
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

duration_entry = ttk.Entry(form_frame, width=30)
duration_entry.grid(
    row=2,
    column=1,
    padx=10,
    pady=10
)


add_button = ttk.Button(
    window,
    text="Add Study Session",
    command=add_study_session
)
add_button.pack(pady=20)

table_label = ttk.Label(
    window,
    text="Study Sessions",
    font=("Arial", 14)
)
table_label.pack(pady=(20, 5))


table_frame = ttk.Frame(window)
table_frame.pack(
    padx=20,
    pady=10,
    fill="both",
    expand=True
)


columns = ("date", "subject", "topic", "duration")

session_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)


session_table.heading("date", text="Date")
session_table.heading("subject", text="Subject")
session_table.heading("topic", text="Topic")
session_table.heading("duration", text="Duration")


session_table.column("date", width=120)
session_table.column("subject", width=180)
session_table.column("topic", width=250)
session_table.column("duration", width=100)


session_table.pack(
    fill="both",
    expand=True
)

delete_button = ttk.Button(
    window,
    text="Delete Selected Session",
    command=delete_selected_session
)

delete_button.pack(pady=10)

refresh_session_table()

window.mainloop()