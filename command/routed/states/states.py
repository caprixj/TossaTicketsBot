from aiogram.fsm.state import StatesGroup, State


class MsellStates(StatesGroup):
    waiting_for_quantity = State()
    waiting_for_confirmation = State()
