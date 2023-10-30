class ExistChatError(Exception):
    """
    Ошибка уже существующего чата
    """
    ...


class NoExistChatError(Exception):
    """
    Ошибка несуществующего чата
    """
    ...
