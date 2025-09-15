from datetime import datetime


class CreatedAtMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs["created_at"] = datetime.now()

        return super().__new__(cls, name, bases, attrs)


class MyClass(metaclass=CreatedAtMeta):
    def __init__(self, value):
        self.value = value


obj1 = MyClass("test")

print(f"Class create: {MyClass.created_at}")
