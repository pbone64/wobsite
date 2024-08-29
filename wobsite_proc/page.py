from dataclasses import dataclass

from lxml import html, etree
from lxml.html import HtmlElement

from wobsite_proc.manifests.page import PageManifest

@dataclass
class ParsedPage:
    manifest: PageManifest
    content: HtmlElement

    def to_string(self) -> str:
        return etree.tostring(self.content, encoding="unicode", method="html")

def parse_html(manifest: PageManifest) -> ParsedPage:
    path = (manifest.path / manifest.file)

    with path.open() as file:
        fragment = html.fragment_fromstring(
            file.read(),
            create_parent = "wobsite-page-content" # type: ignore
        )

    return ParsedPage(
        manifest = manifest,
        content = fragment
    )