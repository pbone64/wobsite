import os.path
from pathlib import Path
from typing import Any, Callable, Generic, List, Tuple, TypeVar, override

from lxml import html
from lxml.html import builder as E

from wobsite.compiler import Artifact, LeafTarget, OutputPage, PageMeta, ParsedPage, ParsedTemplate, RootTarget, Target, TemplateMeta, CompilationContext

# general targets
IN = TypeVar("IN")
OUT = TypeVar("OUT")
class ValueLeaf(Generic[OUT], LeafTarget[OUT]):
    value: OUT

    def __init__(self, value: OUT) -> None:
        self.value = value

    def _resolve(self, input: None, ctx: CompilationContext) -> OUT:
        return self.value

class RunSynchronous(RootTarget[List[RootTarget[Any]]]):
    depenedencies: List[Target[Any, Any]]

    def __init__(self, dependencies: List[RootTarget[Any]]) -> None:
        super().__init__(ValueLeaf(dependencies))

    def _resolve(self, input: List[RootTarget[Any]], ctx: CompilationContext) -> None:
        for dep in self.depenedencies:
            dep.resolve(ctx)

class WriteArtifact(RootTarget[Tuple[Artifact, Path]]):
    def _resolve(self, input: Tuple[Artifact, Path], ctx: CompilationContext) -> None:
        artifact = input[0]
        path = input[1]

        artifact.write_to(path)

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
    def _resolve(self, input: None, ctx: CompilationContext) -> Tuple[OUT1, OUT2]:
        return (
            self.input_1.resolve(ctx), self.input_2.resolve(ctx)
        )

class Process(Generic[IN, OUT], Target[IN, OUT]):
    proc: Callable[[IN], OUT]

    def __init__(self, proc: Callable[[IN], OUT], input: Target[Any, IN]) -> None:
        self.proc = proc
        super().__init__(input)

    @override
    def _resolve(self, input: IN, ctx: CompilationContext) -> OUT:
        return self.proc(input)
    
class Exec(Generic[IN, OUT], Target[Target[IN, OUT], OUT]):
    @override
    def _resolve(self, input: Target[IN, OUT], ctx: CompilationContext) -> OUT:
        return input.resolve(ctx)

class BuildOutputPage(Target[Tuple[ParsedPage, ParsedTemplate | None], OutputPage]):
    @override
    def _resolve(self, input: Tuple[ParsedPage, ParsedTemplate | None], ctx: CompilationContext) -> OutputPage:
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

#### HTML parsers
# Custom elements
HTML_TAG_PAGE_META = "wobsite-page"
HTML_ATTRIB_PAGE_META_TEMPLATE = "template"
HTML_ATTRIB_PAGE_META_OUTPUT_FILE = "output_file"

HTML_TAG_PAGE_PLACEHOLDER = "wobsite-page-placeholder"

class ParseHtmlPage(Target[Path, ParsedPage]):
    @override
    def _resolve(self, input: Path, ctx: CompilationContext) -> ParsedPage:
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

class ResolveTemplatePath(Target[str, Path]):
    @override
    def _resolve(self, input: str, ctx: CompilationContext) -> Path:
        return super()._resolve(input, ctx) # TODO
    
class MetaParsePage(Target[Path, Target[Path, ParsedPage]]):
    @override
    def _resolve(self, input: Path, ctx: CompilationContext) -> Target[Path, ParsedPage]:
        if not input.is_file():
            raise Exception(f"{input} is not a file")

        ext = os.path.splitext(input.name)

        return super()._resolve(input, ctx) # TODO

class MetaParseTemplate(Target[Path, Target[Path, ParsedTemplate]]):
    @override
    def _resolve(self, input: Path, ctx: CompilationContext) -> Target[Path, ParsedTemplate]:
        if not input.is_file():
            raise Exception(f"{input} is not a file")

        ext = os.path.splitext(input.name)

        return super()._resolve(input, ctx) # TODO

class MetaCheckTemplate(Target[ParsedPage, LeafTarget[Tuple[ParsedPage, ParsedTemplate | None]]]):
    @override
    def _resolve(self, input: ParsedPage, ctx: CompilationContext) -> LeafTarget[Tuple[ParsedPage, ParsedTemplate | None]]:
        if input.meta.template is None:
            return ValueLeaf((input, None))
        else:
            return AssembleTuple[ParsedPage, ParsedTemplate | None](
                input_1 = ValueLeaf(input),
                input_2 = Exec(input = MetaParseTemplate(
                    input = ResolveTemplatePath(
                        input = ValueLeaf(input.meta.template)
                    )
                ))
            )

class MetaBuildPage(Target[Path, WriteArtifact]):
    @override
    def _resolve(self, input: Path, ctx: CompilationContext) -> WriteArtifact:
        return WriteArtifact(
            input = Process(
                proc = lambda p : (p, p.path),

                input = BuildOutputPage(
                    input = Exec(input = MetaCheckTemplate(
                        input = Exec(MetaParsePage(
                            input = ValueLeaf(input)
                        ))
                    ))
                )
            )
        )
