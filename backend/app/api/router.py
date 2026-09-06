from fastapi import APIRouter
from app.api.v1 import auth
from app.api.v1 import conversations
from app.api.v1 import customers
from app.api.v1 import stock

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/v1")
api_router.include_router(conversations.router, prefix="/v1")
api_router.include_router(customers.router, prefix="/v1")
api_router.include_router(stock.router, prefix="/v1")