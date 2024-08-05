from abc import ABC, abstractmethod
from datetime import date, datetime, time
from typing import Dict, Generic, List, TypeVar, override

type TomlValue = str | int | float | bool | datetime | date | time | TomlArray | TomlTable
type TomlArray = List[TomlValue]
type TomlTable = Dict[str, TomlValue]

T = TypeVar("T", bound = TomlValue, covariant = True)
class OptionalTomlKey(Generic[T], ABC):
    table: List[str]
    key: str

    def __init__(self, key: str, table: None | str | list[str] = None) -> None:
        if table is None:
            self.table = []
        elif isinstance(table, str):
            self.table = [table]
        else:
            self.table = table

        parts = parse_toml_path(key)
        self.table.extend(parts[1])
        self.key = parts[0]

    @abstractmethod
    def _checktype(self, value: TomlValue) -> bool:
        pass

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

        if self._checktype(p):
            return p # type: ignore
        # This list check is an annoying hack but checktype should be fast so I'm not worried
        if self._checktype([p]):
            return [p] # type: ignore
        else:
            return None
        
    def full_path(self) -> list[str]:
        return self.table + [self.key]

class RequiredTomlKey(Generic[T], OptionalTomlKey[T]):
    @override
    def get_in(self, toml: Dict[str, TomlValue]) -> T:
        v = super().get_in(toml)

        if v is None:
            raise Exception(f"Required toml value {self.full_path} not found.")

        return v
    
class RequiredTomlTable(RequiredTomlKey[TomlTable]):
    @override
    def _checktype(self, value: TomlValue) -> bool:
        return isinstance(value, (dict
            #List[str], List[int], List[float], List[bool], List[datetime], List[date], List[time],
            #Dict[str, str], Dict[str, int], Dict[str, float], Dict[str, bool], Dict[str, datetime], Dict[str, date], Dict[str, time]
        ))

class RequiredTomlArray(RequiredTomlKey[TomlArray]):
    @override
    def _checktype(self, value: TomlValue) -> bool:
        return isinstance(value, list)

class RequiredTomlString(RequiredTomlKey[str]):
    @override
    def _checktype(self, value: TomlValue) -> bool:
        return isinstance(value, str)

class DefaultedTomlKey(Generic[T], OptionalTomlKey[T]):
    default_value: T

    def __init__(self, default_value: T, key: str, table: None | str | List[str] = None) -> None:
        self.default_value = default_value
        super().__init__(key, table)

    @override
    def get_in(self, toml: Dict[str, TomlValue]) -> T:
        v = super().get_in(toml)

        if v is None:
            return self.default_value

        return v

def parse_toml_path(text: str) -> tuple[str, list[str]]:
    parts = text.split('.')

    last = len(parts) - 1
    return parts[last], parts[:last]
