from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Final, Optional

from wobsite_proc.toml_utils import OptionalTomlString, RequiredTomlString, RequiredTomlTable

KEY_PAGE_TABLE: Final[RequiredTomlTable] = RequiredTomlTable("page")

KEY_FILE: Final[RequiredTomlString] = RequiredTomlString("file", KEY_PAGE_TABLE)
KEY_TEMPLATE: Final[OptionalTomlString] = OptionalTomlString("template", KEY_PAGE_TABLE)

@dataclass
class PageManifest:
    dir: Path
    path: Path
    file: str
    template: Optional[str]

def parse_file(path: Path, dir: Path) -> PageManifest:
    with path.open("rb") as file:
        toml = tomllib.load(file)

    return PageManifest(
        dir = dir,
        path = path,
        file = KEY_FILE.get_in(toml),
        template = KEY_TEMPLATE.get_in(toml)
    )
