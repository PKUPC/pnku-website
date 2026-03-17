import base64
import re

from typing import Any

import bleach
import jinja2
import markdown

from bleach_allowlist import markdown_attrs, markdown_tags
from markdown.extensions import Extension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.md_in_html import MarkdownInHtmlExtension
from markdown.extensions.sane_lists import SaneListExtension
from markdown.extensions.tables import TableExtension
from markdown.postprocessors import Postprocessor

from .media import media_wrapper


class LinkTargetExtension(Extension):
    class LinkTargetProcessor(Postprocessor):
        EXT_LINK_RE = re.compile(r'<a href="(?!#)')  # only external links

        def run(self, text: str) -> str:
            return self.EXT_LINK_RE.sub('<a target="_blank" rel="noopener noreferrer" href="', text)

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.postprocessors.register(self.LinkTargetProcessor(), 'link-target-processor', 100)


markdown_processor = markdown.Markdown(
    extensions=[
        FencedCodeExtension(),
        CodeHiliteExtension(guess_lang=False, use_pygments=True, noclasses=True),
        MarkdownInHtmlExtension(),
        TableExtension(),
        SaneListExtension(),
        LinkTargetExtension(),
    ],
    output_format='html',
)


def b64encode_filter(s: Any, encoding: str = 'utf-8') -> str:
    data: bytes = b''
    if isinstance(s, str):
        data = s.encode(encoding)
    elif isinstance(s, bytes):
        data = s
    else:
        raise ValueError(f'Invalid type: {type(s)}')
    return base64.b64encode(data).decode('ascii')


def render_template(template_str: str, args: dict[str, Any]) -> str:
    # jinja2 to md
    env = jinja2.Environment(
        loader=jinja2.DictLoader({'index.md': template_str}),
        autoescape=True,
        auto_reload=False,
    )
    env.globals['media_wrapper'] = media_wrapper
    env.filters['b64encode'] = b64encode_filter
    md_str = env.get_template('index.md').render(**args)

    # md to str
    markdown_processor.reset()
    return markdown_processor.convert(md_str)


def set_link_attrs(attrs, new=False):  # type: ignore[no-untyped-def]
    attrs[(None, 'target')] = '_blank'
    attrs[(None, 'rel')] = 'noopener noreferrer'
    return attrs


def pure_render_template(template_str: str) -> str:
    # md to str
    markdown_processor.reset()
    md_html = markdown_processor.convert(template_str)
    clean_html = bleach.clean(md_html, markdown_tags, markdown_attrs)
    clean_html = bleach.linkify(clean_html, callbacks=[set_link_attrs])

    return clean_html
