# Student Management System

A menu-driven student record management project using Python, SQLite, and CSV.

## Features
- Add, view, search, update, and delete student records
- Input checks for required fields, age, academic year, gender, phone, and email
- SQLite database created automatically (`students.db`)
- Export records to CSV for Excel or Power BI
- Summary statistics (total students, average age, year-wise and gender-wise counts)

## Requirements
- Python 3.9+ (standard library only; no pip installs required)

## Run
Open a terminal in this folder and run:

```bash
python student_management_system.py
```

If `python` does not work on Windows, try:

```bash
py student_management_system.py
```

## Files
- `student_management_system.py` — application
- `students.db` — generated database after first run
- `students_export.csv` — generated when CSV export is selected

## Privacy
Use synthetic/sample records for demos. Do not publish real student phone numbers, email addresses, or other personal data. The database and export are local files; review them before sharing.

## Project attribution
This is a revised learning implementation prepared from the project idea shared in the conversation. If adapting code from another author's repository, preserve attribution and comply with that repository's license.
