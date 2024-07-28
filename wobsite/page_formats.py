from typing import IO
from xml.dom import minidom
import html5lib

from markdown_it import MarkdownIt

from wobsite.page import PageManifest, PageFormat

class HtmlPageFormat(PageFormat):
    def __init__(self) -> None:
        super().__init__(["html", "htm"])

    def compile_page(self, manifest: PageManifest, file: IO[str]) -> minidom.DocumentFragment:
        try:
            return html5lib.parseFragment(file, treebuilder="dom") # type: ignore
        except Exception as e:
            raise Exception(f"Could not parse HTML page {manifest.content_file_path}") from e

class MdPageFormat(PageFormat):
    md: MarkdownIt

    def __init__(self) -> None:
        super().__init__(["md"])
        self.md = MarkdownIt('commonmark', {"breaks": True})

    def compile_page(self, manifest: PageManifest, file: IO[str]) -> minidom.DocumentFragment:
        # TODO suboptimal. I would like to directly render a DocumentFragment from md
        try:
            return html5lib.parseFragment(self.md.render(file.read()), treebuilder="dom") # type: ignore
        except Exception as e:
            raise Exception(f"Could not parse Markdown page {manifest.content_file_path}") from e
