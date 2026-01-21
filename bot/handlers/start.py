from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from ..db.session import AsyncSessionLocal
from ..db.models.user import User
from ..db.models.chat import Chat
from ..logger_conf import logger

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    async with AsyncSessionLocal() as session:
        # --- USER ---
        user = await session.scalar(
            User.__table__.select().where(User.tg_id == message.from_user.id)
        )

        if not user:
            user = User(
                tg_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
            )
            session.add(user)
            logger.info(f"New user: {message.from_user.id}")

        # --- CHAT ---
        chat = await session.scalar(
            Chat.__table__.select().where(Chat.tg_chat_id == message.chat.id)
        )

        if not chat:
            chat = Chat(
                tg_chat_id=message.chat.id,
                title=message.chat.title,
                is_group=message.chat.type in ("group", "supergroup"),
            )
            session.add(chat)
            logger.info(f"New chat: {message.chat.id}")

        await session.commit()

    # --- RESPONSE ---
    if message.chat.type in ("group", "supergroup"):
        text = (
            "🍻 Я в деле!\n\n"
            "Теперь я считаю, кто сколько пьёт.\n"
            "Не осуждаю. Только фиксирую 😌\n\n"
            "Команды:\n"
            "/drink — записать выпитое через диалог\n"
            "/stats — посмотреть статистику пользователя\n"
            "/top [week|month|all] — топ пользователей по объёму\n"
            "/beer — топ марок пива\n"
            "/undo — удалить своё последнее событие"
        )
    else:
        text = (
            "🍺 Привет!\n\n"
            "Я — beerStat_bot.\n"
            "Записываю пиво, считаю литры и деньги.\n\n"
            "Команды:\n"
            "/drink — добавить пиво через диалог\n"
            "/stats [week|month|all] — твоя статистика или за период\n"
            "/top [week|month|all] — топ пользователей по объёму\n"
            "/beer — топ марок пива\n"
            "/undo — удалить своё последнее событие\n\n"
            "Начнём культурно. Или как получится 😏"
        )

    await message.answer(text)
