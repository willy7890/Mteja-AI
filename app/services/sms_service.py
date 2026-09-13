import africastalking
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
sms = africastalking.SMS


class SMSService:

    @staticmethod
    async def send_sms(to: str, message: str) -> bool:
        try:
        
            if to.startswith("0"):
                to = "+255" + to[1:]
            elif not to.startswith("+"):
                to = "+" + to

            response = sms.send(message, [to])
            logger.info(f"SMS sent successfully to {to} | Response: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {to}: {str(e)}")
            return False

    @staticmethod
    async def send_otp_sms(to: str, otp_code: str, purpose: str = "registration") -> bool:
        message = f"Mteja AI: Namba yako ya uthibitisho (OTP) ni {otp_code}. Itaisha baada ya dakika 10. Usishiriki na mtu yeyote."
        return await SMSService.send_sms(to=to, message=message)