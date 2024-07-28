from typing import Any, List, Dict, IO
from abc import abstractmethod
from dataclasses import dataclass

from os import path
from copy import deepcopy

import tomllib
from xml.dom.minidom import Document, DocumentFragment

from wobsite.spec import template_elements
from wobsite.spec.manifests import template as templatespec

@dataclass
class TemplateManifest:
    """Data structure represented by a .template.toml file"""

    manifest_file_path: str
    content_file_path: str

    content_file: str
    name: str
    macros: Dict[str, Any]

    def open_content_file(self) -> IO[str]:
        return open(self.content_file_path, "rt", encoding="utf-8")

def template_manifest_from_toml(file_path: str) -> TemplateManifest:
    if not path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} does not exist")
    
    directory = path.realpath(path.dirname(file_path))

    with open(file_path, "rb") as file:
        toml = tomllib.load(file)

    name = templatespec.NAME_KEY.get_or_default_in(toml, path.basename(file_path).split('.')[0])

    content_file = templatespec.FILE_KEY.get_in(toml)
    content_file_path = path.join(directory, content_file)

    macros: Dict[str, Any] = templatespec.MACROS_TABLE.get_or_default_in(toml, {})

    return TemplateManifest(file_path, content_file_path, content_file, name, macros)

@dataclass
class CompiledTemplate:
    manifest: TemplateManifest
    document: Document

    def clone(self) -> "CompiledTemplate":
        return CompiledTemplate(
            self.manifest,
            deepcopy(self.document)
        )
    
    def substitute_content(self, page_content: DocumentFragment) -> None:
        for node in self.document.getElementsByTagName(template_elements.PAGE_CONTENT_ELEMENT):
            node.parentNode.replaceChild(page_content, node)

    def text(self) -> str:
        return self.document.toprettyxml()

class TemplateFormat:
    extensions: List[str]

    def __init__(self, extensions: List[str]) -> None:
        self.extensions = extensions

    @abstractmethod
    def compile_template(self, manifest: TemplateManifest, file: IO[str]) -> Document:
        pass

class TemplateCompiler:
    formats: List[TemplateFormat]
    __ext_lookup: Dict[str, TemplateFormat]

    def __init__(self, formats: List[TemplateFormat]) -> None:
        self.formats = formats

        self.__ext_lookup = {}
        for f in self.formats:
            for ext in f.extensions:
                if ext in self.__ext_lookup:
                    raise Exception

                self.__ext_lookup[ext] = f

    def format_from_ext(self, ext: str) -> TemplateFormat:
        ext = ext.removeprefix('.')
        if not self.format_supported(ext):
            raise ValueError(f"{ext} is not a supported template format")

        return self.__ext_lookup[ext]
    
    def format_supported(self, ext: str) -> bool:
        return ext in self.__ext_lookup
    
    def compile(self, manifest: TemplateManifest) -> CompiledTemplate:
        ext = path.splitext(manifest.content_file_path)[1]
        parser = self.format_from_ext(ext)

        with manifest.open_content_file() as file:
            return CompiledTemplate(manifest, parser.compile_template(manifest, file))