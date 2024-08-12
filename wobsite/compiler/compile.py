from pathlib import Path
from typing import Tuple, override

from lxml.html import builder as E

from wobsite.compiler import OutputPage, ParsedPage, ParsedTemplate, CompileTarget, CompilationContext

class ResolveTemplatePath(CompileTarget[str, Path]):
    @override
    def _resolve(self, input: str, ctx: CompilationContext) -> Path:
        return super()._resolve(input, ctx) # TODO
    
class MetaParsePage(CompileTarget[Path, CompileTarget[Path, ParsedPage]]):
    @override
    def _resolve(self, input: Path, ctx: CompilationContext) -> CompileTarget[Path, ParsedPage]:
        if not input.is_file():
            raise Exception(f"{input} is not a file")

        #ext = os.path.splitext(input.name)

        return super()._resolve(input, ctx) # TODO

class MetaParseTemplate(CompileTarget[Path, CompileTarget[Path, ParsedTemplate]]):
    @override
    def _resolve(self, input: Path, ctx: CompilationContext) -> CompileTarget[Path, ParsedTemplate]:
        if not input.is_file():
            raise Exception(f"{input} is not a file")

        #ext = os.path.splitext(input.name)

        return super()._resolve(input, ctx) # TODO

# FIXME two stage compilation
# class MetaCheckTemplate(CompileTarget[ParsedPage, LeafTarget[CompilationContext, Tuple[ParsedPage, ParsedTemplate | None]]]):
#     @override
#     def _resolve(self, input: ParsedPage, ctx: CompilationContext) -> LeafTarget[CompilationContext, Tuple[ParsedPage, ParsedTemplate | None]]:
#         if input.meta.template is None:
#             return ValueLeaf((input, None))
#         else:
#             return AssembleTuple[CompilationContext, ParsedPage, ParsedTemplate | None](
#                 input_1 = ValueLeaf(input),
#                 input_2 = Exec(input = MetaParseTemplate(
#                     input = ResolveTemplatePath(
#                         input = ValueLeaf(input.meta.template)
#                     )
#                 ))
#             )

HTML_TAG_PAGE_PLACEHOLDER = "wobsite-page-placeholder"
class BuildOutputPage(CompileTarget[Tuple[ParsedPage, ParsedTemplate | None], OutputPage]):
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
