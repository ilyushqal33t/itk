class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SimpleSingleton(metaclass=SingletonMeta):
    def __init__(self, name: str = "default"):
        self.name = name
        print(f"Создан SimpleSingleton с именем: {name}")
