import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
import jwt
from src.core.security import SECRET_KEY

@pytest.mark.asyncio
class TestAlertsAPI:
    
    async def test_get_alerts_unauthorized(self, client):
        response = await client.get("/alerts/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_unread_count(self, test_user, client):
        user = await test_user()
        token = jwt.encode({"sub": user.login}, SECRET_KEY, algorithm="HS256")
        
        response = await client.get(
            "/alerts/unread-count",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data

    async def test_mark_alert_read(self, test_user, client):
        user = await test_user()
        token = jwt.encode({"sub": user.login}, SECRET_KEY, algorithm="HS256")
        
        response = await client.post(
            "/alerts/1/read",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    async def test_mark_all_alerts_read(self, test_user, client):
        user = await test_user()
        token = jwt.encode({"sub": user.login}, SECRET_KEY, algorithm="HS256")
        
        response = await client.post(
            "/alerts/read-all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK