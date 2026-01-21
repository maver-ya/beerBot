from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select
from datetime import datetime

from ..db.session import AsyncSessionLocal
from ..db.models.user import User
from ..db.models.chat import Chat
from ..db.models.drink import DrinkEvent, DrinkParticipant
from ..utils.achievements import check_achievements

router = Router()


@router.message(Command("drink"))
async def drink_handler(message: Message):
    """
    Запись выпитого пива.
    Формат:
    /drink <название> <литры> <цена> [участники через @username через запятую]
    Пример:
    /drink Bud 0.5 150
    /drink Heineken 1 300 @user1,@user2
    """
    args = message.text.split()
    if len(args) < 4:
        return await message.answer(
            "Использование:\n"
            "/drink <название> <литры> <цена> [@user1,@user2,...]"
        )

    beer_name = args[1]
    try:
        volume_l = float(args[2])
        price_rub = float(args[3])
    except ValueError:
        return await message.answer("❌ Литры и цена должны быть числами")

    participants_usernames = []
    if len(args) > 4:
        participants_usernames = args[4].split(",")

    async with AsyncSessionLocal() as session:
        # --- USER ---
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
        if not user:
            return await message.answer("❌ Ты не зарегистрирован в системе")

        # --- CHAT ---
        chat = await session.scalar(select(Chat).where(Chat.tg_chat_id == message.chat.id))
        if not chat:
            # Создаём чат, если нет
            chat = Chat(tg_chat_id=message.chat.id, title=message.chat.title)
            session.add(chat)
            await session.commit()
            await session.refresh(chat)

        # --- CREATE EVENT ---
        event = DrinkEvent(
            beer_name=beer_name,
            volume_l=volume_l,
            price_rub=price_rub,
            creator_id=user.id,
            chat_id=chat.id,
            created_at=datetime.utcnow()
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)

        # --- ADD PARTICIPANTS ---
        participant_ids = [user.id]  # creator всегда участвует
        if participants_usernames:
            for uname in participants_usernames:
                participant = await session.scalar(select(User).where(User.username == uname.lstrip("@")))
                if participant:
                    participant_ids.append(participant.id)

        share = 1 / len(participant_ids)
        for pid in participant_ids:
            dp = DrinkParticipant(
                user_id=pid,
                drink_event_id=event.id,
                share=share
            )
            session.add(dp)

        await session.commit()

    # --- RESPONSE ---
    participants_text = ", ".join(participants_usernames) if participants_usernames else "только ты"
    await message.answer(
        f"🍺 Записано: {beer_name} {volume_l:.2f} л за {price_rub:.2f} ₽\n"
        f"👥 Участники: {participants_text}"
    )

    # --- CHECK ACHIEVEMENTS ---
    await check_achievements(user.id, message.bot, message.chat.id)
