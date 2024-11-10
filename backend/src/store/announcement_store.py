import time

from enum import Enum

from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .. import utils
from . import Table


class AnnouncementStore(Table):
    __tablename__ = 'announcement'

    class Category(Enum):
        GENERAL = '通用'

        @classmethod
        def name_list(cls) -> list[str]:
            return [x.name for x in cls]

        @classmethod
        def dict(cls) -> dict[str, str]:
            return {x.name: x.value for x in cls}

    publish_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(time.time()))
    sorting_index: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)
    category: Mapped[str] = mapped_column(String(128), nullable=False, default=Category.GENERAL.name)
    title: Mapped[int] = mapped_column(Text, nullable=False)
    content_template: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f'[@{utils.format_timestamp(self.publish_at)} {self.title}]'
