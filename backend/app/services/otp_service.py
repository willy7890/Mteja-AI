from datetime import datetime, timedelta, timezone
import hmac
import logging
import secrets
import string

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.otp import OTPChannel, OTPCode, OTPPurpose
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

try:
    from app.services.sms_service import SMSService
except ImportError:
    SMSService = None


class OTPService:

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        return "".join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    async def create_otp(
        db: AsyncSession,
        email: str | None = None,
        phone: str | None = None,
        channel: OTPChannel = OTPChannel.EMAIL,
        purpose: OTPPurpose = OTPPurpose.REGISTRATION,
        user_id: int | None = None,
        expiry_minutes: int = 10,
    ) -> OTPCode:

        now_utc = datetime.now(timezone.utc)

        # Invalidate previous unused OTPs for the same entity and purpose
        query = select(OTPCode).where(
            and_(
                OTPCode.purpose == purpose,
                OTPCode.is_used == False,
                OTPCode.expires_at > now_utc,
            )
        )
        if email:
            query = query.where(OTPCode.email == email)
        if phone:
            query = query.where(OTPCode.phone == phone)

        result = await db.execute(query)
        old_otps = result.scalars().all()
        for old in old_otps:
            old.is_used = True

        code = OTPService.generate_otp()
        otp = OTPCode(
            user_id=user_id,
            email=email,
            phone=phone,
            code=code,
            channel=channel,
            purpose=purpose,
            expires_at=now_utc + timedelta(minutes=expiry_minutes),
        )
        db.add(otp)
        await db.commit()
        await db.refresh(otp)

        # Send via Email
        if channel == OTPChannel.EMAIL and email:
            if settings.ENVIRONMENT.lower() == "local":
                logger.info("Local OTP generated: email=%s purpose=%s code=%s", email, purpose.value, otp.code)
            success = await EmailService.send_otp_email(
                to=email, otp_code=otp.code, purpose=purpose.value
            )
            if not success:
                otp.is_used = True
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="OTP email could not be delivered. Please try again later.",
                )

        # Send via SMS
        elif channel == OTPChannel.SMS and phone:
            if settings.ENVIRONMENT.lower() == "local":
                logger.info("Local OTP generated: phone=%s purpose=%s code=%s", phone, purpose.value, otp.code)
            if SMSService and hasattr(SMSService, "send_otp_sms"):
                success = await SMSService.send_otp_sms(
                    to=phone, otp_code=otp.code, purpose=purpose.value
                )
                logger.info("OTP SMS delivery result: success=%s", bool(success))

        return otp

    @staticmethod
    async def verify_otp(
        db: AsyncSession,
        code: str,
        email: str | None = None,
        phone: str | None = None,
        purpose: OTPPurpose = OTPPurpose.REGISTRATION,
    ) -> OTPCode:
        query = select(OTPCode).where(
            and_(
                OTPCode.purpose == purpose,
                OTPCode.is_used == False,
            )
        )
        if email:
            query = query.where(OTPCode.email == email)
        if phone:
            query = query.where(OTPCode.phone == phone)

        query = query.order_by(OTPCode.created_at.desc(), OTPCode.id.desc()).limit(1)
        result = await db.execute(query)
        otp = result.scalar_one_or_none()

        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code",
            )

        if otp.is_expired():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired",
            )

        if otp.attempts >= otp.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum attempts exceeded",
            )

        otp.attempts += 1

        if not hmac.compare_digest(otp.code, code):
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code",
            )

        otp.is_used = True
        otp.used_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(otp)

        return otp