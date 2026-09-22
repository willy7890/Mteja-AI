import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.channel import ChannelIntegration
from app.models.conversation import Conversation
from app.models.customer import Customer
from app.models.message import Message
from app.models.telegram import TelegramLink, TelegramSession
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.models.organization import Organization
from app.services.agent_service import generate_agent_reply


logger = logging.getLogger(__name__)


def format_telegram_reply(result: object) -> str:
    if isinstance(result, str):
        return result

    if not isinstance(result, dict):
        return str(result)

    message = result.get("message")
    if message:
        return str(message)

    payload = result.get("result")

    if isinstance(payload, dict):
        message = payload.get("message")

        if message:
            return str(message)

        if "ideas" in payload and isinstance(payload["ideas"], list):
            ideas = "\n".join(f"- {idea}" for idea in payload["ideas"])
            return f"Haya ni mawazo ya kampeni:\n{ideas}"

        if "order_id" in payload and "status" in payload:
            return (
                f"Order {payload['order_id']} status: "
                f"{payload['status']}"
            )

        if "product" in payload and "price" in payload:
            return (
                f"Price for {payload['product']}: "
                f"{payload['price']}"
            )

        details = "\n".join(
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in payload.items()
        )

        if details:
            return details

    return "Nimepokea ujumbe wako, lakini sijapata jibu la kina bado."


