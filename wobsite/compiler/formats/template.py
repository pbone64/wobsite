from pathlib import Path
from typing import override

from lxml import html

from wobsite.compiler import CompilationContext, ParsedTemplate, CompileTarget, TemplateMeta

class ParseHtmlTemplate(CompileTarget[Path, ParsedTemplate]):
    @override
    def _resolve(self, input: Path, ctx: CompilationContext) -> ParsedTemplate:
        with input.open() as file:
            document = html.document_fromstring(
                file.read(),
            )

        # meta_elem = document.find(f".//{HTML_TAG_TEMPLATE_META}")

        # if meta_elem:
        #     name = meta_elem.get(HTML_ATTRIB_TEMPLATE_META_NAME)
        #     meta = TemplateMeta(name)

        #     parent = meta_elem.getparent()

        #     if parent:
        #         meta_elem.remove(parent)
        # else:
        #     meta = TemplateMeta()

        return ParsedTemplate(
            meta = TemplateMeta(),
            content = document
        )