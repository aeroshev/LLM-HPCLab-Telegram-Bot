from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from hpc_bot.exceptions import ExistChatError
from hpc_bot.telegram.fsm import UserMode
from hpc_bot.telegram.manager import ModelManager
from hpc_bot.telegram.messages import (
    CURRENT_STATE_TEXT,
    EXIST_CHAT_TEXT,
    HELLO_TEXT,
    HELP_TEXT,
    INLINE_MODE_TEXT,
    RESET_CHAT_TEXT,
    WINDOW_MODE_TEXT,
)

command_router: Router = Router(name='command_router')


@command_router.message(CommandStart())
async def command_start_handler(message: Message, manager: ModelManager, state: FSMContext) -> None:
    """
    Начать взаимодействие с ботом `/start` командой
    :param message: сообщение от пользователя
    :param manager: менеджер управления инференсом модели.
    :param state: состояние конечного автомата пользователя.
    :return:
    """
    await state.set_state(UserMode.window)

    try:
        await manager.start_conversion(message.chat.id, message.from_user.username)
    except ExistChatError:
        await message.answer(EXIST_CHAT_TEXT)
    else:
        await message.answer(HELLO_TEXT.format(username=hbold(message.from_user.full_name)))


@command_router.message(Command('reset_context'))
async def command_clean_context(message: Message, manager: ModelManager) -> None:
    """
    Очистить весь контекст переписки с ботом
    :param message: сообщение от пользователя
    :param manager: менеджер управления инференсом модели.
    :return:
    """
    await manager.reset_context(message.chat.id)
    await message.answer(RESET_CHAT_TEXT)


@command_router.message(Command('help'))
async def command_help_handler(message: Message) -> None:
    """
    Вернуть подсказку для общения с ботом
    :param message: сообщение от пользователя
    :return:
    """
    await message.answer(HELP_TEXT)


@command_router.message(Command('inline'))
async def command_inline_mode(message: Message, state: FSMContext) -> None:
    """
    Команда на включение режима линейной переписки с пользователем.
    :param message: сообщение от пользователя.
    :param state: состояние конечного автомата пользователя.
    :return:
    """
    await state.set_state(UserMode.inline)
    await message.answer(INLINE_MODE_TEXT)


@command_router.message(Command('window'))
async def command_window_mode(message: Message, state: FSMContext) -> None:
    """
    Комманда на включение режима скользящего окна переписки с пользователем.
    :param message: сообщение от пользователя.
    :param state: состояние конечного автомата пользователя.
    :return:
    """
    await state.set_state(UserMode.window)
    await message.answer(WINDOW_MODE_TEXT)


@command_router.message(Command('current_mode'))
async def command_current_mode(message: Message, state: FSMContext) -> None:
    """
    Команда на получение текущего режима переписки с пользователем.
    :param message: сообщение от пользователя.
    :param state: состояние конечного автомата пользователя.
    :return:
    """
    state = await state.get_state()
    await message.answer(CURRENT_STATE_TEXT.format(state=state))
