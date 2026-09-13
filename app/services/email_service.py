from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)


class EmailService:
    
    @staticmethod
    async def send_email(to: str, subject: str, html: str) -> bool:
        try:
            message = MessageSchema(
                subject=subject,
                recipients=[to],
                body=html,
                subtype=MessageType.html,
            )
            await fm.send_message(message)
            logger.info(f"Email sent successfully to {to}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            return False

    @staticmethod
    async def send_otp_email(to: str, otp_code: str, purpose: str = "registration") -> bool:
        subject = "Your Mteja AI Verification Code"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>OTP Verification</title></head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center;">Mteja AI</h2>
                <p style="font-size: 16px; color: #555;">
                    Habari,<br><br>
                    Namba yako ya uthibitisho (OTP) ni:
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563eb; background: #eff6ff; padding: 15px 25px; border-radius: 8px;">
                        {otp_code}
                    </span>
                </div>
                <p style="font-size: 14px; color: #777;">
                    OTP hii itaisha baada ya <strong>10 minutes</strong>.<br>
                    Usishiriki namba hii na mtu yeyote.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 25px 0;">
                <p style="font-size: 12px; color: #999; text-align: center;">
                    © 2026 Mteja AI. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """

        return await EmailService.send_email(to=to, subject=subject, html=html)