import time
from typing import TYPE_CHECKING, Any

from sqlalchemy import Integer, String, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import Mapped, mapped_column

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from . import UserStore
from . import Table


class SubmissionStore(Table):
    __tablename__ = 'submission'

    MAX_FLAG_LEN = 128
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False, default=lambda: int(1000 * time.time()))
    # 提交者的 id，队伍信息会直接在对应的 State 中管理
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    puzzle_key: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(String(MAX_FLAG_LEN), nullable=False)
    # 一些随意添加的额外信息，突出一个灵活
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True, default=None)
