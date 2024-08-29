from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Final, List, Optional

from wobsite_proc.toml_utils import RequiredTomlArray, RequiredTomlTable, strify

FILE_NAME: Final[str] = "wobsite.toml"

KEY_SITE_TABLE: Final[RequiredTomlTable] = RequiredTomlTable("site")

KEY_TEMPLATES: Final[RequiredTomlArray] = RequiredTomlArray("templates", KEY_SITE_TABLE)
KEY_PAGES: Final[RequiredTomlArray] = RequiredTomlArray("pages", KEY_SITE_TABLE)
KEY_ASSETS: Final[RequiredTomlArray] = RequiredTomlArray("assets", KEY_SITE_TABLE)

@dataclass
class SiteManifest:
    templates: List[str]
    pages: List[str]
    assets: List[str]

def parse_file(path: Path) -> SiteManifest:
    with path.open("rb") as file:
        toml = tomllib.load(file)

    return SiteManifest(
        templates = strify(KEY_TEMPLATES.get_in(toml)),
        pages = strify(KEY_PAGES.get_in(toml)),
        assets = strify(KEY_ASSETS.get_in(toml))
    )

def get_in(path: Path) -> Optional[SiteManifest]:
    mpath = (path / FILE_NAME)
    if not mpath.exists():
        return None
    
    return parse_file(path)