import gc
import logging

import torch

from hpc_bot.exceptions import ExistChatError, NoExistChatError
from hpc_bot.model.conversion import DEFAULT_SYSTEM_PROMPT, Conversation, Message, Role
from hpc_bot.model.inference import ModelInference
from hpc_bot.telegram.cache import ConversationCache

_LOGGER = logging.getLogger(__name__)


class ModelManager:
    """
    Менеджер для управления сообщениями для модели
    """

    __slots__ = (
        'inference',
        'cache'
    )

    def __init__(
        self,
        inference: ModelInference,
        cache: ConversationCache
    ) -> None:
        self.inference: ModelInference = inference
        self.cache: ConversationCache = cache

    @property
    def start_message(self) -> Message:
        """
        Стартовое сообщение для любого промпта.
        :param:
        :return:
        """
        return Message(
            role=Role.SYSTEM,
            content=DEFAULT_SYSTEM_PROMPT
        )

    @staticmethod
    def clean_mem() -> None:
        """
        Очистить память на девайсах.
        :param:
        :return:
        """
        gc.collect()
        torch.cuda.empty_cache()

    async def compress_conversation(
            self,
            conversation: Conversation,
            chat_id: int,
            max_size: int | None = None
    ) -> None:
        """
        Вытеснять первые сообщения из списка переписки.
        :param conversation: объект переписки.
        :param chat_id: индефикатор чата к которому относится переписка.
        :param max_size: предельное число символов.
                         Если не указывать, то будет выброшено только одно сообщение.
        """
        max_size = max_size or (conversation.size - 1)
        while conversation.size > max_size and len(conversation) > 1:
            await self.cache.pop_first_message(chat_id)
            conversation.pop_first_message()

        if len(conversation) < 2:
            raise RuntimeError("Can't operate message")

    async def start_conversion(self, chat_id: int, username: str) -> None:
        """
        Начать переписку с ботом положив создав ключ
        и положив туда системный промпт.
        :param chat_id: индефикатор чата, для различия пользователей.
        :param username: логин пользователя.
        :return:
        """
        exist: bool = await self.cache.exist_chat(chat_id)
        if exist:
            raise ExistChatError()

        await self.cache.start_conversation(chat_id, username)

    async def answer(self, chat_id: int, message: str) -> str:
        """
        Получить ответ от модели.
        :param chat_id: индефикатор чата, для различия пользователей.
        :param message: сообщение от пользователя.
        :return: сообщение от модели.
        """
        exist: bool = await self.cache.exist_chat(chat_id)
        if not exist:
            raise NoExistChatError()

        messages: list[Message] = [self.start_message]
        messages += await self.cache.get_correspondence(chat_id)

        user_message: Message = Message(role=Role.USER, content=message)
        messages.append(user_message)
        await self.cache.put_message(chat_id, user_message)

        conversation: Conversation = Conversation(messages=messages)

        run: bool = True
        while run:
            try:
                output: str = self.inference(conversation)
                run = False
            except torch.cuda.OutOfMemoryError:
                _LOGGER.warning(f"Закончилась память, длина контекста - {conversation.size}")
                await self.compress_conversation(conversation, chat_id)
            except Exception as e:
                _LOGGER.exception(e)
                raise e
            finally:
                self.clean_mem()

        bot_message: Message = Message(role=Role.BOT, content=output)
        await self.cache.put_message(chat_id, bot_message)

        return output

    async def reset_context(self, chat_id: int) -> None:
        """
        Очистить переписку с моделью.
        :param chat_id: индефикатор чата, для различия пользователей.
        :return:
        """
        await self.cache.clear_conversion(chat_id)
