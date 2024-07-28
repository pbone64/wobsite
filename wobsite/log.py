from typing import Callable
from dataclasses import dataclass

@dataclass
class Log:
    print_delegate: Callable[[str], None] = print
    indent_str = "  "
    indent_count = 0

    def indent(self):
        self.indent_count += 1

    def outdent(self):
        self.indent_count -= 1

        if self.indent_count < 0:
            self.indent_count = 0

    def print(self, msg: str):
        self.print_delegate(self.__get_indent() + msg)

    def info(self, msg: str):
        self.print(msg)

    def warn(self, msg: str):
        self.print(f"WARNING: {msg}")

    def err(self, msg: str):
        self.print(f"Error: {msg}")

    def __get_indent(self) -> str:
        return self.indent_str * self.indent_count
