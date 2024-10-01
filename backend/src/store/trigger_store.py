from sqlalchemy import Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from . import Table


class TriggerStore(Table):
    __tablename__ = 'trigger'

    tick: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    timestamp_s: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
