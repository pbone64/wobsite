from dataclasses import dataclass
from typing import Callable, List, TypeVar, Generic

@dataclass
class WobsiteCompilation:
    pass

@dataclass
class CompiledWobsite:
    pages: List[object]

IN = TypeVar("IN", contravariant=True)
OUT = TypeVar("OUT", covariant=True)
class Target(Generic[IN, OUT]):
    def __init__(self, input: "Target[object, IN]") -> None:
        self.input = input

    resolve: Callable[["Target[object, IN]", WobsiteCompilation], OUT]
    input: "Target[object, IN]"

    def get(self, ctx: WobsiteCompilation) -> OUT:
        return self.resolve(self.input, ctx)

class RootTarget(Generic[IN], Target[IN, None]):
    pass

class LeafTarget(Generic[OUT], Target[None, OUT]):
    pass
