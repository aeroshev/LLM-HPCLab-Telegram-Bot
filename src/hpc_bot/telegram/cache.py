import os

import redis.asyncio as redis

from hpc_bot.model.conversion import Message
from hpc_bot.singleton import Singleton


class ConversationCache(metaclass=Singleton):
    """
    Кэш для хранения переписок с моделью
    """
    KEY_PATTERN: str = 'conversation:{chat_id}'
    USER_CHAT: str = 'active_chats_users'

    __slots__ = ('cache',)

    def __init__(self) -> None:
        cache_host: str = os.environ.get('CACHE_ADDRESS', 'localhost')
        self.cache = redis.Redis(host=cache_host, port=6379, decode_responses=True)

    async def start_conversation(self, chat_id: int, username: str) -> None:
        """
        Создать ключ переписки с указанием username пользователя.
        :param chat_id: индефикатор чата в Telegram.
        :param username: логин пользователя.
        :param message: сообщение заданного формата.
        :return:
        """
        await self.cache.hset(
            self.USER_CHAT,
            str(chat_id),
            username
        )

    async def put_message(self, chat_id: int, message: Message) -> None:

        """
        Положить новое сообщение в кэш.
        :param chat_id: индефикатор чата в Telegram.
        :param message: сообщение заданного формата.
        :return:
        """
        await self.cache.rpush(
            self.KEY_PATTERN.format(chat_id=chat_id),
            message.model_dump_json()
        )

    async def clear_conversion(self, chat_id: int) -> None:
        """
        Сбросить переписку с ботом
        :param chat_id: индефикатор чата в Telegram
        :return:
        """
        await self.cache.delete(self.KEY_PATTERN.format(chat_id=chat_id))

    async def pop_first_message(self, chat_id: int) -> None:
        """
        Выбросить первое сообщение из переписки
        :param chat_id: индефикатор чата в Telegram
        :return:
        """
        await self.cache.lpop(self.KEY_PATTERN.format(chat_id=chat_id))

    async def get_correspondence(self, chat_id: int) -> list[Message]:
        """
        Получить всю переписку конркетного чата
        :param chat_id: индефикатор чата в Telegram
        :return: список всех сообщений
        """
        messages: list[str] = await self.cache.lrange(
            self.KEY_PATTERN.format(chat_id=chat_id),
            0,
            -1
        )
        return [
            Message.model_validate_json(message)
            for message in messages
        ]

    async def metric_depth_correspondence(self, chat_id: int) -> int:
        """
        Получить глубину переписки
        :param chat_id: индефикатор чата в Telegram
        :return: глубина переписки
        """
        return await self.cache.llen(self.KEY_PATTERN.format(chat_id=chat_id))

    async def metric_chat_counts(self) -> int:
        """
        Получить количество текущих чатов
        :param:
        :return: количество активных чатов
        """
        return await self.cache.hlen(self.USER_CHAT)

    async def get_actual_chats(self) -> list[str]:
        """
        Получить все актуальные чаты.
        :param:
        :return: индефикаторы актуальных чатов.
        """
        return await self.cache.hkeys(self.USER_CHAT)

    async def exist_chat(self, chat_id: int) -> bool:
        """
        Проверить, существует ли данный чат.
        :param chat_id: индефикатор чата в Telegram.
        :return: существует или не существует выбранный чат.
        """
        username: str | None = await self.cache.hget(self.USER_CHAT, str(chat_id))
        return True if username else False
