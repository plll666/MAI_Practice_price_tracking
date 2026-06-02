import pytest
from fastapi import status

@pytest.mark.asyncio
class TestAuth:
    async def test_register_success(self, client):
        response = await client.post("/auth/register", json={
            "login": "newuser",
            "password": "password123"
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_login(self, client):
        await client.post("/auth/register", json={
            "login": "duplicate",
            "password": "password123"
        })
        response = await client.post("/auth/register", json={
            "login": "duplicate",
            "password": "password123"
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    async def test_login_success(self, test_user, client):
        user = await test_user()
        form_data = {
            "username": user.login, 
            "password": "testpass123"
        }
        response = await client.post("auth/login", data=form_data)
        assert response.status_code == status.HTTP_200_OK

    async def test_login_invalid_credentials(self, test_user, client):
        await test_user()
        response = await client.post("/auth/login", data={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED