from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Final

from wobsite_proc.toml_utils import RequiredTomlString, RequiredTomlTable

KEY_TEMPLATE_TABLE: Final[RequiredTomlTable] = RequiredTomlTable("template")

KEY_FILE: Final[RequiredTomlString] = RequiredTomlString("file", KEY_TEMPLATE_TABLE)
KEY_NAME: Final[RequiredTomlString] = RequiredTomlString("name", KEY_TEMPLATE_TABLE)

@dataclass
class TemplateManifest:
    path: Path
    name: str
    file: str

def parse_file(path: Path) -> TemplateManifest:
    with path.open("rb") as file:
        toml = tomllib.load(file)

    return TemplateManifest(
        path = path,
        name = KEY_NAME.get_in(toml),
        file = KEY_FILE.get_in(toml)
    )
