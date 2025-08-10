from flask import Flask, render_template, request
from twilio.rest import Client
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Config
STUDENT_DATA_CSV = 'student_data.csv'
ATTENDANCE_LOG_CSV = 'logs/attendance_log.csv'

# Twilio client
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
client = Client(account_sid, auth_token)

def send_sms(to_number, message):
    """Send SMS via Twilio"""
    try:
        msg = client.messages.create(
            body=message,
            from_=twilio_number,
            to=to_number
        )
        return True, f"Message SID: {msg.sid}"
    except Exception as e:
        return False, str(e)

def log_attendance(student_id, student_name):
    """Log attendance with timestamp"""
    os.makedirs("logs", exist_ok=True)
    log_df = pd.DataFrame(
        [[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), student_id, student_name]],
        columns=["Timestamp", "Student_ID", "Name"]
    )
    if not os.path.exists(ATTENDANCE_LOG_CSV):
        log_df.to_csv(ATTENDANCE_LOG_CSV, index=False)
    else:
        log_df.to_csv(ATTENDANCE_LOG_CSV, mode='a', header=False, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mark', methods=['POST'])
def mark_attendance():
    student_id = request.form.get('student_id', '').strip()

    if not student_id:
        return render_template('index.html', message="❌ Please enter a Student ID.")

    try:
        # Read tab-separated CSV
        students_df = pd.read_csv(STUDENT_DATA_CSV, dtype=str, sep="\t")
        # Normalize column names
        students_df.columns = students_df.columns.str.strip().str.lower().str.replace('\ufeff', '', regex=True)
    except FileNotFoundError:
        return render_template('index.html', message="❌ student_data.csv not found.")
    except Exception as e:
        return render_template('index.html', message=f"❌ Error reading CSV: {e}")

    if 'id' not in students_df.columns:
        return render_template('index.html', message="❌ CSV file missing 'ID' column.")

    student_row = students_df[students_df['id'] == student_id]

    if student_row.empty:
        return render_template('index.html', message=f"❌ Student with ID {student_id} not found.")

    student_name = student_row.iloc[0]['name']
    phone_number = str(student_row.iloc[0]['father_phone']).strip()

    if phone_number == "-" or phone_number == "" or len(phone_number) < 10:
        return render_template('index.html', message=f"❌ No valid phone number for {student_name}.")

    if len(phone_number) == 10:
        phone_number = "+91" + phone_number
    elif not phone_number.startswith("+"):
        return render_template('index.html', message="❌ Invalid phone number format.")

    sms_text = f"Dear Parent, your child {student_name} is present today."

    success, info = send_sms(phone_number, sms_text)

    if success:
        log_attendance(student_id, student_name)
        return render_template('index.html', message=f"✅ SMS sent to {student_name}'s parent.")
    else:
        return render_template('index.html', message=f"❌ Failed to send SMS: {info}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
