from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Generic, List, Dict, TypeVar, override

type TomlValue = str | int | float | bool | datetime | date | time | TomlArray | TomlTable
type TomlArray = List[TomlValue]
type TomlTable = Dict[str, TomlValue]

T = TypeVar('T',bound=TomlValue)
N = TypeVar('N',bound=TomlValue)

@dataclass(init=False)
class TomlKey(Generic[T]):
    table: List[str]
    key: str

    def __init__(self, key: str, table: None | str | list[str] = None):
        if table is None:
            table = []

        if isinstance(table, str):
            self.table = [table]
        else:
            self.table = table

        parts = parse_toml_path(key)
        self.table.extend(parts[1])
        self.key = parts[0]

    def get_in(self, toml: Dict[str, TomlValue]) -> None | T:
        table = toml
        for t in self.table:
            if t not in table or not isinstance(table[t], dict):
                return None
            
            table = table[t]

            assert isinstance(table, dict)

        assert isinstance(table, dict)

        if self.key not in table:
            return None
        
        p = table[self.key]

        # TODO FIXME THIS IS INCREDIBLY BROKEN. TYPES ARE NOT CHECKED
        return p # type: ignore
    
    def present_in(self, toml: TomlTable) -> bool:
        table = toml
        for t in self.table:
            if t not in table or not isinstance(table[t], dict):
                return False
            
            table = table[t]

            assert isinstance(table, dict)

        return self.key in table
    
    def subd(self, key: str, default_value: N) -> "DefaultedTomlKey[N]":
        return DefaultedTomlKey[N](default_value, key, self.full_path())
    
    # _ args are to make methods generic
    def subr(self, key: str, _: List[N] = []) -> "RequiredTomlKey[N]":
        return RequiredTomlKey[N](key, self.full_path())
    
    def sub(self, key: str, _: List[N] = []) -> "TomlKey[N]":
        return TomlKey[N](key, self.full_path())

    def full_path(self) -> list[str]:
        return self.table + [self.key]

    def __str__(self) -> str:
        return '.'.join(self.full_path())

class DefaultedTomlKey(Generic[T], TomlKey[T]):
    default_value: T

    def __init__(self, default_value: T, key: str, table: None | str | List[str] = None):
        self.default_value = default_value
        super().__init__(key, table)

    @override
    def get_in(self, toml: TomlTable) -> T:
        s = super().get_in(toml)

        if s is None:
            return self.default_value
        else:
            return s

class RequiredTomlKey(Generic[T], TomlKey[T]):
    @override
    def get_in(self, toml: TomlTable) -> T:
        s = super().get_in(toml)

        if s is None:
            raise ValueError(f"Required property {self.full_path()} is missing")

        return s


def parse_toml_path(text: str) -> tuple[str, list[str]]:
    parts = text.split('.')

    last = len(parts) - 1
    return parts[last], parts[:last]