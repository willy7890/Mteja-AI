import pytest

@pytest.mark.asyncio
async def test_conversations_flow_and_isolation(client):
    # 1. Sajili User wa Org 1 na upate Token
    await client.post("/api/v1/auth/register", json={
        "email": "agent1@mteja.ai",
        "full_name": "Agent One",
        "password": "Password123",
        "organization_name": "Support Org"
    })
    login_a = await client.post("/api/v1/auth/login", data={
        "username": "agent1@mteja.ai",
        "password": "Password123"
    })
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    cust_res = await client.post("/api/v1/customers/", json={
        "name": "Juma Hassan",
        "phone": "255711223344"
    }, headers=headers_a)
    customer_id = cust_res.json()["id"]

    conv_res = await client.post("/api/v1/conversations/", json={
        "customer_id": customer_id,
        "channel": "whatsapp",
        "status": "open"
    }, headers=headers_a)
    assert conv_res.status_code in [200, 201]
    conv_id = conv_res.json()["id"]

    list_res = await client.get("/api/v1/conversations/", headers=headers_a)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    await client.post("/api/v1/auth/register", json={
        "email": "agent2@otherorg.ai",
        "full_name": "Agent Two",
        "password": "Password123",
        "organization_name": "Other Org"
    })
    login_b = await client.post("/api/v1/auth/login", data={
        "username": "agent2@otherorg.ai",
        "password": "Password123"
    })
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    get_conv_b = await client.get(f"/api/v1/conversations/{conv_id}", headers=headers_b)
    assert get_conv_b.status_code == 404