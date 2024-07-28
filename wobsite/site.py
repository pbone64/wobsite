from typing import Any, Dict, List
from dataclasses import dataclass

from os import path

import tomllib

from wobsite.spec.manifests import site as sitespec
from wobsite.util import TomlKey

@dataclass
class SiteManifest:
    """Data structure represented by wobsite.manifest.toml"""

    directory: str

    name: str

    template_directories: List[str]
    page_directories: List[str]
    asset_directories: List[str]

    macro_values: Dict[str, Any]

def site_manifest_from_toml(file_path: str) -> SiteManifest:
    if not path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} does not exist")

    directory = path.basename(file_path)

    with open(file_path, "rb") as file:
        toml = tomllib.load(file)

    name = sitespec.NAME_KEY.get_in(toml)

    template_directories = __get_directories_list(toml, sitespec.TEMPLATES_DIRECTORIES_KEY)
    page_directories = __get_directories_list(toml, sitespec.PAGES_DIRECTORIES_KEY)
    asset_directories = __get_directories_list(toml, sitespec.ASSETS_DIRECTORIES_KEY)

    macro_values: Dict[str, Any] = sitespec.MACROS_TABLE.get_or_default_in(toml, {})

    return SiteManifest(directory, name, template_directories, page_directories, asset_directories, macro_values)

def __get_directories_list(toml: Dict[str, Any], key: TomlKey) -> List[str]:
    value = key.get_in(toml)
    if isinstance(value, str):
        return [value]
    elif isinstance(value, list):
        return value
    else:
        raise Exception("Unsupported type")
