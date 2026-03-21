from pydantic import BaseModel, ConfigDict


# Базовая схема пользователя
class UserBase(BaseModel):
    login: str


# То, что прилетает от фронта при регистрации
class UserCreate(UserBase):
    password: str


# То, что отдаем обратно без пароля
class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# Схема для JWT токена
class Token(BaseModel):
    access_token: str
    token_type: str