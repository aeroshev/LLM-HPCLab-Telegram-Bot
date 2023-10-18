from exceptions import ExistChatError, NotExistChatError
from model.conversion import DEFAULT_SYSTEM_PROMPT, Conversation, Message, Role
from model.inference import ModelInference
from telegram.cache import ConversionCache


class ModelManager:
    """
    Менеджер для управления сообщениями для модели
    """

    __slots__ = (
        'inference',
        'cache'
    )

    def __init__(
        self,
        inference: ModelInference,
        cache: ConversionCache
    ) -> None:
        self.inference: ModelInference = inference
        self.cache: ConversionCache = cache

    async def start_conversion(self, chat_id: int, username: str) -> None:
        """
        Начать переписку с ботом положив создав ключ
        и положив туда системный промпт.
        :param chat_id: индефикатор чата, для различия пользователей.
        :param username: логин пользователя.
        :return:
        """
        exist: bool = await self.cache.exist_chat(chat_id)
        if exist:
            raise ExistChatError()

        message: Message = Message(
            role=Role.SYSTEM,
            content=DEFAULT_SYSTEM_PROMPT
        )
        await self.cache.start_conversation(chat_id, username, message)

    async def answer(self, chat_id: int, message: str) -> str:
        """
        Получить ответ от модели.
        :param chat_id: индефикатор чата, для различия пользователей.
        :param message: сообщение от пользователя.
        :return: сообщение от модели.
        """
        messages: list[Message] = await self.cache.get_correspondence(chat_id)
        if len(messages) < 1:
            raise NotExistChatError()

        user_message: Message = Message(role=Role.USER, content=message)
        messages.append(user_message)
        await self.cache.put_message(chat_id, user_message)

        conversation: Conversation = Conversation(messages=messages)
        output: str = self.inference(conversation)

        bot_message: Message = Message(role=Role.BOT, content=output)
        await self.cache.put_message(chat_id, bot_message)

        return output

    async def reset_context(self, chat_id: int, username: str) -> None:
        """
        Очистить переписку с моделью.
        :param chat_id: индефикатор чата, для различия пользователей.
        :return:
        """
        await self.cache.clear_conversion(chat_id)
        await self.start_conversion(chat_id, username)
