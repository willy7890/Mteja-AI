from fastapi import APIRouter
from app.api.v1 import webhooks

from app.api.v1 import (
    agents,
    ai,
    admin,
    auth,
    campaigns,
    conversations,
    customers,
    dashboard,
    deals,
    leads,
    media,
    stock,
    telegram,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/v1/auth")
api_router.include_router(conversations.router, prefix="/v1/conversations")
api_router.include_router(customers.router, prefix="/v1/customers")
api_router.include_router(stock.router, prefix="/v1/stock")
api_router.include_router(telegram.router, prefix="/v1")
api_router.include_router(agents.router, prefix="/v1/agents")
api_router.include_router(dashboard.router, prefix="/v1/dashboard")
api_router.include_router(campaigns.router, prefix="/v1/campaigns")
api_router.include_router(deals.router, prefix="/v1/deals")
api_router.include_router(leads.router, prefix="/v1/leads")
api_router.include_router(ai.router, prefix="/v1")
api_router.include_router(admin.router, prefix="/v1")
api_router.include_router(media.router, prefix="/v1")
api_router.include_router(webhooks.router, prefix="/v1")
