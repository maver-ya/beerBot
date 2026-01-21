from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from datetime import datetime

from ..db.session import AsyncSessionLocal
from ..db.models.user import User
from ..db.models.chat import Chat
from ..db.models.drink import DrinkEvent, DrinkParticipant
from ..utils.achievements import check_achievements

router = Router()


class DrinkForm(StatesGroup):
    beer_name = State()
    volume = State()
    price = State()
    participants = State()


@router.message(Command("drink"))
async def drink_start(message: Message, state: FSMContext):
    """Начало диалога добавления выпитого"""
    await state.clear()
    await state.set_state(DrinkForm.beer_name)
    await message.answer("🍺 Введи название пива:")


@router.message(DrinkForm.beer_name)
async def drink_name(message: Message, state: FSMContext):
    await state.update_data(beer_name=message.text)
    await state.set_state(DrinkForm.volume)
    await message.answer("🧪 Введи объём в литрах (например, 0.5):")


@router.message(DrinkForm.volume)
async def drink_volume(message: Message, state: FSMContext):
    try:
        volume = float(message.text.replace(",", "."))
    except ValueError:
        return await message.answer("❌ Пожалуйста, введи число (литры).")
    await state.update_data(volume=volume)
    await state.set_state(DrinkForm.price)
    await message.answer("💰 Введи стоимость в рублях (например, 150):")


@router.message(DrinkForm.price)
async def drink_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        return await message.answer("❌ Пожалуйста, введи число (цена).")
    await state.update_data(price=price)
    await state.set_state(DrinkForm.participants)
    await message.answer(
        "👥 Введи участников через @username через запятую, или напиши 'нет', если только ты:"
    )


@router.message(DrinkForm.participants)
async def drink_participants(message: Message, state: FSMContext):
    data = await state.get_data()
    beer_name = data["beer_name"]
    volume_l = data["volume"]
    price_rub = data["price"]
    participants_text = message.text.strip()

    participants_usernames = []
    if participants_text.lower() != "нет":
        participants_usernames = [u.strip().lstrip("@") for u in participants_text.split(",")]

    async with AsyncSessionLocal() as session:
        # --- USER ---
        user = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
        if not user:
            return await message.answer("❌ Ты не зарегистрирован в системе")

        # --- CHAT ---
        chat = await session.scalar(select(Chat).where(Chat.tg_chat_id == message.chat.id))
        if not chat:
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
            created_at=datetime.utcnow(),
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)

        # --- ADD PARTICIPANTS ---
        participant_ids = [user.id]
        if participants_usernames:
            for uname in participants_usernames:
                participant = await session.scalar(select(User).where(User.username == uname))
                if participant:
                    participant_ids.append(participant.id)

        share = 1 / len(participant_ids)
        for pid in participant_ids:
            dp = DrinkParticipant(user_id=pid, drink_event_id=event.id, share=share)
            session.add(dp)

        await session.commit()

    participants_text_reply = ", ".join(participants_usernames) if participants_usernames else "только ты"
    await message.answer(
        f"🍺 Записано: {beer_name} {volume_l:.2f} л за {price_rub:.2f} ₽\n"
        f"👥 Участники: {participants_text_reply}"
    )

    # --- CHECK ACHIEVEMENTS ---
    await check_achievements(user.id, message.bot, message.chat.id)

    # --- Завершаем FSM ---
    await state.clear()
