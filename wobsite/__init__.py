import shutil
from typing import Callable, Dict, TypeVar, List
from dataclasses import dataclass

import os
from os import path

from wobsite.macro import MacroStack
from wobsite.spec.manifests import site as sitespec
from wobsite.spec.manifests import template as templatespec
from wobsite.spec.manifests import page as pagespec
from wobsite.website import SiteManifest, site_manifest_from_toml
from wobsite.template import TemplateManifest, template_manifest_from_toml, TemplateCompiler
from wobsite.page import PageManifest, page_manifest_from_toml, PageCompiler
from wobsite.template_formats import HtmlTemplateFormat
from wobsite.page_formats import HtmlPageFormat, MdPageFormat

#### TODO switch from html5lib + minidom to lxml

#### TODO configuration improvements:
# TODO website-level output encoding option

#### TODO code structure improvements:
# TODO artifact path handling is incredibly cursed
# TODO better errors
# TODO unify format & processor types
# TODO unify manifest parsing

#### TODO features:
# TODO warn about improper manifests rather than failing
# TODO toml attribute type validation
# TODO macro expansion
# TODO incremental builds

#### TODO documentation:
# TODO write docs
# TODO write tests

# Is this seriously how generics are meant to be used? This seems wrong
T = TypeVar('T')

@dataclass(init=False)
class Wobsite:
    directory: str
    manifest: SiteManifest

    templates: List[TemplateManifest]
    pages: List[PageManifest]

    __template_lookup: Dict[str, TemplateManifest]

    def __init__(self, path: str):
        self.directory = os.path.realpath(os.path.basename(path))

        site_manifest_path = os.path.join(self.directory, sitespec.FILE_NAME)

        try:
            self.manifest = site_manifest_from_toml(site_manifest_path)
        except FileNotFoundError as e:
            raise Exception(f"{self.directory} does not contain a site manifest (wobsite.toml)")
        except Exception as e:
            raise Exception(f"Could not parse site manifest at {site_manifest_path}") from e

        try:
            self.templates = self.__build_list(
                self.manifest.template_directories,
                templatespec.FILE_EXT,
                template_manifest_from_toml
            )
        except Exception as e:
            raise Exception(f"Could not parse template manifests") from e

        try:
            self.pages = self.__build_list(
                self.manifest.page_directories,
                pagespec.FILE_EXT,
                page_manifest_from_toml
            )
        except Exception as e:
            raise Exception(f"Could not parse page manifests") from e

        self.__template_lookup = {}

        for template in self.templates:
            if template.name in self.__template_lookup:
                raise Exception(f"""
                                Multiple templates with name {template.name} exist:
                                  {self.__template_lookup[template.name].manifest_file_path}
                                  {template.manifest_file_path}
                                """)
            
            self.__template_lookup[template.name] = template

    def __build_list(self, directories: List[str], ext: str, proc: Callable[[str], T]) -> List[T]:
        l: List[T] = []

        for directory in directories:
            directory = path.join(self.directory, directory)
            for file in os.listdir(directory):

                if (file).endswith(ext):
                    l.append(proc(path.join(directory, file)))

        return l

    def compile(self) -> None:
        template_compiler = TemplateCompiler([ HtmlTemplateFormat() ])
        page_compiler = PageCompiler([ HtmlPageFormat(), MdPageFormat() ])

        macros = MacroStack()

        macros.push(self.manifest.macro_values)

        if path.exists(self.__artifact_path()):
            shutil.rmtree(self.__artifact_path())

        os.mkdir(self.__artifact_path())

        for page in self.pages:
            print(f"Compiling template {page.template}")
            try:
                if page.template not in self.__template_lookup:
                    raise Exception(f"Template {page.template} does not exist")

                template = self.__template_lookup[page.template]
                compiled_template = template_compiler.compile(template)
                macros.push(template.macro_values)
            except Exception as e:
                raise Exception(f"Error while compiling template {page.template}.") from e

            print(f"Compiling page {page.content_file_path}")
            try:
                compiled_page = page_compiler.compile(page)
                macros.push(page.macro_values)
            except Exception as e:
                raise Exception(f"Error while compiling page {page.manifest_file_path}.") from e
            
            print(f"Building page {page.output_file_name}")
            try:
                compiled_template.substitute_content(compiled_page.content)
            except Exception as e:
                raise Exception(f"Error while building page {page.output_file_name}.") from e
            
            print(f"Expanding macros...")
            try:
                compiled_template.expand_macros(macros)
            except Exception as e:
                raise Exception(f"Error wile expanding macros in page {page.manifest_file_path}.") from e
            
            # TODO better way to handle output
            output = compiled_template.tostring()
            self.__write_build_artifact(f"{page.output_file_name}.html", output)

            macros.pop()
            macros.pop()
            
        for asset_dir in self.manifest.asset_directories:
            asset_path = path.join(self.manifest.directory, asset_dir)
            print(f"Copying asset directory {asset_path}")

            try:
                if not os.path.exists(asset_path):
                    raise FileNotFoundError(f"{asset_path} does not exist")
            
                output_dir = path.join(self.__artifact_path(), asset_dir)
                shutil.copytree(asset_path, output_dir)
            except Exception as e:
                raise Exception(f"Error while copying asset folder {asset_dir}") from e

    def __artifact_path(self) -> str:
        return path.join(self.directory, self.manifest.output_directory)

    def __write_build_artifact(self, file_name: str, text: str) -> None:
        artifact_path = path.join(self.__artifact_path(), file_name)

        if path.exists(artifact_path):
            print(f"File {artifact_path} already exists. Something is wrong")
            os.remove(artifact_path)

        with open(artifact_path, "xt") as file:
            file.write(text)
