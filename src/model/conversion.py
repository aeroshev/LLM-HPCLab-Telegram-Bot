from enum import Enum
from typing import Final

from pydantic import BaseModel, ConfigDict

DEFAULT_MESSAGE_TEMPLATE: Final[str] = "<s>{role}\n{content}</s>\n"
DEFAULT_SYSTEM_PROMPT: Final[str] = "Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им."  # noqa


class Role(str, Enum):
    SYSTEM = 'system'
    USER = 'user'
    BOT = 'bot'


class Message(BaseModel):
    """
    Класс сообщения пользователя или бота
    """
    model_config = ConfigDict(
        strict=True,
        extra='forbid'
    )

    role: Role
    content: str


class Conversation:
    """
    Класс диалога модели с пользователем.
    Формирует промт заранее опредлённого формата.
    """

    __slots__ = (
        'message_template',
        'start_token_id',
        'bot_token_id',
        'messages'
    )

    def __init__(
        self,
        message_template: str = DEFAULT_MESSAGE_TEMPLATE,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        start_token_id: int = 1,
        bot_token_id: int = 9225,
        messages: list[Message] | None = None
    ) -> None:
        self.message_template: str = message_template
        self.start_token_id: int = start_token_id
        self.bot_token_id: int = bot_token_id
        if not messages:
            self.messages: list[Message] = [
                Message(
                    role=Role.SYSTEM,
                    content=system_prompt
                )
            ]
        else:
            self.messages = messages

    def get_start_token_id(self) -> int:
        return self.start_token_id

    def get_bot_token_id(self) -> int:
        return self.bot_token_id

    def add_user_message(self, message: str) -> None:
        self.messages.append(
            Message(
                role=Role.USER,
                content=message
            )
        )

    def add_bot_message(self, message: str) -> None:
        self.messages.append(
            Message(
                role=Role.BOT,
                content=message
            )
        )

    def __len__(self) -> int:
        return len(self.messages)

    def get_prompt(self, tokenizer) -> str:
        final_text: str = ""
        for message in self.messages:  # type: dict[str, str]
            message_text: str = self.message_template.format(**message.model_dump())
            final_text += message_text
        final_text += tokenizer.decode([self.start_token_id, self.bot_token_id])
        return final_text.strip()
