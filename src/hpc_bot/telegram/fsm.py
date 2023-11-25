from aiogram.fsm.state import State, StatesGroup


class UserMode(StatesGroup):
    """
    Группа схожих состояний конечного автомата.
    """
    window = State()
    inline = State()
