from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_db
from src.schemas.products import ProductCreate, ProductResponse
from src.repositories.product_repository import ProductRepository
from src.services.product_service import ProductService
from src.core.logger import logger

router = APIRouter(prefix="/products", tags=["Products"])

async def get_product_service(db: AsyncSession = Depends(get_db)):
    repo = ProductRepository(db)
    return ProductService(repo)

@router.post("/new_link", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(
    product_data: ProductCreate,
    product_service: ProductService = Depends(get_product_service)
):
    try:
        return await product_service.add_and_parse_product(product_data)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")