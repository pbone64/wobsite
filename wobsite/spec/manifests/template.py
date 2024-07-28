from typing import Final

from wobsite.util import TomlKey
from wobsite.spec.manifests import __common

FILE_EXT: Final[str] = "template.toml"

TEMPLATE_TABLE: Final[TomlKey] = TomlKey("template")
NAME_KEY: Final[TomlKey] = TEMPLATE_TABLE.sub("name")
FILE_KEY: Final[TomlKey] = TEMPLATE_TABLE.sub("file")

MACROS_TABLE: Final[TomlKey] =  __common.TABLE_MACROS
