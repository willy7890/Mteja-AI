import pytest

@pytest.mark.asyncio
async def test_multi_tenant_isolation(client):
    res_a = await client.post("/api/v1/auth/register", json={
        "email": "org_a@mteja.ai", "full_name": "User A",
        "password": "Password123", "organization_name": "Org A"
    })
    token_a = (await client.post("/api/v1/auth/login", data={
        "username": "org_a@mteja.ai", "password": "Password123"
    })).json()["access_token"]
   
    res_b = await client.post("/api/v1/auth/register", json={
        "email": "org_b@mteja.ai", "full_name": "User B",
        "password": "Password123", "organization_name": "Org B"
    })
    token_b = (await client.post("/api/v1/auth/login", data={
        "username": "org_b@mteja.ai", "password": "Password123"
    })).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    create_res = await client.post("/api/v1/customers/", json={
        "name": "Customer A", "phone": "255700000001"
    }, headers=headers_a)
    assert create_res.status_code == 201
    cust_id = create_res.json()["id"]

    headers_b = {"Authorization": f"Bearer {token_b}"}
    get_res = await client.get(f"/api/v1/customers/{cust_id}", headers=headers_b)
    assert get_res.status_code == 404