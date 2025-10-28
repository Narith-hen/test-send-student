# ⚡ Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Login
- Open: `http://localhost:5000`
- Username: `admin`
- Password: `admin123`

### Step 2: Configure Email
1. Click **Settings** in sidebar
2. Enter your Gmail address
3. Enter your App Password ([Get it here](https://myaccount.google.com/apppasswords))
4. Click **Save Configuration**

### Step 3: Upload & Send
1. Click **Upload Results**
2. Upload your CSV file (use `sample_students.csv` for testing)
3. Click **Students**
4. Select students
5. Click **Send Results**

## 📧 Gmail App Password Setup

1. Enable 2-Factor Authentication: [Google Security](https://myaccount.google.com/security)
2. Get App Password: [App Passwords](https://myaccount.google.com/apppasswords)
3. Select "Mail" → Generate
4. Copy the 16-character password

## 📊 CSV File Format

```csv
name,email,english,professional_life,algorithm,web_design,term1_total,year
John Doe,john@example.com,85,90,78,92,345,2024
```

**Required Columns:**
- `name` - Student name
- `email` - Student email
- `english` - English score (0-100)
- `professional_life` - Professional Life score (0-100)
- `algorithm` - Algorithm score (0-100)
- `web_design` - Web Design score (0-100)
- `term1_total` - Total score
- `year` - Academic year

## 🎯 Features at a Glance

| Feature | Location | What it does |
|---------|----------|--------------|
| **Dashboard** | `/dashboard` | View statistics and charts |
| **Upload** | `/upload` | Import student data from CSV/Excel |
| **Students** | `/students` | View, search, and send results |
| **Logs** | `/logs` | Track email delivery status |
| **Settings** | `/settings` | Configure email credentials |

## 🔧 Common Commands

**Start Server:**
```bash
python app.py
```

**Stop Server:**
Press `CTRL+C` in terminal

**Install Dependencies:**
```bash
python -m pip install -r requirements.txt
```

**Export Logs:**
Click "Export Logs" button on Logs page

## 💡 Pro Tips

✅ **Test First** - Send to your own email before bulk sending
✅ **Check Spam** - First emails may go to spam folder
✅ **Gmail Limits** - Max ~500 emails/day on free accounts
✅ **Preview Data** - Review students page before sending
✅ **Save Logs** - Export logs for record keeping

## 🐛 Troubleshooting

**Email Not Sending?**
- Verify App Password in Settings
- Check 2-Factor Auth is enabled
- Review Email Logs for errors

**Can't Upload File?**
- Check file format (CSV or Excel only)
- Verify all required columns present
- Ensure column names match exactly

**Port Already Used?**
- Change port in `app.py` to 5001
- Access at `http://localhost:5001`

## 📱 Access URLs

- **Local:** http://localhost:5000
- **Login:** http://localhost:5000/login
- **Dashboard:** http://localhost:5000/dashboard
- **Upload:** http://localhost:5000/upload
- **Students:** http://localhost:5000/students
- **Logs:** http://localhost:5000/logs
- **Settings:** http://localhost:5000/settings

## 🔒 Security Reminders

- ⚠️ Change default password after first login
- ⚠️ Never share your App Password
- ⚠️ Don't commit `.env` file
- ⚠️ Use environment variables in production

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Review `SETUP_GUIDE.md` for installation steps
3. See error messages in browser console
4. Check terminal for Python errors

---

**System Status:** ✅ Running on http://localhost:5000

**Default Login:** admin / admin123

**Version:** 1.0.0
