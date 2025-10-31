import sqlite3
from datetime import datetime

# Check email logs
conn = sqlite3.connect('student_results.db')
c = conn.cursor()

print("=" * 60)
print("RECENT EMAIL LOGS (Last 10)")
print("=" * 60)

logs = c.execute('''SELECT student_name, student_email, status, error_message, sent_date 
                    FROM email_logs 
                    ORDER BY sent_date DESC 
                    LIMIT 10''').fetchall()

if logs:
    for i, log in enumerate(logs, 1):
        print(f"\n{i}. {log[0]} ({log[1]})")
        print(f"   Status: {log[2]}")
        print(f"   Time: {log[4]}")
        if log[3]:
            print(f"   Error: {log[3]}")
else:
    print("No email logs found.")

print("\n" + "=" * 60)
print("STUDENTS IN DATABASE")
print("=" * 60)

students = c.execute('SELECT id, first_name, last_name, email, class FROM students LIMIT 5').fetchall()
if students:
    for student in students:
        print(f"{student[0]}. {student[1]} {student[2]} ({student[3]}) - {student[4]}")
else:
    print("No students found.")

conn.close()

print("\n" + "=" * 60)
print("EMAIL CONFIGURATION CHECK")
print("=" * 60)

import os
from dotenv import load_dotenv
load_dotenv()

mail_user = os.environ.get('MAIL_USERNAME', 'NOT SET')
mail_pass = os.environ.get('MAIL_PASSWORD', 'NOT SET')

print(f"MAIL_USERNAME: {mail_user}")
print(f"MAIL_PASSWORD: {'*' * len(mail_pass) if mail_pass != 'NOT SET' else 'NOT SET'}")
