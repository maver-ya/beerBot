from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from sqlalchemy import select, delete, desc

from ..db.session import AsyncSessionLocal
from ..db.models.user import User
from ..db.models.chat import Chat
from ..db.models.drink import DrinkEvent, DrinkParticipant

router = Router()


@router.message(Command("undo"))
async def undo_last_drink(message: Message):
    async with AsyncSessionLocal() as session:
        # ── USER ──
        user = await session.scalar(
            select(User).where(User.tg_id == message.from_user.id)
        )
        if not user:
            return await message.answer("🤔 У тебя ещё нет записей.")

        # ── CHAT ──
        chat = await session.scalar(
            select(Chat).where(Chat.tg_chat_id == message.chat.id)
        )
        if not chat:
            return await message.answer("🤔 В этом чате ещё нет записей.")

        # ── LAST EVENT ──
        drink_event = await session.scalar(
            select(DrinkEvent)
            .where(
                DrinkEvent.creator_id == user.id,
                DrinkEvent.chat_id == chat.id,
            )
            .order_by(desc(DrinkEvent.created_at))
            .limit(1)
        )

        if not drink_event:
            return await message.answer("❌ Нечего отменять.")

        # ── DELETE PARTICIPANTS ──
        await session.execute(
            delete(DrinkParticipant).where(
                DrinkParticipant.drink_event_id == drink_event.id
            )
        )

        # ── DELETE EVENT ──
        await session.delete(drink_event)
        await session.commit()

    await message.answer(
        "❌ Последняя запись удалена:\n"
        f"🍺 {drink_event.beer_name}\n"
        f"📦 {drink_event.volume_l} л\n"
        f"💰 {drink_event.price_rub} ₽"
    )
