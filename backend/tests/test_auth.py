import pytest
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

from jose import jwt
from sqlalchemy import select

from app.core.config import settings
from app.models.otp import OTPCode, OTPPurpose
from app.models.user import User
from app.services.email_service import EmailService
from app.core.rate_limit import _memory_counters
from app.core.security import (
    create_google_oauth_state,
    google_oauth_state_failure,
    validate_google_oauth_state,
)


def test_google_oauth_state_validation_reasons():
    valid_state = create_google_oauth_state()
    assert google_oauth_state_failure(valid_state, valid_state) is None
    assert google_oauth_state_failure(valid_state, None) == "cookie_missing"
    assert google_oauth_state_failure(valid_state, "different-cookie") == "cookie_mismatch"

    expired_state = jwt.encode(
        {
            "sub": "google-oauth",
            "nonce": "expired-nonce",
            "type": "google_oauth_state",
            "exp": 0,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    assert google_oauth_state_failure(expired_state, expired_state) == "expired"

    parts = valid_state.split(".")
    signature = parts[2]
    parts[2] = ("A" if signature[0] != "A" else "B") + signature[1:]
    tampered_state = ".".join(parts)
    assert google_oauth_state_failure(tampered_state, tampered_state) == "bad_signature"

@pytest.mark.asyncio
async def test_register_user_success(client, db_session, monkeypatch):
    async def delivered(**kwargs):
        return True

    monkeypatch.setattr(EmailService, "send_otp_email", delivered)
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@mteja.ai",
            "full_name": "Test User",
            "password": "TestPassword123",
            "organization_name": "Test Org"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "verification code" in data["message"]
    user = (await db_session.execute(select(User).where(User.email == "test@mteja.ai"))).scalar_one()
    assert user.email_verified is False
    otp = (await db_session.execute(select(OTPCode).where(OTPCode.email == user.email))).scalar_one()
    assert otp.purpose == OTPPurpose.EMAIL_VERIFICATION

@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client, monkeypatch):
    async def delivered(**kwargs):
        return True

    monkeypatch.setattr(EmailService, "send_otp_email", delivered)
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@mteja.ai",
            "full_name": "Duplicate User",
            "password": "TestPassword123",
            "organization_name": "Test Org"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_success(client, db_session):
    user = (await db_session.execute(select(User).where(User.email == "test@mteja.ai"))).scalar_one_or_none()
    if user:
        user.email_verified = True
        await db_session.commit()
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@mteja.ai",
            "password": "TestPassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    login_otps = await db_session.execute(
        select(OTPCode).where(OTPCode.email == "test@mteja.ai", OTPCode.purpose == OTPPurpose.LOGIN)
    )
    assert login_otps.scalars().all() == []


@pytest.mark.asyncio
async def test_unverified_email_login_returns_machine_code(client, db_session):
    user = (await db_session.execute(select(User).where(User.email == "test@mteja.ai"))).scalar_one_or_none()
    assert user is not None
    user.email_verified = False
    await db_session.commit()
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@mteja.ai", "password": "TestPassword123"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "EMAIL_NOT_VERIFIED"

@pytest.mark.asyncio
async def test_login_invalid_password_fails(client):
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@mteja.ai",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_google_login_issues_signed_state_and_nonce_cookie(client, monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "google-client-secret")

    response = await client.get("/api/v1/auth/google", follow_redirects=False)

    assert response.status_code == 307
    state = parse_qs(urlsplit(response.headers["location"]).query)["state"][0]
    cookie_state = response.cookies.get("google_oauth_state")
    cookie_header = response.headers["set-cookie"].lower()
    assert cookie_state == state
    assert validate_google_oauth_state(state, cookie_state)
    assert "httponly" in cookie_header
    redirect_uri = parse_qs(urlsplit(response.headers["location"]).query)["redirect_uri"][0]
    assert redirect_uri == settings.GOOGLE_REDIRECT_URI
    if settings.GOOGLE_REDIRECT_URI.startswith("https://"):
        assert "secure" in cookie_header
        assert "samesite=none" in cookie_header
    else:
        assert "secure" not in cookie_header
        assert "samesite=lax" in cookie_header
    assert "max-age=600" in cookie_header


