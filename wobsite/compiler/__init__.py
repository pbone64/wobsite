from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, TypeVar, Generic, overload

from lxml.html import HtmlElement

from wobsite.site import SiteManifest
from wobsite.spec.manifests.page import PageManifest

IN = TypeVar("IN", contravariant=True)
OUT = TypeVar("OUT", covariant=True)

@dataclass
class ParsedPage:
    manifest: PageManifest
    content: HtmlElement

class ContentParser(Generic[OUT], ABC):
    supported_extensions: List[str]

    @abstractmethod
    def __init__(self, supported_extensions: str | List[str]):
        if isinstance(supported_extensions, str):
            self.supported_extensions = [supported_extensions]
        else:
            self.supported_extensions = supported_extensions

    @abstractmethod
    def parse_content(self, content_file: Path) -> ParsedPage:
        pass

@dataclass
class WobsiteCompilation:
    manifest: SiteManifest

@dataclass
class CompiledWobsite:
    pages: List[object]

class Target(Generic[IN, OUT], ABC):
    @overload
    def __init__(self, input: "Target[object, IN]") -> None:
        self.__is_input_target = True
        self.__init__(input)

    @overload
    def __init__(self, input: IN) -> None:
        self.__is_input_target = False
        self.__init__(input)

    def __init__(self, input) -> None: # type: ignore
        self.input = input

    input: "Target[object, IN]" | IN
    __is_input_target: bool

    def resolve(self, ctx: WobsiteCompilation) -> OUT:
        if self.__is_input_target:
            return self._resolve(self.input.resolve(ctx), ctx) # type: ignore
        else:
            return self._resolve(self.input, ctx) # type: ignore

    @abstractmethod
    def _resolve(self, input: IN, ctx: WobsiteCompilation) -> OUT:
        pass

class RootTarget(Generic[IN], Target[IN, None]):
    pass

class LeafTarget(Generic[OUT], Target[None, OUT]):
    def __init__(self) -> None:
        super().__init__(None)

    def resolve(self, ctx: WobsiteCompilation) -> OUT:
        return self._resolve(None, ctx)
