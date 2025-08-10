# Attendance SMS System (Flask + Twilio)

This app allows a teacher to mark attendance by entering a student ID, automatically sending an SMS to the parent using Twilio, and logging the attendance.

## Features
- Lookup student details from `student_data.csv`
- Send SMS via Twilio API
- Log attendance in `logs/attendance_log.csv`
- Simple web interface for marking attendance

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
