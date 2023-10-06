from prometheus_client import Gauge, Summary, Info, Enum

DEPTH_CONVERSION: Gauge = Gauge('depth_conversion', 'Глубина чата с пользователем', ['chat_id'])
CHAT_COUNTS: Gauge = Gauge('quantity_chats', 'Количество открытых чатов')
REQUEST_TIME: Summary = Summary('request_processing_seconds', 'Время выполнения запроса')

# MODEL_INFO: Info = Info()
# STATUS: Enum = Enum('')
