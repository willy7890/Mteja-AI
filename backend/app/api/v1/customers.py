from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.organization import Organization
from app.schemas.customer import (
    CustomerRegisterRequest, 
    CustomerLoginRequest, 
    CustomerResponse,
    TokenResponse,
    CustomerCreateRequest,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    customer = Customer(
        name=data.name,
        phone=data.phone,
        email=data.email,
        organization_id=current_user.organization_id,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Customer).where(
        Customer.id == customer_id,
        Customer.organization_id == current_user.organization_id,
    ))
    customer = result.scalar_one_or_none()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/register", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def register_customer(data: CustomerRegisterRequest, db: AsyncSession = Depends(get_db)):
    org_res = await db.execute(select(Organization).where(Organization.id == data.organization_id))
    if not org_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Organization not found")

    existing = await db.execute(select(Customer).where(Customer.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Customer email already registered")

    customer = Customer(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),  # Hakikisha ni password_hash badala ya hashed_password kama model inavyoelekeza
        organization_id=data.organization_id
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    return customer

@router.post("/login", response_model=TokenResponse)
async def login_customer(data: CustomerLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.email == data.email))
    customer = result.scalar_one_or_none()

    # Tumia password_hash kama ndivyo ilivyofafanuliwa kwenye Customer model
    if not customer or not verify_password(data.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token_data = {"sub": str(customer.id), "org_id": customer.organization_id, "role": "customer"}
    access_token = create_access_token(token_data)

    return TokenResponse(access_token=access_token, token_type="bearer")