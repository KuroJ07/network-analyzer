import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SENDER = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER = os.getenv("EMAIL_RECEIVER")


def send_alert(ip: str, hostname: str, timestamp: str, is_new: bool) -> bool:
    """
    Send an email alert when a device is detected on the network.
    is_new: True if this device has never been seen before
    Returns True if sent successfully, False otherwise.
    """
    if not all([SENDER, PASSWORD, RECEIVER]):
        print("[alerts] Email credentials not configured — skipping alert")
        return False

    subject = (
        f"⚠ New Device on Network: {ip}"
        if is_new
        else f"↑ Known Device Rejoined: {ip}"
    )

    body = f"""
Network Analyzer Alert
======================

{"🚨 NEW DEVICE — never seen before" if is_new else "📶 Known device rejoined the network"}

IP Address : {ip}
Hostname   : {hostname}
First Seen : {timestamp}
Time       : {timestamp}

{"This device has not been seen on your network before. Verify you recognize it." if is_new else "This is a known device that left and rejoined the network."}

--
Network Analyzer | Home Network Monitor
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER
        msg["To"] = RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECEIVER, msg.as_string())

        return True

    except Exception as e:
        print(f"[alerts] Failed to send email: {e}")
        return False