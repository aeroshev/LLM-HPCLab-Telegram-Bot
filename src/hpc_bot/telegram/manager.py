import gc
import logging
from typing import Final

import torch

from hpc_bot.exceptions import ExistChatError, NoExistChatError
from hpc_bot.model.conversion import DEFAULT_SYSTEM_PROMPT, Conversation, Message, Role
from hpc_bot.model.inference import ModelInference
from hpc_bot.telegram.cache import ConversationCache

_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


class ModelManager:
    """
    Менеджер для управления сообщениями для модели
    """

    __slots__ = (
        '_inference',
        '_cache'
    )

    def __init__(
        self,
        inference: ModelInference,
        cache: ConversationCache
    ) -> None:
        self._inference: ModelInference = inference
        self._cache: ConversationCache = cache

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
            await self._cache.pop_first_message(chat_id)
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
        exist: bool = await self._cache.exist_chat(chat_id)
        if exist:
            raise ExistChatError()

        await self._cache.start_conversation(chat_id, username)

    async def slide_window_asnwer(self, conversation: Conversation, chat_id: int) -> str:
        """
        Задать вопрос модели в режиме скользящего окна. Если память переполнилась, то старые сообщения будут вытесняться.
        :param conversation: переписка с пользователем.
        :param chat_id: индефикатор чата пользователя.
        :return: ответ модели.
        """
        while True:
            try:
                output: str = self._inference(conversation)
                break
            except torch.cuda.OutOfMemoryError:
                _LOGGER.warning(
                    f"Закончилась память, длина контекста - {conversation.size}, чат - {chat_id}"
                )
                await self.compress_conversation(conversation, chat_id)
            except Exception as e:
                _LOGGER.exception(e)
                raise e
            finally:
                self.clean_mem()

        return output

    async def inline_answer(self, conversation: Conversation, chat_id: int) -> str:
        """
        Задать вопрос модели в линейном режиме. Если память переполнилась, то сообщить об этом пользователю.
        :param conversation: переписка с пользователем.
        :param chat_id: индефикатор чата пользователя.
        :return: ответ модели.
        """
        try:
            output: str = self._inference(conversation)
        except torch.cuda.OutOfMemoryError as e:
            _LOGGER.warning(
                f"Закончилась память, длина контекста - {conversation.size}, чат - {chat_id}"
            )
            raise e
        except Exception as e:
            _LOGGER.exception(e)
            raise e
        finally:
            self.clean_mem()

        return output

    async def answer(self, chat_id: int, message: str, state: str) -> str:
        """
        Получить ответ от модели.
        :param chat_id: индефикатор чата, для различия пользователей.
        :param message: сообщение от пользователя.
        :return: сообщение от модели.
        """
        exist: bool = await self._cache.exist_chat(chat_id)
        if not exist:
            raise NoExistChatError()

        messages: list[Message] = [self.start_message]
        messages += await self._cache.get_correspondence(chat_id)

        user_message: Message = Message(role=Role.USER, content=message)
        messages.append(user_message)
        await self._cache.put_message(chat_id, user_message)

        conversation: Conversation = Conversation(messages=messages)

        if state == 'UserMode:window':
            output: str = await self.slide_window_asnwer(conversation, chat_id)
        elif state == 'UserMode:inline':
            output: str = await self.inline_answer(conversation, chat_id)
        else:
            raise RuntimeError("Can't determine state")

        bot_message: Message = Message(role=Role.BOT, content=output)
        await self._cache.put_message(chat_id, bot_message)

        return output

    async def reset_context(self, chat_id: int) -> None:
        """
        Очистить переписку с моделью.
        :param chat_id: индефикатор чата, для различия пользователей.
        :return:
        """
        await self._cache.clear_conversion(chat_id)
