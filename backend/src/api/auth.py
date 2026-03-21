from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from src.database.database import get_db
from src.schemas.auth import UserCreate, UserResponse, Token
from src.repositories.user_repository import UserRepository
from src.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Auth"])


# Вспомогательная функция, чтобы не писать создание репозитория в каждой ручке
def get_user_repo(db: Session = Depends(get_db)):
    return UserRepository(db)


@router.post("/register", response_model=UserResponse)
def register(
        user_data: UserCreate,
        user_repo: UserRepository = Depends(get_user_repo)
):
    # 1. Проверяем, свободен ли логин
    if user_repo.get_user_by_login(user_data.login):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already registered"
        )

    # 2. Создаем
    return user_repo.create_user(user_data)


@router.post("/login", response_model=Token)
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),  # Стандартная форма FastAPI (username, password)
        user_repo: UserRepository = Depends(get_user_repo)
):
    # form_data.username - это будет наш login
    user = user_repo.get_user_by_login(form_data.username)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Генерация токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}