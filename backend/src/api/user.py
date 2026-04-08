from fastapi import APIRouter, Depends, HTTPException, status
from src.database.models import Users
from src.repositories.user_repository import UserRepository
from src.api.auth import get_current_user, get_user_repo
from src.schemas.auth import ContactCreate, ContactResponse

# Создаем новый роутер специально для эндпоинтов пользователя
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/me/contacts", response_model=ContactResponse)
async def update_user_contacts(
        contacts_data: ContactCreate,
        current_user: Users = Depends(get_current_user),
        user_repo: UserRepository = Depends(get_user_repo)
):
    """
    Создает или обновляет контактные данные для текущего пользователя.

    Эндпоинт защищен. Требует наличия валидного JWT-токена в заголовках.
    Принимает JSON с необязательными полями email, phone_number, tg.
    Обновляет только переданные поля.
    """
    contacts = await user_repo.upsert_contacts(
        user_id=current_user.id,
        contacts_data=contacts_data
    )

    # Модель Contacts будет автоматически преобразована в схему ContactResponse
    return contacts