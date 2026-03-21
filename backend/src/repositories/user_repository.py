from typing import Optional, Type  # Добавляем импорты типов
from sqlalchemy.orm import Session
from src.database.models import Users
from src.schemas.auth import UserCreate
from src.core.security import get_password_hash


class UserRepository:
    def __init__(self, db: Session):
        self.db: Session = db

    def get_user_by_login(self, login: str) -> Optional[Users]:
        return self.db.query(Users).filter(Users.login == login).first()

    def create_user(self, user: UserCreate) -> Users:
        hashed_password = get_password_hash(user.password)

        db_user = Users(
            login=user.login,
            password_hash=hashed_password,
            is_active=True
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user