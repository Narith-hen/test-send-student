from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import pandas as pd
import sqlite3
from datetime import datetime
import json
from functools import wraps

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')

mail = Mail(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database initialization
def init_db():
    conn = sqlite3.connect('student_results.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  email TEXT NOT NULL,
                  full_name TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  first_name TEXT NOT NULL,
                  last_name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  class TEXT,
                  hw1 REAL,
                  participation REAL,
                  q1 REAL,
                  final_khmer REAL,
                  final_english REAL,
                  total REAL,
                  grade TEXT,
                  comments TEXT,
                  upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  uploaded_by INTEGER,
                  FOREIGN KEY (uploaded_by) REFERENCES users (id))''')
    
    # Email logs table
    c.execute('''CREATE TABLE IF NOT EXISTS email_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_id INTEGER,
                  student_name TEXT,
                  student_email TEXT,
                  status TEXT,
                  sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  sent_by INTEGER,
                  error_message TEXT,
                  FOREIGN KEY (student_id) REFERENCES students (id),
                  FOREIGN KEY (sent_by) REFERENCES users (id))''')
    
    # Create default admin user
    default_password = generate_password_hash('admin123')
    try:
        c.execute("INSERT INTO users (username, password, email, full_name) VALUES (?, ?, ?, ?)",
                  ('admin', default_password, 'admin@school.com', 'Administrator'))
    except sqlite3.IntegrityError:
        pass  # User already exists
    
    conn.commit()
    conn.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = sqlite3.connect('student_results.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        user = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload')
@login_required
def upload_page():
    return render_template('upload.html')

@app.route('/students')
@login_required
def students_page():
    return render_template('students.html')

@app.route('/logs')
@login_required
def logs_page():
    return render_template('logs.html')

@app.route('/settings')
@login_required
def settings_page():
    return render_template('settings.html')

# API Endpoints
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type. Please upload CSV or Excel file'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read file based on extension
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Validate required columns
        required_columns = ['first name', 'last name', 'email', 'class', 'hw1', 'participation', 'q1', 'final khmer', 'final english', 'total', 'grade', 'comments']
        missing_columns = [col for col in required_columns if col not in df.columns.str.lower()]
        
        if missing_columns:
            os.remove(filepath)
            return jsonify({'success': False, 'message': f'Missing columns: {", ".join(missing_columns)}'}), 400
        
        # Normalize column names
        df.columns = df.columns.str.lower()
        
        # Store in database
        conn = sqlite3.connect('student_results.db')
        c = conn.cursor()
        
        # Clear existing students for this upload
        c.execute("DELETE FROM students WHERE uploaded_by = ?", (session['user_id'],))
        
        for _, row in df.iterrows():
            c.execute('''INSERT INTO students 
                         (first_name, last_name, email, class, hw1, participation, q1, final_khmer, final_english, total, grade, comments, uploaded_by)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (row['first name'], row['last name'], row['email'], row['class'], 
                       row['hw1'], row['participation'], row['q1'], row['final khmer'], 
                       row['final english'], row['total'], row['grade'], row['comments'], session['user_id']))
        
        conn.commit()
        conn.close()
        
        # Clean up file
        os.remove(filepath)
        
        return jsonify({'success': True, 'message': f'Successfully uploaded {len(df)} students', 'count': len(df)})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'}), 500

