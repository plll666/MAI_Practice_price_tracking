from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from src.database.database import get_db
from src.database.models import Alerts, Users
from src.api.products import get_current_user
from src.core.hashid import encode_id

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class AlertResponse(BaseModel):
    id: int
    product_id: str
    message: str
    current_price: Optional[float] = None
    target_price: Optional[float] = None
    is_read: bool
    created_at: datetime
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[AlertResponse])
async def get_alerts(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить уведомления пользователя."""
    query = (
        select(Alerts)
        .where(Alerts.user_id == current_user.id)
        .order_by(desc(Alerts.created_at))
        .limit(50)
    )
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    response = []
    for alert in alerts:
        product_query = select(Alerts.__table__.c).where(Alerts.id == alert.id)
        product_img = None
        
        from src.database.models import Products
        img_query = select(Products.image_url).where(Products.id == alert.product_id)
        img_result = await db.execute(img_query)
        product_img = img_result.scalar_one_or_none()
        
        response.append(AlertResponse(
            id=alert.id,
            product_id=encode_id(alert.product_id),
            message=alert.message,
            current_price=float(alert.current_price) if alert.current_price else None,
            target_price=float(alert.target_price) if alert.target_price else None,
            is_read=alert.is_read,
            created_at=alert.created_at,
            image_url=product_img
        ))
    
    return response


@router.post("/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отметить уведомление как прочитанное."""
    query = (
        update(Alerts)
        .where(Alerts.id == alert_id, Alerts.user_id == current_user.id)
        .values(is_read=True)
    )
    await db.execute(query)
    await db.commit()
    return {"success": True}


@router.post("/read-all")
async def mark_all_alerts_read(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отметить все уведомления как прочитанные."""
    query = (
        update(Alerts)
        .where(Alerts.user_id == current_user.id, Alerts.is_read == False)
        .values(is_read=True)
    )
    await db.execute(query)
    await db.commit()
    return {"success": True}


@router.get("/unread-count")
async def get_unread_count(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить количество непрочитанных уведомлений."""
    from sqlalchemy import func
    query = (
        select(func.count(Alerts.id))
        .where(Alerts.user_id == current_user.id, Alerts.is_read == False)
    )
    result = await db.execute(query)
    count = result.scalar()
    return {"count": count or 0}
