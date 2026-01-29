import re

from bs4 import BeautifulSoup


RE_IMG_MARKDOWN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def extract_image_urls(markup: str) -> list[str]:
    urls = []
    soup = BeautifulSoup(markup, "html.parser")
    urls.extend(str(src) for img in soup.find_all("img") if (src := img.get("src")))
    urls.extend(match.group(1) for match in RE_IMG_MARKDOWN.finditer(markup))
    return urls
