from sqlalchemy import select
from bot.db.session import AsyncSessionLocal
from bot.db.models.achievement import Achievement
from bot.db.models.drink import DrinkEvent, DrinkParticipant
from aiogram.types import User, Message


# Достижения в литрах
ACHIEVEMENT_LEVELS = [1, 5, 10, 25, 50]


async def check_achievements(user_id: int, bot, chat_id):
    async with AsyncSessionLocal() as session:
        # Считаем общее количество литров
        stmt = (
            select(func.sum(DrinkEvent.volume_l * DrinkParticipant.share))
            .join(DrinkParticipant, DrinkParticipant.drink_event_id == DrinkEvent.id)
            .where(DrinkParticipant.user_id == user_id)
        )
        result = await session.execute(stmt)
        total_volume = result.scalar() or 0

        # Смотрим какие уже есть достижения
        stmt2 = select(Achievement.level).where(Achievement.user_id == user_id)
        result2 = await session.execute(stmt2)
        existing_levels = {r[0] for r in result2.all()}

        new_levels = [lvl for lvl in ACHIEVEMENT_LEVELS if total_volume >= lvl and lvl not in existing_levels]

        for lvl in new_levels:
            ach = Achievement(
                user_id=user_id,
                level=lvl,
                description=f"Выпито {lvl} литров пива 🍺"
            )
            session.add(ach)
            await session.commit()

            # Отправка сообщения в чат
            await congratulate_user(message.from_user, volume, message)


async def congratulate_user(user: User, volume: float, message: Message):

    """
    Отправляет сообщение о выпитом объёме пользователем с кликабельным именем.
    """
    name = user.full_name  # или user.first_name
    text = f"🎉 Поздравляем, <a href='tg://user?id={user.id}'>{name}</a>! Выпито {volume} литров пива 🍺"
    await message.answer(text, parse_mode='HTML')
