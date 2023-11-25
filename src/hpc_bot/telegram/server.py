import asyncio
import os
from typing import Final

import redis.asyncio as redis
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy

from hpc_bot.metrics import start_tracking
from hpc_bot.model.inference import ModelInference
from hpc_bot.settings import BOT_TOKEN
from hpc_bot.telegram.cache import ConversationCache
from hpc_bot.telegram.command_hadlers import command_router
from hpc_bot.telegram.common_handlers import common_router
from hpc_bot.telegram.manager import ModelManager

TOKEN: Final[str] = BOT_TOKEN


async def main() -> None:
    """
    Запуск бота и его метрик.
    :param:
    :return:
    """
    dp: Final[Dispatcher] = Dispatcher(
        storage=RedisStorage(
            redis=redis.Redis(
                host=os.environ.get('CACHE_ADDRESS', 'localhost'),
                port=6379,
                decode_responses=True
            )
        ),
        fsm_strategy=FSMStrategy.USER_IN_CHAT,
        manager=ModelManager(
            inference=ModelInference(),
            cache=ConversationCache()
        )
    )
    dp.include_routers(command_router, common_router)

    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    start_tracking(loop, ConversationCache())

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)
