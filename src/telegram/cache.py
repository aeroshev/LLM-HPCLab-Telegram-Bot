import os

import redis.asyncio as redis

from model.conversion import Message


class ConversionCache:
    """
    Кэш для хранения переписок с моделью
    """
    __slots__ = ('cache',)

    def __init__(self) -> None:
        cache_host: str = os.environ.get('CACHE_ADDRESS', 'localhost')
        self.cache = redis.Redis(host=cache_host, port=6379, decode_responses=True)
    
    async def put_message(self, chat_id: int, message: Message) -> None:

        """
        Положить новое сообщение в кэш
        :param chat_id: индефикатор чата в Telegram
        :return:
        """
        await self.cache.rpush(
            f'conversation:{chat_id}',
            message.model_dump_json()
        )

    async def clear_conversion(self, chat_id: int) -> None:
        """
        Сбросить переписку с ботом
        :param chat_id: индефикатор чата в Telegram
        :return:
        """
        await self.cache.delete(f'conversation:{chat_id}')
    
    async def get_correspondence(self, chat_id: int) -> list[Message]:
        """
        Получить всю переписку конркетного чата
        :param chat_id: индефикатор чата в Telegram
        :return: список всех сообщений
        """
        messages: list[str] = await self.cache.lrange(
            f'conversation:{chat_id}',
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
        return await self.cache.llen(f'conversation:{chat_id}')

    async def metric_chat_counts(self) -> int:
        """
        Получить количество текущих чатов
        :param:
        :return: количество активных чатов
        """
        return len([
            key
            async for key in self.cache.scan_iter('conversation:*')
        ])
    
    async def get_actual_chats(self) -> list[str]:
        """
        Получить все актуальные чаты.
        :param:
        :return: индефикаторы актуальных чатов.
        """
        return [
            key.split(':')[1]
            async for key in self.cache.scan_iter('conversation:*')
        ]

    async def exist_chat(self, chat_id: int) -> bool:
        """
        Проверить, существует ли данный чат.
        :param chat_id: индефикатор чата в Telegram.
        :return: существует или не существует выбранный чат.
        """
        quantity: int = await self.cache.exists(f"conversation:{chat_id}")
        return True if quantity > 0 else False
