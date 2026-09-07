# Study Tracker

A Python Study Tracker developed incrementally from a basic command-line application into a SQLite-backed desktop application.

The project was intentionally built step by step, with each meaningful improvement committed separately to GitHub.

## Features

### Study Sessions

- Add study sessions
- View all study sessions
- Edit existing sessions
- Delete sessions
- Automatically record the study date
- Validate study duration
- Trim user input to avoid accidental spaces

Each study session contains:

- Date
- Subject
- Topic
- Duration in minutes

### Search and Filtering

- Filter sessions by subject
- Search sessions by topic
- Filter sessions by date
- Sort sessions by date

### Daily Goals and Progress

- Set a daily study goal
- Store the goal in SQLite
- View today's study time
- View daily goal completion percentage
- Track current study streak

### Statistics

- Total study time
- Study time by subject
- Weekly study statistics
- Monthly study statistics

### Desktop Application

The project includes a Tkinter desktop interface with:

- Study session form
- Study session table
- Add, edit, and delete actions
- Daily goal tracking
- Study summary dashboard
- Subject filtering
- Topic search
- Scrollable study session table
- Persistent SQLite storage

## Technologies Used

- Python
- SQLite
- Tkinter
- Git
- GitHub

## Project Structure

```text
study-tracker/
├── study_tracker.py
├── study_tracker_gui.py
├── README.md
└── .gitignore