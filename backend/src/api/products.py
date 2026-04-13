from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from src.core.hashid import decode_id

from src.database.database import get_db
from src.schemas.products import ProductCreate, ProductResponse, ProductListResponse
from src.repositories.product_repository import ProductRepository
from src.repositories.user_repository import UserRepository
from src.services.product_service import ProductService
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

@router.post("/new_link", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(
    product_data: ProductCreate,
    current_user = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service)
):
    try:
        return await product_service.add_and_parse_product(
            user_id=current_user.id, 
            product_data=product_data
        )
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

@router.get("/{hashed_id}", response_model=ProductResponse)
async def get_product(
    hashed_id: str,
    current_user = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service)
):
    product_id = decode_id(hashed_id)
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product