from typing import IO

from lxml import html
from lxml.etree import _ElementTree # type: ignore

from wobsite.template import TemplateManifest, TemplateFormat

class HtmlTemplateFormat(TemplateFormat):
    def __init__(self) -> None:
        super().__init__(["html", "htm"])

    def parse_template(self, manifest: TemplateManifest, file: IO[str]) -> _ElementTree:
        try:
            return html.parse(file)
        except Exception as e:
            raise Exception(f"Could not parse HTML template {manifest.content_file_path}") from e
