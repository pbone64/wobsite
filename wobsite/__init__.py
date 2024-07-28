import shutil
from typing import Callable, Dict, TypeVar, List
from dataclasses import dataclass

import os
from os import path

from wobsite.spec.manifests import site as sitespec
from wobsite.spec.manifests import template as templatespec
from wobsite.spec.manifests import page as pagespec
from wobsite.website import SiteManifest, site_manifest_from_toml
from wobsite.template import CompiledTemplate, TemplateManifest, template_manifest_from_toml, TemplateCompiler
from wobsite.page import PageManifest, page_manifest_from_toml, PageCompiler
from wobsite.template_formats import HtmlTemplateFormat
from wobsite.page_formats import HtmlPageFormat, MdPageFormat

#### TODO switch from html5lib + minidom to lxml

#### TODO configuration improvements:
# TODO custom build artifact folder
# TODO page name attribute (output page name)
# TODO website-level output encoding option

#### TODO code structure improvements:
# TODO artifact path handling is incredibly cursed
# TODO better errors
# TODO unify format & processor types
# TODO unify manifest parsing

#### TODO features:
# TODO asset folder handling
# TODO warn about improper manifest rather than failing
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
    __compiled_templates: Dict[str, CompiledTemplate]

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
        self.__compiled_templates = {}

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

        if path.exists(self.__artifact_path()):
            shutil.rmtree(self.__artifact_path())

        os.mkdir(self.__artifact_path())

        for page in self.pages:
            print(f"Compiling page {page.content_file_path}")
            try:
                if page.template is None:
                    output = page.open_content_file().read()
                else:
                    compiled_page = page_compiler.compile(page)

                    template = self.__instantiate_template(page.template, template_compiler).clone()
                    template.substitute_content(compiled_page.content)
                    output = template.text()

                self.__write_build_artifact(f"{path.splitext(path.basename(page.content_file_path))[0]}.html", output)
            except Exception as e:
                raise Exception(f"Error while compiling {page.content_file_path}.") from e

    def __instantiate_template(self, name: str, template_compiler: TemplateCompiler) -> CompiledTemplate:
        if name not in self.__compiled_templates:
            if name not in self.__template_lookup:
                raise ValueError(f"Template {name} not found")

            self.__compiled_templates[name] = template_compiler.compile(self.__template_lookup[name])

        return self.__compiled_templates[name].clone()

    def __artifact_path(self) -> str:
        return path.join(self.directory, self.manifest.output_directory)

    def __write_build_artifact(self, file_name: str, text: str) -> None:
        artifact_path = path.join(self.__artifact_path(), file_name)

        if path.exists(artifact_path):
            print(f"File {artifact_path} already exists. Something is wrong")
            os.remove(artifact_path)

        with open(artifact_path, "xt") as file:
            file.write(text)
