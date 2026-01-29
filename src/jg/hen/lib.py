import re

from lxml import html
from lxml.etree import ParserError


def extract_image_urls(readme: str) -> list[str]:
    urls = []
    try:
        html_tree = html.fragment_fromstring(readme, create_parent=True)
    except (ParserError, TypeError):
        html_tree = None
    if html_tree is not None:
        urls.extend(
            src for img in html_tree.cssselect("img") if (src := img.get("src"))
        )
    urls.extend(match.group(1) for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", readme))
    return urls
