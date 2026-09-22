import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    oauth2_scheme,
    verify_password,
)
from app.models.organization import Organization
from app.models.otp import OTPChannel, OTPPurpose
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse
from app.schemas.otp import OTPResponse, SendOTPRequest, VerifyOTPRequest
from app.services.otp_service import OTPService

router = APIRouter(tags=["Authentication"])


# ==========================================
# GOOGLE OAUTH ENDPOINTS
# ==========================================

@router.get("/google")
async def google_login():
    """Inaanzisha mchakato wa ku-login na Google na ku-redirect mtumiaji."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google login is not configured",
        )

    state = create_access_token({"sub": "google-oauth", "state": secrets.token_urlsafe(24)})
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    )


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """Inapokea callback kutoka Google na kutengeneza au ku-authenticate mtumiaji."""
    state_payload = decode_token(state)
    if not state_payload or state_payload.get("sub") != "google-oauth":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid Google login state"
        )

    async with httpx.AsyncClient() as client:
        # 1. Exchange Auth Code for Access Token
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
            # Print maelezo kamili ya error kwenye terminal kwa ajili ya debugging
            print(f"\n❌ GOOGLE TOKEN ERROR ({token_response.status_code}): {token_response.text}\n")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google authorization failed: {token_response.json().get('error_description', token_response.text)}"
            )

        google_token = token_response.json().get("access_token")

        # 2. Get User Profile from Google
        profile_response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {google_token}"},
        )
        if profile_response.is_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Could not read Google profile"
            )

    profile = profile_response.json()
    email = profile.get("email")
    if not email or not profile.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Google email is not verified"
        )

    # 3. Find or Create User
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
            detail="Inactive user"
        )

    # 4. Generate Application Tokens
    token_data = {"sub": str(user.id), "org": user.organization_id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    redirect_params = urlencode({
        "access_token": access_token,
        "refresh_token": refresh_token,
    })
    return RedirectResponse(f"{settings.FRONTEND_URL}/login?{redirect_params}")


# ==========================================
# STANDARD AUTH ENDPOINTS
# ==========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Inasajili mtumiaji mpya pamoja na Organization yake."""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )

    organization = Organization(name=data.organization_name)
    db.add(organization)
    await db.flush()

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        organization_id=organization.id,
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
    """Ina-authenticate mtumiaji na kurudisha access & refresh tokens."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )

    token_data = {"sub": str(user.id), "org": user.organization_id}

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """Inatengeneza tokens mpya kwa kutumia refresh token halali."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    org_id = payload.get("org")

    return TokenResponse(
        access_token=create_access_token({"sub": user_id, "org": org_id}),
        refresh_token=create_refresh_token({"sub": user_id, "org": org_id}),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Inarudisha taarifa za mtumiaji aliyelog-in kwa sasa."""
    return current_user


@router.post("/logout")
async def logout():
    """Inamtoa mtumiaji kwenye mfumo."""
    return {"message": "Successfully logged out"}


# ==========================================
# OTP ENDPOINTS
# ==========================================

@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(
    payload: SendOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    """Inatengeneza na kutuma nambari ya OTP kwa Email au SMS."""
    if payload.channel == OTPChannel.EMAIL and not payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required when channel is email",
        )

    if payload.channel == OTPChannel.SMS and not payload.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required when channel is sms",
        )

    otp = await OTPService.create_otp(
        db=db,
        email=payload.email,
        phone=payload.phone,
        channel=payload.channel,
        purpose=payload.purpose,
    )

    # Logging ya muda kwenye terminal
    print(f"\n🔐 OTP Generated → {otp.code} | Channel: {payload.channel.value} | To: {payload.email or payload.phone}\n")

    return OTPResponse(
        message=f"OTP sent successfully via {payload.channel.value}",
        expires_in=600,
    )


@router.post("/verify-otp")
async def verify_otp(
    payload: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    """Inahakiki kama namba ya OTP iliyoingizwa ni sahihi na haijatoka muda wake."""
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