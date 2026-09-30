import secrets
import shutil
import logging
import hashlib
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.rate_limit import _increment
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_google_oauth_state,
    decode_token,
    get_current_user,
    google_oauth_state_failure,
    hash_password,
    oauth2_scheme,
    verify_password,
)
from app.models.organization import Organization
from app.models.otp import OTPChannel, OTPPurpose
from app.models.user import User, UserRole
from app.schemas.auth import (
    EmailCodeRequest,
    EmailRequest,
    MessageResponse,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.otp import OTPResponse, SendOTPRequest, VerifyOTPRequest
from app.services.otp_service import OTPService

router = APIRouter(tags=["Authentication"])
logger = logging.getLogger(__name__)

GOOGLE_STATE_COOKIE = "google_oauth_state"
GOOGLE_STATE_TTL_SECONDS = 600
GOOGLE_STATE_COOKIE_PATH = "/"

# Only these frontends may receive login tokens after Google sign-in.
DEFAULT_FRONTEND_URL = "https://mtejaai.signiai.co.tz"
DEFAULT_ALLOWED_REDIRECTS = {
    DEFAULT_FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}


def trial_has_expired(trial_ends_at: datetime | None) -> bool:
    if trial_ends_at is None:
        return False
    if trial_ends_at.tzinfo is None:
        trial_ends_at = trial_ends_at.replace(tzinfo=timezone.utc)
    return trial_ends_at <= datetime.now(timezone.utc)


def get_frontend_url() -> str:
    """Main frontend URL (never the Render backend URL)."""
    url = (getattr(settings, "FRONTEND_URL", "") or DEFAULT_FRONTEND_URL).rstrip("/")
    return url


def is_allowed_redirect(url: str) -> bool:
    url = (url or "").rstrip("/")
    configured = {
        origin.strip().rstrip("/")
        for origin in (getattr(settings, "ALLOWED_REDIRECTS", "") or "").split(",")
        if origin.strip()
    }
    configured.add(get_frontend_url())
    return url in DEFAULT_ALLOWED_REDIRECTS or url in configured


def pick_safe_redirect(url: str | None) -> str:
    """Return url if it is an allowed frontend, otherwise the default frontend."""
    candidate = (url or "").rstrip("/")
    if candidate.startswith(("http://", "https://")) and is_allowed_redirect(candidate):
        return candidate
    return get_frontend_url()


def google_state_cookie_options():
    secure = settings.GOOGLE_REDIRECT_URI.startswith("https://")
    return {
        "key": GOOGLE_STATE_COOKIE,
        "path": GOOGLE_STATE_COOKIE_PATH,
        "secure": secure,
        "httponly": True,
        "samesite": "none" if secure else "lax",
    }


def google_failure_redirect(frontend_url: str, message: str, reason: str) -> RedirectResponse:
    logger.warning("Google OAuth failed: reason=%s", reason)
    response = RedirectResponse(
           f"{frontend_url}/login?{urlencode({'error_description': message})}"
    )
    response.delete_cookie(**google_state_cookie_options())
    return response


@router.get("/google")
async def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google login is not configured",
        )

    safe_redirect_to = pick_safe_redirect(request.query_params.get("redirect_to"))

    state = create_google_oauth_state(safe_redirect_to)
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    response = RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    )
    response.set_cookie(
        value=state,
        max_age=GOOGLE_STATE_TTL_SECONDS,
        **google_state_cookie_options(),
    )
    return response


