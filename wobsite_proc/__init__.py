from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from wobsite_proc import template, page
from wobsite_proc.log import Log
from wobsite_proc.manifests import page as page_manifest, site as site_manifest, template as template_manifest
def compile_wobsite(path: Path) -> bool:
    log = Log()

    manifest = site_manifest.get_in(path)

    if not manifest:
        log.err(f"{path / site_manifest.FILE_NAME} does not exist")
        return False
    
    log.info(f"Compiling {path}")

    template_paths = __get_dirs(path, manifest.templates)

    if template_paths is None:
        log.err(f"Template path {path} does not exist")
        return False
    
    template_manifests = {
        m.name: m for m in [
            template_manifest.parse_file(m) for p in template_paths for m in __find(p, "toml")
        ]
    }

    log.info(f"Found {len(template_manifests)} templates")

    page_paths = __get_dirs(path, manifest.pages)

    if page_paths is None:
        log.err(f"Page path {path} does not exist")
        return False

    page_manifests = [
        page_manifest.parse_file(m) for p in page_paths for m in __find(p, "toml")
    ]

    output: List[__BuildArtifact] = []
    for p in page_manifests:
        cpage = page.parse_html(p)
        rpath = p.path.relative_to(path)
        if p.template is None:
            log.info(f"Compiled templateless page {p.path}")
            output.append(__BuildArtifact(rpath, cpage.to_string()))

        if p.template not in template_manifests:
            log.err(f"Template {p.template} required by page {p.path} not found")
            return False
        
        p_template = template_manifests[p.template]
        ctemplate = template.parse_html(p_template)
        ctemplate.substitute_content(cpage.content, log)

        log.info(f"Compiled page {p.path} with template {p_template.name}")
        output.append(__BuildArtifact(rpath, ctemplate.to_string()))

    output_base_dir = (path / ".output")

    for o in output:
        with open(output_base_dir / o.path, "rt") as file:
            file.write(o.text)

    # TODO assets

    return True

@dataclass
class __BuildArtifact:
    path: Path
    text: str

def __get_dirs(path: Path, subdirs: List[str]) -> Optional[List[Path]]:
    dirs = [path / i for i in subdirs]

    for p in dirs:
        if not p.exists():
            return None
        
    return dirs

def __find(path: Path, ext: str) -> List[Path]:
    return [p for p in path.glob(f"**/*.{ext}")]
