from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Final

from wobsite.util import DefaultedTomlKey, RequiredTomlKey, TomlTable
from wobsite.spec.manifests import __common

FILE_EXT: Final[str] = "template.toml"

TEMPLATE_TABLE: Final[RequiredTomlKey[TomlTable]] = RequiredTomlKey("template")
NAME_KEY: Final[RequiredTomlKey[str]] = TEMPLATE_TABLE.subr("name")
FILE_KEY: Final[RequiredTomlKey[str]] = TEMPLATE_TABLE.subr("file")

MACROS_TABLE: Final[DefaultedTomlKey[TomlTable]] =  __common.TABLE_MACROS

@dataclass
class TemplateManifest:
    """Data structure represented by a .page.toml file"""

    path: Path

    name: str
    file: str
    macro_values: Dict[str, str]
