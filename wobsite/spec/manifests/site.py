from typing import Final

from wobsite.util import DefaultedTomlKey, RequiredTomlKey, TomlKey
from wobsite.spec.manifests import __common

FILE_NAME: Final[str] = "wobsite.toml"

SITE_TABLE: Final[RequiredTomlKey] = RequiredTomlKey("site")
TEMPLATES_DIRECTORIES_KEY: Final[RequiredTomlKey] = SITE_TABLE.subr("templates")
PAGES_DIRECTORIES_KEY: Final[RequiredTomlKey] = SITE_TABLE.subr("pages")
ASSETS_DIRECTORIES_KEY: Final[TomlKey] = SITE_TABLE.sub("assets")
OUTPUT_DIRECTORY_KEY: Final[DefaultedTomlKey] = SITE_TABLE.subd("build", "output")

MACROS_TABLE: Final[DefaultedTomlKey] = __common.TABLE_MACROS
