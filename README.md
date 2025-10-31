# 🎓 Student Result System

A professional web application for teachers and administrators to send student scores automatically via email with just one click. Built with Flask and modern UI design.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 📸 Screenshots

### Dashboard
Modern analytics dashboard with statistics and charts showing student performance metrics.

### Upload Results
Drag-and-drop interface for easy CSV/Excel file uploads with real-time validation.

### Students Management
Interactive table to view, search, and select students for bulk email sending.

### Email Logs
Comprehensive logging system to track email delivery status and history.

## ✨ Features

- ✅ **Bulk Email Sending** - Send personalized results to multiple students with one click
- ✅ **CSV/Excel Upload** - Import student data from spreadsheet files
- ✅ **Email Templates** - Professional HTML email templates with grade calculations
- ✅ **Analytics Dashboard** - View statistics, charts, and performance metrics
- ✅ **Email Logs** - Track email delivery status with detailed logging
- ✅ **Export Reports** - Download email logs as CSV for record keeping
- ✅ **User Authentication** - Secure login system for teachers/admins
- ✅ **Responsive Design** - Modern UI with Tailwind CSS that works on all devices
- ✅ **Search & Filter** - Find students and logs quickly with search functionality
- ✅ **Grade Calculation** - Automatic grade calculation based on average scores

## 🚀 Technology Stack

**Backend:**
- Python 3.8+
- Flask 3.0.0 (REST API)
- SQLite (Database)
- Flask-Mail (Email service)

**Frontend:**
- HTML5
- Tailwind CSS (Styling)
- JavaScript (ES6+)
- Font Awesome (Icons)
- Chart.js (Analytics charts)

**Libraries:**
- Pandas (Data processing)
- openpyxl (Excel support)
- Werkzeug (Security)

## 📋 Prerequisites

- Python 3.8 or higher
- Gmail account with App Password enabled
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🔧 Installation

### 1. Clone or Download the Project

```bash
cd test-send-student
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Email Settings

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Enable 2-factor authentication on your Gmail account

3. Generate App Password:
   - Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and your device
   - Copy the 16-character password

4. Edit `.env` file:
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-character-app-password
   SECRET_KEY=your-random-secret-key
   ```

## 🎯 Running the Application

### 1. Start the Server

```bash
python app.py
```

The application will start at `http://localhost:5000`

### 2. Login

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change the default password after first login!

### 3. Configure Email

1. Go to Settings page
2. Enter your Gmail address
3. Paste your App Password
4. Click "Save Configuration"

## 📊 Usage Guide

### Step 1: Upload Student Results

1. Navigate to "Upload Results" page
2. Prepare your CSV/Excel file with required columns:
   - `First name` - Student's first name
   - `Last name` - Student's last name
   - `Email` - Student's email address
   - `Class` - Class or course name
   - `HW1` - Homework 1 score
   - `Participation` - Participation score
   - `Q1` - Quiz 1 score
   - `Final Khmer` - Final exam Khmer score
   - `Final English` - Final exam English score
   - `Total` - Total points
   - `Grade` - Letter grade (A+, A, B+, B, etc.)
   - `Comments` - Teacher comments

3. Drag & drop or click to upload file
4. Click "Upload Results"

**Sample CSV Format:**
```csv
First name,Last name,Email,Class,HW1,Participation,Q1,Final Khmer,Final English,Total,Grade,Comments
John,Doe,john@example.com,Web Development,95,90,88,85,92,450,A,Excellent work
Jane,Smith,jane@example.com,Data Science,92,88,95,89,94,458,A,Outstanding performance
```

### Step 2: Preview & Select Students

1. Go to "Students" page
2. Review uploaded student data
3. Use search to find specific students
4. Select students using checkboxes
5. Use "Select All" for bulk selection

### Step 3: Send Results

1. Click "Send Results" button
2. Monitor progress in the modal
3. View success/failure notifications
4. Check "Email Logs" for detailed status

