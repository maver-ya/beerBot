from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func

from ..db.session import AsyncSessionLocal
from ..db.models.drink import Drink

router = Router()


@router.message(Command("top"))
async def top_handler(message: Message):
    args = message.text.split()

    if len(args) < 2 or args[1] not in ("week", "month", "all"):
        await message.answer(
            "Использование:\n"
            "1️⃣ /top week — топ за неделю\n"
            "2️⃣ /top month — топ за месяц\n"
            "3️⃣ /top all — топ за всё время"
        )
        return

    period = args[1]

    if period == "week":
        date_from = datetime.utcnow() - timedelta(days=7)
        title = "🏆 Топ за неделю"
    elif period == "month":
        date_from = datetime.utcnow() - timedelta(days=30)
        title = "🏆 Топ за месяц"
    else:
        date_from = None
        title = "🏆 Топ за всё время"

    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                Drink.user_id,
                func.sum(Drink.amount).label("total")
            )
            .group_by(Drink.user_id)
            .order_by(func.sum(Drink.amount).desc())
            .limit(10)
        )

        if date_from:
            stmt = stmt.where(Drink.created_at >= date_from)

        result = await session.execute(stmt)
        rows = result.all()

    if not rows:
        await message.answer(f"{title}\n\nПока данных нет 🍺")
        return

    text = f"{title}\n\n"

    for i, (user_id, total) in enumerate(rows, start=1):
        text += f"{i}. 👤 {user_id} — 🍺 {total}\n"

    await message.answer(text)
