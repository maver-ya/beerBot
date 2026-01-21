from aiogram.fsm.state import State, StatesGroup

class DrinkStates(StatesGroup):
    beer_name = State()
    volume_l = State()
    price_rub = State()
    add_participants = State()  # Сбор участников