### Step 4: Review Logs

1. Navigate to "Email Logs" page
2. Filter by status (Success/Failed)
3. Search by student name or email
4. Export logs as CSV for record keeping

## 📁 Project Structure

```
test-send-student/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── student_results.db         # SQLite database (auto-created)
├── README.md                  # This file
├── templates/                 # HTML templates
│   ├── login.html            # Login page
│   ├── dashboard.html        # Dashboard with analytics
│   ├── upload.html           # File upload interface
│   ├── students.html         # Student management
│   ├── logs.html             # Email logs viewer
│   └── settings.html         # Configuration settings
└── uploads/                   # Temporary upload folder
```

## 🗄️ Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `password` - Hashed password
- `email` - User email
- `full_name` - Full name
- `created_at` - Creation timestamp

### Students Table
- `id` - Primary key
- `first_name` - Student first name
- `last_name` - Student last name
- `email` - Student email
- `class` - Class or course name
- `hw1` - Homework 1 score
- `participation` - Participation score
- `q1` - Quiz 1 score
- `final_khmer` - Final exam Khmer score
- `final_english` - Final exam English score
- `total` - Total points
- `grade` - Letter grade
- `comments` - Teacher comments
- `upload_date` - Upload timestamp
- `uploaded_by` - User ID (foreign key)

### Email Logs Table
- `id` - Primary key
- `student_id` - Student ID (foreign key)
- `student_name` - Student name
- `student_email` - Student email
- `status` - success/failed
- `sent_date` - Sent timestamp
- `sent_by` - User ID (foreign key)
- `error_message` - Error details (if failed)

## 🎨 UI Features

- **Modern Gradient Design** - Purple to blue gradient theme
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Interactive Cards** - Hover effects and animations
- **Data Visualization** - Bar charts and pie charts for analytics
- **Drag & Drop Upload** - Easy file upload interface
- **Real-time Search** - Instant filtering and search
- **Progress Indicators** - Visual feedback for operations
- **Status Badges** - Color-coded status indicators

## 🔒 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Login required decorators
- SQL injection prevention
- File type validation
- CSRF protection (Flask)
- Environment variable configuration

## 🐛 Troubleshooting

### Email Not Sending

1. Verify Gmail App Password is correct
2. Check 2-factor authentication is enabled
3. Ensure email settings are saved in Settings page
4. Check error messages in Email Logs

### File Upload Fails

1. Verify file format is CSV or Excel (.xlsx, .xls)
2. Check all required columns are present
3. Ensure column names match exactly (case-insensitive)
4. File size must be under 16MB

### Database Errors

1. Delete `student_results.db` file
2. Restart the application (database will be recreated)

### Port Already in Use

```bash
# Change port in app.py
app.run(debug=True, port=5001)  # Use different port
```

## 📝 Best Practices

1. **Regular Backups** - Export logs and backup database regularly
2. **Email Limits** - Gmail has daily sending limits (~500 emails/day)
3. **Test First** - Send test emails to yourself before bulk sending
4. **Data Validation** - Always preview data before sending
5. **Secure Credentials** - Never commit `.env` file to version control

## 🔄 Future Enhancements

- [ ] Multiple email providers (Outlook, SendGrid, etc.)
- [ ] Email scheduling (send at specific time)
- [ ] Custom email templates
- [ ] Multiple term support
- [ ] PDF report generation
- [ ] Student portal (view own results)
- [ ] Email attachments (certificates, etc.)
- [ ] Multi-language support
- [ ] Dark mode toggle
- [ ] Advanced analytics and reports

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section
2. Review the Usage Guide
3. Contact your system administrator

## 🙏 Acknowledgments

- Flask framework team
- Tailwind CSS team
- Font Awesome for icons
- Chart.js for visualizations
- All open-source contributors

---

**Made with ❤️ for Education**

Version 1.0.0 | 2024
