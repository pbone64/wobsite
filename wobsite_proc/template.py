from dataclasses import dataclass
from typing import Final

from lxml import etree, html
from lxml.html import HtmlElement

from wobsite_proc.log import Log;
from wobsite_proc.manifests.template import TemplateManifest

PAGE_CONTENT_ELEMENT: Final[str] = "wobsite-page-content"

@dataclass
class ParsedTemplate:
    manifest: TemplateManifest
    document: HtmlElement

    def substitute_content(self, page_content: HtmlElement, log: Log) -> None:
        placeholder = self.document.find(f".//{PAGE_CONTENT_ELEMENT}")

        if placeholder is None:
            log.warn(f"Template {self.manifest.name} does not contain wobsite-page-content element")
            return

        parent = placeholder.getparent()

        if parent is None:
            self.document = page_content
        else:
            parent.replace(placeholder, page_content)

    def to_string(self) -> str:
        return etree.tostring(self.document, encoding="unicode", method="html")

def parse_html(manifest: TemplateManifest) -> ParsedTemplate:
    path = (manifest.path / manifest.file)

    with path.open() as file:
        document = html.document_fromstring(
            file.read(),
        )

    return ParsedTemplate(manifest, document)