from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from torch.cuda import OutOfMemoryError

from hpc_bot.exceptions import ExistChatError, NoExistChatError
from hpc_bot.model.conversion import DEFAULT_SYSTEM_PROMPT, Conversation, Message, Role
from hpc_bot.telegram.manager import ModelManager


@pytest.fixture(scope='module')
def mock_manager() -> ModelManager:
    return ModelManager(
        inference=MagicMock(name='mock-inference'),
        cache=AsyncMock(name='mock-cache')
    )


def test_start_message(mock_manager: ModelManager) -> None:
    start_message: Message = Message(
        role=Role.SYSTEM,
        content=DEFAULT_SYSTEM_PROMPT
    )
    assert mock_manager.start_message == start_message


def test_clean_mem(mock_manager: ModelManager) -> None:
    with patch('gc.collect') as mock_gc, patch('torch.cuda.empty_cache') as mock_cuda:
        mock_manager.clean_mem()
        assert mock_gc.called
        assert mock_cuda.called


@pytest.mark.asyncio
async def test_start_conversation(mock_manager: ModelManager) -> None:
    chat_id: int = 1
    username: str = 'John'

    mock_manager.cache.exist_chat.return_value = True
    with pytest.raises(ExistChatError):
        await mock_manager.start_conversion(chat_id, username)

    mock_manager.cache.exist_chat.return_value = False
    await mock_manager.start_conversion(chat_id, username)
    assert mock_manager.cache.start_conversation.called


@pytest.mark.asyncio
async def test_compress_conversation(mock_manager: ModelManager) -> None:
    message: str = 'Hello, world!'
    chat_id: int = 1
    conversation: Conversation = Conversation(messages=[Message(role=Role.USER, content=message)])

    with pytest.raises(RuntimeError):
        await mock_manager.compress_conversation(conversation, chat_id)

    conversation = Conversation(messages=[
        Message(role=Role.USER, content=message),
        Message(role=Role.BOT, content=message),
        Message(role=Role.USER, content=message),
        Message(role=Role.BOT, content=message),
    ])
    await mock_manager.compress_conversation(conversation, chat_id)
    assert len(conversation) == 3

    conversation = Conversation(messages=[
        Message(role=Role.USER, content=message),
        Message(role=Role.BOT, content=message),
        Message(role=Role.USER, content=message),
        Message(role=Role.BOT, content=message),
    ])
    await mock_manager.compress_conversation(conversation, chat_id, len(message * 2))
    assert len(conversation) == 2


@pytest.mark.asyncio
async def test_answer(mock_manager: ModelManager) -> None:
    chat_id: int = 1
    message: str = 'Hello, world!'
    original: str = 'Hello, You!'

    # Успешный сценарий
    mock_manager.cache.exist_chat.return_value = True
    mock_manager.cache.get_correspondence.return_value = []
    mock_manager.inference.return_value = original
    output: str = await mock_manager.answer(chat_id, message)
    assert output == original

    # Случай когда чата ещё нет
    mock_manager.cache.exist_chat.return_value = False
    with pytest.raises(NoExistChatError):
        await mock_manager.answer(chat_id, message)
    mock_manager.cache.exist_chat.return_value = True

    # Обработка переполнения в рантайме
    # один раз
    mock_manager.inference.side_effect = [OutOfMemoryError(), original]
    mock_manager.cache.get_correspondence.return_value = [
        Message(role=Role.USER, content=message),
        Message(role=Role.BOT, content=message)
    ]
    output = await mock_manager.answer(chat_id, message * 275)
    assert output == original
    assert mock_manager.cache.pop_first_message.called
    # два раза
    mock_manager.cache.pop_first_message.reset_mock(return_value=True, side_effect=True)
    mock_manager.inference.side_effect = [OutOfMemoryError(), OutOfMemoryError(), original]
    mock_manager.cache.get_correspondence.return_value = [
        Message(role=Role.USER, content=message),
        Message(role=Role.BOT, content=message)
    ]
    output = await mock_manager.answer(chat_id, message * 275)
    assert output == original
    assert mock_manager.cache.pop_first_message.call_count == 2

    # Обработка когда после очистки осталось только системное сообщение
    with pytest.raises(RuntimeError):
        await mock_manager.answer(chat_id, message * 300)
        assert mock_manager.pop_first_message.called

    # Обработка предварительного сжатия
    mock_manager.inference.reset_mock(return_value=True, side_effect=True)
    mock_manager.inference.return_value = original
    mock_manager.cache.get_correspondence.return_value = [
        Message(role=Role.USER, content=message * 500),
        Message(role=Role.BOT, content=message)
    ]
    output = await mock_manager.answer(chat_id, message)
    assert output == original
    assert mock_manager.cache.pop_first_message.called

    # Обработка внезапной ощибки
    mock_manager.inference.side_effect = Exception('test exception')
    with pytest.raises(Exception):
        await mock_manager.answer(chat_id, message)


@pytest.mark.asyncio
async def test_reset_context(mock_manager: ModelManager) -> None:
    chat_id: int = 1

    await mock_manager.reset_context(chat_id)
    assert mock_manager.cache.clear_conversion.called