@app.route('/api/students', methods=['GET'])
@login_required
def get_students():
    conn = sqlite3.connect('student_results.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    students = c.execute("SELECT * FROM students WHERE uploaded_by = ? ORDER BY id DESC", (session['user_id'],)).fetchall()
    conn.close()
    
    students_list = [dict(student) for student in students]
    return jsonify({'success': True, 'students': students_list})

@app.route('/api/send-emails', methods=['POST'])
@login_required
def send_emails():
    data = request.get_json()
    student_ids = data.get('student_ids', [])
    
    if not student_ids:
        return jsonify({'success': False, 'message': 'No students selected'}), 400
    
    # Check if email is configured
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        return jsonify({
            'success': False, 
            'message': 'Email not configured. Please go to Settings and configure your email first.'
        }), 400
    
    conn = sqlite3.connect('student_results.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    success_count = 0
    failed_count = 0
    results = []
    
    for student_id in student_ids:
        student = c.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        
        if not student:
            continue
        
        try:
            # Create email message
            student_name = f"{student['first_name']} {student['last_name']}"
            msg = Message(
                subject=f"Academic Results - {student['class']}",
                recipients=[student['email']]
            )
            
            # Plain text email body (fallback)
            msg.body = f'''
Academic Results Report
Class: {student['class']}

Dear {student_name},

We are pleased to share your academic results for {student['class']}.

Assessment Scores:
- Homework 1 (HW1): {student['hw1']}
- Participation: {student['participation']}
- Quiz 1 (Q1): {student['q1']}
- Final Exam - Khmer: {student['final_khmer']}
- Final Exam - English: {student['final_english']}

Total Score: {student['total']}
Final Grade: {student['grade']}

{f"Teacher Comments: {student['comments']}" if student['comments'] else ''}

Keep up the great work!

Best regards,
Academic Department

---
This is an automated email. Please do not reply to this message.
            '''
            
            # HTML email body (for modern email clients)
            msg.html = f'''
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .result-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
                    .result-table th, .result-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                    .result-table th {{ background-color: #667eea; color: white; }}
                    .total {{ font-weight: bold; font-size: 18px; color: #667eea; }}
                    .grade-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; background: #667eea; color: white; font-weight: bold; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                    .comments {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 15px; border-left: 4px solid #ffc107; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Academic Results Report</h1>
                        <p>Class: {student['class']}</p>
                    </div>
                    <div class="content">
                        <h2>Dear {student_name},</h2>
                        <p>We are pleased to share your academic results for {student['class']}.</p>
                        
                        <table class="result-table">
                            <tr>
                                <th>Assessment</th>
                                <th>Score</th>
                            </tr>
                            <tr>
                                <td>Homework 1 (HW1)</td>
                                <td>{student['hw1']}</td>
                            </tr>
                            <tr>
                                <td>Participation</td>
                                <td>{student['participation']}</td>
                            </tr>
                            <tr>
                                <td>Quiz 1 (Q1)</td>
                                <td>{student['q1']}</td>
                            </tr>
                            <tr>
                                <td>Final Exam - Khmer</td>
                                <td>{student['final_khmer']}</td>
                            </tr>
                            <tr>
                                <td>Final Exam - English</td>
                                <td>{student['final_english']}</td>
                            </tr>
                            <tr class="total">
                                <td>Total Score</td>
                                <td>{student['total']}</td>
                            </tr>
                            <tr class="total">
                                <td>Final Grade</td>
                                <td><span class="grade-badge">{student['grade']}</span></td>
                            </tr>
                        </table>
                        
                        {f'<div class="comments"><strong>Teacher Comments:</strong><br>{student["comments"]}</div>' if student['comments'] else ''}
                        
                        <p>Keep up the great work!</p>
                        <p>Best regards,<br>Academic Department</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email. Please do not reply to this message.</p>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            # Send email
            try:
                mail.send(msg)
                
                # Log success
                c.execute('''INSERT INTO email_logs 
                             (student_id, student_name, student_email, status, sent_by)
                             VALUES (?, ?, ?, ?, ?)''',
                          (student['id'], student_name, student['email'], 'success', session['user_id']))
                
                success_count += 1
                results.append({'id': student['id'], 'name': student_name, 'status': 'success'})
                
            except Exception as email_error:
                # Log failure with detailed error
                error_msg = f"{type(email_error).__name__}: {str(email_error)}"
                c.execute('''INSERT INTO email_logs 
                             (student_id, student_name, student_email, status, sent_by, error_message)
                             VALUES (?, ?, ?, ?, ?, ?)''',
                          (student['id'], student_name, student['email'], 'failed', session['user_id'], error_msg))
                
                failed_count += 1
                results.append({'id': student['id'], 'name': student_name, 'status': 'failed', 'error': error_msg})
                print(f"Error sending to {student_name}: {error_msg}")  # Print to console for debugging
            
        except Exception as e:
            # Catch any other errors (like invalid student data)
            error_msg = f"General error: {str(e)}"
            print(f"Error processing student {student_id}: {error_msg}")
            failed_count += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Sent {success_count} emails successfully, {failed_count} failed',
        'success_count': success_count,
        'failed_count': failed_count,
        'results': results
    })

@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    conn = sqlite3.connect('student_results.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    logs = c.execute('''SELECT * FROM email_logs 
                        WHERE sent_by = ? 
                        ORDER BY sent_date DESC 
                        LIMIT 100''', (session['user_id'],)).fetchall()
    conn.close()
    
    logs_list = [dict(log) for log in logs]
    return jsonify({'success': True, 'logs': logs_list})

@app.route('/api/export-logs', methods=['GET'])
@login_required
def export_logs():
    conn = sqlite3.connect('student_results.db')
    df = pd.read_sql_query('''SELECT student_name, student_email, status, sent_date, error_message 
                              FROM email_logs 
                              WHERE sent_by = ? 
                              ORDER BY sent_date DESC''', conn, params=(session['user_id'],))
    conn.close()
    
    filename = f'email_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df.to_csv(filepath, index=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    conn = sqlite3.connect('student_results.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Total students
    total_students = c.execute("SELECT COUNT(*) as count FROM students WHERE uploaded_by = ?", 
                               (session['user_id'],)).fetchone()['count']
    
    # Total emails sent
    total_sent = c.execute("SELECT COUNT(*) as count FROM email_logs WHERE sent_by = ? AND status = 'success'", 
                          (session['user_id'],)).fetchone()['count']
    
    # Failed emails
    total_failed = c.execute("SELECT COUNT(*) as count FROM email_logs WHERE sent_by = ? AND status = 'failed'", 
                            (session['user_id'],)).fetchone()['count']
    
    # Average scores
    avg_scores = c.execute('''SELECT 
                              AVG(hw1) as avg_hw1,
                              AVG(participation) as avg_participation,
                              AVG(q1) as avg_q1,
                              AVG(final_khmer) as avg_final_khmer,
                              AVG(final_english) as avg_final_english,
                              AVG(total) as avg_total
                              FROM students WHERE uploaded_by = ?''', (session['user_id'],)).fetchone()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_students': total_students,
            'total_sent': total_sent,
            'total_failed': total_failed,
            'avg_hw1': round(avg_scores['avg_hw1'] or 0, 2),
            'avg_participation': round(avg_scores['avg_participation'] or 0, 2),
            'avg_q1': round(avg_scores['avg_q1'] or 0, 2),
            'avg_final_khmer': round(avg_scores['avg_final_khmer'] or 0, 2),
            'avg_final_english': round(avg_scores['avg_final_english'] or 0, 2),
            'avg_total': round(avg_scores['avg_total'] or 0, 2)
        }
    })

@app.route('/api/update-email-config', methods=['POST'])
@login_required
def update_email_config():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    # Update email configuration
    app.config['MAIL_USERNAME'] = email
    app.config['MAIL_PASSWORD'] = password
    app.config['MAIL_DEFAULT_SENDER'] = email
    
    # Save to .env file for persistence
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'w') as f:
            f.write(f'MAIL_USERNAME={email}\n')
            f.write(f'MAIL_PASSWORD={password}\n')
            f.write(f'SECRET_KEY=your-secret-key-change-in-production\n')
    except Exception as e:
        print(f"Warning: Could not save to .env file: {e}")
    
    # Reinitialize mail
    global mail
    mail = Mail(app)
    
    return jsonify({'success': True, 'message': 'Email configuration updated and saved successfully'})

def get_grade(average):
    if average >= 90:
        return 'A'
    elif average >= 80:
        return 'B'
    elif average >= 70:
        return 'C'
    elif average >= 60:
        return 'D'
    else:
        return 'F'

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
