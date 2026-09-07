import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from study_tracker import initialize_database, save_session_to_database


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

    messagebox.showinfo(
        "Success",
        "Study session added successfully!"
    )

    subject_entry.delete(0, tk.END)
    topic_entry.delete(0, tk.END)
    duration_entry.delete(0, tk.END)


initialize_database()

window = tk.Tk()
window.title("Study Tracker")
window.geometry("500x350")


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


window.mainloop()