from pydantic import BaseModel, ConfigDict


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