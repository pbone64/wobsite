from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, TypeVar, Generic, override

from lxml.html import HtmlElement

IN = TypeVar("IN", contravariant=True)
OUT = TypeVar("OUT", covariant=True)

@dataclass(init=False)
class PageMeta:
    template: Optional[str] = None
    output_file: Path

    def __init__(self, template: Optional[str], output_file: Path) -> None:
        self.template = template
        self.output_file = output_file

@dataclass
class ParsedPage:
    meta: PageMeta
    content: List[HtmlElement]

@dataclass
class TemplateMeta:
    name: Optional[str] = None

@dataclass
class ParsedTemplate:
    meta: TemplateMeta
    content: HtmlElement

@dataclass
class OutputPage:
    content: HtmlElement
    path: Path

@dataclass
class WebsiteMeta:
    output_dir: Optional[str] = None

@dataclass
class WobsiteCompilation:
    def get_output_dir(self) -> Path:
        return Path("")

@dataclass
class CompiledWobsite:
    pages: List[object]

class Target(Generic[IN, OUT], ABC):
    def __init__(self, input: "Target[Any, IN]") -> None:
        self.__init__(input)

    input: "Target[Any, IN]"

    def resolve(self, ctx: WobsiteCompilation) -> OUT:
        return self._resolve(self.input.resolve(ctx), ctx) # type: ignore

    @abstractmethod
    def _resolve(self, input: IN, ctx: WobsiteCompilation) -> OUT:
        pass

class RootTarget(Generic[IN], Target[IN, None]):
    pass

class LeafTarget(Generic[OUT], Target[None, OUT]):
    def __init__(self) -> None:
        super().__init__(UnreachableTarget())

    @override
    def resolve(self, ctx: WobsiteCompilation) -> OUT:
        return self._resolve(None, ctx)

class UnreachableTarget(Target[None, None]):
    def __init__(self) -> None:
        pass

    @override
    def resolve(self, ctx: WobsiteCompilation) -> None:
        raise Exception("Unreachable target called")
    
    def _resolve(self, input: None, ctx: WobsiteCompilation) -> None:
        raise Exception("Unreachable target called")