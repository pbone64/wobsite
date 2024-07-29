from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, TypeVar, Generic, overload

@dataclass
class WobsiteCompilation:
    pass

@dataclass
class CompiledWobsite:
    pages: List[object]

IN = TypeVar("IN", contravariant=True)
OUT = TypeVar("OUT", covariant=True)
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
        pass


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
