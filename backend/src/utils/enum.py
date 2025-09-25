from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic_core import core_schema


class EnhancedEnum(Enum):
    """
    集成 pydantic，序列化/反序列化时是以 enum 的 name 值作为标准
    """

    _value_: str

    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:
        return name

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        def serialize_enum(instance: EnhancedEnum) -> str:
            return instance.name

        def validate_enum(value: Any) -> EnhancedEnum:
            if isinstance(value, cls):
                return value
            elif isinstance(value, str):
                try:
                    return cls[value]
                except KeyError:
                    raise ValueError(f"'{value}' is not a valid {cls.__name__}")
            else:
                raise ValueError(f'Expected string or {cls.__name__}, got {type(value)}')

        python_schema = core_schema.with_info_plain_validator_function(lambda value, _: validate_enum(value))

        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema([core_schema.str_schema(), python_schema]),
            python_schema=python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_enum,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def dict(cls) -> dict[str, str]:
        return {name: member.value for name, member in cls.__members__.items()}

    @classmethod
    def list(cls) -> list[tuple[str, str]]:
        return [(name, member.value) for name, member in cls.__members__.items()]

    @property
    def lower_name(self) -> str:
        return self.name.lower()

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, EnhancedEnum):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return False

    def __hash__(self) -> int:
        return hash(self.name)
