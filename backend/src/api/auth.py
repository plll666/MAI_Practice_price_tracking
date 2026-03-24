from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.exc import IntegrityError

from src.database.database import get_db
from src.schemas.auth import UserCreate, UserResponse, Token
from src.repositories.user_repository import UserRepository
from src.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from src.core.logger import logger

router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_user_repo(db: AsyncSession = Depends(get_db)):
    """Вспомогательная зависимость для получения экземпляра UserRepository."""
    return UserRepository(db)


@router.post("/register", response_model=UserResponse)
async def register(
        user_data: UserCreate,
        user_repo: UserRepository = Depends(get_user_repo)
):
    """
    Регистрация нового пользователя в системе.

    - Проверяет, не занят ли логин.
    - Хеширует пароль.
    - Сохраняет пользователя в базу данных.
    """
    try:
        existing_user = await user_repo.get_user_by_login(user_data.login)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login already registered"
            )

        new_user = await user_repo.create_user(user_data)
        return new_user

    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        logger.error(f"Ошибка при регистрации: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_repo: UserRepository = Depends(get_user_repo)
):
    """
    Аутентификация пользователя и выдача JWT токена.

    Требует отправки `username` и `password` в формате form-data.
    """
    try:
        user = await user_repo.get_user_by_login(form_data.username)

        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.login}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при входе: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")