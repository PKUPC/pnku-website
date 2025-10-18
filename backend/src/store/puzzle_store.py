from enum import auto
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src import utils

from . import Table


class PuzzleType(utils.EnhancedEnum):
    NORMAL = auto()
    # PUBLIC 类型题目允许未组队玩家验证答案，只能做简单验证
    PUBLIC = auto()


class PuzzleMetadataModel(BaseModel):
    type: PuzzleType = Field(default=PuzzleType.NORMAL)
    authors: list[str] = Field(default_factory=list)
    story_before: str | None = Field(default=None)
    story_after: str | None = Field(default=None)
    solution: str | None = Field(default=None)


class MediaActionModel(BaseModel):
    name: str
    type: Literal['media']
    media_url: str


class WebpageActionModel(BaseModel):
    name: str
    type: Literal['webpage']
    url: str


class TriggerModel(BaseModel):
    type: str
    value: str
    info: str


class ClipboardModel(BaseModel):
    type: Literal['tencent-html', 'google-html', 'text']
    content: str


class PuzzleStoreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    MAX_TRIGGER_LEN: int = 20

    id: int
    key: str
    slug: str
    title: str
    category: str
    subcategory: str
    sorting_index: int
    errata_template: str
    content_template: str
    clipboard: list[ClipboardModel]
    puzzle_metadata: PuzzleMetadataModel
    actions: list[MediaActionModel | WebpageActionModel]
    triggers: list[TriggerModel]

    @classmethod
    def check_submitted_word(cls, word: str) -> tuple[str, str] | None:
        if len(word) > cls.MAX_TRIGGER_LEN:
            return 'ANSWER_LEN', '提交的答案过长'
        return None

    def describe_actions(self) -> list[dict[str, Any]]:
        rst = []
        for action in self.actions:
            match action:
                case MediaActionModel():
                    rst.append(
                        {
                            'type': action.type,
                            'name': action.name,
                            'media_url': utils.media_wrapper(action.media_url),
                        }
                    )
                case WebpageActionModel():
                    rst.append(
                        {
                            'type': action.type,
                            'name': action.name,
                            'url': action.url,
                        }
                    )
        return rst


class PuzzleStore(Table):
    __tablename__ = 'puzzle'

    key: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(128), nullable=False, default='normal')
    sorting_index: Mapped[int] = mapped_column(Integer, nullable=False)
    errata_template: Mapped[str] = mapped_column(Text, nullable=False)
    content_template: Mapped[str] = mapped_column(Text, nullable=False)
    # 游戏的一些元信息，包括作者、游戏特殊设置等等
    puzzle_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    actions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    # 用户输入后会起作用的词，可以用来实现里程碑功能
    triggers: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)

    # 剪切板信息
    clipboard: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=False)

    METADATA_SNIPPET = """{"author": "Anonymous", "type": "normal"}"""

    TRIGGER_SNIPPETS = {
        'answer': """{"type": "answer", "value" : "", "info": "答案正确"}""",
        'milestone': """{"type": "milestone", "value" : "", "info": "这里是额外的提示信息"}""",
        # 一拍脑袋随便加的，放在这里又有什么关系呢（
        'surprise': """{"type": "surprise", "value" : "", "info": "虽然和答案没什么关系，但是恭喜你发现彩蛋！"}""",
    }

    ACTION_SNIPPETS = {
        'webpage': """{"name": "题目网页", "type": "webpage", "url" : "https://puzzleXX.pkupuzzle.art"}""",
        'media': """{"name": "题目附件", "type": "media", "media_url" : "填写 media 的链接"}""",
    }

    def validated_model(self) -> PuzzleStoreModel:
        """
        return pydantic 验证后的 model，可能会抛异常，需要处理。
        """
        return PuzzleStoreModel.model_validate(self)

    def validate(self) -> tuple[bool, ValidationError | None]:
        try:
            _model = PuzzleStoreModel.model_validate(self)
        except ValidationError as e:
            return False, e
        return True, None
