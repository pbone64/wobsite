from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, List, override

from wobsite.compiler import IN, OUT, BaseTarget
from wobsite.manifests.site import SiteManifest
from wobsite.manifests.template import TemplateManifest

@dataclass
class DiscoverContext:
    site_dir: Path
    site_manifest: SiteManifest

class DiscoverTarget(Generic[IN, OUT], BaseTarget[DiscoverContext, IN, OUT]):
    pass

class BaseMetaDiscover(Generic[OUT], DiscoverTarget[Path, OUT], ABC):
    @abstractmethod
    def parse_manifest(self, path: Path) -> OUT:
        pass

    @override
    def _resolve(self, input: Path, ctx: DiscoverContext) -> OUT:
        return self.parse_manifest(input)
    
class ParseTemplateManifest(DiscoverTarget[Path, TemplateManifest]):
    pass

class MetaDiscoverTemplates(DiscoverTarget[Path, List[ParseTemplateManifest]]):
    pass