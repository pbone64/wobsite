from typing import IO
from xml.dom import minidom
import html5lib

from wobsite.template import TemplateManifest, TemplateFormat

class HtmlTemplateFormat(TemplateFormat):
    def __init__(self):
        super().__init__(["html", "htm"])

    def compile_template(self, manifest: TemplateManifest, file: IO[str]) -> minidom.Document:
        try:
            return html5lib.parse(file, treebuilder="dom")
        except Exception as e:
            raise Exception(f"Could not parse HTML template {manifest.content_file_path}") from e
