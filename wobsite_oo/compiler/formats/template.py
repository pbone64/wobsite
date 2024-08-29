from pathlib import Path
from typing import override

from lxml import html

from wobsite_oo.compiler import ParsedTemplate, TemplateMeta
from wobsite_oo.compiler.generate import GenerationContext, GenerationTarget

class ParseHtmlTemplate(GenerationTarget[Path, ParsedTemplate]):
    @override
    def _resolve(self, input: Path, ctx: GenerationContext) -> ParsedTemplate:
        with input.open() as file:
            document = html.document_fromstring(
                file.read(),
            )

        return ParsedTemplate(
            meta = TemplateMeta(),
            content = document
        )