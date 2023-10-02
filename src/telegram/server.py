import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

import settings
from model.inference import ModelInference, CONVERSION_CACHE

# Bot token can be obtained via https://t.me/BotFather
TOKEN = settings.BOT_TOKEN

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
inference = ModelInference()

_LOGGER = logging.getLogger(__name__)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Привествую, {hbold(message.from_user.full_name)}!\n" \
                         "Это телеграм бот лаборатории HPCLab для общения с моделью LlaMa")


@dp.message(Command('clean_context'))
async def command_clean_context(message: Message) -> None:
    del CONVERSION_CACHE[message.chat_id]


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        model_answer = inference(message.text, message.chat.id)
        await message.answer(model_answer)
    except Exception as e:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Извини, не понял тебя")
        _LOGGER.exception(e)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)
