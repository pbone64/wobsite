from typing import Final

from wobsite.util import DefaultedTomlKey, RequiredTomlKey
from wobsite.spec.manifests import __common

FILE_EXT: Final[str] = "template.toml"

TEMPLATE_TABLE: Final[RequiredTomlKey] = RequiredTomlKey("template")
NAME_KEY: Final[RequiredTomlKey] = TEMPLATE_TABLE.subr("name")
FILE_KEY: Final[RequiredTomlKey] = TEMPLATE_TABLE.subr("file")

MACROS_TABLE: Final[DefaultedTomlKey] =  __common.TABLE_MACROS
