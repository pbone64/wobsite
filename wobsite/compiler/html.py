from pathlib import Path

from lxml import html

from wobsite.compiler import PageMeta, ParsedPage, Target, WobsiteCompilation, DEFAULT_PAGE_META

META_TAG = "wobsite-meta"
META_TAG_TEMPLATE_ATTRIB = "template"
META_TAG_OUTPUT_FILE_ATTRIB = "output_file"

class ParseHtmlPage(Target[Path, ParsedPage]):
    def _resolve(self, input: Path, ctx: WobsiteCompilation) -> ParsedPage:
        fragment = html.fragment_fromstring(
            input.open().read(),
            create_parent="wobsite-page" # type: ignore
        )

        # TODO lxml custom elements
        e = fragment.find(f".//{META_TAG}")

        if e:
            template = e.attrib.get(META_TAG_TEMPLATE_ATTRIB)
            output_file = e.attrib.get(META_TAG_OUTPUT_FILE_ATTRIB)
            meta = PageMeta(template, output_file)

            fragment.remove(e)
        else:
            meta = DEFAULT_PAGE_META

        return ParsedPage(
            meta = meta,
            content = fragment[0]
        )