from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


async def extract_image_urls(markup: str | None) -> list[str]:
    if not markup:
        return []
    soup = BeautifulSoup(markup, "html.parser")
    return [str(src) for img in soup.find_all("img") if (src := img.get("src"))]


async def extract_title(readme: str | None) -> str | None:
    if not readme:
        return None
    soup = BeautifulSoup(readme, "html.parser")
    heading = soup.find(["h1", "h2"])
    return heading.get_text(strip=True) if heading else None


def make_urls_absolute(
    urls: list[str], repo_owner: str, repo_name: str, branch: str
) -> list[str]:
    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/"
    return [_make_url_absolute(url, raw_url) for url in urls]


def _make_url_absolute(url: str, base_url: str) -> str:
    if urlparse(url).scheme:
        return url
    url = url[2:] if url.startswith("./") else url
    return urljoin(base_url, url)
