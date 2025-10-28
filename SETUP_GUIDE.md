# 🚀 Quick Setup Guide

This guide will help you get the Student Result System running in just a few minutes.

## ⚡ Quick Start (5 Minutes)

### Step 1: Install Python Dependencies

Open your terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

This will install all required packages:
- Flask (web framework)
- Flask-Mail (email service)
- Pandas (data processing)
- openpyxl (Excel support)

### Step 2: Set Up Gmail App Password

**Why do you need this?**
Gmail requires an App Password (not your regular password) for third-party applications.

**How to get it:**

1. **Enable 2-Factor Authentication**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Turn on "2-Step Verification"
   - Follow the setup wizard

2. **Generate App Password**
   - Visit [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" from the dropdown
   - Select "Other (Custom name)" and enter "Student Result System"
   - Click "Generate"
   - **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)

3. **Save Your Credentials**
   - Create a copy of `.env.example` named `.env`
   - Edit `.env` and add:
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=abcd efgh ijkl mnop
   SECRET_KEY=change-this-to-random-string
   ```

### Step 3: Run the Application

```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debugger is active!
```

### Step 4: Login

1. Open your browser and go to: `http://localhost:5000`
2. Login with default credentials:
   - **Username:** `admin`
   - **Password:** `admin123`

### Step 5: Configure Email in Settings

1. Click "Settings" in the sidebar
2. Enter your Gmail address
3. Paste your App Password (the 16-character one)
4. Click "Save Configuration"

## 📊 Test with Sample Data

### Create a Sample CSV File

Create a file named `sample_students.csv` with this content:

```csv
name,email,english,professional_life,algorithm,web_design,term1_total,year
Alice Johnson,alice@example.com,92,88,95,90,365,2024
Bob Smith,bob@example.com,78,82,75,80,315,2024
Charlie Brown,charlie@example.com,85,90,88,92,355,2024
Diana Prince,diana@example.com,95,93,90,94,372,2024
```

**Note:** Replace `@example.com` with real email addresses for testing (preferably your own email to verify it works).

### Upload and Test

1. Go to "Upload Results" page
2. Drag and drop your `sample_students.csv` file
3. Click "Upload Results"
4. Go to "Students" page
5. Select one student (use your email for testing)
6. Click "Send Results"
7. Check your email inbox!

## 🎯 Common Issues & Solutions

### Issue 1: "Authentication Failed" Email Error

**Solution:**
- Make sure you're using an App Password, not your regular Gmail password
- Verify 2-factor authentication is enabled
- Check that the email and password are correctly saved in Settings

### Issue 2: Port 5000 Already in Use

**Solution:**
Change the port in `app.py`:
```python
app.run(debug=True, port=5001)  # Use port 5001 instead
```

Then access at: `http://localhost:5001`

### Issue 3: "Module not found" Error

**Solution:**
Make sure you installed all requirements:
```bash
pip install -r requirements.txt
```

If still failing, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue 4: CSV Upload Fails

**Solution:**
- Verify all required columns are present (name, email, english, professional_life, algorithm, web_design, term1_total, year)
- Column names must match exactly (case doesn't matter)
- Email addresses must be valid
- Scores should be numbers (0-100)

## 🔐 Security Checklist

- ✅ Never share your App Password
- ✅ Don't commit `.env` file to version control
- ✅ Change the default admin password
- ✅ Use strong SECRET_KEY in production
- ✅ Keep your Python packages updated

## 📱 Access from Other Devices

To access the system from other devices on your network:

1. Find your computer's IP address:
   - **Windows:** `ipconfig` (look for IPv4 Address)
   - **Mac/Linux:** `ifconfig` (look for inet)

2. Change `app.py` last line to:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5000)
   ```

3. Access from other devices at: `http://YOUR-IP-ADDRESS:5000`

## 🎓 Next Steps

1. **Explore the Dashboard** - View statistics and charts
2. **Upload Real Data** - Import your actual student results
3. **Customize Email Template** - Edit the HTML email in `app.py`
4. **Review Logs** - Check email delivery status
5. **Export Reports** - Download logs as CSV

## 💡 Pro Tips

- **Test with Your Email First** - Always send a test email to yourself before bulk sending
- **Check Spam Folder** - Initial emails might go to spam
- **Gmail Limits** - Free Gmail accounts can send ~500 emails per day
- **Backup Data** - Export logs regularly for record keeping
- **Preview Before Send** - Review student data on the Students page before sending

## 🆘 Need Help?

If you encounter any issues:

1. Check the error message in the browser
2. Look at the terminal/console for Python errors
3. Review the Email Logs page for delivery issues
4. Verify your email configuration in Settings
5. Try the sample data to isolate the problem

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

**You're all set! 🎉**

The system is now ready to send student results professionally and efficiently.
