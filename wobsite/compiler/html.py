from pathlib import Path
from typing import Optional

from lxml import etree

from wobsite.compiler import ParsedPage, Target, WobsiteCompilation

class WobsiteMeta(etree.ElementBase):
    @property
    def template(self) -> Optional[str]:
        return self.get("template")
    
    @property
    def output_file(self) -> Optional[str]:
        return self.get("output_file")

class ParseHtmlPage(Target[Path, ParsedPage]):
    def _resolve(self, input: Path, ctx: WobsiteCompilation) -> ParsedPage:

        return super()._resolve(input, ctx)