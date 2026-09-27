import pytest
from urllib.parse import parse_qs, urlsplit

from jose import jwt

from app.core.config import settings
from app.core.security import create_google_oauth_state, validate_google_oauth_state

@pytest.mark.asyncio
async def test_register_user_success(client):
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
    assert data["email"] == "test@mteja.ai"
    assert "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client):
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
async def test_login_success(client):
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
    assert "secure" in cookie_header
    assert "samesite=none" in cookie_header
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
async def test_google_login_keeps_requesting_frontend_for_redirect(client, monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "google-client-secret")

    response = await client.get(
        "/api/v1/auth/google",
        params={"redirect_to": "https://mteja-ai.vercel.app"},
        follow_redirects=False,
    )

    assert response.status_code == 307
    state = parse_qs(urlsplit(response.headers["location"]).query)["state"][0]
    payload = jwt.decode(state, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["redirect_to"] == "https://mteja-ai.vercel.app"


@pytest.mark.asyncio
async def test_google_callback_redirects_back_to_original_frontend(client):
    state = create_google_oauth_state("https://mteja-ai.vercel.app")

    response = await client.get(
        "/api/v1/auth/google/callback",
        params={"state": state, "error": "access_denied"},
        headers={"Cookie": f"google_oauth_state={state}"},
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"].startswith("https://mteja-ai.vercel.app/login?")


@pytest.mark.asyncio
async def test_google_callback_rejects_state_without_matching_cookie(client, monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "google-client-secret")
    state = create_google_oauth_state()

    response = await client.get(
        "/api/v1/auth/google/callback",
        params={"code": "authorization-code", "state": state},
    )

    assert response.status_code == 400
    assert "state is missing, expired, or invalid" in response.json()["detail"]


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

    assert response.status_code == 400
    assert "state is missing, expired, or invalid" in response.json()["detail"]


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