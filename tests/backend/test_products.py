import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
import jwt
from src.core.security import SECRET_KEY

@pytest.mark.asyncio
class TestProducts:
    
    async def test_get_products_unauthorized(self, client):
        response = await client.get("/products/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("src.celery_work.app.celery_app.send_task")
    async def test_add_product_success(self, mock_send_task, test_user, client):
        user = await test_user()
        
        mock_result = MagicMock()
        mock_result.get = MagicMock(return_value={
            "title": "Test Product",
            "brand": "TestBrand",
            "price": 1000,
            "image_url": "https://example.com/image.jpg",
            "source": "example.com"
        })
        mock_send_task.return_value = mock_result
        
        token = jwt.encode({"sub": user.login}, SECRET_KEY, algorithm="HS256")
        
        response = await client.post(
            "/products/new_link",
            json={"url": "https://example.com/product"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    @patch("src.celery_work.app.celery_app.send_task")
    async def test_add_product_invalid_url(self, mock_send_task, test_user, client):
        user = await test_user(login="testuser2", password="testpass123")
        token = jwt.encode({"sub": user.login}, SECRET_KEY, algorithm="HS256")
        
        response = await client.post(
            "/products/new_link",
            json={"url": "not-a-valid-url"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY