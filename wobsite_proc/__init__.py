from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Callable, List, Optional

from wobsite_proc import template, page
from wobsite_proc.log import Log
from wobsite_proc.manifests import page as page_manifest, site as site_manifest, template as template_manifest
def compile_wobsite(path: Path) -> bool:
    log = Log()

    log.info(f"Compiling {path}")

    manifest = site_manifest.get_in(path)

    if manifest is None:
        log.err(f"{path / site_manifest.FILE_NAME} does not exist")
        return False

    template_paths = __get_dirs(
        path,
        manifest.templates,
        lambda p: log.err(f"Template path {p} does not exist")
    )

    if template_paths is None:
        return False
    
    template_manifests = {
        m.name: m for m in [
            template_manifest.parse_file(m, p) for p in template_paths for m in __find(p, "toml")
        ]
    }

    log.info(f"Found {len(template_manifests)} template(s)")

    page_paths = __get_dirs(
        path,
        manifest.pages,
        lambda p: log.err(f"Page path {p} does not exist")
    )

    if page_paths is None:
        return False

    page_manifests = [
        page_manifest.parse_file(m, p) for p in page_paths for m in __find(p, "toml")
    ]

    log.info(f"Found {len(page_manifests)} page(s)")

    output: List[__BuildArtifact] = []
    for p in page_manifests:
        cpage = page.parse_html(p)
        rpath = p.path.parent.relative_to(p.dir) / p.file
        if p.template is None:
            log.info(f"Compiled templateless page {p.path}")
            output.append(__BuildArtifact(rpath, cpage.to_string()))
            continue

        if p.template not in template_manifests:
            log.err(f"Template {p.template} required by page {p.path} not found")
            return False
        
        p_template = template_manifests[p.template]
        ctemplate = template.parse_html(p_template)
        ctemplate.substitute_content(cpage.content, log)

        log.info(f"Compiled page {p.path} with template {p_template.name}")
        output.append(__BuildArtifact(rpath, ctemplate.to_string()))

    output_base_dir = (path / ".output")
    shutil.rmtree(output_base_dir)
    output_base_dir.mkdir(parents = True, exist_ok = True)

    for o in output:
        opath = output_base_dir / o.path
        with open(opath, "xt") as file:
            opath.parent.mkdir(parents = True, exist_ok = True)
            file.write(o.text)

    asset_paths = __get_dirs(
        path,
        manifest.assets,
        lambda p: log.err(f"Asset path {p} does not exist")
    )

    if asset_paths is None:
        log.err(f"Asset path path {path} does not exist")
        return False

    for p in asset_paths:
        for a in __find(p, None):
            rpath = a.relative_to(p)
            opath = output_base_dir / rpath
            log.info(f"Copying asset {a} to {opath}")
            shutil.copy2(a, opath)

    return True

@dataclass
class __BuildArtifact:
    path: Path
    text: str

def __get_dirs(path: Path, subdirs: List[str], err_callback: Callable[[Path], None]) -> Optional[List[Path]]:
    dirs = [path / i for i in subdirs]
    err = False

    for p in dirs:
        if not p.exists():
            err_callback(p)
            err = True

    if err:
        return None
    else:
        return dirs

def __find(path: Path, ext: str | None) -> List[Path]:
    if ext is None:
        return [p for p in path.glob(f"**/*")]
    else:
        return [p for p in path.glob(f"**/*.{ext}")]
