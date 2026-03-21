from sqlalchemy.orm import Session
from src.database.models import Users
from src.schemas.auth import UserCreate
from src.core.security import get_password_hash


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_login(self, login: str):
        # API ничего не знает про select/filter, оно просто просит юзера
        return self.db.query(Users).filter(Users.login == login).first()

    def create_user(self, user: UserCreate):
        # Хешируем пароль здесь, перед записью
        hashed_password = get_password_hash(user.password)

        # Создаем модель SQLAlchemy (Users) из Pydantic схемы (UserCreate)
        db_user = Users(
            login=user.login,
            password_hash=hashed_password,
            is_active=True
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user