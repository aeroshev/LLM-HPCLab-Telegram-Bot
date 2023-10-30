import asyncio
import logging
from typing import Final

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hbold

from hpc_bot.exceptions import ExistChatError, NoExistChatError
from hpc_bot.metrics import start_tracking
from hpc_bot.model.inference import ModelInference
from hpc_bot.settings import BOT_TOKEN
from hpc_bot.telegram.cache import ConversationCache
from hpc_bot.telegram.manager import ModelManager
from hpc_bot.telegram.messages import (
    CONFUSED_TEXT,
    EXIST_CHAT_TEXT,
    HELLO_TEXT,
    HELP_TEXT,
    NO_EXIST_CHAT_TEXT,
    RESET_CHAT_TEXT,
    TO_HARD_TEXT,
)

TOKEN: Final[str] = BOT_TOKEN

dp: Dispatcher = Dispatcher()

CACHE: Final[ConversationCache] = ConversationCache()
manager: ModelManager = ModelManager(
    inference=ModelInference(),
    cache=CACHE
)

_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    Начать взаимодействие с ботом `/start` командой
    :param message: сообщение от пользователя
    :return:
    """
    try:
        await manager.start_conversion(message.chat.id, message.from_user.username)
    except ExistChatError:
        await message.answer(EXIST_CHAT_TEXT)
    else:
        await message.answer(HELLO_TEXT.format(username=hbold(message.from_user.full_name)))


@dp.message(Command('reset_context'))
async def command_clean_context(message: types.Message) -> None:
    """
    Очистить весь контекст переписки с ботом
    :param message: сообщение от пользователя
    :return:
    """
    await manager.reset_context(message.chat.id)
    await message.answer(RESET_CHAT_TEXT)


@dp.message(Command('help'))
async def command_help_handler(message: types.Message) -> None:
    """
    Вернуть подсказку для общения с ботом
    :param message: сообщение от пользователя
    :return:
    """
    await message.answer(HELP_TEXT)


@dp.message()
async def conversation_handler(message: types.Message) -> None:
    """
    Задать вопрос LLM модели.
    :param message: сообщение от пользователя
    :return:
    """
    try:
        model_answer: str = await manager.answer(message.chat.id, message.text)
        await message.answer(model_answer)
    except RuntimeError:
        await message.answer(TO_HARD_TEXT)
    except NoExistChatError:
        await message.answer(NO_EXIST_CHAT_TEXT)
    except Exception as e:
        await message.answer(CONFUSED_TEXT)
        _LOGGER.exception(e)


async def main() -> None:
    """
    Запуск бота и его метрик.
    :param:
    :return:
    """
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    start_tracking(loop, CACHE)

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)
