import logging
from typing import Optional
from app.core.config import settings

try:
    import africastalking
except ImportError:
    africastalking = None

logger = logging.getLogger(__name__)

# Initialize Africa's Talking only if the library exists and API Key is provided
sms = None
if africastalking is not None and getattr(settings, "AT_API_KEY", None):
    try:
        username = getattr(settings, "AT_USERNAME", "sandbox") or "sandbox"
        africastalking.initialize(username, settings.AT_API_KEY)
        sms = africastalking.SMS
        logger.info("Africa's Talking SMS client initialized successfully.")
    except Exception as e:
        logger.warning(f"Failed to initialize Africa's Talking SMS client: {e}")
else:
    logger.info("Africa's Talking SMS client skipped: Missing API key or library.")


class SMSService:

    @staticmethod
    def format_phone_number(to: str) -> str:
        """Formats Tanzanian local numbers (0XXXXXXXXX) into E.164 (+255XXXXXXXXX)."""
        clean_num = to.strip().replace(" ", "").replace("-", "")
        if clean_num.startswith("0"):
            return "+255" + clean_num[1:]
        elif not clean_num.startswith("+"):
            return "+" + clean_num
        return clean_num

    @staticmethod
    async def send_sms(to: str, message: str) -> bool:
        """Sends an outbound SMS message via Africa's Talking."""
        formatted_to = SMSService.format_phone_number(to)

        if sms is None:
            logger.warning(
                f"[SMS MOCK] Service uninitialized. Would have sent to {formatted_to}: '{message}'"
            )
            return True  # Returns True in dev mode so flow proceeds smoothly

        try:
            response = sms.send(message, [formatted_to])
            logger.info(f"SMS sent successfully to {formatted_to} | Response: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {formatted_to}: {str(e)}")
            return False

    @staticmethod
    async def send_otp_sms(to: str, otp_code: str, purpose: str = "registration") -> bool:
        """Sends an OTP confirmation SMS."""
        message = (
            f"Mteja AI: Namba yako ya uthibitisho (OTP) ni {otp_code}. "
            f"Itaisha baada ya dakika 10. Usishiriki na mtu yeyote."
        )
        return await SMSService.send_sms(to=to, message=message)