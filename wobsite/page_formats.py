from typing import IO

from lxml.html import HtmlElement, fragment_fromstring
from markdown_it import MarkdownIt

from wobsite.page import PageFormat, PageManifest
from wobsite.spec import custom_elements

class HtmlPageFormat(PageFormat):
    def __init__(self) -> None:
        super().__init__(["html", "htm"])

    def parse_page(self, manifest: PageManifest, file: IO[str]) -> HtmlElement:
        try:
            return fragment_fromstring(
                file.read(),
                # types-lxml hints create_parent as bool instead of bool | str
                create_parent=custom_elements.PAGE_CONTENT_ELEMENT # type: ignore
            )
        except Exception as e:
            raise Exception(f"Could not parse HTML page {manifest.content_file_path}") from e

class MdPageFormat(PageFormat):
    md: MarkdownIt

    def __init__(self) -> None:
        super().__init__(["md"])
        self.md = MarkdownIt('commonmark', {"breaks": True})

    def parse_page(self, manifest: PageManifest, file: IO[str]) -> HtmlElement:
        # TODO suboptimal. I would like to directly render an HtmlElement from md
        try:
            return fragment_fromstring(
                self.md.render(file.read()),
                create_parent=custom_elements.PAGE_CONTENT_ELEMENT # type: ignore
            )
        except Exception as e:
            raise Exception(f"Could not parse Markdown page {manifest.content_file_path}") from e
