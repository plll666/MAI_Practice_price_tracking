from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    login: str


# То, что приходит на регистрацию
class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str

class ContactCreate(BaseModel):
    """Схема для создания/обновления контактных данных пользователя."""
    email: Optional[str] = None
    phone_number: Optional[str] = None
    tg: Optional[str] = None


class ContactResponse(ContactCreate):
    """Схема для отображения контактных данных пользователя."""
    user_id: int

    model_config = ConfigDict(from_attributes=True)