async def _google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    cookie_state = request.cookies.get(GOOGLE_STATE_COOKIE)
    state_matches_cookie = bool(state and cookie_state and secrets.compare_digest(state, cookie_state))
    state_failure = google_oauth_state_failure(state, cookie_state)
    logger.info(
        "Google OAuth callback host=%s has_state=%s has_cookie=%s state==cookie=%s",
        request.url.hostname,
        bool(state),
        bool(cookie_state),
        state_matches_cookie,
    )

    if state_failure:
        frontend_redirect = get_frontend_url()
        logger.warning("Google OAuth state validation failed: reason=%s", state_failure)
        return google_failure_redirect(
            frontend_redirect,
            "Google sign-in could not be verified. Please restart sign-in.",
            state_failure,
        )

    payload = decode_token(state)
    frontend_redirect = pick_safe_redirect(payload.get("redirect_to") if payload else None)

    if error:
        message = error_description or error
        return google_failure_redirect(frontend_redirect, message, "provider_error")

    if not code:
        return google_failure_redirect(
            frontend_redirect,
            "Google authorization response was incomplete. Please try again.",
            "missing_code",
        )

    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            if token_response.is_error:
                logger.error("Google token exchange failed: status=%s", token_response.status_code)
                return google_failure_redirect(
                    frontend_redirect,
                    "Google authorization failed. Please try again.",
                    "token_exchange_failed",
                )

            google_token = token_response.json().get("access_token")
            if not google_token:
                return google_failure_redirect(
                    frontend_redirect,
                    "Google authorization did not return an access token.",
                    "missing_google_access_token",
                )

            profile_response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {google_token}"},
            )
            if profile_response.is_error:
                logger.error("Google profile request failed: status=%s", profile_response.status_code)
                return google_failure_redirect(
                    frontend_redirect,
                    "Could not read your Google profile.",
                    "profile_request_failed",
                )
            profile = profile_response.json()
    except httpx.RequestError:
        logger.exception("Google OAuth request failed while contacting Google")
        return google_failure_redirect(
            frontend_redirect,
            "Google sign-in is temporarily unavailable. Please try again.",
            "google_network_error",
        )

    email = profile.get("email")
    if not email or not profile.get("email_verified"):
        return google_failure_redirect(
            frontend_redirect,
            "Your Google email is not verified.",
            "email_not_verified",
        )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        organization = Organization(name=f"{profile.get('name', 'Google')} Workspace")
        db.add(organization)
        await db.flush()

        now = datetime.now(timezone.utc)
        user = User(
            email=email,
            full_name=profile.get("name") or email.split("@")[0],
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            organization_id=organization.id,
            is_superuser=False,
            is_verified=True,
            email_verified=True,
            role=UserRole.OWNER,
            trial_started_at=now,
            trial_ends_at=now + timedelta(days=14),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.email_verified:
        user.email_verified = True
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        return google_failure_redirect(
            frontend_redirect,
            "This account is inactive.",
            "inactive_user",
        )

    if trial_has_expired(user.trial_ends_at):
        return google_failure_redirect(
            frontend_redirect,
            "Your 14-day free trial has ended.",
            "trial_expired",
        )

    token_data = {"sub": str(user.id), "org": user.organization_id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    redirect_params = urlencode({
        "access_token": access_token,
        "refresh_token": refresh_token,
    })
    logger.info("Google OAuth succeeded: host=%s", request.url.hostname)
    # Tokens go in the URL fragment (#) so they are not sent to any server or logged.
    response = RedirectResponse(f"{frontend_redirect}/login#{redirect_params}")
    response.delete_cookie(**google_state_cookie_options())
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await _google_callback(
            request=request,
            code=code,
            state=state,
            error=error,
            error_description=error_description,
            db=db,
        )
    except Exception:
        logger.exception("Google OAuth callback processing failed")
        payload = decode_token(state) if state else None
        frontend_redirect = pick_safe_redirect(
            payload.get("redirect_to") if payload else None
        )
        return google_failure_redirect(
            frontend_redirect,
            "Google sign-in could not be completed. Please try again.",
            "callback_processing_error",
        )


async def enforce_email_otp_rate_limit(request: Request, email: str, scope: str) -> None:
    if not settings.RATE_LIMIT_ENABLED:
        return
    email_key = hashlib.sha256(email.strip().lower().encode()).hexdigest()
    ip = request.client.host if request.client else "unknown"
    email_count, _ = await _increment(f"rl:{scope}:email:{email_key}", 900)
    ip_count, reset = await _increment(f"rl:{scope}:ip:{ip}", 900)
    if email_count > 3 or ip_count > 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many code requests. Please wait 15 minutes before trying again.",
            headers={"Retry-After": str(reset)},
        )


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    organization = Organization(name=data.organization_name)
    db.add(organization)
    await db.flush()

    now = datetime.now(timezone.utc)
    normalized_email = data.email.lower()
    is_demo_admin = normalized_email == settings.DEMO_ADMIN_EMAIL.lower()
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        organization_id=organization.id,
        is_superuser=False,
        is_verified=not is_demo_admin,
        email_verified=False,
        role=UserRole.ADMIN if is_demo_admin else UserRole.OWNER,
        trial_started_at=now,
        trial_ends_at=now + timedelta(days=14),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await OTPService.create_otp(
        db=db,
        email=user.email,
        channel=OTPChannel.EMAIL,
        purpose=OTPPurpose.EMAIL_VERIFICATION,
        user_id=user.id,
    )
    return MessageResponse(message="Account created. Check your email for a verification code.")


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email(data: EmailCodeRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or user.email_verified:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    await OTPService.verify_otp(
        db=db,
        code=data.code,
        email=user.email,
        purpose=OTPPurpose.EMAIL_VERIFICATION,
    )
    user.email_verified = True
    await db.commit()
    await db.refresh(user)

    token_data = {"sub": str(user.id), "org": user.organization_id}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    data: EmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await enforce_email_otp_rate_limit(request, str(data.email), "resend_verification")
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if user and not user.email_verified and user.is_active:
        try:
            await OTPService.create_otp(
                db=db,
                email=user.email,
                channel=OTPChannel.EMAIL,
                purpose=OTPPurpose.EMAIL_VERIFICATION,
                user_id=user.id,
            )
        except Exception:
            logger.warning("Verification email delivery failed")
    return MessageResponse(message="If the account needs verification, a new code has been sent.")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: EmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await enforce_email_otp_rate_limit(request, str(data.email), "forgot_password")
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if user and user.is_active:
        try:
            await OTPService.create_otp(
                db=db,
                email=user.email,
                channel=OTPChannel.EMAIL,
                purpose=OTPPurpose.PASSWORD_RESET,
                user_id=user.id,
            )
        except Exception:
            logger.warning("Password reset email delivery failed")
    return MessageResponse(message="If an account exists for this email, we sent a code.")


@router.post("/resend-password-reset", response_model=MessageResponse)
async def resend_password_reset(
    data: EmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await enforce_email_otp_rate_limit(request, str(data.email), "forgot_password")
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if user and user.is_active:
        try:
            await OTPService.create_otp(
                db=db,
                email=user.email,
                channel=OTPChannel.EMAIL,
                purpose=OTPPurpose.PASSWORD_RESET,
                user_id=user.id,
            )
        except Exception:
            logger.warning("Password reset email delivery failed")
    return MessageResponse(message="If an account exists for this email, we sent a code.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    await OTPService.verify_otp(
        db=db,
        code=data.code,
        email=str(data.email),
        purpose=OTPPurpose.PASSWORD_RESET,
    )
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Invalid or expired password reset code")
    user.hashed_password = hash_password(data.new_password)
    await db.commit()
    return MessageResponse(message="Password updated. Please log in.")


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This admin account must be verified by a super admin before login.",
        )

    if not user.email_verified:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Email not verified", "code": "EMAIL_NOT_VERIFIED"},
        )

    if trial_has_expired(user.trial_ends_at):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your 14-day free trial has ended.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    token_data = {"sub": str(user.id), "org": user.organization_id}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    org_id = payload.get("org")
    return TokenResponse(
        access_token=create_access_token({"sub": user_id, "org": org_id}),
        refresh_token=create_refresh_token({"sub": user_id, "org": org_id}),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/profile/avatar", response_model=UserResponse)
async def upload_profile_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    static_dir = Path(__file__).resolve().parents[3] / "static" / "profile-avatars"
    static_dir.mkdir(parents=True, exist_ok=True)
    extension = Path(file.filename or "avatar").suffix.lower() or ".jpg"
    filename = f"user-{current_user.id}-{uuid4().hex}{extension}"
    destination = static_dir / filename
    with destination.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    current_user.avatar_url = f"/static/profile-avatars/{filename}"
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(payload: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    if payload.channel == OTPChannel.EMAIL and not payload.email:
        raise HTTPException(status_code=400, detail="Email is required when channel is email")
    if payload.channel == OTPChannel.SMS and not payload.phone:
        raise HTTPException(status_code=400, detail="Phone number is required when channel is sms")

    otp = await OTPService.create_otp(
        db=db,
        email=payload.email,
        phone=payload.phone,
        channel=payload.channel,
        purpose=payload.purpose,
    )
    if settings.ENVIRONMENT.lower() == "local":
        logger.info("Local OTP generated: channel=%s purpose=%s code=%s", payload.channel.value, payload.purpose.value, otp.code)
    return OTPResponse(
        message=f"OTP sent successfully via {payload.channel.value}",
        expires_in=600,
    )


@router.post("/verify-otp")
async def verify_otp(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    otp = await OTPService.verify_otp(
        db=db,
        code=payload.code,
        email=payload.email,
        phone=payload.phone,
        purpose=payload.purpose,
    )
    return {
        "message": "OTP verified successfully",
        "email": otp.email,
        "phone": otp.phone,
        "purpose": otp.purpose.value,
    }