async def get_or_create_session(
    db,
    integration_id: int,
    chat_id: str,
) -> TelegramSession:

    result = await db.execute(
        select(TelegramSession).where(
            TelegramSession.integration_id == integration_id,
            TelegramSession.telegram_chat_id == chat_id,
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        session = TelegramSession(
            integration_id=integration_id,
            telegram_chat_id=chat_id,
            state="idle",
            temp_data={},
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

    return session


async def update_session(
    db,
    session: TelegramSession,
    state: str,
    temp_data: dict | None = None,
):
    session.state = state

    if temp_data is not None:
        session.temp_data = temp_data

    await db.commit()
    await db.refresh(session)


async def reset_session(
    db,
    session: TelegramSession,
):
    session.state = "idle"
    session.temp_data = {}

    await db.commit()
    await db.refresh(session)


async def get_link(
    db,
    integration_id: int,
    chat_id: str,
) -> TelegramLink | None:

    result = await db.execute(
        select(TelegramLink)
        .where(
            TelegramLink.integration_id == integration_id,
            TelegramLink.telegram_chat_id == chat_id,
            TelegramLink.is_active.is_(True),
        )
        .options(
            selectinload(TelegramLink.user)
        )
    )

    return result.scalar_one_or_none()


async def get_or_create_telegram_conversation(
    db,
    link: TelegramLink,
    update: Update,
):
    chat_id = str(update.effective_chat.id)

    display_name = (
        update.effective_user.full_name
        if update.effective_user
        else "Telegram customer"
    )

    organization_id = link.user.organization_id

    result = await db.execute(
        select(Customer).where(
            Customer.organization_id == organization_id,
            Customer.phone == chat_id,
        )
    )

    customer = result.scalar_one_or_none()

    if not customer:
        customer = Customer(
            name=display_name,
            phone=chat_id,
            organization_id=organization_id,
        )

        db.add(customer)
        await db.flush()

    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.organization_id == organization_id,
            Conversation.customer_id == customer.id,
            Conversation.channel == "telegram",
            Conversation.status == "open",
        )
        .order_by(Conversation.id.desc())
    )

    conversation = result.scalars().first()

    if not conversation:
        conversation = Conversation(
            organization_id=organization_id,
            customer_id=customer.id,
            channel="telegram",
        )

        db.add(conversation)
        await db.flush()

    return conversation


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Legacy polling handler.

    This function is kept for compatibility, but production
    multi-tenant Telegram traffic should use the webhook service.
    """

    integration_id = context.application.bot_data.get("integration_id")

    if not integration_id:
        logger.error("Telegram integration_id missing from bot context")
        await update.message.reply_text(
            "Samahani, Telegram integration haijasanidiwa vizuri."
        )
        return

    chat_id = str(update.effective_chat.id)

    async with AsyncSessionLocal() as db:

        link = await get_link(
            db,
            integration_id,
            chat_id,
        )

        if link:
            await update.message.reply_text(
                "Karibu tena Mteja AI! Tayari umeshaunganishwa "
                "na akaunti yako.\n\n"
                "Andika chochote unachotaka kufanya."
            )
            return

        session = await get_or_create_session(
            db,
            integration_id,
            chat_id,
        )

        await update_session(
            db,
            session,
            state="idle",
            temp_data={},
        )

        keyboard = ReplyKeyboardMarkup(
            [["Login", "Register"]],
            one_time_keyboard=True,
            resize_keyboard=True,
        )

        await update.message.reply_text(
            "Karibu Mteja AI! 👋\n\n"
            "Bado hujaunganisha akaunti yako. Chagua moja:",
            reply_markup=keyboard,
        )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Legacy polling handler.

    Production webhook will call the same business logic
    using the correct integration_id.
    """

    if not update.message or not update.message.text:
        return

    integration_id = context.application.bot_data.get("integration_id")

    if not integration_id:
        logger.error("Telegram integration_id missing from bot context")
        await update.message.reply_text(
            "Samahani, Telegram integration haijasanidiwa vizuri."
        )
        return

    chat_id = str(update.effective_chat.id)
    text = update.message.text.strip()

    async with AsyncSessionLocal() as db:

        link = await get_link(
            db,
            integration_id,
            chat_id,
        )

        if link:

            conversation = await get_or_create_telegram_conversation(
                db,
                link,
                update,
            )

            user_message = Message(
                conversation_id=conversation.id,
                sender_type="customer",
                sender_name=(
                    update.effective_user.full_name
                    if update.effective_user
                    else "Telegram customer"
                ),
                content=text,
            )

            db.add(user_message)
            await db.flush()

            reply_text = await generate_agent_reply(text)

            db.add(
                Message(
                    conversation_id=conversation.id,
                    sender_type="agent",
                    sender_name="mteja-ai",
                    content=reply_text,
                )
            )

            await db.commit()

            await update.message.reply_text(reply_text)
            return

        session = await get_or_create_session(
            db,
            integration_id,
            chat_id,
        )

        state = session.state

        temp_data = (
            dict(session.temp_data)
            if session.temp_data
            else {}
        )

        if text.lower() == "login" and state == "idle":

            await update_session(
                db,
                session,
                state="login_email",
                temp_data={},
            )

            await update.message.reply_text(
                "Weka email yako:",
                reply_markup=ReplyKeyboardRemove(),
            )

            return

        if text.lower() == "register" and state == "idle":

            await update_session(
                db,
                session,
                state="register_fullname",
                temp_data={},
            )

            await update.message.reply_text(
                "Weka jina lako kamili:",
                reply_markup=ReplyKeyboardRemove(),
            )

            return

        if state == "login_email":

            temp_data["email"] = text

            await update_session(
                db,
                session,
                state="login_password",
                temp_data=temp_data,
            )

            await update.message.reply_text(
                "Weka password yako:"
            )

            return

        if state == "login_password":

            email = temp_data.get("email")
            password = text

            if not email:

                await update.message.reply_text(
                    "Samahani, kuna tatizo la kiufundi. "
                    "Tafadhali anza tena kwa /start"
                )

                await reset_session(db, session)
                return

            result = await db.execute(
                select(User).where(
                    User.email == email
                )
            )

            user = result.scalar_one_or_none()

            if not user or not verify_password(
                password,
                user.hashed_password,
            ):

                await update.message.reply_text(
                    "Email au password si sahihi. "
                    "Jaribu tena kwa /start"
                )

                await reset_session(db, session)
                return

            existing_link_result = await db.execute(
                select(TelegramLink).where(
                    TelegramLink.integration_id == integration_id,
                    TelegramLink.telegram_chat_id == chat_id,
                )
            )

            existing_link = (
                existing_link_result.scalar_one_or_none()
            )

            if existing_link:
                existing_link.user_id = user.id
                existing_link.telegram_username = (
                    update.effective_user.username
                    if update.effective_user
                    else None
                )
                existing_link.is_active = True

            else:
                new_link = TelegramLink(
                    integration_id=integration_id,
                    telegram_chat_id=chat_id,
                    telegram_username=(
                        update.effective_user.username
                        if update.effective_user
                        else None
                    ),
                    user_id=user.id,
                    is_active=True,
                )

                db.add(new_link)

            await reset_session(db, session)

            await db.commit()

            await update.message.reply_text(
                f"Umefanikiwa kuingia! Karibu "
                f"{user.full_name or user.email} 🎉\n\n"
                "Sasa umeunganishwa na Mteja AI kupitia Telegram."
            )

            return

        if state == "register_fullname":

            temp_data["full_name"] = text

            await update_session(
                db,
                session,
                state="register_email",
                temp_data=temp_data,
            )

            await update.message.reply_text(
                "Weka email yako:"
            )

            return

        if state == "register_email":

            result = await db.execute(
                select(User).where(
                    User.email == text
                )
            )

            existing = result.scalar_one_or_none()

            if existing:

                await update.message.reply_text(
                    "Email hii tayari imesajiliwa. "
                    "Jaribu Login kwa /start"
                )

                await reset_session(db, session)
                return

            temp_data["email"] = text

            await update_session(
                db,
                session,
                state="register_password",
                temp_data=temp_data,
            )

            await update.message.reply_text(
                "Weka password (angalau herufi 6):"
            )

            return

        if state == "register_password":

            if len(text) < 6:

                await update.message.reply_text(
                    "Password ni fupi mno. "
                    "Weka password ya angalau herufi 6:"
                )

                return

            temp_data["password"] = text

            await update_session(
                db,
                session,
                state="register_orgname",
                temp_data=temp_data,
            )

            await update.message.reply_text(
                "Weka jina la Organization/Kampuni yako:"
            )

            return

        if state == "register_orgname":

            org_name = text

            required_keys = (
                "email",
                "full_name",
                "password",
            )

            missing = [
                key
                for key in required_keys
                if key not in temp_data
            ]

            if missing:

                logger.warning(
                    "Session %s missing keys %s",
                    session.id,
                    missing,
                )

                await update.message.reply_text(
                    "Samahani, kuna tatizo la kiufundi. "
                    "Tafadhali anza tena kwa /start"
                )

                await reset_session(db, session)
                return

            org = Organization(
                name=org_name
            )

            db.add(org)
            await db.flush()

            new_user = User(
                email=temp_data["email"],
                full_name=temp_data["full_name"],
                hashed_password=hash_password(
                    temp_data["password"]
                ),
                is_active=True,
                is_superuser=False,
                organization_id=org.id,
            )

            db.add(new_user)
            await db.flush()

            new_link = TelegramLink(
                integration_id=integration_id,
                telegram_chat_id=chat_id,
                telegram_username=(
                    update.effective_user.username
                    if update.effective_user
                    else None
                ),
                user_id=new_user.id,
                is_active=True,
            )

            db.add(new_link)

            await reset_session(db, session)

            await db.commit()

            await update.message.reply_text(
                f"Hongera {new_user.full_name}! "
                "Akaunti yako imetengenezwa na "
                "imeunganishwa na Telegram. "
                "Karibu Mteja AI 🎉"
            )

            return

        await update.message.reply_text(
            "Sielewi ujumbe huu. Andika /start kuanza."
        )


def build_telegram_app(
    integration_id: int,
    bot_token: str,
) -> Application:

    if not bot_token:
        raise RuntimeError(
            "Telegram bot token is required"
        )

    app = (
        Application
        .builder()
        .token(bot_token)
        .build()
    )

    app.bot_data["integration_id"] = integration_id

    app.add_handler(
        CommandHandler(
            "start",
            start_command,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    return app