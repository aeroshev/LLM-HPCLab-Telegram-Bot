import asyncio

from prometheus_client import Gauge, Summary

from telegram.cache import ConversionCache

DEPTH_CONVERSION: Gauge = Gauge('depth_conversion', 'Глубина чата с пользователем', ['chat_id'])
CHAT_COUNTS: Gauge = Gauge('quantity_chats', 'Количество открытых чатов')
REQUEST_TIME: Summary = Summary('request_processing_seconds', 'Время выполнения запроса')


async def depth_conversion_track(cache: ConversionCache, sleep_time: int = 5) -> None:
    """
    Проставить в метрике глубину каждого чата.
    :param cache: кэш откуда брать информацию о записях.
    :param sleep_time: интервал с которым следует обновлять информацию.
    :return:
    """
    while True:
        running_chats: list[str] = await cache.get_actual_chats()
        for chat in running_chats:
            depth: int = await cache.metric_depth_correspondence(chat)
            DEPTH_CONVERSION.labels(chat).set(depth)
        await asyncio.sleep(sleep_time)


async def chat_counts_track(cache: ConversionCache, sleep_time: int = 5) -> None:
    """
    Проставить в метрике количество активных чатов.
    :param cache: кэш откуда брать информацию о записях.
    :param sleep_time: интервал с которым следует обновлять информацию.
    :return:
    """
    while True:
        chat_counts: int = await cache.metric_chat_counts()
        CHAT_COUNTS.set(chat_counts)
        await asyncio.sleep(sleep_time)
