import shutil
from typing import Callable, Dict, TypeVar, List
from dataclasses import dataclass

import os
from os import path

from wobsite.spec.manifests import site as sitespec
from wobsite.spec.manifests import template as templatespec
from wobsite.spec.manifests import page as pagespec
from wobsite.site import SiteManifest, site_manifest_from_toml
from wobsite.template import CompiledTemplate, TemplateManifest, template_manifest_from_toml, TemplateCompiler
from wobsite.page import PageManifest, page_manifest_from_toml, PageCompiler
from wobsite.template_formats import HtmlTemplateFormat
from wobsite.page_formats import HtmlPageFormat, MdPageFormat

# TODO set up repeatable installs

#### TODO configuration improvements:
# TODO website-level output encoding option
# TODO custom build artifact folder
# TODO page name attribute (output page name)

#### TODO code structure improvements:
# TODO artifact path handling is incredibly cursed
# TODO unify format & processor types
# TODO unify manifest parsing

#### TODO features:
# TODO cli interface
# TODO macro expansion
# TODO incremental builds
# TODO toml attribute type validation

#### TODO documentation:
# TODO write a readme 
# TODO write spec
# TODO write tests

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
        self.manifest = site_manifest_from_toml(os.path.join(self.directory, sitespec.FILE_NAME))

        self.templates = self.__build_list(self.manifest.template_directories, templatespec.FILE_EXT, template_manifest_from_toml)

        self.pages = self.__build_list(
            self.manifest.page_directories,
            pagespec.FILE_EXT,
            page_manifest_from_toml
        )

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

    T = TypeVar('T')
    def __build_list(self, directories: List[str], ext: str, proc: Callable[[str], T]) -> List[T]:
        l = []

        for directory in directories:
            directory = path.join(self.directory, directory)
            for file in os.listdir(directory):

                if (file).endswith(ext):
                    l.append(proc(path.join(directory, file)))

        return l

    def compile(self):
        template_compiler = TemplateCompiler([ HtmlTemplateFormat() ])
        page_compiler = PageCompiler([ HtmlPageFormat(), MdPageFormat() ])

        if path.exists(self.__artifact_path()):
            shutil.rmtree(self.__artifact_path())

        os.mkdir(self.__artifact_path())

        for page in self.pages:
            print(f"Compiling page {page.content_file_path}")
            try:
                if page.template == None:
                    output = page.open_content_file().read()
                else:
                    compiled_page = page_compiler.compile(page)

                    template = self.__instantiate_template(page.template, template_compiler).clone()
                    template.substitute_content(compiled_page.content)
                    output = template.text()

                self.__write_build_artifact(f"{path.splitext(path.basename(page.content_file_path))[0]}.html", output)
            except Exception as e:
                raise Exception(f"Error while compiling {page.content_file_path}.") from e

    def __instantiate_template(self, name: str, template_compiler: TemplateCompiler):
        if name not in self.__compiled_templates:
            if name not in self.__template_lookup:
                raise ValueError(f"Template {name} not found")

            self.__compiled_templates[name] = template_compiler.compile(self.__template_lookup[name])

        return self.__compiled_templates[name].clone()

    def __artifact_path(self):
        return path.join(self.directory, ".build")

    def __write_build_artifact(self, file_name: str, text: str):
        artifact_path = path.join(self.__artifact_path(), file_name)

        if path.exists(artifact_path):
            print(f"File {artifact_path} already exists. Something is wrong")
            os.remove(artifact_path)

        with open(artifact_path, "xt") as file:
            file.write(text)
