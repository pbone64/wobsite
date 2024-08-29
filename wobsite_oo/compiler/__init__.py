from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Generic, override

from lxml.html import HtmlElement

IN = TypeVar("IN", contravariant=True)
OUT = TypeVar("OUT", covariant=False) # TODO Exec and RunSynchrounous don't work if OUT is covariant
CTX = TypeVar("CTX")

type TargetInput[CTX, IN] = BaseTarget[CTX, Any, IN]
class BaseTarget(Generic[CTX, IN, OUT], ABC):
    input: TargetInput[CTX, IN]

    def __init__(self, input: TargetInput[CTX, IN]) -> None:
        self.input = input

    def resolve(self, ctx: CTX) -> OUT:
        return self._resolve(self.input.resolve(ctx), ctx)

    @abstractmethod
    def _resolve(self, input: IN, ctx: CTX) -> OUT:
        pass

class Process(Generic[CTX, IN, OUT], BaseTarget[CTX, IN, OUT]):
    proc: Callable[[IN], OUT]

    def __init__(self, proc: Callable[[IN], OUT], input: BaseTarget[CTX, Any, IN]) -> None:
        self.proc = proc
        super().__init__(input)

    @override
    def _resolve(self, input: IN, ctx: CTX) -> OUT:
        return self.proc(input)

class Exec(Generic[CTX, OUT], BaseTarget[CTX, BaseTarget[CTX, Any, OUT], OUT]):
    @override
    def _resolve(self, input: BaseTarget[CTX, Any, OUT], ctx: CTX) -> OUT:
        return input.resolve(ctx)

class RootTarget(Generic[CTX, IN], BaseTarget[CTX, IN, None]):
    pass

class RunSynchronous(Generic[CTX], RootTarget[CTX, List[RootTarget[CTX, Any]]]):
    def _resolve(self, input: List[RootTarget[CTX, Any]], ctx: CTX) -> None:
        for dep in input:
            dep.resolve(ctx)

class LeafTarget(Generic[CTX, OUT], BaseTarget[CTX, None, OUT]):
    def __init__(self) -> None:
        super().__init__(UnreachableTarget[CTX]())

    @override
    def resolve(self, ctx: CTX) -> OUT:
        return self._resolve(None, ctx)

OUT1 = TypeVar("OUT1", covariant=True)
OUT2 = TypeVar("OUT2", covariant=True)
class AssembleTuple(Generic[CTX, OUT1, OUT2], LeafTarget[CTX, Tuple[OUT1, OUT2]]):
    input_1: BaseTarget[CTX, Any, OUT1]
    input_2: BaseTarget[CTX, Any, OUT2]

    def __init__(self, input_1: BaseTarget[CTX, Any, OUT1], input_2: BaseTarget[CTX, Any, OUT2]) -> None:
        self.input_1 = input_1
        self.input_2 = input_2

        super().__init__()

    @override
    def _resolve(self, input: None, ctx: CTX) -> Tuple[OUT1, OUT2]:
        return (
            self.input_1.resolve(ctx), self.input_2.resolve(ctx)
        )


class UnreachableTarget(Generic[CTX], BaseTarget[CTX, None, None]):
    def __init__(self) -> None:
        pass

    @override
    def resolve(self, ctx: CTX) -> None:
        raise Exception("Unreachable target called")
    
    def _resolve(self, input: None, ctx: CTX) -> None:
        raise Exception("Unreachable target called")


class Artifact(ABC):
    @abstractmethod
    def write_to(self, path: Path) -> None:
        pass

A = TypeVar("A", bound=Artifact)
class WriteArtifact(Generic[A], RootTarget[Any, Tuple[A, Path]]):
    def _resolve(self, input: Tuple[A, Path], ctx: Any) -> None:
        artifact = input[0]
        path = input[1]

        artifact.write_to(path)

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