@pytest.mark.asyncio
async def test_google_login_uses_localhost_cookie_settings(client, monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "google-client-secret")
    monkeypatch.setattr(
        settings,
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/api/v1/auth/google/callback",
    )

    response = await client.get("/api/v1/auth/google", follow_redirects=False)

    cookie_header = response.headers["set-cookie"].lower()
    assert "samesite=lax" in cookie_header
    assert "secure" not in cookie_header


@pytest.mark.asyncio
async def test_google_login_falls_back_for_disallowed_redirect(client, monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "google-client-secret")

    response = await client.get(
        "/api/v1/auth/google",
        params={"redirect_to": "https://attacker.example"},
        follow_redirects=False,
    )

    assert response.status_code == 307
    state = parse_qs(urlsplit(response.headers["location"]).query)["state"][0]
    payload = jwt.decode(state, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["redirect_to"] == settings.FRONTEND_URL


@pytest.mark.asyncio
async def test_google_callback_falls_back_for_disallowed_frontend(client):
    state = create_google_oauth_state("https://mteja-ai.vercel.app")

    response = await client.get(
        "/api/v1/auth/google/callback",
        params={"state": state, "error": "access_denied"},
        headers={"Cookie": f"google_oauth_state={state}"},
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"].startswith(f"{settings.FRONTEND_URL}/login?")


@pytest.mark.asyncio
async def test_google_callback_rejects_state_without_matching_cookie(client, monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "google-client-secret")
    state = create_google_oauth_state()

    response = await client.get(
        "/api/v1/auth/google/callback",
        params={"code": "authorization-code", "state": state},
    )

    assert response.status_code == 307
    assert response.headers["location"].startswith(f"{settings.FRONTEND_URL}/login?")
    assert "error_description=" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_rejects_expired_state(client):
    expired_state = jwt.encode(
        {
            "sub": "google-oauth",
            "nonce": "expected-nonce",
            "type": "google_oauth_state",
            "exp": 0,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    response = await client.get(
        "/api/v1/auth/google/callback",
        params={"code": "authorization-code", "state": expired_state},
        headers={"Cookie": f"google_oauth_state={expired_state}"},
    )

    assert response.status_code == 307
    assert response.headers["location"].startswith(f"{settings.FRONTEND_URL}/login?")
    assert "error_description=" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_accepts_matching_state_and_clears_cookie(client):
    state = create_google_oauth_state()

    response = await client.get(
        "/api/v1/auth/google/callback",
        params={"state": state, "error": "access_denied"},
        headers={"Cookie": f"google_oauth_state={state}"},
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"].startswith(f"{settings.FRONTEND_URL}/login?")
    cleared_cookie = response.headers["set-cookie"].lower()
    assert 'google_oauth_state=""' in cleared_cookie
    assert "max-age=0" in cleared_cookie


@pytest.mark.asyncio
async def test_verify_email_consumes_code_and_returns_tokens(client, db_session, monkeypatch):
    async def delivered(**kwargs):
        return True

    monkeypatch.setattr(EmailService, "send_otp_email", delivered)
    email = "verify-new@mteja.ai"
    registered = await client.post("/api/v1/auth/register", json={
        "email": email, "full_name": "Verify User", "password": "TestPassword123",
        "organization_name": "Verify Org",
    })
    assert registered.status_code == 201
    otp = (await db_session.execute(select(OTPCode).where(OTPCode.email == email))).scalar_one()
    response = await client.post("/api/v1/auth/verify-email", json={"email": email, "code": otp.code})
    assert response.status_code == 200
    assert response.json()["access_token"]
    user = (await db_session.execute(select(User).where(User.email == email))).scalar_one()
    assert user.email_verified is True
    reused = await client.post("/api/v1/auth/verify-email", json={"email": email, "code": otp.code})
    assert reused.status_code == 400


@pytest.mark.asyncio
async def test_verify_email_wrong_code_counts_attempts(client, db_session, monkeypatch):
    async def delivered(**kwargs):
        return True

    monkeypatch.setattr(EmailService, "send_otp_email", delivered)
    email = "wrong-code@mteja.ai"
    await client.post("/api/v1/auth/register", json={
        "email": email, "full_name": "Wrong User", "password": "TestPassword123",
        "organization_name": "Wrong Org",
    })
    for _ in range(5):
        response = await client.post("/api/v1/auth/verify-email", json={"email": email, "code": "000000"})
        assert response.status_code == 400
    otp = (await db_session.execute(select(OTPCode).where(OTPCode.email == email))).scalar_one()
    assert otp.attempts == 5
    locked = await client.post("/api/v1/auth/verify-email", json={"email": email, "code": otp.code})
    assert locked.status_code == 400


@pytest.mark.asyncio
async def test_verify_email_expired_code_fails(client, db_session, monkeypatch):
    async def delivered(**kwargs):
        return True

    monkeypatch.setattr(EmailService, "send_otp_email", delivered)
    email = "expired-verification@mteja.ai"
    await client.post("/api/v1/auth/register", json={
        "email": email, "full_name": "Expired User", "password": "TestPassword123",
        "organization_name": "Expired Verification Org",
    })
    otp = (await db_session.execute(select(OTPCode).where(
        OTPCode.email == email, OTPCode.purpose == OTPPurpose.EMAIL_VERIFICATION
    ))).scalar_one()
    otp.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    await db_session.commit()
    response = await client.post("/api/v1/auth/verify-email", json={"email": email, "code": otp.code})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_forgot_password_is_generic_for_unknown_email(client):
    response = await client.post("/api/v1/auth/forgot-password", json={"email": "unknown@mteja.ai"})
    assert response.status_code == 200
    assert response.json()["message"] == "If an account exists for this email, we sent a code."


@pytest.mark.asyncio
async def test_reset_password_changes_password_and_consumes_code(client, db_session, monkeypatch):
    async def delivered(**kwargs):
        return True

    monkeypatch.setattr(EmailService, "send_otp_email", delivered)
    email = "reset-user@mteja.ai"
    await client.post("/api/v1/auth/register", json={
        "email": email, "full_name": "Reset User", "password": "TestPassword123",
        "organization_name": "Reset Org",
    })
    await client.post("/api/v1/auth/forgot-password", json={"email": email})
    otp = (await db_session.execute(select(OTPCode).where(
        OTPCode.email == email, OTPCode.purpose == OTPPurpose.PASSWORD_RESET
    ))).scalar_one()
    response = await client.post("/api/v1/auth/reset-password", json={
        "email": email, "code": otp.code, "new_password": "NewPassword123",
    })
    assert response.status_code == 200
    login = await client.post("/api/v1/auth/login", data={
        "username": email, "password": "NewPassword123",
    })
    assert login.status_code == 403  # Email verification remains independently required.
    reused = await client.post("/api/v1/auth/reset-password", json={
        "email": email, "code": otp.code, "new_password": "AnotherPassword123",
    })
    assert reused.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_expired_code_fails(client, db_session, monkeypatch):
    async def delivered(**kwargs):
        return True

    monkeypatch.setattr(EmailService, "send_otp_email", delivered)
    email = "expired-reset@mteja.ai"
    await client.post("/api/v1/auth/register", json={
        "email": email, "full_name": "Expired Reset", "password": "TestPassword123",
        "organization_name": "Expired Org",
    })
    await client.post("/api/v1/auth/forgot-password", json={"email": email})
    otp = (await db_session.execute(select(OTPCode).where(
        OTPCode.email == email, OTPCode.purpose == OTPPurpose.PASSWORD_RESET
    ))).scalar_one()
    otp.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    await db_session.commit()
    response = await client.post("/api/v1/auth/reset-password", json={
        "email": email, "code": otp.code, "new_password": "NewPassword123",
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_wrong_code_fails(client, db_session, monkeypatch):
    async def delivered(**kwargs):
        return True

    monkeypatch.setattr(EmailService, "send_otp_email", delivered)
    email = "wrong-reset@mteja.ai"
    await client.post("/api/v1/auth/register", json={
        "email": email, "full_name": "Wrong Reset", "password": "TestPassword123",
        "organization_name": "Wrong Reset Org",
    })
    await client.post("/api/v1/auth/forgot-password", json={"email": email})
    response = await client.post("/api/v1/auth/reset-password", json={
        "email": email, "code": "000000", "new_password": "NewPassword123",
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_forgot_password_rate_limit_applies_by_email_and_ip(client):
    _memory_counters.clear()
    email = "limited-reset@mteja.ai"
    responses = [
        await client.post("/api/v1/auth/forgot-password", json={"email": email})
        for _ in range(4)
    ]
    assert [response.status_code for response in responses] == [200, 200, 200, 429]


@pytest.mark.asyncio
async def test_password_schemas_require_eight_characters(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "short-password@mteja.ai", "full_name": "Short User", "password": "1234567",
        "organization_name": "Short Org",
    })
    assert response.status_code == 422