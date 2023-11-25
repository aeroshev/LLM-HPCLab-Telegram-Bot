import logging
from typing import Final

import torch
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from hpc_bot.exceptions import NoExistChatError
from hpc_bot.telegram.manager import ModelManager
from hpc_bot.telegram.messages import (
    CONFUSED_TEXT,
    NO_EXIST_CHAT_TEXT,
    NO_STATE_TEXT,
    OUT_MEMORY_ERROR_TEXT,
    TO_HARD_TEXT,
)

_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

common_router: Router = Router(name='common_router')


@common_router.message()
async def conversation_handler(message: Message, manager: ModelManager, state: FSMContext) -> None:
    """
    Задать вопрос LLM модели.
    :param message: сообщение от пользователя.
    :param manager: менеджер управления инференсом модели.
    :param state: состояние конечного автомата пользователя.
    :return:
    """
    state: str = await state.get_state()
    if not state:
        await message.answer(NO_STATE_TEXT)
        return

    try:
        model_answer: str = await manager.answer(message.chat.id, message.text, state)
        await message.answer(model_answer)
    except torch.cuda.OutOfMemoryError:
        await message.answer(OUT_MEMORY_ERROR_TEXT)
    except RuntimeError:
        await message.answer(TO_HARD_TEXT)
    except NoExistChatError:
        await message.answer(NO_EXIST_CHAT_TEXT)
    except Exception as e:
        await message.answer(CONFUSED_TEXT)
        _LOGGER.exception(e)
