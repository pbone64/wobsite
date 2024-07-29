# WriteOutputPage -> ExpandMacroTags -> BuildOutputPage -> (ParsePageContent -> ParsePageManifest -> ValueLeaf, ParseTemplateContent -> ParseTemplateManifest -> ValueLeaf)

from pathlib import Path
import tomllib
from typing import override

from wobsite.compiler import ParsedPage, Target, WobsiteCompilation

import wobsite.spec.manifests.page as pagespec
from wobsite.spec.manifests.page import PageManifest

import wobsite.spec.manifests.template as templatespec
from wobsite.spec.manifests.template import TemplateManifest

class ParsePageManifest(Target[Path, PageManifest]):
    @override
    def _resolve(self, input: Path, ctx: WobsiteCompilation) -> PageManifest:
        with input.open("rb") as file:
            toml = tomllib.load(file)

        return PageManifest(
            path = input,

            file = pagespec.FILE_KEY.get_in(toml),
            template = pagespec.TEMPLATE_KEY.get_in(toml),
            output = pagespec.OUTPUT_KEY.get_in(toml),
            macro_values = {i: str(j) for i, j in pagespec.MACROS_TABLE.get_in(toml)}
        )

class ParsePageContent(Target[PageManifest, ParsedPage]):
    @override
    def _resolve(self, input: PageManifest, ctx: WobsiteCompilation) -> ParsedPage:
        #dir = input.path.parent
        #path = dir.joinpath(input.file)

        return super()._resolve(input, ctx)

class ParseTemplateManifest(Target[Path, TemplateManifest]):
    @override
    def _resolve(self, input: Path, ctx: WobsiteCompilation) -> TemplateManifest:
        with input.open("rb") as file:
            toml = tomllib.load(file)

        return TemplateManifest(
            path = input,

            name = templatespec.NAME_KEY.get_in(toml),
            file = templatespec.FILE_KEY.get_in(toml),
            macro_values = {i: str(j) for i, j in templatespec.MACROS_TABLE.get_in(toml)}
        )
