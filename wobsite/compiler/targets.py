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
    resolve: Callable[["Target[object, IN]", WobsiteCompilation], OUT]
    input: "Target[object, IN]"

class RootTarget(Generic[IN], Target[IN, None]):
    pass

class LeafTarget(Generic[OUT], Target[None, OUT]):
    pass
