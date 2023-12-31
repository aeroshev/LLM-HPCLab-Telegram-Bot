from typing import Final

HELLO_TEXT: Final[str] = "Привествую, {username}!\nЭто телеграм бот лаборатории HPCLab для общения с моделью LlaMa"  # noqa

CONFUSED_TEXT: Final[str] = "Извини, не понял тебя"

HELP_TEXT: Final[str] = "Я телеграмм бот LLM модели Llama 7B лаборатории HPC НИЯУ МИФИ.\nПросто напиши в чат, чтобы общаться со мной.\n/start - начать общение со мной.\n/reset_context - сбросить историю переписок со мной.\n/help - вызвать подсказку.\n/inline - включить режим постоянного хранения переписки.\n/window - включить режим скользящего окна.\n/current_mode - показать текущий режим переписки."  # noqa

TO_HARD_TEXT: Final[str] = "Это слишком сложный запрос для меня, спроси что-нибудь другое"

RESET_CHAT_TEXT: Final[str] = "Я всё забыл о чём говорили раньше. Начнём с чистого листа"

EXIST_CHAT_TEXT: Final[str] = "У нас с тобой уже есть история переписки, если хочешь начать заново, выбери команду /reset_context"  # noqa

NO_EXIST_CHAT_TEXT: Final[str] = "Похоже мы ещё не начали диалог, отправь команду /start, чтобы начать общение со мной"  # noqa

INLINE_MODE_TEXT: Final[str] = "Включен режим постоянного контекста, старые записи не будут удаляться, но при достижении лимита памяти возможности писать ещё сообщения не будет"  # noqa

WINDOW_MODE_TEXT: Final[str] = "Включен режим скользящего окна, позволящий бесконечно общаться с ботом, но самые старые сообщения будет удалться по мере заполнения памяти"  # noqa

CURRENT_STATE_TEXT: Final[str] = "Сейчас включен режим {state}"

OUT_MEMORY_ERROR_TEXT: Final[str] = "У меня закончилась память, больше не могу отвечать, выбери режим window или сбрось контекст"  # noqa

NO_STATE_TEXT: Final[str] = "Не задан режим диалога, выбери один из режимов переписки"
