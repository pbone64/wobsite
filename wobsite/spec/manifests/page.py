from typing import Final

from wobsite.util import DefaultedTomlKey, RequiredTomlKey, TomlKey
from wobsite.spec.manifests import __common

FILE_EXT: Final[str] = "page.toml"

PAGE_TABLE: Final[RequiredTomlKey] = RequiredTomlKey("page")
FILE_KEY: Final[RequiredTomlKey] = PAGE_TABLE.subr("file")
TEMPLATE_KEY: Final[TomlKey] = PAGE_TABLE.subr("template")
OUTPUT_KEY: Final[TomlKey] = PAGE_TABLE.sub("output")

MACROS_TABLE: Final[DefaultedTomlKey] = __common.TABLE_MACROS
