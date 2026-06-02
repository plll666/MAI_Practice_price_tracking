import pytest
from unittest.mock import MagicMock, AsyncMock
from src.repositories.user_repository import UserRepository
from src.schemas.auth import UserCreate, ContactCreate

@pytest.mark.asyncio
class TestUserRepositoryIntegration:
    
    async def test_get_user_by_login_integration(self):
        mock_db = MagicMock()
        mock_db.execute = AsyncMock()
        
        mock_result = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "testuser"
        
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        repo = UserRepository(mock_db)
        result = await repo.get_user_by_login("testuser")
        assert result is not None

    async def test_create_user_integration(self):
        mock_db = AsyncMock()
        mock_db.commit = AsyncMock()
        mock_db.flush = AsyncMock()
        mock_db.rollback = AsyncMock()
        
        repo = UserRepository(mock_db)
        user_data = UserCreate(login="newuser", password="password123")
        
        result = await repo.create_user(user_data)
        assert result is not None

    async def test_get_user_by_login_integration(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_result.scalars.return_value.first.return_value = mock_user
        
        repo = UserRepository(mock_db)
        result = await repo.get_user_by_login("testuser")
        
        assert result is not None
        assert result.login == "testuser"