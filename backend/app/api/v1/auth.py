import secrets
import shutil
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_google_oauth_state,
    decode_token,
    get_current_user,
    hash_password,
    oauth2_scheme,
    validate_google_oauth_state,
    verify_password,
)
from app.models.organization import Organization
from app.models.otp import OTPChannel, OTPPurpose
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse
from app.schemas.otp import OTPResponse, SendOTPRequest, VerifyOTPRequest
from app.services.otp_service import OTPService

router = APIRouter(tags=["Authentication"])

GOOGLE_STATE_COOKIE = "google_oauth_state"
GOOGLE_STATE_TTL_SECONDS = 600
GOOGLE_STATE_COOKIE_PATH = "/"


def google_state_cookie_options():
    secure = settings.GOOGLE_REDIRECT_URI.startswith("https://")
    return {
        "key": GOOGLE_STATE_COOKIE,
        "path": GOOGLE_STATE_COOKIE_PATH,
        "secure": secure,
        "httponly": True,
        "samesite": "none" if secure else "lax",
    }


@router.get("/google")
async def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google login is not configured",
        )

    redirect_to = request.query_params.get("redirect_to") or settings.FRONTEND_URL
    safe_redirect_to = redirect_to.rstrip("/")
    if not safe_redirect_to.startswith(("http://", "https://")):
        safe_redirect_to = settings.FRONTEND_URL

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


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    cookie_state = request.cookies.get(GOOGLE_STATE_COOKIE)
    print(f"DEBUG GOOGLE: has_state={bool(state)} has_cookie={bool(cookie_state)}")

    if not state or not validate_google_oauth_state(state, cookie_state):
        response = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Google login state is missing, expired, or invalid. Restart sign-in."
            },
        )
        response.delete_cookie(**google_state_cookie_options())
        return response

    payload = decode_token(state)
    frontend_redirect = payload.get("redirect_to") if payload else settings.FRONTEND_URL
    if not frontend_redirect or not str(frontend_redirect).startswith(("http://", "https://")):
        frontend_redirect = settings.FRONTEND_URL
    frontend_redirect = frontend_redirect.rstrip("/")

    if error:
        message = error_description or error
        response = RedirectResponse(
            f"{frontend_redirect}/login?{urlencode({'error_description': message})}"
        )
        response.delete_cookie(**google_state_cookie_options())
        return response

    if not code:
        response = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Google authorization response was incomplete"},
        )
        response.delete_cookie(**google_state_cookie_options())
        return response

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
            print(f"\n❌ GOOGLE TOKEN ERROR ({token_response.status_code}): {token_response.text}\n")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google authorization failed: {token_response.json().get('error_description', token_response.text)}",
            )

        google_token = token_response.json().get("access_token")

        profile_response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {google_token}"},
        )
        if profile_response.is_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not read Google profile",
            )

    profile = profile_response.json()
    email = profile.get("email")
    if not email or not profile.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google email is not verified",
        )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        organization = Organization(name=f"{profile.get('name', 'Google')} Workspace")
        db.add(organization)
        await db.flush()

        user = User(
            email=email,
            full_name=profile.get("name") or email.split("@")[0],
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            organization_id=organization.id,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    token_data = {"sub": str(user.id), "org": user.organization_id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    redirect_params = urlencode({
        "access_token": access_token,
        "refresh_token": refresh_token,
    })
    response = RedirectResponse(f"{frontend_redirect}/login?{redirect_params}")
    response.delete_cookie(**google_state_cookie_options())
    return response


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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
        role=UserRole.ADMIN if is_demo_admin else UserRole.OWNER,
        trial_started_at=now,
        trial_ends_at=now + timedelta(days=14),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


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

    if user.trial_ends_at and user.trial_ends_at <= datetime.now(timezone.utc):
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
    print(f"\n🔐 OTP Generated → {otp.code} | Channel: {payload.channel.value} | To: {payload.email or payload.phone}\n")
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