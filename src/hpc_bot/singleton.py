class Singleton(type):
    """
    Метакласс для создания классов по паттерну одиночка
    """
    _instances: dict[str, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
