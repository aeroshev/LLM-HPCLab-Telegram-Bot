from typing import Final

HELLO_TEXT: Final[str] = "Привествую, {username}!\nЭто телеграм бот лаборатории HPCLab для общения с моделью LlaMa"  # noqa

CONFUSED_TEXT: Final[str] = "Извини, не понял тебя"

HELP_TEXT: Final[str] = "Я телеграмм бот LLM модели Llama 7B лаборатории HPC НИЯУ МИФИ.\nПросто напиши в чат, чтобы общаться со мной.\n/start - начать общение со мной.\n/reset_context - сбросить историю переписок со мной.\n/help - вызвать подсказку."  # noqa

TO_HARD_TEXT: Final[str] = "Это слишком сложный запрос для меня, спроси что-нибудь другое"

RESET_CHAT_TEXT: Final[str] = "Я всё забыл о чём говорили раньше. Начнём с чистого листа"

EXIST_CHAT_TEXT: Final[str] = "У нас с тобой уже есть история переписки, если хочешь начать заново, выбери команду /reset_context"  # noqa

NO_EXIST_CHAT_TEXT: Final[str] = "Похоже мы ещё не начали диалог, отправь команду /start, чтобы начать общение со мной"  # noqa
