import logging
import asyncio
from typing import Final

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold

import settings
from model.inference import ModelInference
from telegram.cache import ConversionCache
from telegram.manager import ModelManager
from exceptions import ExistChatError, NotExistChatError
from metrics import depth_conversion_track, chat_counts_track

TOKEN: Final[str] = settings.BOT_TOKEN

dp: Dispatcher = Dispatcher()

CACHE: Final[ConversionCache] = ConversionCache()
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
        await manager.start_conversion(message.chat.id)
    except ExistChatError:
        await message.answer("У нас с тобой уже есть история переписки, если хочешь начать заново," \
                             " выбери команду /reset_context")
    else:
        await message.answer(f"Привествую, {hbold(message.from_user.full_name)}!\n" \
                            "Это телеграм бот лаборатории HPCLab для общения с моделью LlaMa")


@dp.message(Command('reset_context'))
async def command_clean_context(message: types.Message) -> None:
    """
    Очистить весь контекст переписки с ботом
    :param message: сообщение от пользователя
    :return:
    """
    await manager.reset_context(message.chat.id)


@dp.message(Command('help'))
async def command_help_handler(message: types.Message) -> None:
    """
    Вернуть подсказку для общения с ботом
    :param message: сообщение от пользователя
    :return:
    """
    await message.answer(
        '''
        Я телеграмм бот LLM модели Llama 7B лаборатории HPC НИЯУ МИФИ.
        Просто напиши в чат, чтобы общаться со мной.
        /start - начать общение со мной.
        /reset_context - сбросить историю переписок со мной.
        /help - вызвать подсказку.
        '''
    )


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
    except NotExistChatError:
        await message.answer("Похоже мы не начали общение, введи команду /start для старта переписки")
    except Exception as e:
        await message.answer("Извини, не понял тебя")
        _LOGGER.exception(e)


async def main() -> None:
    """
    Запуск бота и его метрик.
    :param:
    :return:
    """
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    loop.create_task(depth_conversion_track(CACHE))
    loop.create_task(chat_counts_track(CACHE))

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)
