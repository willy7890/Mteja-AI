import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.token import TokenValidationError
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.future import select

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.routes.telegram import manager as telegram_socket_manager
from app.core.security import get_password_hash, verify_password
from app.models.user import User

# Initialize FastAPI APIRouter
router = APIRouter(prefix="/telegram", tags=["Telegram Webhook"])

# Retrieve token safely from environment variables
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN.strip()

# Initialize Bot safely without crashing Uvicorn startup
bot = None
if BOT_TOKEN:
    try:
        bot = Bot(token=BOT_TOKEN)
    except TokenValidationError:
        print("⚠️ WARNING: TELEGRAM_BOT_TOKEN is invalid. Please check your .env file.")

dp = Dispatcher(storage=MemoryStorage())
aiogram_router = Router()


class AuthStates(StatesGroup):
    choosing_auth = State()
    register_email = State()
    register_password = State()
    login_email = State()
    login_password = State()


# Aiogram Handlers
@aiogram_router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Register (Sajili Akaunti)")],
            [KeyboardButton(text="Login (Ingia)")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "Karibu Mteja AI! 👋\nBado haujaunganisha akaunti yako. Chagua moja kuanza:",
        reply_markup=keyboard,
    )
    await state.set_state(AuthStates.choosing_auth)


@aiogram_router.message(AuthStates.choosing_auth)
async def handle_auth_choice(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if "Register" in text:
        await message.answer(
            "Weka email yako kwa ajili ya usajili:",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(AuthStates.register_email)
    elif "Login" in text:
        await message.answer(
            "Weka email yako:", reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(AuthStates.login_email)
    else:
        await message.answer("Tafadhali chagua kati ya Register au Login.")


@aiogram_router.message(AuthStates.register_email)
async def process_reg_email(message: types.Message, state: FSMContext):
    email = message.text.strip().lower()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        if result.scalars().first():
            await message.answer(
                "Email hii tayari imeshasajiliwa! Bonyeza /start kuingia (Login)."
            )
            await state.clear()
            return

    await state.update_data(email=email)
    await message.answer("Tengeneza password yako mpya:")
    await state.set_state(AuthStates.register_password)


@aiogram_router.message(AuthStates.register_password)
async def process_reg_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    email = data.get("email")

    async with AsyncSessionLocal() as session:
        new_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        session.add(new_user)
        await session.commit()

    await message.answer(
        f"🎉 Hongera! Akaunti ya {email} imetengenezwa kikamilifu.\nSasa unaweza kuanza kuuliza maswali!"
    )
    await state.clear()


@aiogram_router.message(AuthStates.login_email)
async def process_login_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text.strip().lower())
    await message.answer("Weka password yako:")
    await state.set_state(AuthStates.login_password)


@aiogram_router.message(AuthStates.login_password)
async def process_login_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    email = data.get("email")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalars().first()

        if user and verify_password(password, user.hashed_password):
            await message.answer(
                "Umefanikiwa kuingia! 🎉 Unaweza kuuliza swali lolote sasa."
            )
            await state.clear()
        else:
            await message.answer(
                "Email au password si sahihi. Jaribu tena kwa /start"
            )
            await state.clear()


# Attach Aiogram router to Dispatcher
dp.include_router(aiogram_router)


# FastAPI Webhook Endpoint
@router.post("/webhook")
async def telegram_webhook(request: Request):
    if not bot:
        raise HTTPException(
            status_code=500,
            detail="Telegram Bot Token parameter is missing or invalid in server configuration."
        )
    
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot=bot, update=update)
        message = data.get("message") or {}
        if message:
            await telegram_socket_manager.broadcast(
                {
                    "id": message.get("message_id"),
                    "sender": message.get("from", {}).get("first_name", "Telegram User"),
                    "chat_id": message.get("chat", {}).get("id"),
                    "text": message.get("text", ""),
                    "channel": "telegram",
                    "timestamp": "Just now",
                }
            )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))