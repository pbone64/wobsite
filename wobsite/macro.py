from typing import Dict, List


class MacroStack:
    __storage: List[Dict[str, str]]

    def __init__(self) -> None:
        self.__storage = []

    def push(self, macros: Dict[str, str]) -> None:
        self.__storage.append(macros)

    def pop(self) -> None:
        try:
            self.__storage.pop()
        except IndexError:
            pass

    def get_value(self, key: str) -> str:
        for d in self.__storage:
            if key in d:
                return d[key]

        return key