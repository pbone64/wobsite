from typing import IO
from xml.dom import minidom
import html5lib
from markdown_it import MarkdownIt

from wobsite.page import PageManifest, PageFormat

class HtmlPageFormat(PageFormat):
    def __init__(self):
        super().__init__(["html", "htm"])

    def compile_page(self, manifest: PageManifest, file: IO[str]) -> minidom.DocumentFragment:
        return html5lib.parseFragment(file, treebuilder="dom")

class MdPageFormat(PageFormat):
    md: MarkdownIt

    def __init__(self):
        super().__init__(["md"])
        self.md = MarkdownIt('commonmark', {"breaks": True})

    def compile_page(self, manifest: PageManifest, file: IO[str]) -> minidom.DocumentFragment:
        # TODO suboptimal. I would like to directly render a DocumentFragment from md
        return html5lib.parseFragment(self.md.render(file.read()), treebuilder="dom")
