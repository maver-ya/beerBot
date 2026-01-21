from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func
from datetime import datetime, timedelta

from ..db.session import AsyncSessionLocal
from ..db.models.user import User
from ..db.models.drink import DrinkEvent, DrinkParticipant

router = Router()


@router.message(Command("stats"))
async def stats_user(message: Message):
    """
    Статистика пользователя.
    Поддержка периодов: week, month, all
    В группе можно указать @username
    """
    args = message.text.split()

    # --- Определяем пользователя ---
    username = None
    period = "all"

    if len(args) > 1:
        if args[1] in ("week", "month", "all"):
            period = args[1]
        elif args[1].startswith("@"):
            username = args[1].lstrip("@")
        # проверка на оба аргумента
        if len(args) > 2 and args[2] in ("week", "month", "all"):
            period = args[2]

    if not username:
        username = message.from_user.username

    # --- Дата для фильтра ---
    now = datetime.utcnow()
    if period == "week":
        date_from = now - timedelta(days=7)
    elif period == "month":
        date_from = now - timedelta(days=30)
    else:
        date_from = None

    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(User).where(User.username == username))
        if not user:
            return await message.answer("🤔 Пользователь не найден")

        # --- Основной запрос ---
        stmt = (
            select(
                func.sum(DrinkEvent.volume_l * DrinkParticipant.share).label("total_volume"),
                func.sum(DrinkEvent.price_rub * DrinkParticipant.share).label("total_price"),
                func.count(DrinkEvent.id).label("events_count")
            )
            .join(DrinkParticipant, DrinkParticipant.drink_event_id == DrinkEvent.id)
            .where(DrinkParticipant.user_id == user.id)
        )

        if date_from:
            stmt = stmt.where(DrinkEvent.created_at >= date_from)

        result = await session.execute(stmt)
        total_volume, total_price, events_count = result.one()

    total_volume = total_volume or 0
    total_price = total_price or 0
    events_count = events_count or 0

    await message.answer(
        f"📊 Статистика для {username} ({period}):\n\n"
        f"🍺 Выпито: {total_volume:.2f} л\n"
        f"💰 Потрачено: {total_price:.2f} ₽\n"
        f"🗓 Количество событий: {events_count}"
    )
