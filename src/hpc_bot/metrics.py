import asyncio
from pathlib import Path

from prometheus_client import Gauge, Summary

from hpc_bot.telegram.cache import ConversationCache

DEPTH_CONVERSION: Gauge = Gauge('depth_conversion', 'Глубина чата с пользователем', ['chat_id'])
CHAT_COUNTS: Gauge = Gauge('quantity_chats', 'Количество открытых чатов')
REQUEST_TIME: Summary = Summary('request_processing_seconds', 'Время выполнения запроса')
WEIGHTS_SIZE: Gauge = Gauge('weights_size', 'Размер весов модели')

WEIGTHS_PATH: str = '/root/.cache'


def get_size(folder_path: str = '.') -> int:
    """
    Получить размер директории.
    :param folder_path: путь до директории.
    :return: размер директории в байтах.
    """
    return sum(
        file.stat().st_size
        for file in Path(folder_path).glob('**/*')
        if file.is_file()
    )


async def depth_conversion_track(cache: ConversationCache, sleep_time: int = 5) -> None:
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


async def chat_counts_track(cache: ConversationCache, sleep_time: int = 5) -> None:
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


async def weights_size_track(sleep_time: int = 5) -> None:
    """
    Отслеживать размер весов в volume.
    :param sleep_time: интервал с которым следует обновлять информацию.
    :return:
    """
    while True:
        WEIGHTS_SIZE.set(get_size(WEIGTHS_PATH))
        await asyncio.sleep(sleep_time)


def start_tracking(loop: asyncio.AbstractEventLoop, cache: ConversationCache, sleep_time: int = 5) -> None:
    """
    Начать отслеживание метрик.
    :param loop: событийный цикл в котором необходимо создать задачи отслеживания метрик.
    :param cache: кэш откуда брать информацию о записях.
    :param sleep_time: интервал с которым следует обновлять информацию.
    :return:
    """
    loop.create_task(depth_conversion_track(cache, sleep_time))
    loop.create_task(chat_counts_track(cache, sleep_time))
    loop.create_task(weights_size_track(sleep_time))
