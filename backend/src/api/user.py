from fastapi import APIRouter, Depends, HTTPException, status
from src.database.models import Users
from src.repositories.user_repository import UserRepository
from src.api.auth import get_current_user, get_user_repo
from src.schemas.auth import ContactCreate, ContactResponse
from src.core.logger import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me/contacts", response_model=ContactResponse)
async def get_user_contacts(
        current_user: Users = Depends(get_current_user),
        user_repo: UserRepository = Depends(get_user_repo)
):
    """Получить контактные данные текущего пользователя."""
    logger.info(f"Пользователь '{current_user.login}' запросил свои контактные данные")

    contacts = await user_repo.get_contacts(current_user.id)
    if not contacts:
        logger.info(f"Контактные данные для пользователя '{current_user.login}' не найдены")
        return {"user_id": current_user.id, "email": None, "phone_number": None, "tg": None}

    logger.info(
        f"Контактные данные пользователя '{current_user.login}' найдены: email={contacts.email is not None}, phone={contacts.phone_number is not None}, tg={contacts.tg is not None}")
    return contacts


@router.post("/me/contacts", response_model=ContactResponse)
async def update_user_contacts(
        contacts_data: ContactCreate,
        current_user: Users = Depends(get_current_user),
        user_repo: UserRepository = Depends(get_user_repo)
):
    """
    Создает или обновляет контактные данные для текущего пользователя.
    """
    logger.info(f"Пользователь '{current_user.login}' обновляет контактные данные")

    old_contacts = await user_repo.get_contacts(current_user.id)

    contacts = await user_repo.upsert_contacts(
        user_id=current_user.id,
        contacts_data=contacts_data
    )

    changes = []
    if old_contacts:
        if old_contacts.email != contacts.email:
            changes.append(f"email: '{old_contacts.email or 'не указан'}' -> '{contacts.email or 'не указан'}'")
        if old_contacts.phone_number != contacts.phone_number:
            changes.append(
                f"phone: '{old_contacts.phone_number or 'не указан'}' -> '{contacts.phone_number or 'не указан'}'")
        if old_contacts.tg != contacts.tg:
            changes.append(f"telegram: '{old_contacts.tg or 'не указан'}' -> '{contacts.tg or 'не указан'}'")

    if changes:
        logger.info(f"Контактные данные пользователя '{current_user.login}' обновлены: {', '.join(changes)}")
    else:
        logger.info(f"Контактные данные пользователя '{current_user.login}' сохранены (без изменений)")

    return contacts