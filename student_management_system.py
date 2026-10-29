"""
Student Management System
Python + SQLite + CSV export

Run: python student_management_system.py
Database is created automatically in the same folder.
"""

import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "students.db"
EXPORT_PATH = BASE_DIR / "students_export.csv"


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK(age BETWEEN 1 AND 120),
            year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 10),
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    return conn


def input_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be blank. Try again.")


def input_int(prompt, minimum=None, maximum=None):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"Value must be at least {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"Value must be at most {maximum}.")
            continue
        return value


def input_phone(prompt="Phone number (10 digits): "):
    while True:
        phone = input(prompt).strip()
        # Kept as text so leading zeroes are not lost.
        if phone.isdigit() and len(phone) == 10:
            return phone
        print("Enter exactly 10 digits (digits only).")


def input_email(prompt="Email: "):
    while True:
        email = input(prompt).strip()
        if (
            len(email) <= 254
            and "@" in email
            and email.rfind(".") > email.find("@") + 1
            and " " not in email
        ):
            return email
        print("Enter a valid-looking email address.")


def input_gender(prompt="Gender (Male/Female/Other/Prefer not to say): "):
    allowed = {
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "prefer not to say": "Prefer not to say",
    }
    while True:
        value = input(prompt).strip().lower()
        if value in allowed:
            return allowed[value]
        print("Choose Male, Female, Other, or Prefer not to say.")


def fetch_student(student_id):
    with connect_db() as conn:
        return conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()


def print_student(student):
    if not student:
        return
    print("-" * 45)
    print(f"Student ID : {student['student_id']}")
    print(f"Name       : {student['name']}")
    print(f"Age        : {student['age']}")
    print(f"Year       : {student['year']}")
    print(f"Gender     : {student['gender']}")
    print(f"Phone      : {student['phone']}")
    print(f"Email      : {student['email']}")
    print("-" * 45)


