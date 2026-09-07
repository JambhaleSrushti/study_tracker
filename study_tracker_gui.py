import tkinter as tk
from tkinter import ttk


def show_form_values():
    subject = subject_entry.get().strip()
    topic = topic_entry.get().strip()
    duration = duration_entry.get().strip()

    print("Subject:", subject)
    print("Topic:", topic)
    print("Duration:", duration)


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


ttk.Label(form_frame, text="Subject:").grid(
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


ttk.Label(form_frame, text="Topic:").grid(
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


ttk.Label(form_frame, text="Duration (minutes):").grid(
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
    command=show_form_values
)

add_button.pack(pady=20)


window.mainloop()