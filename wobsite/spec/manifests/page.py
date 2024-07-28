from typing import Final

from wobsite.util import TomlKey
from wobsite.spec.manifests import __common

FILE_EXT: Final[str] = "page.toml"

PAGE_TABLE: Final[TomlKey] = TomlKey("page")
FILE_KEY: Final[TomlKey] = PAGE_TABLE.sub("file")
TEMPLATE_KEY: Final[TomlKey] = PAGE_TABLE.sub("template")

MACROS_TABLE: Final[TomlKey] = __common.TABLE_MACROS
