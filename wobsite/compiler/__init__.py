from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic, override

from lxml.html import HtmlElement

IN = TypeVar("IN", contravariant=True)
OUT = TypeVar("OUT", covariant=True)

@dataclass
class CompilationContext:
    def get_output_dir(self) -> Path:
        return Path("") # TODO

class Target(Generic[IN, OUT], ABC):
    def __init__(self, input: "Target[Any, IN]") -> None:
        self.__init__(input)

    input: "Target[Any, IN]"

    def resolve(self, ctx: CompilationContext) -> OUT:
        return self._resolve(self.input.resolve(ctx), ctx) # type: ignore

    @abstractmethod
    def _resolve(self, input: IN, ctx: CompilationContext) -> OUT:
        pass

class RootTarget(Generic[IN], Target[IN, None]):
    pass

class LeafTarget(Generic[OUT], Target[None, OUT]):
    def __init__(self) -> None:
        super().__init__(UnreachableTarget())

    @override
    def resolve(self, ctx: CompilationContext) -> OUT:
        return self._resolve(None, ctx)

class UnreachableTarget(Target[None, None]):
    def __init__(self) -> None:
        pass

    @override
    def resolve(self, ctx: CompilationContext) -> None:
        raise Exception("Unreachable target called")
    
    def _resolve(self, input: None, ctx: CompilationContext) -> None:
        raise Exception("Unreachable target called")


class Artifact(ABC):
    @abstractmethod
    def write_to(self, path: Path) -> None:
        pass

@dataclass(init=False)
class PageMeta:
    template: Optional[str] = None
    output_file: Path

    def __init__(self, template: Optional[str], output_file: Path) -> None:
        self.template = template
        self.output_file = output_file

@dataclass
class WebsiteMeta:
    output_dir: Optional[str] = None

@dataclass
class ParsedPage:
    meta: PageMeta
    content: List[HtmlElement]

@dataclass
class TemplateMeta:
    pass

@dataclass
class ParsedTemplate:
    meta: TemplateMeta
    content: HtmlElement

@dataclass
class OutputPage(Artifact):
    content: HtmlElement
    path: Path

    @override
    def write_to(self, path: Path) -> None:
        return super().write_to(path)

@dataclass
class CompilationSettings:
    page_parsers: Dict[str, Callable[[LeafTarget[Path]], Target[Path, ParsedPage]]]
    template_parsers: Dict[str, Callable[[LeafTarget[Path]], Target[Path, ParsedTemplate]]]
    