from fastapi import APIRouter

# Import all individual routers from your v1 modules
from app.api.v1 import (
    auth,
    conversations,
    customers,
    stock,
    webhooks,
    agents,
    dashboard,
    campaigns,
    deals,
    leads,
)

api_router = APIRouter()

# Include each router with appropriate prefixes and tags
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(
    conversations.router, prefix="/conversations", tags=["Unified Inbox"]
)
api_router.include_router(
    customers.router, prefix="/customers", tags=["Customers"]
)
api_router.include_router(stock.router, prefix="/stock", tags=["Stock & Inventory"])
api_router.include_router(
    webhooks.router, prefix="/webhooks", tags=["Social Media Webhooks"]
)
api_router.include_router(
    agents.router, prefix="/agent", tags=["AI & Analytics Agent"]
)
api_router.include_router(
    dashboard.router, prefix="/dashboard", tags=["Dashboard Analytics"]
)
api_router.include_router(
    campaigns.router, prefix="/campaigns", tags=["Broadcast Campaigns"]
)
api_router.include_router(deals.router, prefix="/deals", tags=["Sales Deals"])
api_router.include_router(leads.router, prefix="/leads", tags=["Lead Management"])