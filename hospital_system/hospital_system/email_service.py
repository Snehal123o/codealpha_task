"""Sends appointment emails over SMTP."""
import os, smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
HOSPITAL = os.getenv("HOSPITAL_NAME", "Smart Care Hospital")

def send_email(to, subject, body):
    user, pw = os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD")
    if not user or not pw:
        return False, "Email is not configured (add SMTP_USER and SMTP_PASSWORD to .env)."
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = f"{HOSPITAL} <{user}>", to, subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(os.getenv("SMTP_HOST", "smtp.gmail.com"),
                          int(os.getenv("SMTP_PORT", "587")), timeout=20) as s:
            s.starttls(); s.login(user, pw); s.send_message(msg)
        return True, "Email sent."
    except Exception as e:
        return False, f"Email failed: {e}"

def booking_email(a):
    return (f"Hello {a['patient_name']},\n\n"
            f"Your appointment is confirmed.\n\n"
            f"Appointment ID : #{a['id']}\n"
            f"Doctor         : Dr. {a['doctor_name']} ({a['specialization']})\n"
            f"Date           : {a['appt_date']}\n"
            f"Time           : {a['appt_time']}\n"
            f"Reason         : {a['reason'] or '-'}\n\n"
            f"Please arrive 10 minutes early. To cancel, log in to the portal.\n\n"
            f"Regards,\n{HOSPITAL}")

def cancel_email(a):
    return (f"Hello {a['patient_name']},\n\n"
            f"Your appointment #{a['id']} with Dr. {a['doctor_name']} on "
            f"{a['appt_date']} at {a['appt_time']} has been cancelled.\n\n"
            f"You can book a new slot anytime from the portal.\n\nRegards,\n{HOSPITAL}")
