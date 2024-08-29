from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Tuple, override

from lxml.html import builder as E

from wobsite_oo.compiler import IN, OUT, BaseTarget, OutputPage, ParsedPage, ParsedTemplate

@dataclass
class GenerationContext:
    def get_output_dir(self) -> Path:
        return Path("") # TODO

class GenerationTarget(Generic[IN, OUT], BaseTarget[GenerationContext, IN, OUT]):
    pass

class ResolveTemplatePath(GenerationTarget[str, Path]):
    @override
    def _resolve(self, input: str, ctx: GenerationContext) -> Path:
        return super()._resolve(input, ctx) # TODO

class MetaParsePage(GenerationTarget[Path, GenerationTarget[Path, ParsedPage]]):
    @override
    def _resolve(self, input: Path, ctx: GenerationContext) -> GenerationTarget[Path, ParsedPage]:
        if not input.is_file():
            raise Exception(f"{input} is not a file")

        #ext = os.path.splitext(input.name)

        return super()._resolve(input, ctx) # TODO

class MetaParseTemplate(GenerationTarget[Path, GenerationTarget[Path, ParsedTemplate]]):
    @override
    def _resolve(self, input: Path, ctx: GenerationContext) -> GenerationTarget[Path, ParsedTemplate]:
        if not input.is_file():
            raise Exception(f"{input} is not a file")

        #ext = os.path.splitext(input.name)

        return super()._resolve(input, ctx) # TODO

HTML_TAG_PAGE_PLACEHOLDER = "wobsite-page-placeholder"
class GeneratePage(GenerationTarget[Tuple[ParsedPage, ParsedTemplate | None], OutputPage]):
    @override
    def _resolve(self, input: Tuple[ParsedPage, ParsedTemplate | None], ctx: GenerationContext) -> OutputPage:
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

# FIXME two stage compilation
# class MetaBuildPage(CompileTarget[Path, WriteArtifact]):
#     @override
#     def _resolve(self, input: Path, ctx: CompilationContext) -> WriteArtifact:
#         return WriteArtifact(
#             input = Process(
#                 proc = lambda p : (p, p.path),

#                 input = BuildOutputPage(
#                     input = Exec(input = MetaCheckTemplate(
#                         input = Exec(MetaParsePage(
#                             input = ValueLeaf(input)
#                         ))
#                     ))
#                 )
#             )
#         )
