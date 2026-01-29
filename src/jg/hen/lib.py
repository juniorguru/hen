import re

from lxml import html


def extract_image_urls(readme: str) -> list[str]:
    urls = []
    html_tree = html.fromstring(readme)
    urls.extend(img.get("src") for img in html_tree.cssselect("img"))
    urls.extend(match.group(1) for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", readme))
    return urls
