from abc import ABC, abstractmethod
from dataclasses import dataclass
from glob import iglob
from pathlib import Path
from typing import Any, Generic, Iterable, override

from wobsite_oo.compiler import IN, OUT, BaseTarget
from wobsite_oo.manifests import site as site_manifest, template as template_manifest
from wobsite_oo.manifests.site import SiteManifest
from wobsite_oo.manifests.template import TemplateManifest

@dataclass
class DiscoverContext:
    site_dir: Path
    site_manifest: SiteManifest

class DiscoverTarget(Generic[IN, OUT], BaseTarget[DiscoverContext, IN, OUT]):
    pass

class DValueLeaf(Generic[OUT], DiscoverTarget[None, OUT]):
    value: OUT

    def __init__(self, value: OUT) -> None:
        self.value = value

    def _resolve(self, input: None, ctx: DiscoverContext) -> OUT:
        return self.value

class BaseManifestParseTarget(Generic[OUT], DiscoverTarget[Path, OUT], ABC):
    @abstractmethod
    def parse_manifest(self, path: Path) -> OUT:
        pass

    @override
    def _resolve(self, input: Path, ctx: DiscoverContext) -> OUT:
        return self.parse_manifest(input)

class ParseSiteManifest(BaseManifestParseTarget[SiteManifest]):
    @override
    def parse_manifest(self, path: Path) -> SiteManifest:
        return site_manifest.parse_file(path)

class ParseTemplateManifest(BaseManifestParseTarget[TemplateManifest]):
    @override
    def parse_manifest(self, path: Path) -> TemplateManifest:
        return template_manifest.parse_file(path)

class BaseManifestDiscover(Generic[OUT], DiscoverTarget[Path, Iterable[BaseManifestParseTarget[OUT]]]):
    @abstractmethod
    def parse_manifest(self, path: DiscoverTarget[Any, Path]) -> BaseManifestParseTarget[OUT]:
        pass

    @override
    def _resolve(self, input: Path, ctx: DiscoverContext) -> Iterable[BaseManifestParseTarget[OUT]]:
        return map(lambda x: self.parse_manifest(DValueLeaf(x)), map(lambda t: Path(t), iglob(str(input.with_segments("**", "*.[Tt[Oo[Mm[Ll]")), recursive=True)))

class DiscoverTemplates(BaseManifestDiscover[TemplateManifest]):
    @override
    def parse_manifest(self, path: DiscoverTarget[Any, Path]) -> BaseManifestParseTarget[TemplateManifest]:
        return ParseTemplateManifest(path)
