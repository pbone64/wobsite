from pathlib import Path
from typing import override

from lxml import html

from wobsite.compiler import PageMeta, ParsedPage
from wobsite.compiler.compile import CompilationContext, CompileTarget

HTML_TAG_PAGE_META = "wobsite-page"
HTML_ATTRIB_PAGE_META_TEMPLATE = "template"
HTML_ATTRIB_PAGE_META_OUTPUT_FILE = "output_file"

HTML_TAG_PAGE_PLACEHOLDER = "wobsite-page-placeholder"

class ParseHtmlPage(CompileTarget[Path, ParsedPage]):
    @override
    def _resolve(self, input: Path, ctx: CompilationContext) -> ParsedPage:
        with input.open() as file:
            fragment = html.fragment_fromstring(
                file.read(),
                create_parent=HTML_TAG_PAGE_META # type: ignore
            )

        # TODO lxml custom elements
        meta_elem = fragment.find(f".//{HTML_TAG_PAGE_META}")

        if meta_elem:
            template = meta_elem.get(HTML_ATTRIB_PAGE_META_TEMPLATE)
            output_file = meta_elem.get(HTML_ATTRIB_PAGE_META_OUTPUT_FILE)

            if output_file:
                output_file = ctx.get_output_dir().joinpath(output_file)
            else:
                output_file = ctx.get_output_dir().joinpath(input.name)

            meta = PageMeta(template, output_file)

            fragment.remove(meta_elem)
        else:
            meta = PageMeta(None, input)

        return ParsedPage(
            meta = meta,
            content = list(fragment)
        )