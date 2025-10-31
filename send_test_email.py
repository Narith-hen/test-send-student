from flask_mail import Mail, Message
from flask import Flask
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Setup Flask app
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')

mail = Mail(app)

# Test student data
test_student = {
    'first_name': 'Narith',
    'last_name': 'Hen',
    'class': 'Web Development',
    'hw1': 95,
    'participation': 90,
    'q1': 88,
    'final_khmer': 85,
    'final_english': 92,
    'total': 450,
    'grade': 'A',
    'comments': 'Excellent work! Keep it up.'
}

print("=" * 60)
print("SENDING TEST EMAIL")
print("=" * 60)
print(f"From: {app.config['MAIL_USERNAME']}")
print(f"To: {app.config['MAIL_USERNAME']} (sending to yourself)")
print("Subject: Test - Academic Results")
print("=" * 60)

try:
    with app.app_context():
        student_name = f"{test_student['first_name']} {test_student['last_name']}"
        
        msg = Message(
            subject=f"TEST - Academic Results - {test_student['class']}",
            recipients=[app.config['MAIL_USERNAME']]  # Send to yourself for testing
        )
        
        # Plain text version
        msg.body = f'''
Academic Results Report
Class: {test_student['class']}

Dear {student_name},

We are pleased to share your academic results for {test_student['class']}.

Assessment Scores:
- Homework 1 (HW1): {test_student['hw1']}
- Participation: {test_student['participation']}
- Quiz 1 (Q1): {test_student['q1']}
- Final Exam - Khmer: {test_student['final_khmer']}
- Final Exam - English: {test_student['final_english']}

Total Score: {test_student['total']}
Final Grade: {test_student['grade']}

Teacher Comments: {test_student['comments']}

Keep up the great work!

Best regards,
Academic Department

---
This is a TEST email from Student Result System.
'''
        
        # HTML version
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
                .test-banner {{ background: #dc3545; color: white; padding: 10px; text-align: center; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="test-banner">⚠️ THIS IS A TEST EMAIL ⚠️</div>
            <div class="container">
                <div class="header">
                    <h1>📚 Academic Results Report</h1>
                    <p>Class: {test_student['class']}</p>
                </div>
                <div class="content">
                    <h2>Dear {student_name},</h2>
                    <p>We are pleased to share your academic results for {test_student['class']}.</p>
                    
                    <table class="result-table">
                        <tr>
                            <th>Assessment</th>
                            <th>Score</th>
                        </tr>
                        <tr>
                            <td>Homework 1 (HW1)</td>
                            <td>{test_student['hw1']}</td>
                        </tr>
                        <tr>
                            <td>Participation</td>
                            <td>{test_student['participation']}</td>
                        </tr>
                        <tr>
                            <td>Quiz 1 (Q1)</td>
                            <td>{test_student['q1']}</td>
                        </tr>
                        <tr>
                            <td>Final Exam - Khmer</td>
                            <td>{test_student['final_khmer']}</td>
                        </tr>
                        <tr>
                            <td>Final Exam - English</td>
                            <td>{test_student['final_english']}</td>
                        </tr>
                        <tr class="total">
                            <td>Total Score</td>
                            <td>{test_student['total']}</td>
                        </tr>
                        <tr class="total">
                            <td>Final Grade</td>
                            <td><span class="grade-badge">{test_student['grade']}</span></td>
                        </tr>
                    </table>
                    
                    <div class="comments"><strong>📝 Teacher Comments:</strong><br>{test_student['comments']}</div>
                    
                    <p>Keep up the great work! 🎉</p>
                    <p>Best regards,<br>Academic Department</p>
                </div>
                <div class="footer">
                    <p>This is a TEST email from Student Result System.</p>
                    <p>You are receiving this because you sent it to yourself for testing.</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        mail.send(msg)
        
        print("✅ SUCCESS! Test email sent.")
        print(f"\nCheck your inbox at: {app.config['MAIL_USERNAME']}")
        print("Also check your SPAM/JUNK folder if you don't see it.")
        print("\nThe email contains:")
        print("- Beautiful HTML design with gradient header")
        print("- Table with all assessment scores")
        print("- Teacher comments section")
        print("- Plain text fallback for simple email clients")
        
except Exception as e:
    print(f"❌ ERROR sending email: {e}")
    print(f"\nError type: {type(e).__name__}")
    import traceback
    print("\nFull error:")
    traceback.print_exc()

print("=" * 60)
