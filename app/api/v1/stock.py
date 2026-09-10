from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.stock import Stock
from app.models.user import User
from app.schemas.stock import StockCreate, StockResponse, StockUpdate

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.post("/", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def create_stock(
    data: StockCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stock = Stock(
        organization_id=current_user.organization_id,
        name=data.name,
        quantity=data.quantity,
        price=data.price,
        class_name=data.class_name,
    )
    db.add(stock)
    await db.commit()
    await db.refresh(stock)
    return stock


@router.get("/", response_model=list[StockResponse])
async def list_stock(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Stock).where(Stock.organization_id == current_user.organization_id).order_by(Stock.id))
    return result.scalars().all()


async def _get_stock(stock_id: int, current_user: User, db: AsyncSession) -> Stock:
    result = await db.execute(select(Stock).where(
        Stock.id == stock_id,
        Stock.organization_id == current_user.organization_id,
    ))
    stock = result.scalar_one_or_none()
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock item not found")
    return stock


@router.patch("/{stock_id}", response_model=StockResponse)
async def update_stock(
    stock_id: int,
    data: StockUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stock = await _get_stock(stock_id, current_user, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(stock, field, value)
    await db.commit()
    await db.refresh(stock)
    return stock


@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock(
    stock_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stock = await _get_stock(stock_id, current_user, db)
    await db.delete(stock)
    await db.commit()