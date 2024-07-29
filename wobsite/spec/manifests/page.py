from dataclasses import dataclass
from typing import Dict, Final

from wobsite.util import DefaultedTomlKey, RequiredTomlKey, TomlKey, TomlTable
from wobsite.spec.manifests import __common

FILE_EXT: Final[str] = "page.toml"

PAGE_TABLE: Final[RequiredTomlKey[TomlTable]] = RequiredTomlKey("page")
FILE_KEY: Final[RequiredTomlKey[str]] = PAGE_TABLE.subr("file")
TEMPLATE_KEY: Final[RequiredTomlKey[str]] = PAGE_TABLE.subr("template")
OUTPUT_KEY: Final[TomlKey[str]] = PAGE_TABLE.sub("output")

MACROS_TABLE: Final[DefaultedTomlKey[TomlTable]] = __common.TABLE_MACROS

@dataclass
class PageManifest:
    """Data structure represented by a .page.toml file"""

    file: str
    template: str
    output: str | None
    macro_values: Dict[str, str]
