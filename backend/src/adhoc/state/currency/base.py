from __future__ import annotations

from typing import Any


class Currency:
    def __init__(self, name: str, value: int = 0, denominator: int = 1, precision: int = 0):
        """
        货币类，内部永远用 int 存储，用 denominator 和 denominator 来控制实际显示的值
        denominator 表示实际的值应该为 1 / denominator
        precision 表示在计算后应当保留几位小数，0 即为整数，代码没有保证对于任意长度都是正确的

        denominator 和 precision 只在传给前端显示时有用，内部全是 int，支持的各类计算也只会关注 value

        """
        self._value = value
        self._name = name
        self._denominator = denominator
        self._precision = precision

    def desc(self) -> dict[str, Any]:
        return {
            'value': self._value,
            'denominator': self._denominator,
            'precision': self._precision,
        }

    def __add__(self, other: Any) -> Currency:
        if isinstance(other, Currency):
            return Currency(self._name, self._value + other._value, self._denominator, self._precision)
        elif isinstance(other, int):
            return Currency(self._name, self._value + other, self._denominator, self._precision)
        else:
            return NotImplemented

    def __radd__(self, other: Any) -> Currency:
        if isinstance(other, int):
            return Currency(self._name, self._value + other, self._denominator, self._precision)
        else:
            return NotImplemented

    def __sub__(self, other: Any) -> Currency:
        if isinstance(other, Currency):
            return Currency(self._name, self._value - other._value, self._denominator, self._precision)
        elif isinstance(other, int):
            return Currency(self._name, self._value - other, self._denominator, self._precision)
        else:
            return NotImplemented

    def __rsub__(self, other: Any) -> Currency:
        if isinstance(other, int):
            return Currency(self._name, other - self._value, self._denominator, self._precision)
        else:
            return NotImplemented

    def __mul__(self, other: Any) -> Currency:
        """支持 Currency * Currency 和 Currency * int"""
        if isinstance(other, Currency):
            return Currency(self._name, self._value * other._value, self._denominator, self._precision)
        elif isinstance(other, int):
            return Currency(self._name, self._value * other, self._denominator, self._precision)
        else:
            return NotImplemented

    def __rmul__(self, other: Any) -> Currency:
        if isinstance(other, int):
            return Currency(self._name, self._value * other, self._denominator, self._precision)
        else:
            return NotImplemented

    def __str__(self) -> str:
        """字符串表示"""
        return f'{self._name}: {self._value}'

    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"Currency(name='{self._name}', value={self._value}, denominator={self._denominator}, precision={self._precision})"

    @property
    def value(self) -> int:
        return self._value

    @property
    def type(self) -> str:
        return self._name
