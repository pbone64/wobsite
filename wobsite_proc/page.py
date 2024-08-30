from dataclasses import dataclass

from lxml import html, etree
from lxml.html import HtmlElement
from markdown_it import MarkdownIt

from wobsite_proc.manifests.page import PageManifest

@dataclass
class ParsedPage:
    manifest: PageManifest
    content: HtmlElement

    def to_string(self) -> str:
        return etree.tostring(self.content, encoding="unicode", method="html")

def parse_html(manifest: PageManifest) -> ParsedPage:
    path = (manifest.dir / manifest.file)

    with path.open("rt") as file:
        fragment = html.fragment_fromstring(
            file.read(),
            create_parent = "wobsite-page-content" # type: ignore
        )

    return ParsedPage(
        manifest = manifest,
        content = fragment
    )

def parse_md(manifest: PageManifest) -> ParsedPage:
    md = MarkdownIt('commonmark', {"breaks": True})
    path = (manifest.dir / manifest.file)
    
    with path.open("rt") as file:
        fragment = html.fragment_fromstring(
            md.render(file.read()),
            create_parent=custom_elements.PAGE_CONTENT_ELEMENT # type: ignore
        )

    return ParsedPage(
        manifest = manifest,
        content = fragment
    )
