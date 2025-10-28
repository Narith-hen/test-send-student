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
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  english REAL,
                  professional_life REAL,
                  algorithm REAL,
                  web_design REAL,
                  term1_total REAL,
                  year TEXT,
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
        required_columns = ['name', 'email', 'english', 'professional_life', 'algorithm', 'web_design', 'term1_total', 'year']
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
                         (name, email, english, professional_life, algorithm, web_design, term1_total, year, uploaded_by)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (row['name'], row['email'], row['english'], row['professional_life'], 
                       row['algorithm'], row['web_design'], row['term1_total'], row['year'], session['user_id']))
        
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
            msg = Message(
                subject=f"Academic Results - Term 1, {student['year']}",
                recipients=[student['email']]
            )
            
            # Calculate grade
            average = student['term1_total'] / 4
            grade = get_grade(average)
            
            # Email body
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
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Academic Results Report</h1>
                        <p>Term 1 - {student['year']}</p>
                    </div>
                    <div class="content">
                        <h2>Dear {student['name']},</h2>
                        <p>We are pleased to share your academic results for Term 1, {student['year']}.</p>
                        
                        <table class="result-table">
                            <tr>
                                <th>Subject</th>
                                <th>Score</th>
                            </tr>
                            <tr>
                                <td>English</td>
                                <td>{student['english']}</td>
                            </tr>
                            <tr>
                                <td>Professional Life</td>
                                <td>{student['professional_life']}</td>
                            </tr>
                            <tr>
                                <td>Algorithm</td>
                                <td>{student['algorithm']}</td>
                            </tr>
                            <tr>
                                <td>Web Design</td>
                                <td>{student['web_design']}</td>
                            </tr>
                            <tr class="total">
                                <td>Total</td>
                                <td>{student['term1_total']}</td>
                            </tr>
                            <tr class="total">
                                <td>Average</td>
                                <td>{average:.2f}</td>
                            </tr>
                            <tr class="total">
                                <td>Grade</td>
                                <td>{grade}</td>
                            </tr>
                        </table>
                        
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
            mail.send(msg)
            
            # Log success
            c.execute('''INSERT INTO email_logs 
                         (student_id, student_name, student_email, status, sent_by)
                         VALUES (?, ?, ?, ?, ?)''',
                      (student['id'], student['name'], student['email'], 'success', session['user_id']))
            
            success_count += 1
            results.append({'id': student['id'], 'name': student['name'], 'status': 'success'})
            
        except Exception as e:
            # Log failure
            c.execute('''INSERT INTO email_logs 
                         (student_id, student_name, student_email, status, sent_by, error_message)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (student['id'], student['name'], student['email'], 'failed', session['user_id'], str(e)))
            
            failed_count += 1
            results.append({'id': student['id'], 'name': student['name'], 'status': 'failed', 'error': str(e)})
    
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
                              AVG(english) as avg_english,
                              AVG(professional_life) as avg_professional,
                              AVG(algorithm) as avg_algorithm,
                              AVG(web_design) as avg_web_design
                              FROM students WHERE uploaded_by = ?''', (session['user_id'],)).fetchone()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_students': total_students,
            'total_sent': total_sent,
            'total_failed': total_failed,
            'avg_english': round(avg_scores['avg_english'] or 0, 2),
            'avg_professional': round(avg_scores['avg_professional'] or 0, 2),
            'avg_algorithm': round(avg_scores['avg_algorithm'] or 0, 2),
            'avg_web_design': round(avg_scores['avg_web_design'] or 0, 2)
        }
    })

@app.route('/api/update-email-config', methods=['POST'])
@login_required
def update_email_config():
    data = request.get_json()
    
    # Update email configuration
    app.config['MAIL_USERNAME'] = data.get('email')
    app.config['MAIL_PASSWORD'] = data.get('password')
    app.config['MAIL_DEFAULT_SENDER'] = data.get('email')
    
    # Reinitialize mail
    global mail
    mail = Mail(app)
    
    return jsonify({'success': True, 'message': 'Email configuration updated successfully'})

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
