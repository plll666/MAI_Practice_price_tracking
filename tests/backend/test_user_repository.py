import pytest
from unittest.mock import MagicMock, AsyncMock
from src.repositories.user_repository import UserRepository
from src.schemas.auth import UserCreate, ContactCreate

@pytest.mark.asyncio
class TestUserRepository:

    async def test_get_user_by_login_exists(self):
        mock_db = AsyncMock()
        
        mock_result = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "testuser"
        
        # Настройка цепочки вызовов
        mock_result.scalars.return_value.first.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        repo = UserRepository(mock_db)
        result = await repo.get_user_by_login("testuser")
        assert result is not None
        assert result.login == "testuser"

    async def test_get_user_by_login_not_exists(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result
        
        repo = UserRepository(mock_db)
        result = await repo.get_user_by_login("nonexistent")
        assert result is None

    async def test_create_user(self):
        mock_db = AsyncMock()
        
        repo = UserRepository(mock_db)
        user_data = UserCreate(login="newuser", password="password123")
        
        result = await repo.create_user(user_data)
        # Проверяем, что commit был вызван (у AsyncMock это делается через await)
        mock_db.commit.assert_called_once()
        assert result is not None

    async def test_upsert_contacts(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_db.execute.return_value = mock_result
        mock_result.scalars.return_value.first.return_value = None # или какой-то объект
        repo = UserRepository(mock_db)
        contacts_data = ContactCreate(email="test@test.com")
    
        result = await repo.upsert_contacts(1, contacts_data)
        mock_db.commit.assert_called_once()
        assert result is not None

    async def test_get_contacts(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_contacts = MagicMock()
        
        mock_result.scalars.return_value.first.return_value = mock_contacts
        mock_db.execute.return_value = mock_result
        
        repo = UserRepository(mock_db)
        result = await repo.get_contacts(1)
        assert result is not None