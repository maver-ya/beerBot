from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func, desc

from ..db.session import AsyncSessionLocal
from ..db.models.user import User
from ..db.models.chat import Chat
from ..db.models.drink import DrinkEvent, DrinkParticipant

router = Router()


@router.message(Command("beer"))
async def beer_top(message: Message):
    """
    Топ марок пива.
    В ЛС — личная статистика
    В группе — по чату
    """
    async with AsyncSessionLocal() as session:
        # --- Определяем чат и фильтр ---
        chat_id = None
        user_id = None

        if message.chat.type in ("group", "supergroup"):
            chat = await session.scalar(select(Chat).where(Chat.tg_chat_id == message.chat.id))
            if not chat:
                return await message.answer("😇 Пока в этом чате нет данных")
            chat_id = chat.id
        else:
            user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
            if not user:
                return await message.answer("😇 У тебя ещё нет записей")
            user_id = user.id

        # --- Запрос топ марок ---
        stmt = (
            select(
                DrinkEvent.beer_name,
                func.sum(DrinkEvent.volume_l * DrinkParticipant.share).label("total_volume")
            )
            .join(DrinkParticipant, DrinkParticipant.drink_event_id == DrinkEvent.id)
        )

        if chat_id:
            stmt = stmt.where(DrinkEvent.chat_id == chat_id)
        if user_id:
            stmt = stmt.where(DrinkParticipant.user_id == user_id)

        stmt = stmt.group_by(DrinkEvent.beer_name).order_by(desc("total_volume")).limit(10)

        result = await session.execute(stmt)
        rows = result.all()

    if not rows:
        return await message.answer("😇 Пока нет данных о марках пива 🍺")

    text = "🍻 Топ марок пива:\n\n"
    for i, (beer_name, volume) in enumerate(rows, start=1):
        text += f"{i}. {beer_name} — {volume:.2f} л\n"

    await message.answer(text)
