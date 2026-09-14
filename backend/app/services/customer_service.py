# customer business logic service for MTEJA AI
# Domain operations, orchestration, and multi-tenant isolation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.customer import Customer
from typing import List, Optional


class CustomerService:

  @staticmethod
  async def get_customer_by_phone(
      db: AsyncSession, phone: str, organization_id: int
  ) -> Optional[Customer]:
    """Find a customer by phone number within the organization."""
    result = await db.execute(
        select(Customer).where(
            Customer.phone == phone,
            Customer.organization_id == organization_id,
        )
    )
    return result.scalar_one_or_none()

  @staticmethod
  async def create_customer(
      db: AsyncSession,
      organization_id: int,
      name: str,
      phone: Optional[str] = None,
      email: Optional[str] = None,
  ) -> Customer:
    """Create a new customer record."""
    customer = Customer(
        organization_id=organization_id, name=name, phone=phone, email=email
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer

  @staticmethod
  async def list_customers(
      db: AsyncSession, organization_id: int
  ) -> List[Customer]:
    """List all customers for the organization."""
    result = await db.execute(
        select(Customer).where(Customer.organization_id == organization_id)
    )
    return result.scalars().all()


customer_service = CustomerService()