from typing import Any, List, Dict, IO
from abc import abstractmethod
from dataclasses import dataclass

from os import path

import tomllib
from lxml.html import HtmlElement

from wobsite.spec.manifests import page as pagespec
    

def page_manifest_from_toml(file_path: str) -> PageManifest:
    if not path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} does not exist")

    directory = path.realpath(path.dirname(file_path))

    with open(file_path, "rb") as file:
        toml = tomllib.load(file)

    content_file = pagespec.FILE_KEY.get_in(toml)
    content_file_path = path.join(directory, content_file)

    output_file = pagespec.OUTPUT_KEY.get_or_default_in(
        toml,
        path.splitext(path.basename(content_file))[0]
    )

    template = pagespec.TEMPLATE_KEY.get_in(toml)
    macro_values: Dict[str, Any] = pagespec.MACROS_TABLE.get_or_default_in(toml, {})

    return PageManifest(file_path, content_file_path, content_file, output_file, template, macro_values)

@dataclass
class ParsedPage:
    manifest: PageManifest
    content: HtmlElement

class PageFormat:
    extensions: List[str]

    def __init__(self, extensions: List[str]) -> None:
        self.extensions = extensions

    @abstractmethod
    def parse_page(self, manifest: PageManifest, file: IO[str]) -> HtmlElement:
        pass

class PageParser:
    formats: List[PageFormat]
    __ext_lookup: Dict[str, PageFormat]

    def __init__(self, formats: List[PageFormat]) -> None:
        self.formats = formats


        self.__ext_lookup = {}
        for f in self.formats:
            for ext in f.extensions:
                if ext in self.__ext_lookup:
                    raise Exception

                self.__ext_lookup[ext] = f

    def format_from_ext(self, ext: str) -> PageFormat:
        ext = ext.removeprefix('.')
        if not self.format_supported(ext):
            raise ValueError(f"{ext} is not a supported page format")

        return self.__ext_lookup[ext]
    
    def format_supported(self, ext: str) -> bool:
        return ext in self.__ext_lookup
    
    def parse(self, manifest: PageManifest) -> ParsedPage:
        ext = path.splitext(manifest.content_file_path)[1]
        parser = self.format_from_ext(ext)

        with manifest.open_content_file() as file:
            return ParsedPage(manifest, parser.parse_page(manifest, file))
