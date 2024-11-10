import re

from typing import Any, Dict

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


# class AddLinkToImgExtension(Extension):
#     IMG_PATTERN = r'<img\s+[^>]*src="([^"]+)"[^>]*>'
#
#     class AddLinkToImgProcessor(InlineProcessor):
#         def handleMatch(self, m: Match[str], data: Any) -> tuple[Element, int, int] | tuple[None, None, None]:
#             el = Element("a")
#             el.attrib["href"] = m.groups()[0]
#             el.text = m.group()
#             return el, m.start(0), m.end(0)
#
#     def extendMarkdown(self, md: markdown.Markdown) -> None:
#         md.inlinePatterns.register(self.AddLinkToImgProcessor(AddLinkToImgExtension.IMG_PATTERN, md),
#                                    'add-link-to-img-processor', 100)


markdown_processor = markdown.Markdown(
    extensions=[
        FencedCodeExtension(),
        CodeHiliteExtension(guess_lang=False, use_pygments=True, noclasses=True),
        MarkdownInHtmlExtension(),
        TableExtension(),
        SaneListExtension(),
        LinkTargetExtension(),
        # AddLinkToImgExtension(),
    ],
    output_format='html',
)


def render_template(template_str: str, args: Dict[str, Any]) -> str:
    # jinja2 to md
    env = jinja2.Environment(
        loader=jinja2.DictLoader({'index.md': template_str}),
        autoescape=True,
        auto_reload=False,
    )
    env.globals['media_wrapper'] = media_wrapper
    md_str = env.get_template('index.md').render(**args)

    # md to str
    markdown_processor.reset()
    return markdown_processor.convert(md_str)


def pure_render_template(template_str: str) -> str:
    # md to str
    markdown_processor.reset()
    md_html = markdown_processor.convert(template_str)
    clean_html = bleach.clean(md_html, markdown_tags, markdown_attrs)
    # print(clean_html)
    return clean_html
