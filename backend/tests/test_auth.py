import pytest

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
    # Jaribu kusajili mara ya pili barua pepe ile ile
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