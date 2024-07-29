from typing import Final

from wobsite.util import DefaultedTomlKey, RequiredTomlKey, TomlKey, TomlTable
from wobsite.spec.manifests import __common

FILE_NAME: Final[str] = "wobsite.toml"

SITE_TABLE: Final[RequiredTomlKey[TomlTable]] = RequiredTomlKey("site")
TEMPLATES_DIRECTORIES_KEY: Final[RequiredTomlKey[str]] = SITE_TABLE.subr("templates")
PAGES_DIRECTORIES_KEY: Final[RequiredTomlKey[str]] = SITE_TABLE.subr("pages")
ASSETS_DIRECTORIES_KEY: Final[TomlKey[str]] = SITE_TABLE.sub("assets")
OUTPUT_DIRECTORY_KEY: Final[DefaultedTomlKey[str]] = SITE_TABLE.subd("build", "output")

MACROS_TABLE: Final[DefaultedTomlKey[TomlTable]] = __common.TABLE_MACROS
