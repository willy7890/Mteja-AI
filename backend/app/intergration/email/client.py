# email API client for MTEJA AI
# Official API calls, rate limiting, retries, and error handling
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings


class EmailClient:

  @staticmethod
  def send_email_reply(recipient: str, subject: str, reply_content: str) -> bool:
    user = getattr(settings, "GMAIL_USER", "")
    password = getattr(settings, "GMAIL_APP_PASSWORD", "")

    if not user or not password:
      print("Gmail credentials are not configured in settings/environment.")
      return False

    msg = MIMEMultipart()
    msg["From"] = user
    msg["To"] = recipient
    msg["Subject"] = f"Re: {subject}"

    msg.attach(MIMEText(reply_content, "plain"))

    try:
      # Connect to Gmail SMTP server
      server = smtplib.SMTP("smtp.gmail.com", 587)
      server.starttls()
      server.login(user, password)
      server.sendmail(user, recipient, msg.as_string())
      server.quit()
      return True
    except Exception as e:
      print(f"Failed to send email reply: {e}")
      return False