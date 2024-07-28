from dataclasses import dataclass
from typing import Any, Self, List, Dict, TypeVar

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

    def get_in(self, toml: Dict[str, Any]) -> Any:
        table = toml
        for t in self.table:
            if t not in table:
                raise Exception

            table = table[t]

        if self.key not in table:
            raise Exception

        return table[self.key]
    
    T = TypeVar('T')
    def get_or_default_in(self, toml: Dict[str, Any], default: T) -> T:
        try:
            return self.get_in(toml)
        except:
            return default
    
    def exists_in(self, toml: Dict[str, Any]) -> bool:
        table = toml
        for t in self.table:
            if t not in table or not isinstance(table[t], dict):
                return False
            
            table = table[t]

        return self.key in table
    
    def sub(self, key: str) -> "TomlKey":
        return TomlKey(key, self.full_path())

    def full_path(self) -> list[str]:
        return self.table + [self.key]

    def __str__(self) -> str:
        return '.'.join(self.full_path())
    
    def __hash__(self) -> int:
        return str(self).__hash__()

def parse_toml_path(text: str) -> tuple[str, list[str]]:
    parts = text.split('.')

    last = len(parts) - 1
    return parts[last], parts[:last]