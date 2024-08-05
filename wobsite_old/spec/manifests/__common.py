from wobsite.util import DefaultedTomlKey, TomlTable
from typing import Final

TABLE_MACROS: Final[DefaultedTomlKey[TomlTable]] = DefaultedTomlKey({}, "macros")

# Macro Contexts #
# MACRO_CTX_WEBSITE: str = "site"
# MACRO_CTX_TEMPLATE: str = "template"
# MACRO_CTX_PAGE: str = "page"
