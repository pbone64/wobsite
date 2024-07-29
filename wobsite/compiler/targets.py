# WriteOutputPage -> ExpandMacroTags -> BuildOutputPage -> (ParsePageContent -> ParsePageManifest -> ValueLeaf, ParseTemplateContent -> ParseTemplateManifest -> ValueLeaf)

import tomllib
from typing import BinaryIO, override

from wobsite.compiler import Target, WobsiteCompilation
import wobsite.spec.manifests.page as pagespec
from wobsite.spec.manifests.page import PageManifest


class ParsePageManifestTarget(Target[BinaryIO, PageManifest]):
    @override
    def _resolve(self, input: BinaryIO, ctx: WobsiteCompilation) -> PageManifest:
        toml = tomllib.load(input)

        return PageManifest(
            file=pagespec.FILE_KEY.get_in(toml),
            template=pagespec.TEMPLATE_KEY.get_in(toml),
            output=pagespec.OUTPUT_KEY.get_in(toml),
            macro_values={i: str(j) for i, j in pagespec.MACROS_TABLE.get_in(toml)}
        )
