# WriteOutputPage -> ExpandMacroTags -> BuildOutputPage -> (ParsePageContent -> ParsePageManifest -> ValueLeaf, ParseTemplateContent -> ParseTemplateManifest -> ValueLeaf)

from pathlib import Path

from wobsite.compiler import ParsedPage, Target, WobsiteCompilation

class ParseMdPage(Target[Path, ParsedPage]):
    def _resolve(self, input: Path, ctx: WobsiteCompilation) -> ParsedPage:
        raise Exception("md parsing not implemented")
