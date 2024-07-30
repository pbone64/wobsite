from pathlib import Path
from typing import Any, Callable, Generic, Optional, Tuple, TypeVar, override

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
OUT = TypeVar("OUT")
class ValueLeaf(Generic[OUT], LeafTarget[OUT]):
    value: OUT

    def __init__(self, value: OUT) -> None:
        self.value = value

    def _resolve(self, input: None, ctx: WobsiteCompilation) -> OUT:
        return self.value

# class RunSynchronous(RootTarget[List[RootTarget[Any]]]):
#     depenedencies: List[Target[Any, Any]]

#     def __init__(self, dependencies: List[RootTarget[Any]]) -> None:
#         super().__init__(ValueLeaf(dependencies))

#     def _resolve(self, input: List[RootTarget[Any]], ctx: WobsiteCompilation) -> None:
#         for dep in self.depenedencies:
#             dep.resolve(ctx)

OUT1 = TypeVar("OUT1")
OUT2 = TypeVar("OUT2")
class AssembleTuple(Generic[OUT1, OUT2], LeafTarget[Tuple[OUT1, OUT2]]):
    input_1: Target[Any, OUT1]
    input_2: Target[Any, OUT2]

    def __init__(self, input_1: Target[Any, OUT1], input_2: Target[Any, OUT2]) -> None:
        self.input_1 = input_1
        self.input_2 = input_2

        super().__init__()

    @override
    def _resolve(self, input: None, ctx: WobsiteCompilation) -> Tuple[OUT1, OUT2]:
        return (
            self.input_1.resolve(ctx), self.input_2.resolve(ctx)
        )

class ConditionallyAssembleTuple(Generic[OUT1, OUT2], AssembleTuple[OUT1, Optional[OUT2]]):
    condition: Callable[[OUT1], bool]

    def __init__(self, input_1: Target[Any, OUT1], condition: Callable[[OUT1], bool], input_2: Target[Any, OUT2]) -> None:
        self.condition = condition

        super().__init__(input_1, input_2)

    @override
    def _resolve(self, input: None, ctx: WobsiteCompilation) -> Tuple[OUT1, Optional[OUT2]]:
        c = self.input_1.resolve(ctx)

        if self.condition(c):
            return (c, self.input_2.resolve(ctx))
        else:
            return (c, None)
        
# C = TypeVar("C")
# class Conditional(Generic[C, OUT], LeafTarget[OUT]):
#     intermediate_target: Target[Any, C]
#     condition: Callable[[C], bool]
#     true: Target[Any, OUT]
#     false: Target[Any, OUT]

#     def __init__(self, intermediate_target: Target[Any, C], condition: Callable[[C], bool], true: Target[Any, OUT], false: Target[Any, OUT]) -> None:
#         self.intermediate_target = intermediate_target
#         self.condition = condition
#         self.true = true
#         self.false = false

#         super().__init__()

#     @override
#     def _resolve(self, input: None, ctx: WobsiteCompilation) -> OUT:
#         c = self.intermediate_target.resolve(ctx)

#         if self.condition(c):
#             return self.true.resolve(ctx)
#         else:
#             return self.false.resolve(ctx)


# meta keys
class BuildOutputPage(Target[Tuple[ParsedPage, ParsedTemplate | None], OutputPage]):
    @override
    def _resolve(self, input: Tuple[ParsedPage, ParsedTemplate | None], ctx: WobsiteCompilation) -> OutputPage:
        page = input[0]
        template = input[1]

        path = ctx.get_output_dir().joinpath(page.meta.output_file)

        page_content = E.DIV(page.content)
        page_content.set("id", "wobsite-page-content")

        if not template:
            return OutputPage(
                content = page_content,
                path = path
            )

        document = template.content

        e = document.find(f".//{HTML_TAG_PAGE_PLACEHOLDER}")

        if not e:
            pass # WARN: template does not contain page placeholder
        else:
            p = e.getparent()

            if not p:
                # If the placeholder element is the root, then disregard the template content entirely
                return OutputPage(
                    content = page_content,
                    path = path
                )
            else:
                p.replace(e, page_content)

        return OutputPage(
            content = page_content,
            path = path
        )

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

class ParseHtmlTemplate(Target[Path, ParsedTemplate]):
    @override
    def _resolve(self, input: Path, ctx: WobsiteCompilation) -> ParsedTemplate:
        with input.open() as file:
            document = html.document_fromstring(
                file.read(),
            )

        meta_elem = document.find(f".//{HTML_TAG_TEMPLATE_META}")

        if meta_elem:
            name = meta_elem.get(HTML_ATTRIB_TEMPLATE_META_NAME)
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

test = BuildOutputPage(
    input = ConditionallyAssembleTuple[ParsedPage, ParsedTemplate](
        condition = lambda page : page.meta.template is not None,

        input_1 = ParseHtmlPage(
            input = ValueLeaf(Path(""))
        ),

        input_2 = ParseHtmlTemplate(
            input = ValueLeaf(Path(""))
        )
    )
)

