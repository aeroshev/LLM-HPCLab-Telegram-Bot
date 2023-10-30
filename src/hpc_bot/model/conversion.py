from enum import Enum
from typing import Final

from pydantic import BaseModel, ConfigDict

DEFAULT_MESSAGE_TEMPLATE: Final[str] = "<s>{role}\n{content}</s>\n"
DEFAULT_RESPONSE_TEMPLATE: Final[str] = "<s>bot\n"
DEFAULT_SYSTEM_PROMPT: Final[str] = "Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им. Отвечай кратко."  # noqa


class Role(str, Enum):
    """
    Роли в промпте модели.
    """
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

    def __len__(self) -> int:
        """
        Количество символов в сообщении.
        :param:
        :return: целое число символов.
        """
        return len(self.content)


class Conversation:
    """
    Класс диалога модели с пользователем.
    Формирует промт заранее опредлённого формата.
    """

    __slots__ = (
        'message_template',
        'response_template',
        'messages'
    )

    def __init__(
        self,
        message_template: str = DEFAULT_MESSAGE_TEMPLATE,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        response_template: str = DEFAULT_RESPONSE_TEMPLATE,
        messages: list[Message] | None = None
    ) -> None:
        self.message_template: str = message_template
        self.response_template: str = response_template
        if not messages:
            self.messages: list[Message] = [
                Message(
                    role=Role.SYSTEM,
                    content=system_prompt
                )
            ]
        else:
            self.messages = messages

    def pop_first_message(self) -> Message:
        """
        Выбросить первое сообщение из переписки.
        :param:
        :return: сообщение, которое было выброшено.
        """
        return self.messages.pop(1)

    def __len__(self) -> int:
        """
        Вернуить количество сообщений в переписке.
        :param:
        :return: целое число сообщений.
        """
        return len(self.messages)

    @property
    def size(self) -> int:
        """
        Вернуть количество символов в переписке.
        :param:
        :return: целое число символов.
        """
        return sum([len(msg) for msg in self.messages])

    def get_prompt(self) -> str:
        """
        Подготовить промт для модели Mistal.
        :param:
        :return: строка промпта.
        """
        final_text: str = ""
        for message in self.messages:  # type: Message
            message_text: str = self.message_template.format(**message.model_dump())
            final_text += message_text
        final_text += self.response_template
        return final_text.strip()
