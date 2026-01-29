import asyncio
import re
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup


RE_IMG_MARKDOWN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def _parse_image_urls(markup: str) -> list[str]:
    soup = BeautifulSoup(markup, "html.parser")
    urls = [str(src) for img in soup.find_all("img") if (src := img.get("src"))]
    urls.extend(match.group(1) for match in RE_IMG_MARKDOWN.finditer(markup))
    return urls


async def extract_image_urls(markup: str) -> list[str]:
    with ThreadPoolExecutor() as executor:
        future = executor.submit(_parse_image_urls, markup)
        return future.result()
