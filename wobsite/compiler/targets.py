from pathlib import Path
from typing import Generic, Tuple, TypeVar, override

from lxml import html
from lxml.html import builder as E

from wobsite.compiler import LeafTarget, OutputPage, PageMeta, ParsedPage, ParsedTemplate, Target, TemplateMeta, WobsiteCompilation

# Custom elements
HTML_TAG_PAGE_META = "wobsite-page"
HTML_ATTRIB_PAGE_META_TEMPLATE = "template"
HTML_ATTRIB_PAGE_META_OUTPUT_FILE = "output_file"

HTML_TAG_TEMPLATE_META = "wobsite-template"
HTML_ATTRIB_TEMPLATE_META_NAME = "name"

HTML_TAG_PAGE_PLACEHOLDER = "wobsite-page-placeholder"

# general targets
OUT1 = TypeVar("OUT1")
OUT2 = TypeVar("OUT2")
class AssembleTuple(Generic[OUT1, OUT2], LeafTarget[Tuple[OUT1, OUT2]]):
    input_1: Target[object, OUT1]
    input_2: Target[object, OUT2]

    def __init__(self, input_1: Target[object, OUT1], input_2: Target[object, OUT2]) -> None:
        self.input_1 = input_1
        self.input_2 = input_2

    @override
    def resolve(self, ctx: WobsiteCompilation) -> Tuple[OUT1, OUT2]:
        return (
            self.input_1.resolve(ctx), self.input_2.resolve(ctx)
        )

# meta keys

class BuildOutputPage(Target[Tuple[ParsedPage, ParsedTemplate | None], OutputPage]):
    @override
    def _resolve(self, input: Tuple[ParsedPage, ParsedTemplate | None], ctx: WobsiteCompilation) -> OutputPage:
        path = Path("")

        page = input[0]
        template = input[1]

        if not template:
            if len(page.content) < 1:
                # If page content is empty and no template is defined, create an empty <html></html> tag as content
                return OutputPage(
                    content = E.HTML(),
                    path = path
                )
            elif len(page.content) == 1:
                return OutputPage(
                    content = page.content[0],
                    path = path
                )
            else:
                return OutputPage(
                    content = E.HTML(page.content),
                    path = path
                )
            
        document = template.content

        e = document.find(f".//{HTML_TAG_PAGE_PLACEHOLDER}")

        if not e:
            pass # WARN: template does not contain page placeholder
        else:
            p = e.getparent()

            if not p:
                pass #TODO

        return super()._resolve(input, ctx)

# HTML parsers
class ParseHtmlPage(Target[Path, ParsedPage]):
    @override
    def _resolve(self, input: Path, ctx: WobsiteCompilation) -> ParsedPage:
        with input.open() as file:
            fragment = html.fragment_fromstring(
                file.read(),
                create_parent="wobsite-page" # type: ignore
            )

        # TODO lxml custom elements
        meta_elem = fragment.find(f".//{HTML_TAG_PAGE_META}")

        if meta_elem:
            template = meta_elem.attrib.get(HTML_ATTRIB_PAGE_META_TEMPLATE)
            output_file = meta_elem.attrib.get(HTML_ATTRIB_PAGE_META_OUTPUT_FILE)
            meta = PageMeta(input, template, output_file)

            fragment.remove(meta_elem)
        else:
            meta = PageMeta(input)

        return ParsedPage(
            meta = meta,
            content = list(fragment)
        )

class ParseHtmlTemplate(Target[Path, ParsedTemplate]):
    @override
    def _resolve(self, input: Path, ctx: WobsiteCompilation) -> ParsedTemplate:
        with input.open() as file:
            document = html.document_fromstring(
                file.read(),
            )

        meta_elem = document.find(f".//{HTML_TAG_TEMPLATE_META}")

        if meta_elem:
            name = meta_elem.attrib.get(HTML_ATTRIB_TEMPLATE_META_NAME)
            meta = TemplateMeta(name)

            parent = meta_elem.getparent()

            if parent:
                meta_elem.remove(parent)
        else:
            meta = TemplateMeta()

        return ParsedTemplate(
            meta = meta,
            content = document
        )
