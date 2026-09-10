from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    oauth2_scheme,
)
from app.models.user import User
from app.models.organization import Organization
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse

from app.schemas.otp import SendOTPRequest, VerifyOTPRequest, OTPResponse
from app.services.otp_service import OTPService
from app.models.otp import OTPChannel, OTPPurpose


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

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
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    token_data = {"sub": str(user.id), "org": user.organization_id}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    org_id = payload.get("org")

    new_access = create_access_token({"sub": user_id, "org": org_id})
    new_refresh = create_refresh_token({"sub": user_id, "org": org_id})

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}

@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(
    payload: SendOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    if payload.channel == OTPChannel.EMAIL and not payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required when channel is email"
        )
    
    if payload.channel == OTPChannel.SMS and not payload.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required when channel is sms"
        )

    otp = await OTPService.create_otp(
        db=db,
        email=payload.email,
        phone=payload.phone,
        channel=payload.channel,
        purpose=payload.purpose,
    )
# temporarily printing for OTP
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