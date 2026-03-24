from pydantic import BaseModel, ConfigDict


# Базовая схема
class UserBase(BaseModel):
    login: str


# То, что приходит на регистрацию
class UserCreate(UserBase):
    password: str


# То, что отдаем обратно
class UserResponse(UserBase):
    id: int
    is_active: bool

    # Чтобы ORM объекты превращались в Pydantic
    model_config = ConfigDict(from_attributes=True)


# Схема для токена
class Token(BaseModel):
    access_token: str
    token_type: str