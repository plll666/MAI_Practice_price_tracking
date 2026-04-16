from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from src.core.hashid import encode_id, decode_id

from src.database.database import get_db
from src.database.models import Subscriptions, PriceHistory, ProductLinks
from src.schemas.products import (
    ProductCreate, 
    ProductResponse, 
    ProductListResponse, 
    ProductPriceResponse, 
    ProductPriceListResponse,
    PriceHistoryResponse,
    TargetPriceUpdate
)
from src.repositories.product_repository import ProductRepository
from src.repositories.price_history_repository import PriceHistoryRepository
from src.repositories.user_repository import UserRepository
from src.services.product_service import ProductService
from src.services.price_service import PriceService
from src.core.security import SECRET_KEY, ALGORITHM
from src.core.logger import logger
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/products", tags=["Products"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_login(login)
    if user is None:
        raise credentials_exception
    return user


async def get_product_service(db: AsyncSession = Depends(get_db)):
    repo = ProductRepository(db)
    return ProductService(repo)


async def get_price_service(db: AsyncSession = Depends(get_db)):
    repo = PriceHistoryRepository(db)
    return PriceService(repo)


@router.post("/new_link", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(
    product_data: ProductCreate,
    current_user = Depends(get_current_user),
    product_service = Depends(get_product_service),
    db: AsyncSession = Depends(get_db)
):
    try:
        product = await product_service.add_and_parse_product(
            user_id=current_user.id, 
            product_data=product_data
        )
        
        sub_query = select(Subscriptions.target_price).where(
            Subscriptions.user_id == current_user.id,
            Subscriptions.product_id == product.id
        )
        result = await db.execute(sub_query)
        target_price = result.scalar_one_or_none()
        
        price_query = (
            select(PriceHistory.price)
            .join(ProductLinks)
            .where(ProductLinks.product_id == product.id)
            .order_by(PriceHistory.parsed_at.desc())
            .limit(1)
        )
        price_result = await db.execute(price_query)
        current_price = price_result.scalar_one_or_none()
        
        url_query = (
            select(ProductLinks.url)
            .where(ProductLinks.product_id == product.id)
            .limit(1)
        )
        url_result = await db.execute(url_query)
        product_url = url_result.scalar_one_or_none()
        
        response = {
            "id": encode_id(product.id),
            "title": product.title,
            "brand": product.brand,
            "image_url": product.image_url,
            "url": product_url,
            "current_price": float(current_price) if current_price else 0.0,
            "target_price": float(target_price) if target_price else None
        }
        
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", response_model=ProductListResponse)
async def get_products(
    current_user = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service)
):
    items = await product_service.get_all_products(user_id=current_user.id)
    return {"products": items}


@router.get("/prices", response_model=ProductPriceListResponse)
async def get_product_prices(
    current_user = Depends(get_current_user),
    price_service: PriceService = Depends(get_price_service)
):
    """Получить последние цены для товаров пользователя."""
    products_data = await price_service.get_user_products_with_prices(current_user.id)
    
    products = [
        ProductPriceResponse(
            id=encode_id(p["id"]),
            title=p["title"],
            current_price=p["current_price"],
            previous_price=p["previous_price"],
            shop=p["shop"],
            last_parsed_at=p["last_parsed_at"]
        )
        for p in products_data
    ]
    
    return {"products": products}


@router.get("/{hashed_id}/history", response_model=PriceHistoryResponse)
async def get_product_history(
    hashed_id: str,
    current_user = Depends(get_current_user),
    price_service: PriceService = Depends(get_price_service),
    days: int = Query(default=30, ge=1, le=365, description="Количество дней")
):
    """Получить историю цен товара."""
    product_id = decode_id(hashed_id)
    
    if product_id is None:
        logger.warning(f"Получен некорректный ID товара: '{hashed_id}' от пользователя '{current_user.login}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный ID товара"
        )
    
    logger.info(f"Запрос истории цен товара {product_id} за {days} дней от пользователя '{current_user.login}'")
    history_data = await price_service.get_product_price_history(product_id, days)
    
    logger.info(f"История цен товара {product_id}: {len(history_data['history'])} записей за {days} дней")
    
    return PriceHistoryResponse(
        product_id=encode_id(history_data["product_id"]),
        history=history_data["history"],
        min_price=history_data["min_price"],
        max_price=history_data["max_price"],
        avg_price=history_data["avg_price"],
        change_from_first=history_data["change_from_first"],
        change_percent=history_data["change_percent"]
    )


@router.get("/{hashed_id}", response_model=ProductResponse)
async def get_product(
    hashed_id: str,
    current_user = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service)
):
    product_id = decode_id(hashed_id)
    
    if product_id is None:
        logger.warning(f"Получен некорректный ID товара: '{hashed_id}' от пользователя '{current_user.login}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный ID товара"
        )
    
    logger.info(f"Запрос товара {product_id} от пользователя '{current_user.login}'")
    product = await product_service.get_product_by_id(product_id, user_id=current_user.id)
    
    if not product:
        logger.warning(f"Товар {product_id} не найден для пользователя '{current_user.login}'")
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    logger.info(f"Товар {product_id} успешно найден для '{current_user.login}'")
    return product


@router.post("/{hashed_id}/target-price")
async def update_target_price(
    hashed_id: str,
    data: TargetPriceUpdate,
    current_user = Depends(get_current_user),
    product_service = Depends(get_product_service)
):
    """Обновить желаемую цену для товара."""
    product_id = decode_id(hashed_id)
    
    if product_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный ID товара"
        )
    
    product = await product_service.get_product_by_id(product_id, user_id=current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    success = await product_service.update_target_price(current_user.id, product_id, data.target_price)
    
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка сохранения")
    
    logger.info(f"Обновлен target_price для товара {product_id}: {data.target_price}")
    
    return {"success": True, "target_price": data.target_price}