def add_student():
    print("\n--- Add Student ---")
    student_id = input_int("Student ID (positive number): ", 1)
    if fetch_student(student_id):
        print("That student ID already exists.")
        return

    name = input_nonempty("Full name: ")
    age = input_int("Age (1-120): ", 1, 120)
    year = input_int("Academic year (1-10): ", 1, 10)
    gender = input_gender()
    phone = input_phone()
    email = input_email()

    try:
        with connect_db() as conn:
            conn.execute("""
                INSERT INTO students
                (student_id, name, age, year, gender, phone, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, name, age, year, gender, phone, email))
        print("Student added successfully.")
    except sqlite3.IntegrityError:
        print("Could not add record. Check the details and try again.")


def view_students():
    with connect_db() as conn:
        students = conn.execute(
            "SELECT * FROM students ORDER BY student_id"
        ).fetchall()
    if not students:
        print("\nNo student records found.")
        return

    print(f"\nStudents found: {len(students)}")
    for student in students:
        print_student(student)


def search_student():
    print("\n--- Search Student ---")
    student_id = input_int("Enter student ID: ", 1)
    student = fetch_student(student_id)
    if student:
        print_student(student)
    else:
        print("No student found with that ID.")


def update_student():
    print("\n--- Update Student ---")
    student_id = input_int("Enter student ID to update: ", 1)
    student = fetch_student(student_id)
    if not student:
        print("No student found with that ID.")
        return

    print_student(student)
    print("Press Enter to keep the current value.")
    fields = {
        "name": ("Name", student["name"]),
        "age": ("Age", str(student["age"])),
        "year": ("Academic year", str(student["year"])),
        "gender": ("Gender", student["gender"]),
        "phone": ("Phone", student["phone"]),
        "email": ("Email", student["email"]),
    }
    updated = {}
    for key, (label, current) in fields.items():
        while True:
            value = input(f"{label} [{current}]: ").strip()
            if not value:
                updated[key] = current
                break
            if key == "age":
                try:
                    num = int(value)
                    if 1 <= num <= 120:
                        updated[key] = num
                        break
                except ValueError:
                    pass
                print("Age must be a whole number from 1 to 120.")
            elif key == "year":
                try:
                    num = int(value)
                    if 1 <= num <= 10:
                        updated[key] = num
                        break
                except ValueError:
                    pass
                print("Year must be a whole number from 1 to 10.")
            elif key == "gender":
                allowed = {
                    "male": "Male", "female": "Female", "other": "Other",
                    "prefer not to say": "Prefer not to say"
                }
                if value.lower() in allowed:
                    updated[key] = allowed[value.lower()]
                    break
                print("Choose Male, Female, Other, or Prefer not to say.")
            elif key == "phone":
                if value.isdigit() and len(value) == 10:
                    updated[key] = value
                    break
                print("Enter exactly 10 digits.")
            elif key == "email":
                if ("@" in value and value.rfind(".") > value.find("@") + 1
                        and " " not in value and len(value) <= 254):
                    updated[key] = value
                    break
                print("Enter a valid-looking email.")
            else:
                updated[key] = value
                break

    with connect_db() as conn:
        conn.execute("""
            UPDATE students
            SET name=?, age=?, year=?, gender=?, phone=?, email=?
            WHERE student_id=?
        """, (
            updated["name"], updated["age"], updated["year"],
            updated["gender"], updated["phone"], updated["email"],
            student_id
        ))
    print("Student updated successfully.")


def delete_student():
    print("\n--- Delete Student ---")
    student_id = input_int("Enter student ID to delete: ", 1)
    student = fetch_student(student_id)
    if not student:
        print("No student found with that ID.")
        return

    print_student(student)
    confirm = input("Permanently delete this record? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Delete cancelled.")
        return

    with connect_db() as conn:
        conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    print("Student deleted.")


def export_csv():
    with connect_db() as conn:
        students = conn.execute(
            "SELECT * FROM students ORDER BY student_id"
        ).fetchall()
    headers = ["student_id", "name", "age", "year", "gender", "phone", "email"]
    with EXPORT_PATH.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for student in students:
            writer.writerow([student[h] for h in headers])
    print(f"Export complete: {EXPORT_PATH}")
    print("Open this CSV file in Excel or import it into Power BI.")
    print("Protect personal student data; share only anonymized/sample data.")


def show_statistics():
    with connect_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        avg_age = conn.execute("SELECT AVG(age) FROM students").fetchone()[0]
        year_rows = conn.execute("""
            SELECT year, COUNT(*) AS count
            FROM students GROUP BY year ORDER BY year
        """).fetchall()
        gender_rows = conn.execute("""
            SELECT gender, COUNT(*) AS count
            FROM students GROUP BY gender ORDER BY gender
        """).fetchall()

    print("\n--- Student Statistics ---")
    print(f"Total students: {total}")
    print(f"Average age: {avg_age:.1f}" if avg_age is not None else "Average age: N/A")
    print("\nStudents by academic year:")
    if year_rows:
        for row in year_rows:
            print(f"  Year {row['year']}: {row['count']}")
    else:
        print("  No records yet.")
    print("\nStudents by gender:")
    if gender_rows:
        for row in gender_rows:
            print(f"  {row['gender']}: {row['count']}")
    else:
        print("  No records yet.")


def show_menu():
    print("""
========== STUDENT MANAGEMENT SYSTEM ==========
1. Add student
2. View all students
3. Search student
4. Update student
5. Delete student
6. Export students to CSV
7. Show statistics
8. Exit
===============================================
""")


def main():
    # Create the database/table at startup.
    with connect_db():
        pass

    while True:
        show_menu()
        choice = input("Choose an option (1-8): ").strip()
        actions = {
            "1": add_student,
            "2": view_students,
            "3": search_student,
            "4": update_student,
            "5": delete_student,
            "6": export_csv,
            "7": show_statistics,
        }
        if choice == "8":
            print("Thank you for using Student Management System.")
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except (sqlite3.Error, OSError) as error:
                print(f"An operation failed: {error}")
        else:
            print("Invalid choice. Please choose 1 to 8.")


if __name__ == "__main__":
    main()
