from dataclasses import dataclass
from datetime import date, datetime, time
from typing import List, Dict, override

type TomlValue = str | int | float | bool | datetime | date | time | TomlArray | TomlTable
type TomlArray = List[TomlValue]
type TomlTable = Dict[str, TomlValue]

@dataclass(init=False)
class TomlKey:
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

    def get_in(self, toml: Dict[str, TomlValue]) -> None | TomlValue:
        table = toml
        for t in self.table:
            if t not in table or not isinstance(table[t], dict):
                return None
            
            table = table[t]

            assert isinstance(table, dict)

        assert isinstance(table, dict)

        if self.key not in table:
            return None

        return table[self.key]
    
    def present_in(self, toml: TomlTable) -> bool:
        table = toml
        for t in self.table:
            if t not in table or not isinstance(table[t], dict):
                return False
            
            table = table[t]

            assert isinstance(table, dict)

        return self.key in table
    
    def subd(self, key: str, default_value: TomlValue) -> "DefaultedTomlKey":
        return DefaultedTomlKey(default_value, key, self.full_path())
    
    def subr(self, key: str) -> "RequiredTomlKey":
        return RequiredTomlKey(key, self.full_path())
    
    def sub(self, key: str) -> "TomlKey":
        return TomlKey(key, self.full_path())

    def full_path(self) -> list[str]:
        return self.table + [self.key]

    def __str__(self) -> str:
        return '.'.join(self.full_path())

class DefaultedTomlKey(TomlKey):
    default_value: TomlValue

    def __init__(self, default_value: TomlValue, key: str, table: None | str | List[str] = None):
        self.default_value = default_value
        super().__init__(key, table)

    @override
    def get_in(self, toml: TomlTable) -> TomlValue:
        s = super().get_in(toml)

        if s is None:
            return self.default_value
        else:
            return s

class RequiredTomlKey(TomlKey):
    @override
    def get_in(self, toml: TomlTable) -> TomlValue:
        s = super().get_in(toml)

        if s is None:
            raise ValueError(f"Required property {self.full_path()} is missing")

        return s


def parse_toml_path(text: str) -> tuple[str, list[str]]:
    parts = text.split('.')

    last = len(parts) - 1
    return parts[last], parts[:last]