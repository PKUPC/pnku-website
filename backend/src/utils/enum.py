from enum import Enum


class EnumWrapper(Enum):
    @classmethod
    def dict(cls) -> dict[str, str]:
        return {name: member.value for name, member in cls.__members__.items()}

    @classmethod
    def list(cls) -> list[tuple[str, str]]:
        return [(name, member.value) for name, member in cls.__members__.items()]
