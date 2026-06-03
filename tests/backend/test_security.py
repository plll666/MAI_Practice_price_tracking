import pytest
from src.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta

class TestSecurity:
    
    def test_get_password_hash(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_success(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) == True

    def test_verify_password_failure(self):
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) == False

    def test_create_access_token(self):
        token = create_access_token(data={"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)

    def test_create_access_token_with_expire(self):
        token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(minutes=30)
        )
        assert token is not None