from typing import Final

from wobsite.util import TomlKey
from wobsite.spec.manifests import __common


FILE_NAME: Final[str] = "wobsite.toml"

SITE_TABLE: Final[TomlKey] = TomlKey("site")
NAME_KEY: Final[TomlKey] = SITE_TABLE.sub("name")

TABLE_DIRECTORIES: Final[TomlKey] = SITE_TABLE.sub("directories")
TEMPLATES_DIRECTORIES_KEY: Final[TomlKey] = TABLE_DIRECTORIES.sub("templates")
PAGES_DIRECTORIES_KEY: Final[TomlKey] = TABLE_DIRECTORIES.sub("pages")
ASSETS_DIRECTORIES_KEY: Final[TomlKey] = TABLE_DIRECTORIES.sub("assets")

MACROS_TABLE: Final[TomlKey] = __common.TABLE_MACROS
